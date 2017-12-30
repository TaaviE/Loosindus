#!/usr/bin/python3
# coding=utf-8
# author=Taavi Eomäe

#####
# TODO:
# * Migrate to Flask-Security from basic HTTP auth
# * Add support for multiple shufflings in one instance
# * Add marking gifts as bougth
#
# Known flaws:
# * SecretSanta can't match less than two people or people from less than one family
####

# Plotting
import matplotlib as pylab

pylab.use("Agg")  # Because we won't have a GUI on the server itself
import matplotlib.pyplot as plotlib
import networkx as netx

# Graphing
import secretsanta

# Utilities
import copy
import datetime
import json
import random

# Flask
from flask import request, render_template, session
from flask_security import login_required

# App specific config
from config import Config, db, app

# Database models
from models import users_model, notes_model, family_model, shuffles_model, groups_model

import sys

sys.setrecursionlimit(2000)


# Views
@app.route("/test")
@login_required
def test():
    return render_template("error.html", error="Here you go!")


# These lines that are commented out are one way to initially define the values you wish to use
#
# Contains placeholder names (with ids) and members_to_families that are going to
# be written into a file on first launch, after that it's
# going to be loaded from there and these lines could be removed
# fam_1 = {"Fam1_1": 0, "Fam1_2": 0, "Fam1_3": 0, "Fam1_4": 0}
# fam_2 = {"Fam2_1": 0, "Fam2_2": 0, "Fam2_3": 0}
# fam_3 = {"Fam3_1": 0, "Fam3_2": 0}
# fam_4 = {"Fam4_1": 0, "Fam4_2": 0, "Fam4_3": 0, "Fam4_4": 0}
# fam_5 = {"Fam5_1": 0, "Fam5_2": 0}

# families = [fam_1, fam_2, fam_3, fam_4, fam_5]

# names_proper = {
#
# As the software displays messages in estonian it'd be
# better if names had an genitive form to look up, feel free
# to remove this list, it is saved into a file on first launch
# and then loaded from there on future launches
#
#    "Fam1_1": "Fam_1_1i"
# }

# Just for assigning members_to_families a few colors, if you have more than five members_to_families, add more
chistmasy_colors = ["#B3000C", "#DC3D2A", "#0DEF42", "#00B32C", "#0D5901"]


def getpersonid(name):
    return users_model.User.query.filter(users_model.User.username == name).first().id


def getfamilyid(passed_person_id):
    return users_model.User.query.get(passed_person_id).family_id


def getpersonname(passed_person_id):
    return users_model.User.query.get(passed_person_id).username


def gettargetname(passed_person_id):
    try:
        print("Found target: ")
        return shuffles_model.Shuffle.query.get(passed_person_id).getter
    except Exception:
        print("DID NOT FIND TARGET FOR PERSON!")
        return -1


@app.route("/")
@login_required
def index():
    #    username = request.authorization.username
    user_id = session["user_id"]
    username = getpersonname(user_id)
    return render_template("index.html", auth=username)


@app.route("/shuffle")
@login_required
def shuffle():
    user_id = session["user_id"]
    username = getpersonname(user_id)
    print(username)
    gifter = getpersonid(username)
    print(gifter)
    giftee = gettargetname(gifter)
    print(giftee)
    return render_template("shuffle.html", id=giftee)


@app.route("/notes")
@login_required
def notes():
    user_id = session["user_id"]
    username = getpersonname(user_id)
    notes_from_file = ["Praegu on siin ainult veel tühjus, ei tahagi jõuludeks midagi?"]
    try:
        db_notes = notes_model.Notes.query.get(user_id)
        #    with open("./notes/" + useridno) as file:
        #        notes_from_file = json.load(file)
        if db_notes is not None:  # Don't want to display None
            notes_from_file = db_notes.notes
    except Exception as e:
        print(e)

    if len(notes_from_file) <= 0:
        notes_from_file = ["Praegu on siin ainult veel tühjus, ei tahagi jõuludeks midagi?"]
    return render_template("notes.html", list=notes_from_file)


@app.route("/createnote", methods=["GET"])
@login_required
def createnote():
    return render_template("createnote.html", title="Lisa uus")


@app.route("/createnote", methods=["POST"])
@login_required
def createnote_add():
    print("Got a post request to add a note")
    user_id = session["user_id"]
    username = getpersonname(user_id)
    print("Found user:", username)
    print("Found user id:", user_id)
    currentnotes = []
    addednote = request.form["note"]

    if len(addednote) > 1000:
        return render_template("error.html", message="Pls no hax " + username + "!!")
    elif len(addednote) <= 0:
        return render_template("error.html",
                               message="Jõuluvana tühjust tuua ei saa, " + username + "!")
    print("Trying to add a note:", addednote)
    try:
        print("Opening file", user_id)
        #    with open("./notes/" + useridno, "r") as file:
        #        currentnotes = json.load(file)
        db_notes = notes_model.Notes.query.get(user_id)
        if db_notes is not None:  # Don't want to display None
            currentnotes = db_notes.notes
    except Exception as e:
        print(e)
    if len(currentnotes) == 999:
        return render_template("error.html",
                               message="Soovinimekiri muutuks liiga pikaks, " + username + "")

    currentnotes.append(addednote)

    #    with open("./notes/" + useridno, "w") as file:
    #        file.write(json.dumps(currentnotes))
    db_entry_notes = notes_model.Notes(
        user_id=user_id,
        notes=currentnotes,
    )
    db.session.add(db_entry_notes)
    db.session.commit()
    return render_template("success.html", action="Lisatud", link="./notes")


@app.route("/editnote", methods=["GET"])
@login_required
def editnote():
    user_id = session["user_id"]
    username = getpersonname(user_id)
    currentnotes = []
    print("Trying to remove a note:", request.args["id"])
    try:
        int(request.args["id"])  # Just check if the id passed can be converted to an integer
    except Exception:
        return render_template("error.html", message="Pls no hax " + username + "!!")

    try:
        print("Opening file", user_id)
        #        with open("./notes/" + useridno, "r") as file:
        #            currentnotes = json.load(file)
        db_notes = notes_model.Notes.query.get(user_id)
        if db_notes is not None:  # Don't want to display None
            currentnotes = db_notes.notes
    except Exception as e:
        print(e)

    if int(request.args["id"]) >= len(currentnotes):
        return render_template("error.html", message="Ei leidnud seda, mida muuta tahtsid 🤔")
    return render_template("createnote.html", action="Muuda", placeholder=currentnotes[int(request.args["id"])])


@app.route("/editnote", methods=["POST"])
@login_required
def editnote_edit():
    print("Got a post request to edit a note")
    user_id = session["user_id"]
    username = getpersonname(user_id)
    print("Found user id:", user_id)
    currentnotes = []
    addednote = request.form["note"]
    print("Trying to add a note:", addednote)
    try:
        print("Opening file", user_id)
        #        with open("./notes/" + user_id, "r") as file:
        #            currentnotes = json.load(file)
        db_notes = notes_model.Notes.query.get(user_id)
        if db_notes is not None:  # Don't want to display None
            currentnotes = db_notes.notes
    except Exception as e:
        print(e)

    currentnotes[int(request.args["id"])] = addednote

    #    with open("./notes/" + user_id, "w") as file:
    #        file.write(json.dumps(currentnotes))
    db_entry_notes = notes_model.Notes(
        user_id=user_id,
        notes=currentnotes,
    )
    db.session.add(db_entry_notes)
    db.session.commit()
    return render_template("success.html", action="Muudetud", link="./notes")


@app.route("/removenote")
@login_required
def deletenote():
    user_id = session["user_id"]
    username = getpersonname(user_id)
    currentnotes = []
    print("Trying to remove a note:", request.args["id"])
    try:
        print("Opening file", user_id)
        #        with open("./notes/" + useridno, "r") as file:
        #            currentnotes = json.load(file)
        db_notes = notes_model.Notes.query.get(user_id)
        if db_notes is not None:  # Don't want to display None
            currentnotes = db_notes.notes
    except Exception as e:
        print(e)

    try:
        currentnotes.pop(int(request.args["id"]))
    except Exception:
        return render_template("error.html", message="Ei leidnud seda, mida kustutada tahtsid")

    #    with open("./notes/" + useridno, "w") as file:
    #        file.write(json.dumps(currentnotes))
    db_entry_notes = notes_model.Notes(
        user_id=user_id,
        notes=currentnotes,
    )
    db.session.add(db_entry_notes)
    db.session.commit()
    print("Removed", username, "note with ID", request.args["id"])
    return render_template("success.html", action="Eemaldatud", link="./notes")


@app.route("/graph")
@login_required
def graph():
    user_id = session["user_id"]
    family_id = users_model.User.query.get(user_id).family_id
    family_obj = family_model.Family.query.get(family_id)
    family_group = family_obj.group
    return render_template("graph.html",
                           id="number " + str(session["user_id"]),
                           image=str(family_group) + ".png")


@app.route("/settings")
def settings():
    user_id = session["user_id"]
    user_obj = users_model.User.query.get(user_id)
    user_family_id = user_obj.family_id
    user_family = family_model.Family.query.get(user_family_id)
    user_family_group = user_family.group

    db_families = family_model.Family.query.filter(family_model.Family.id == user_family_id)
    families = {}
    for family in db_families:
        families[family.name] = {}
        people_in_family = users_model.User.query.filter(family_model.Family.id == family.id)

        for member in people_in_family:
            families[family.name][member.username] = member.id

    is_family_admin = False
    if len(families) > 0:
        is_family_admin = True

    db_groups = groups_model.Groups.query.filter(groups_model.Groups.admin == user_id)
    groups = {}
    for group in db_groups:
        groups[group.description] = {}
        group_families = family_model.Family.query.filter(family_model.Family.group == group.id)
        for g_family in group_families:
            groups[group.description][g_family.name] = g_family.id

    is_group_admin = False
    if len(groups) > 0:
        is_group_admin = True

    families = {}
    families_in_group = family_model.Family.query.filter(family_model.Family.group == user_family_group)
    for group_family in families_in_group:
        families[group_family.name] = group_family.id

    return render_template("settings.html",
                           user_id=user_id,
                           user_name=user_obj.username,
                           family_admin=is_family_admin,
                           group_admin=is_group_admin,
                           families=families,
                           groups=groups)


@app.route("/secretgraph")
@login_required
def secretgraph():
    check = check_if_admin()
    if check is not None:
        return check
    return render_template("graph.html",
                           id=str(getpersonname(session["user_id"])),
                           image="secretgraph.png")


def check_if_admin():
    user_id = session["user_id"]
    requester = getpersonname(user_id)
    if requester != "admin" and requester != "taavi":
        return render_template("error.html", message="Pls no hax " + requester + "!!")
    else:
        return None


"""@app.route("/setup")
@login_required
def setup():
    check = check_if_admin()
    if check is not None:
        return check
    return render_template("createfamilies.html")


@app.route("/setup", methods=["POST"])
@login_required
def setup_post():
    try:
        check = check_if_admin()
        if check is not None:
            return check
    except Exception:
        return login()

    input_families = []
    for family_index, family in enumerate(request.form):
        input_families.insert(family_index, {})
        for member in request.form[family].split(","):
            member = member.strip().capitalize()
            input_families[family_index][member] = 0

    print("Generating user IDs based on setup input table")
    current_person_id = 0  # Start from 0
    for current_family in input_families:
        for current_person in current_family:  # Assign ID for every person
            current_family[current_person] = current_person_id
            current_person_id += 1

    with open("./ids.json", "w") as file:
        file.write(json.dumps(input_families))
        print("Wrote user IDs to file")

    return render_template("success.html", action="Genereeritud", link="./kill")


@app.route("/kill")
@login_required
def kill():
    check = check_if_admin()
    if check is not None:
        return check
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()
"""


@app.route("/family")
@login_required
def family():
    user_id = session["user_id"]
    family_id = users_model.User.query.get(user_id).family_id
    family_members = users_model.User.query.filter(users_model.User.family_id == family_id).all()
    family_member_names = []
    for member in family_members:
        family_member_names.append(member.username)
    return render_template("show_family.html", names=family_member_names)


@app.route("/recreategraph")
@login_required
def regraph():
    #    check = check_if_admin()
    #    if check is not None:
    #        return check

    user_id = session["user_id"]
    family_id = users_model.User.query.get(user_id).family_id
    family_obj = family_model.Family.query.get(family_id)
    family_group = family_obj.group

    database_families = family_model.Family.query.filter(family_model.Family.group == family_group).all()
    database_all_families_with_members = []
    for db_family in database_families:
        database_family_members = users_model.User.query.filter(users_model.User.family_id == db_family.id).all()
        database_all_families_with_members.append(database_family_members)

    families = []
    family_ids_map = {}
    for family_index, list_family in enumerate(database_all_families_with_members):
        families.insert(family_index, {})
        for person_index, person in enumerate(list_family):
            family_ids_map[family_index] = person.family_id
            families[family_index][person.username] = person.id

    families_give_copy = copy.deepcopy(families)  # Does the person need to give a gift
    for family_index, family_members in enumerate(families_give_copy):
        for person in family_members:
            families_give_copy[family_index][person] = True

    families_take_copy = copy.deepcopy(families)  # Does the person need to take a gift
    for family_index, family_members in enumerate(families_take_copy):
        for person in family_members:
            families_take_copy[family_index][person] = True

    families_shuf_nam = {}
    families_shuf_ids = {}
    #    print("Starting finding matches")
    """""
    # This comment block contains self-written algorithm that isn't as robust 
    # as the library's solution thus this is not used for now
    
    for index, family in enumerate(families_list_copy):  # For each family among every family
        for person in family:  # For each person in given family
            if families_give_copy[index][person] == True:  # If person needs to gift
                #                print("Looking for a match for:", person, getpersonid(person))
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
                            families_shuf_ids[getpersonid(person)] = getpersonid(receiving_person)
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

    last_connections = secretsanta.ConnectionGraph.ConnectionGraph(members_to_families, families_to_members)
    # connections.add(source, target, year)
    current_year = datetime.datetime.now().year
    print(current_year, "is the year of Linux Desktop")

    santa = secretsanta.secretsanta.SecretSanta(families_to_members, members_to_families, last_connections)
    new_connections = santa.generate_connections(current_year)

    shuffled_ids_str = {}
    for connection in new_connections:
        families_shuf_ids[connection.source] = connection.target
        families_shuf_nam[getpersonname(connection.source)] = getpersonname(connection.target)
        shuffled_ids_str[str(connection.source)] = str(connection.target)

        #    print(shuffled_names)
        #    print(shuffled_ids)

    for giver, getter in families_shuf_ids.items():
        db_entry_shuffle = shuffles_model.Shuffle(
            giver=giver,
            getter=getter,
        )
        try:
            db.session.add(db_entry_shuffle)
            db.session.commit()
        except:
            db.session.rollback()
            row = shuffles_model.Shuffle.query.get(giver)
            row.getter = getter
            db.session.commit()

    digraph = netx.DiGraph(iterations=10000, scale=2)
    digraph.add_nodes_from(copy.deepcopy(families_shuf_ids).keys())

    for source, destination in copy.deepcopy(families_shuf_ids).items():
        digraph.add_edges_from([(source, destination)])

    save_graph(digraph, "./static/" + str(family_group) + ".png")
    del digraph
    rerendernamegraph()  # create the graph with names

    return render_template("success.html", action="Genereeritud", link="./notes")


@app.route("/rerendergraph")
@login_required
def rerender():
    check = check_if_admin()
    if check is not None:
        return check

    digraph = netx.DiGraph(iterations=100000000, scale=2)
    digraph.add_nodes_from(copy.deepcopy(families_shuf_ids).keys())

    for source, destination in copy.deepcopy(families_shuf_ids).items():
        digraph.add_edges_from([(source, destination)])

    save_graph(digraph, "./static/graph.png")
    return render_template("success.html", action="Genereeritud", link="./notes")


@app.route("/rerendernamegraph")
@login_required
def rerendernamegraph():
    check = check_if_admin()
    if check is not None:
        return check

    digraph = netx.DiGraph(iterations=100000000, scale=2)  # This is probably a horrible idea with more nodes

    for shuffled_ids_id in copy.deepcopy(families_shuf_ids).keys():
        digraph.add_node(shuffled_ids_id)

    for source, destination in copy.deepcopy(families_shuf_ids).items():
        digraph.add_edges_from([(source, destination)])

    save_graph(digraph, "./static/secretgraph.png", colored=True)

    return render_template("success.html", action="Genereeritud", link="./graph")


def save_graph(passed_graph, file_name, colored=False):
    # This function just saves a networkx graph into a .png file without any GUI(!)
    plotlib.figure(num=None, figsize=(10, 10), dpi=60)
    plotlib.axis("off")  # Turn off the axis display
    fig = plotlib.figure(1)
    pos = netx.circular_layout(passed_graph)

    if colored:  # Try to properly color the nodes
        for node in passed_graph:
            node_color = random.choice(chistmasy_colors)
            netx.draw_networkx_nodes([node], pos, node_size=1500, node_color=node_color)
    else:
        netx.draw_networkx_nodes(passed_graph, pos, node_size=1500, node_color=chistmasy_colors[0])

    netx.draw_networkx_edges(passed_graph, pos)

    if colored:
        name_id_lookup_dict = {}  # Let's create a name-id mapping

        for name in shuffled_names.keys():
            name_id_lookup_dict[getpersonid(name)] = name

        netx.draw_networkx_labels(passed_graph, pos, labels=name_id_lookup_dict)
    else:
        netx.draw_networkx_labels(passed_graph, pos)
    cut = 0
    xmax = 1.1 + cut * max(xx for xx, yy in pos.values())
    ymax = 1.1 + cut * max(yy for xx, yy in pos.values())
    xmin = -1.1 + cut * min(xx for xx, yy in pos.values())
    ymin = -1.1 + cut * min(yy for xx, yy in pos.values())
    plotlib.xlim(xmin, xmax)
    plotlib.ylim(ymin, ymax)

    fig.savefig(file_name, bbox_inches="tight")
    plotlib.close()
    print("Saved generated graph to file:", file_name)
    del fig


@app.route("/giftingto")
@login_required
def giftingto():
    check = check_if_admin()
    user_id = session["user_id"]
    username = getpersonname(user_id)
    if check is not None:  # Let's not let everyone read everyone's lists
        if request.args["id"] != str(gettargetname(user_id)):
            return check

    try:  # Yeah, only valid IDs please
        value = int(user_id)
        if value < 0:
            raise Exception
    except Exception:
        return render_template("error.html", message="Pls no hax " + username + "!!")

    currentnotes = ["Praegu on siin ainult veel tühjus"]
    try:
        print("Opening file:", user_id)
        with open("./notes/" + user_id, "r") as file:
            currentnotes = json.load(file)
    except Exception as e:
        print(e)

    # try:  # Not the prettiest, but tries to display names in the correct form
    #    return render_template("show_notes.html", notes=currentnotes, target=names_proper[username])
    # except Exception:
    return render_template("show_notes.html", notes=currentnotes, target=getpersonname(user_id))


@app.route("/login", methods=["GET"])
def login():
    render_template("security/login_user.html")


@app.route("/register", methods=["GET"])
def register():
    render_template("security/register_user.html")


@app.route("/change", methods=["GET"])
@login_required
def change():
    render_template("security/change_password.html")


@app.route("/reset", methods=["GET"])
def reset():
    render_template("security/reset_password.html")


@app.route("/confirm", methods=["GET"])
def confirmation():
    render_template("security/send_confirmation.html")


if __name__ == "__main__":
    if Config.DEBUG:
        print("Starting in debug!")
        app.run(debug=Config.DEBUG, use_evalex=False, host="0.0.0.0", port=5000)
    else:
        print("Starting in production.")
        app.run(debug=Config.DEBUG, use_evalex=False, host="127.0.0.1")
