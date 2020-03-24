# coding=utf-8
# Copyright: Taavi Eomäe 2018-2020
# SPDX-License-Identifier: AGPL-3.0-only
"""
Celery worker that solves the graph problem given to it
"""
from datetime import datetime
from typing import Dict, List, Tuple

import sentry_sdk
from celery.utils.log import get_task_logger
from sqlalchemy import and_

from main import celery, db
from models.events_model import ShufflingEvent
from models.family_model import Family
from models.shuffles_model import Shuffle
from models.users_model import User
from secretsanta import connectiongraph, secretsantagraph

logger = get_task_logger(__name__)

from utility_standalone import set_recursion_limit

set_recursion_limit()


@celery.task(bind=True, acks_late=True)
def calculate_shuffle(self, event_id):
    """
    Just calculates a shuffle based on the given parameters
    @warning Assumes permission has been checked
    """
    event: ShufflingEvent = ShufflingEvent.query.get(event_id).one()
    database_families: List[Family] = event.group.families

    # Gather together a list of tuples that contain the family id and a list of all its members
    database_all_families_with_members: List[Tuple[int, List[User]]] = []
    for db_family in database_families:
        database_all_families_with_members.append((db_family.id, db_family.members))

    user_id_to_user_number = {}
    user_number_to_user_id = {}
    start_id = 0
    for family_id, db_family in database_all_families_with_members:
        for member in db_family:
            user_number_to_user_id[start_id] = member.user_id
            user_id_to_user_number[member.user_id] = start_id
            start_id += 1

    families = []
    family_ids_map = {}
    # Give every family a new ID
    for family_index, (list_family_id, list_family) in enumerate(database_all_families_with_members):
        families.insert(family_index, {})
        for person_index, person in enumerate(list_family):
            family_ids_map[family_index] = list_family_id
            families[family_index][person.first_name] = user_id_to_user_number[person.user_id]

    families_shuf_ids = {}
    members_to_families = {}
    # Create a lookup table for each person to family ID
    for family_id, family_members in enumerate(families):
        for person, person_id in family_members.items():
            members_to_families[person_id] = family_id

    families_to_members = {}
    # Create a lookup table for each family to user ID
    for family_id, family_members in enumerate(families):
        families_to_members[family_id] = set()
        for person, person_id in family_members.items():
            currentset = families_to_members[family_id]
            currentset.update([person_id])

    # Create a graph for last years' shuffle
    last_connections = connectiongraph.ConnectionGraph(members_to_families, families_to_members)

    for group_shuffle in Shuffle.query.filter(Shuffle.group == event.group_id).all():  # Get last previous shuffles
        last_connections.add(user_id_to_user_number[group_shuffle.giver],
                             user_id_to_user_number[group_shuffle.getter],
                             group_shuffle.year)

    # Get current year
    time_right_now = datetime.now()
    logger.info("{} is the year of Linux Desktop".format(time_right_now.year))

    # Create a graph for
    santa = secretsantagraph.SecretSantaGraph(families_to_members, members_to_families, last_connections)

    shuffled_ids_str = {}
    for connection in santa.generate_connections(time_right_now.year):
        families_shuf_ids[connection.source] = connection.target
        shuffled_ids_str[str(connection.source)] = str(connection.target)

    logger.info(shuffled_ids_str)

    # Do sanity checking on the generated sequence
    if not basic_shuffle_sanity_check(families_shuf_ids, len(user_id_to_user_number)):
        return False

    # Store shuffle into the database
    for giver, getter in families_shuf_ids.items():
        db_entry_shuffle = Shuffle(
            giver=user_number_to_user_id[giver],
            getter=user_number_to_user_id[getter],
            event_id=event_id
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


def basic_shuffle_sanity_check(shuffle: Dict[int, int], len_people):
    """
    Performs basic shuffle sanity checking by checking for cyclicity,
    if everyone has a shuffle and noone gets two gifts

    @param shuffle: Given shuffle
    @param len_people: Amount of people in the shuffle
    @return: If the shuffle passes basic sanity checks
    """
    # If there's inequal amount of shuffles to people
    if len(shuffle) != len_people:
        logger.error("Not everyone was shuffled in the group")
        return False

    # If there's less different receivers than the amount of people
    if len(set(shuffle.values())) != len_people:
        return False

    # Create a dictionary graph,
    graph = {}
    for giver, getter in shuffle.items():
        graph[giver] = getter

    if len(graph) <= 0:
        return False

    valid = True
    while len(graph) != 0:
        getter = list(graph.keys())[0]
        valid = traverse_graph(graph, getter, getter)
        if not valid:
            return False

    return valid


def traverse_graph(graph: Dict[int, int], location: int, beginning: int):
    """
    Traverses entire graph, checks if cyclic

    @param graph: Complete graph
    @param location: Current location
    @param beginning: Where the iteration was started
    @return: if the current graph is cyclic
    """
    if location in graph.keys():
        if location != beginning:
            traverse_graph(graph, graph[location], beginning)
            graph.pop(location)
        else:
            return False
    else:
        return False
