# coding=utf-8
"""
Celery worker that solves the graph problem given to it
"""
from main import celery


@celery.task(bind=True)
def calculate_shuffle(self, people, connections):
    """
    Just calculates a shuffle based on the given parameters
    """
    family_obj = Family.query.get(family_id)
    time_right_now = datetime.now()

    database_families = Family.query.filter(
        Family.id.in_(
            set([familygroup.family_id for familygroup in FamilyGroup.query.filter(
                FamilyGroup.family_id == family_obj.id
            ).all()])
        )
    ).all()
    database_all_families_with_members = []
    for db_family in database_families:
        database_family_members = UserFamilyAdmin.query.filter(
            UserFamilyAdmin.family_id == db_family.id).all()
        database_all_families_with_members.append((db_family.id, database_family_members))

    user_id_to_user_number = {}
    user_number_to_user_id = {}
    start_id = 0
    for family_id, db_family in database_all_families_with_members:
        for member in db_family:
            user_number_to_user_id[start_id] = member.user_id
            user_id_to_user_number[member.user_id] = start_id
            start_id += 1

    try:
        if not UserGroupAdmin.query.filter(
                UserGroupAdmin.user_id == int(user_id) and UserGroupAdmin.admin == True).one():
            return render_template("utility/error.html",
                                   message=_("Access denied"),
                                   title=_("Error"))
    except NoResultFound:
        return render_template("utility/error.html",
                               message=_("Access denied"),
                               title=_("Error"))
    except Exception as e:
        sentry_sdk.capture_exception(e)

    families = []
    family_ids_map = {}
    for family_index, (list_family_id, list_family) in enumerate(database_all_families_with_members):
        families.insert(family_index, {})
        for person_index, person in enumerate(list_family):
            family_ids_map[family_index] = list_family_id
            families[family_index][get_person_name(person.user_id)] = user_id_to_user_number[person.user_id]

    families_shuf_ids = {}
    members_to_families = {}
    for family_id, family_members in enumerate(families):
        for person, person_id in family_members.items():
            members_to_families[person_id] = family_id

    families_to_members = {}
    for family_id, family_members in enumerate(families):
        families_to_members[family_id] = set()
        for person, person_id in family_members.items():
            currentset = families_to_members[family_id]
            currentset.update([person_id])

    last_connections = secretsanta.connectiongraph.ConnectionGraph(members_to_families, families_to_members)

    family_group = FamilyGroup.query.filter(FamilyGroup.family_id == family_obj.id).one().group_id
    for group_shuffle in Shuffle.query.filter(Shuffle.group == family_group).all():  # Get last previous shuffles
        last_connections.add(user_id_to_user_number[group_shuffle.giver],
                             user_id_to_user_number[group_shuffle.getter],
                             group_shuffle.year)

    logger.info("{} is the year of Linux Desktop".format(time_right_now.year))

    santa = secretsanta.secretsantagraph.SecretSantaGraph(families_to_members, members_to_families, last_connections)

    shuffled_ids_str = {}
    for connection in santa.generate_connections(time_right_now.year):
        families_shuf_ids[connection.source] = connection.target
        shuffled_ids_str[str(connection.source)] = str(connection.target)

    logger.info(shuffled_ids_str)

    for giver, getter in families_shuf_ids.items():
        # The assumption is that one group shouldn't have more than one shuffle a year active
        # at the same time, there can be multiple with different years
        db_entry_shuffle = Shuffle(
            giver=user_number_to_user_id[giver],
            getter=user_number_to_user_id[getter],
            year=time_right_now.year,
            group=family_group
        )
        try:
            db.session.add(db_entry_shuffle)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            sentry_sdk.capture_exception(e)

            try:
                row = Shuffle.query.filter(and_(Shuffle.giver == user_number_to_user_id[giver],
                                                Shuffle.year == time_right_now.year)).one()
                if row.getter != user_number_to_user_id[getter]:
                    row.getter = user_number_to_user_id[getter]
                    db.session.commit()
            except Exception as e2:
                db.session.rollback()
                sentry_sdk.capture_exception(e2)
    return
