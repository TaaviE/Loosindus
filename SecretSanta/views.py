# Create your views here.
import base64
import copy
import datetime
import json
import logging

from Cryptodome.Cipher import AES
from django.shortcuts import render, redirect
from django.views.static import serve
from django.contrib.auth import logout
from raven.contrib.django.raven_compat.models import client

from SecretSanta.models import Family, NoteState, User, Wishlist, Group, GroupAdmin, FamilyAdmin, Shuffle, Name
from SecretSanta.secretsettings import SecretSettings
from SecretSanta.settings import DEBUG
from secretsanta import ConnectionGraph
from secretsanta.secretsanta import SecretSanta

logger = logging.getLogger(__name__)


def get_person_marked(user_id):
    passed_person_id = int(user_id)
    wishlist_marked = Wishlist.objects.all().filter(purchased_by=passed_person_id)
    return wishlist_marked


def get_person_id(name):
    return User.objects.all().filter(username=name).first().id


def get_family_id(passed_person_id):  # TODO: INLINE
    passed_person_id = int(passed_person_id)
    db_families_user_has_conn = FamilyAdmin.objects.all().filter(user_id=passed_person_id)

    db_family = db_families_user_has_conn[0]
    family_id = db_family.family_id
    return family_id


def get_person_name(passed_person_id):
    return User.objects.get(id=passed_person_id).first_name


def get_target_id(passed_person_id):
    try:
        return Shuffle.objects.get(id=passed_person_id).getter
    except Exception:
        return -1


def get_name_in_genitive(name):
    try:
        return Name.objects.get(name=name).genitive
    except Exception:
        return name


def send_graph(request, filename):
    return serve(request, "./generated_graphs/" + filename)  # TODO: D3


def decrypt_id(encrypted_user_id):
    base64_raw_data = base64.urlsafe_b64decode(encrypted_user_id).decode()
    data = json.loads(base64_raw_data)
    ciphertext = base64.b64decode(data[0])
    nonce = base64.b64decode(data[1])
    tag = base64.b64decode(data[2])

    cipher = AES.new(SecretSettings.AES_KEY, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext).decode()

    try:
        cipher.verify(tag)
        logger.info("The message is authentic:", plaintext)
    except ValueError:
        logger.info("Key incorrect or message corrupted!")

    return plaintext


def encrypt_id(user_id):
    cipher = AES.new(SecretSettings.AES_KEY, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(bytes(str(user_id), encoding="utf8"))
    nonce = base64.b64encode(cipher.nonce).decode()
    ciphertext = base64.b64encode(ciphertext).decode()
    tag = base64.b64encode(tag).decode()
    json_package = json.dumps([ciphertext, nonce, tag])
    packed = base64.urlsafe_b64encode(bytes(json_package, "utf8")).decode()

    return packed


def test(request):
    check = check_if_admin(request)
    if check is not None:
        return check
    return render(request, "error.html", {"message": "Here you go!", "page_title": "Error"})


def favicon(request):
    return serve(request, "./static", "favicon-16x16.png")


def index(request):
    user_id = request.user.id
    username = get_person_name(user_id)
    no_shuffle = False
    if get_target_id(user_id) == -1:
        no_shuffle = True

    try:
        user = User.objects.get(id=user_id)
        user.last_activity_at = datetime.datetime.now()
        user.last_activity_ip = "0.0.0.0"  # TODO: Fix
        user.save()
    except Exception:
        client.captureException()

    return render(request, "index.html", {
        "auth": username,
        "no_shuffle": no_shuffle,
        "uid": user_id,
        "page_title": "Kodu"})


def about(request):
    return render(request, "home.html", {"page_title": "🎄 Jõulurakendus", "no_sidebar": True})


def home(request):
    if request.user.is_authenticated:
        return index(request)
    else:
        return about(request)


def contact(request):
    return render(request, "contact.html", {"no_sidebar": True})


def robots(request):
    return serve(request, "robots.txt")


def sitemap(request):
    return serve(request, "sitemap.xml")


def log_user_out(request):
    logout(request)
    return redirect("/")


def shuffle(request):
    user_id = request.user.id
    username = get_person_name(user_id)
    gifter = get_person_id(username)
    giftee = get_target_id(gifter)
    logger.info(username, gifter, giftee)
    return render(request, "shuffle.html", {"page_title": "Loosimine", "id": giftee})


def notes(request):
    user_id = request.user.id
    # username = get_person_name(user_id)
    notes_from_file = {}
    empty = False

    try:
        db_notes = Wishlist.objects.all().filter(user_id=user_id)
        for note in db_notes:
            notes_from_file[note.item] = encrypt_id(note.id)
    except Exception as e:
        if not DEBUG:
            client.captureException()
        raise e

    if len(notes_from_file) <= 0:
        notes_from_file = {"Praegu on siin ainult veel tühjus, ei tahagi jõuludeks midagi?": ("", "")}
        empty = True

    return render(request, "notes.html",
                  {"list": notes_from_file,
                   "empty": empty,
                   "page_title": "Minu jõulusoovid"})


def createnote(request):
    if request.method == "GET":
        return render(request, "createnote.html",
                      {"page_title": "Lisa uus"})
    elif request.method == "POST":
        logger.info("Got a post request to add a note")
        user_id = request.user.id
        username = get_person_name(user_id)
        logger.info("Found user:", username)
        logger.info("Found user id:", user_id)
        currentnotes = {}
        addednote = request.form["note"]

        if len(addednote) > 1000:
            return render(request, "error.html",
                          {"message": "Pls no hax " + username + "!!",
                           "page_title": "Error"})
        elif len(addednote) <= 0:
            return render(request, "error.html",
                          {"message": "Jõuluvana tühjust tuua ei saa, " + username + "!",
                           "page_title": "Error"})

        logger.info("Trying to add a note:", addednote)
        try:
            logger.info("Opening file", user_id)
            #    with open("./notes/" + useridno, "r") as file:
            #        currentnotes = json.load(file)
            db_notes = Wishlist.objects.all().filter(user_id=user_id)
            for note in db_notes:
                currentnotes[note.item] = note.id
        except Exception as e:
            if not DEBUG:
                client.captureException()
            raise e

        if len(currentnotes) >= 200:
            return render(request, "error.html",
                          {"message": "Soovinimekiri muutuks liiga pikaks, " + username + "",
                           "page_title": "Error"})

        db_entry_notes = Wishlist(
            user_id=user_id,
            item=addednote
        )

        try:
            db_entry_notes.save()
        except Exception as e:
            if not DEBUG:
                client.captureException()
            raise e

        return render(request, "success.html",
                      {"action": "Lisatud",
                       "link": "./notes",
                       "page_title": "Lisatud"})


def editnote(request):
    if request.method == "GET":
        user_id = request.user.id
        username = get_person_name(user_id)

        try:
            request_id = request.args["id"]
            request_id = decrypt_id(request_id)
            request_id = int(request_id)

            logger.info(user_id, "is trying to remove a note", request_id)
        except Exception:
            if not DEBUG:
                client.captureException()
            return render(request, "error.html",
                          {"message": "Pls no hax " + username + "!!",
                           "page_title": "Error"})

        try:
            logger.info(user_id, " is editing notes of ", request_id)
            db_note = Wishlist.objects.get(id=request_id)
        except Exception as e:
            if not DEBUG:
                client.captureException()
            raise e

        return render(request, "createnote.html",
                      {"action": "Muuda",
                       "page_title": "Muuda",
                       "placeholder": db_note.item})
    elif request.method == "POST":
        logger.info("Got a post request to edit a note by", end="")
        user_id = request.user.id
        # username = get_person_name(user_id)
        logger.info(" user id:", user_id)

        addednote = request.form["note"]
        try:
            request_id = request.args["id"]
            request_id = decrypt_id(request_id)
            request_id = int(request_id)
        except Exception:
            if not DEBUG:
                client.captureException()
            return render(request, "error.html",
                          {"message": "Viga lingis",
                           "page_title": "Error"})

        db_note = Wishlist.objects.get(id=request_id)

        try:
            if len(addednote) > 1024:
                return render(request, "error.html",
                              {"message": "Proovi vähem soovida",
                               "page_title": "Error"})
            db_note.item = addednote
            db_note.status = NoteState.MODIFIED.value["id"]
            db_note.save()
        except Exception as e:
            if not DEBUG:
                client.captureException()
            raise e

        return render(request, "success.html",
                      {"action": "Muudetud",
                       "link": "./notes",
                       "page_title": "Muudetud"})


def deletenote(request):
    user_id = request.user.id
    username = get_person_name(user_id)

    try:
        request_id = request.args["id"]
        request_id = decrypt_id(request_id)
        request_id = int(request_id)
        logger.info(user_id, " is trying to remove a note", request_id)
    except Exception:
        if not DEBUG:
            client.captureException()
        return render(request, "error.html",
                      {"message": "Viga lingis",
                       "page_title": "Error"})

    try:
        Wishlist.objects.all().filter(id=request_id).delete()
    except Exception:
        if not DEBUG:
            client.captureException()
        return render(request, "error.html", {"message": "Ei leidnud seda, mida kustutada tahtsid", "page_title": "Error"})

    #    with open("./notes/" + useridno, "w") as file:
    #        file.write(json.dumps(currentnotes))

    logger.info("Removed", username, "note with ID", request_id)
    return render(request, "success.html",
                  {"action": "Eemaldatud",
                   "link": "./notes",
                   "page_title": "Eemaldatud"})


def updatenotestatus(request):
    if request.method == "POST":
        user_id = request.user.id

        try:
            status = int(request.form["status"])
            note = Wishlist.objects.get(id=decrypt_id(request.form["id"]))

            if status > -1:
                if int(note.status) == NoteState.PURCHASED.value["id"] or status == \
                        NoteState.MODIFIED.value["id"]:
                    raise Exception("Invalid access")
                note.status = status
                note.purchased_by = user_id
                note.save()
            #        elif status == "off":
            #            note.status = NoteState.DEFAULT.value["id"]
            #            note.purchased_by = None
            elif status == -1:
                if int(note.status) == NoteState.PURCHASED.value["id"] or status == \
                        NoteState.MODIFIED.value["id"]:
                    raise Exception("Invalid access")
                note.status = status
                note.purchased_by = None
                note.save()
            else:
                raise Exception("Invalid status code")
        except Exception as e:
            if not DEBUG:
                client.captureException()
            else:
                logger.info("Failed toggling:", e)
            return render(request, "error.html",
                          {"message": "Ei saanud staatusemuudatusega hakkama", "page_title": "Error", "back": True})

        #    with open("./notes/" + useridno, "w") as file:
        #        file.write(json.dumps(currentnotes))

        return redirect("/giftingto?id=" + str(request.args["id"]), code=303)
    elif request.method == "GET":
        check = check_if_admin(request)
        # if check is not None:
        #   return check

        user_id = request.user.id
        username = get_person_name(user_id)
        invalid_notes = False

        try:
            request_id = request.args["id"]
            request_id = int(decrypt_id(request_id))
        except Exception as e:
            logger.info("Failed decrypting or missing:", e)
            request_id = get_target_id(user_id)

        try:  # Yeah, only valid IDs please
            if request_id == -1:
                return render(request, "error.html",
                              {"message": "Loosimist ei ole veel administraatori poolt tehtud",
                               "page_title": "Error"})
            elif request_id < 0:
                raise Exception()
            elif request_id == int(user_id):
                return render(request, "error.html",
                              {"message": "Sellele nimekirjale on ligipääs keelatud",
                               "page_title": "Keelatud"})
        except Exception:
            if not DEBUG:
                client.captureException()
            return render(request, "error.html",
                          {"message": "Pls no hax " + username + "!!",
                           "page_title": "Error"})

        if check is not None:  # Let's not let everyone read everyone's lists
            if request_id != get_target_id(user_id):
                family_id = get_family_id(user_id)
                family_obj = Family.objects.get(id=family_id)
                family_group = family_obj.group

                database_all_families_with_members = []
                database_families = Family.objects.all().filter(group=family_group)
                for db_family in database_families:
                    database_family_members = FamilyAdmin.objects.all().filter(family_id=db_family.id)
                    database_all_families_with_members.append(database_family_members)

                found = False
                for family in database_all_families_with_members:
                    for member in family:
                        if member.user_id == request_id:
                            found = True

                if not found:
                    return check

        currentnotes = {}

        try:
            logger.info(user_id, "is opening file:", request_id)
            db_notes = Wishlist.objects.all().filter(user_id=request_id)
            if len(db_notes) <= 0:
                raise Exception

            for note in db_notes:
                all_states = [state.value for state in NoteState]
                all_states.remove(NoteState.MODIFIED.value)
                selections = []
                modifyable = False
                name = ""

                if note.status == NoteState.DEFAULT.value["id"]:
                    selections = all_states
                    selections.insert(0, selections.pop(selections.index(NoteState.DEFAULT.value)))
                    modifyable = True
                elif note.status == NoteState.MODIFIED.value["id"]:
                    if note.purchased_by == int(user_id) or note.purchased_by is None:
                        selections = all_states
                        selections.insert(0, NoteState.MODIFIED.value)
                        modifyable = True
                    else:
                        selections = [NoteState.MODIFIED.value]
                        modifyable = False
                    name = note.purchased_by
                elif note.status == NoteState.PURCHASED.value["id"]:
                    selections = [NoteState.PURCHASED.value]
                    name = note.purchased_by
                    modifyable = False
                elif note.status == NoteState.PLANNING_TO_PURCHASE.value["id"]:
                    selections = [NoteState.PLANNING_TO_PURCHASE.value,
                                  NoteState.DEFAULT.value, NoteState.PURCHASED.value]
                    name = note.purchased_by
                    if note.purchased_by == int(user_id):
                        modifyable = True
                    else:
                        modifyable = False

                currentnotes[note.item] = (encrypt_id(note.id), copy.deepcopy(selections), modifyable, name)
        except ValueError:
            if not DEBUG:
                client.captureException()
        except Exception as e:
            currentnotes = {"Praegu on siin ainult veel tühjus": (-1, -1, False, "")}
            invalid_notes = True
            logger.info("Error displaying notes, there might be none:", e)

        return render(request, "show_notes.html",
                      {"notes": currentnotes,
                       "target": get_name_in_genitive(get_person_name(request_id)),
                       "id": encrypt_id(request_id),
                       "page_title": "Kingisoovid",
                       "invalid": invalid_notes,
                       "back": True,})


def graph(request):
    user_id = request.user.id
    try:
        family_id = get_family_id(user_id)
        family_obj = Family.objects.get(id=family_id)
        family_group = family_obj.group
        return render(request, "graph.html",
                      {"id": str(request.user),
                       "image": "graph_" + str(family_group) + ".png",
                       "page_title": "Graaf"})
    except Exception:
        return render(request, "error.html",
                      {"message": "Loosimist ei ole administraatori poolt tehtud", "page_title": "Error"})


def settings(request):
    user_id = request.user.id
    user_obj = User.objects.get(id=user_id)
    is_in_group = False
    is_in_family = False

    db_families_user_has_conn = FamilyAdmin.objects.all().filter(user_id=user_id)

    user_families = {}
    db_groups_user_has_conn = []
    for family_relationship in db_families_user_has_conn:
        family = Family.objects.get(id=family_relationship.family_id)
        user_families[family.name] = (encrypt_id(family.id), family_relationship.admin)
        is_in_family = True
        db_groups_user_has_conn += (Group.objects.all().filter(group=family.group))

    user_groups = {}
    for group_relationship in db_groups_user_has_conn:
        uga_relationship = GroupAdmin.objects.all().filter(user_id=user_id, group_id=group_relationship.id).first()

        if not uga_relationship:
            user_groups[group_relationship.description] = (encrypt_id(group_relationship.id), False)
        else:
            user_groups[group_relationship.description] = (encrypt_id(group_relationship.id), uga_relationship.admin)
        is_in_group = True

    return render(request, "settings.html",
                  {"user_id": user_id,
                   "user_name": user_obj.username,
                   "family_admin": is_in_family,
                   "group_admin": is_in_group,
                   "families": user_families,
                   "groups": user_groups,
                   "page_title": "Seaded",
                   "back_link": "/"})


def editfamily(request):
    if request.method == "GET":
        user_id = request.user.id

        try:
            request_id = request.args["id"]
            request_id = int(decrypt_id(request_id))
        except Exception:
            if not DEBUG:
                client.captureException()
            return render(request, "error.html", {"message": "Tekkis viga, kontrolli linki", "page_title": "Error"})

        if request_id < 0:
            if not DEBUG:
                client.captureException()
            return render(request, "error.html", {"message": "Tekkis viga, kontrolli linki", "page_title": "Error"})

        db_family_members = FamilyAdmin.objects.all().filter(family_id=request_id)

        family = []
        show_admin_column = False
        for member in db_family_members:
            is_admin = False
            is_person = False
            if member.user_id == user_id:
                is_person = True

            family.append((get_person_name(member.user_id), encrypt_id(member.user_id), is_admin, is_person))

        return render(request, "editfam.html",
                      {"family": family,
                       "page_title": "Muuda perekonda",
                       "admin": show_admin_column,
                       "back": False,
                       "back_link": "/settings"})
    elif request.method == "POST":
        # user_id = request.user.id

        # try:
        # action = request.args["action"]
        # request_id = request.args["id"]
        # request_id = int(decrypt_id(request_id))
        # except Exception:
        # return render(request, "error.html", message="Tekkis viga, kontrolli linki", title="Error")

        return None


def editgroup(request):
    if request.method == "GET":
        user_id = request.user.id
        # user_obj = User.objects.get(user_id)

        try:
            request_id = request.args["id"]
            request_id = int(decrypt_id(request_id))
        except Exception:
            if not DEBUG:
                client.captureException()
            request_id = 0

        db_groups_user_is_admin = GroupAdmin.objects.all().filter(user_id=user_id)

        db_groups_user_has_conn = Family.objects.all().filter(group=request_id)

        db_group = db_groups_user_has_conn[request_id]

        db_families_in_group = Family.objects.all().filter(group=db_group.group)

        families = []
        for family in db_families_in_group:
            admin = False

            if family in db_groups_user_is_admin:
                admin = True

            families.append((family.name, encrypt_id(family.id), admin))

        is_admin = False
        if len(db_groups_user_is_admin) > 0:
            is_admin = True

        return render(request, "editgroup.html", {"page_title": "Muuda gruppi", "families": families, "admin": is_admin})
    elif request.method == "POST":
        # user_id = request.user.id
        # user_obj = User.objects.get(user_id)
        return None


def secretgraph(request):
    check = check_if_admin(request)
    if check is not None:
        return check

    request_id = str(request.args["id"])

    return render(request, "graph.html",
                  {"id": str(get_person_name(request.user)),
                   "image": "s" + request_id + ".png",
                   "page_title": "Salajane graaf"})


def check_if_admin(request):
    user_id = request.user.id
    requester = get_person_name(user_id)
    requester = requester.lower()

    if requester != "admin" and requester != "taavi":
        return render(request, "error.html", {"message": "Pls no hax " + requester + "!!", "page_title": "Error"})
    else:
        return None


"""@app.route("/family")
def family(request):
    user_id = request.user.id
    family_id = User.objects.get(user_id).family_id
    family_members = User.objects.all().filter(family_id=family_id).all()
    family_member_names = []
    for member in family_members:
        family_member_names.append(member.username)
    return render(request, "show_family.html", names=family_member_names, title="Perekond")
"""


def regraph(request):
    check = check_if_admin(request)
    if check is not None:
        return check

    user_id = request.user.id
    family_id = get_family_id(user_id)
    family_obj = Family.objects.get(id=family_id)
    family_group = family_obj.group

    database_families = Family.objects.all().filter(group=family_group)
    database_all_families_with_members = []
    for db_family in database_families:
        database_family_members = FamilyAdmin.objects.all().filter(family_id=db_family.id)
        database_all_families_with_members.append(database_family_members)

    families = []
    family_ids_map = {}
    for family_index, list_family in enumerate(database_all_families_with_members):
        families.insert(family_index, {})
        for person_index, person in enumerate(list_family):
            family_ids_map[family_index] = get_family_id(person.user_id)
            families[family_index][get_person_name(person.user_id)] = person.user_id

    families_shuf_nam = {}
    families_shuf_ids = {}
    #    logger.info("Starting finding matches")
    """""
    # This comment block contains self-written algorithm that isn't as robust 
    # as the library's solution thus this is not used for now

    families_give_copy = copy.deepcopy(families)  # Does the person need to give a gift
    for family_index, family_members in enumerate(families_give_copy):
        for person in family_members:
            families_give_copy[family_index][person] = True

    families_take_copy = copy.deepcopy(families)  # Does the person need to take a gift
    for family_index, family_members in enumerate(families_take_copy):
        for person in family_members:
            families_take_copy[family_index][person] = True

    for index, family in enumerate(families_list_copy):  # For each family among every family
        for person in family:  # For each person in given family
            if families_give_copy[index][person] == True:  # If person needs to gift
                #                print("Looking for a match for:", person, get_person_id(person))
                familynumbers = list(range(0, index))
                familynumbers.extend(range(index + 1, len(family) - 1))

                random.shuffle(familynumbers)
                for number in familynumbers:
                    receiving_family_index = number
                    receiving_family = families_take_copy[number]  # For each receiving family
                    #                    print("Looking at other members_to_families:", receiving_family)

                    for receiving_person in receiving_family:  # For each person in other family
                        if families_take_copy[receiving_family_index][receiving_person] == True and \
                                families_give_copy[index][person] == True:  # If person needs to receive
                            families_take_copy[receiving_family_index][receiving_person] = False  
                            #print("Receiving:", receiving_family_index, receiving_person)
                            families_give_copy[index][person] = False  # ; print("Giving:", index, person)
                            families_shuf_nam[person] = receiving_person
                            families_shuf_ids[get_person_id(person)] = get_person_id(receiving_person)
                            #                             print("Breaking")
                            break
    """""

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

    last_connections = ConnectionGraph.ConnectionGraph(members_to_families, families_to_members)
    # connections.add(source, target, year)
    current_year = datetime.datetime.now().year
    logger.info(current_year, "is the year of Linux Desktop")

    santa = SecretSanta(families_to_members, members_to_families, last_connections)
    new_connections = santa.generate_connections(current_year)

    shuffled_ids_str = {}
    for connection in new_connections:
        families_shuf_ids[connection.source] = connection.target
        families_shuf_nam[get_person_name(connection.source)] = get_person_name(connection.target)
        shuffled_ids_str[str(connection.source)] = str(connection.target)

        #    logger.info( shuffled_names)
        #    logger.info( shuffled_ids)

    current_time = datetime.datetime.now()
    for giver, getter in families_shuf_ids.items():
        db_entry_shuffle = Shuffle(
            giver=giver,
            getter=getter,
            year=current_time
        )
        try:
            db_entry_shuffle.save()
        except Exception:
            logger.error("Saving shuffle failed")

    return render(request, "success.html",
                  {"action": "Genereeritud", "link": "./notes", "page_title": "Genereeritud"})


def testmail(request):
    """with mail.connect() as conn:
        logger.info(conn.configure_host().vrfy)
        msg = Message(recipients=["root@localhost"],
                      body="test",
                      subject="test2")

        conn.send(msg)"""
    return render(request, "success.html", {"action": "Sent", "link": "./testmail", "page_title": "Saadetud"})


def login(request):
    return render(request, "security/login_user.html", {"page_title": "🎄 Jõulurakendus", "no_sidebar": True})


def register(request):
    return render(request, "security/register_user.html", {"page_title": "🎄 Jõulurakendus", "no_sidebar": True})


def reset(request):
    return render(request, "security/reset_password.html", {"page_title": "🎄 Jõulurakendus", "no_sidebar": True})


def change(request):
    return render(request, "security/change_password.html", {"page_title": "🎄 Jõulurakendus", "no_sidebar": True})


def forgot(request):
    return render(request, "security/forgot_password.html", {"page_title": "🎄 Jõulurakendus", "no_sidebar": True})
