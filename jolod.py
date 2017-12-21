#!/usr/bin/python3
# coding=utf-8
# author=Taavi Eomäe
import matplotlib as pylab

pylab.use("Agg")  # Because we won't have a GUI on the server itself

#####
# TODO:
# * Migrate to Flask-Security from basic HTTP auth
# * Add support for multiple shufflings in one instance
####

# Flask
from flask import Flask, request, render_template, Response, session
from flask_security import Security, login_required, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import Config
# Graphing
import matplotlib.pyplot as plotlib
import networkx as netx
import secretsanta

# Utilities
import copy
import datetime
import json

# App related config
app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

mail = Mail(app)
debug = Config.DEBUG

# Setup Flask-Security
userroles = db.Table(
    "roles_users",
    db.Column("id", db.Integer(), db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer(), db.ForeignKey("role.id"))
)

from models import users_model, notes_model

user_datastore = SQLAlchemyUserDatastore(db,
                                         users_model.User,
                                         users_model.Role)
security = Security(app, user_datastore)
user_datastore.create_user(email="avamander@gmail.com", password="test1234")


# Views
@app.route("/test")
@login_required
def test():
    return render_template("error.html", error="Here you go!")


@app.route("/register", methods=['GET'])
def register():
    return render_template("security/register_user.html")


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


shuffled_names = {}  # Will contain the shuffled names and IDs
shuffled_ids = {}

# Just for assigning members_to_families a few colors, if you have more than five members_to_families, add more
chistmasy_colors = ["#B3000C", "#DC3D2A", "#0DEF42", "#00B32C", "#0D5901"]
person_colors = {}


def load_forms():
    global names_proper
    try:  # Load user names in genitive form from file
        print("Trying to load user names in genitive form from file")
        with open("./genitive.json", "r") as file:
            tmp_names_proper = eval(str(json.load(file)))
            if len(tmp_names_proper) <= 0:
                raise Exception
        names_proper = tmp_names_proper
        print("Loaded user names in genitive form from file")
    except Exception as e:
        print("Loading failed:", e)
        print("Writing names in genitive form to file")
        with open("./genitive.json", "w") as file:
            file.write(json.dumps(names_proper))
            print("Wrote user names in genitive form to file")


def load_mapping():
    global families
    try:  # Load the person_id mapping from file
        with open("./ids.json", "r") as file:
            tmp_families_json = json.load(file)
            tmp_families = eval(str(tmp_families_json))
            if len(tmp_families) >= 1:
                if len(tmp_families[1]) < 1:
                    raise Exception("2nd family 2spooky4me!")
            else:
                raise Exception("Not enough members_to_families!")
        families = tmp_families
        print("Loaded user IDs from file")
    except Exception as e:
        print("Loading failed:", e)
        print("Generating user IDs")
        current_person_id = 0  # Start from 0
        for current_family in families:
            for current_person in current_family:  # Assign ID for every person
                current_family[current_person] = current_person_id
                current_person_id += 1
        with open("./ids.json", "w") as file:
            file.write(json.dumps(families))
            print("Wrote user IDs to file")


def load_shuffling():
    global shuffled_ids
    global shuffled_names

    try:  # Load the shuffling mapping from file
        with open("./graph.json", "r") as file:
            [shuffled_names, shuffled_ids_tmp] = json.load(file)
        for key in shuffled_ids_tmp:  # Need to fix json not storing integers
            shuffled_ids[int(key)] = shuffled_ids_tmp[key]
        print("Loaded shuffle from file")
    except Exception:
        print("No shuffle exists! Generate one!")


def load_colors():
    global person_colors
    for family_id, family in enumerate(families):
        for person, person_id in family.items():
            person_colors[person_id] = chistmasy_colors[family_id]


def getpersonid(name):
    for current_family in families:
        for current_person in current_family:
            if current_person.lower() == name.lower():
                return current_family[current_person]


def getfamilyid(passed_person_id):
    searched_person_id = int(passed_person_id)
    for current_family_id, current_family in enumerate(families):
        for current_person in current_family:
            # print(person, family[person], passed_person_id)
            if current_family[current_person] == searched_person_id:
                # print(person_id, family[person])
                # print("Found person with this "+str(passed_person_id)+" person_id")
                return current_family_id


def getpersonname(passed_person_id):
    current_person_id = int(passed_person_id)
    for current_family in families:
        for current_person in current_family:
            # print(person, family[person], passed_person_id)
            if current_family[current_person] == current_person_id:
                # print("Found person with this "+str(passed_person_id)+" person_id")
                return current_person


def gettargetname(passed_person_id):
    try:
        print("Found target: ")
        return shuffled_ids[int(passed_person_id)]
    except Exception:
        print(shuffled_ids)
        print("DID NOT FIND TARGET FOR PERSON!")
        return 0


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
    return render_template("graph.html",
                           id="number " + str(session["user_id"]),
                           image="graph.png")


@app.route("/secretgraph")
@login_required
def secretgraph():
    check = check_if_admin()
    if check is not None:
        return check
    return render_template("graph.html",
                           id=str(getpersonname(session["user_id"])),
                           image="secretgraph.png")


@app.route("/dumpinfo")
@login_required
def dumpinfo():
    check = check_if_admin()
    if check is not None:
        return check

    return render_template("error.html", message=str([str(shuffled_names), str(families)]))


def check_if_admin():
    user_id = session["user_id"]
    requester = getpersonname(user_id)
    if requester != "admin" and requester != "taavi":
        return render_template("error.html", message="Pls no hax " + requester + "!!")
    else:
        return None


@app.route("/setup")
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


@app.route("/recreategraph")
@login_required
def regraph():
    check = check_if_admin()
    if check is not None:
        return check

    families_give_copy = copy.deepcopy(families)  # Does the person need to give a gift
    for family_index, family in enumerate(families_give_copy):
        for person in family:
            families_give_copy[family_index][person] = True

    families_take_copy = copy.deepcopy(families)  # Does the person need to take a gift
    for family_index, family in enumerate(families_take_copy):
        for person in family:
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
    for family_id, family in enumerate(families):
        for person, person_id in family.items():
            members_to_families[person_id] = family_id

    families_to_members = {}
    for family_id, family in enumerate(families):
        families_to_members[family_id] = set()
        for person, person_id in family.items():
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

    # Store the values globally
    global shuffled_names
    global shuffled_ids
    shuffled_names = copy.deepcopy(families_shuf_nam)
    shuffled_ids = copy.deepcopy(families_shuf_ids)

    for key, value in shuffled_ids.items():
        shuffled_ids_str[str(key)] = str(value)
    #    print(shuffled_names)
    #    print(shuffled_ids)

    with open("./graph.json", "w") as file:
        file.write(json.dumps([shuffled_names, shuffled_ids_str]))
        print("Wrote shuffle to file")

    digraph = netx.DiGraph(iterations=10000, scale=2)
    digraph.add_nodes_from(copy.deepcopy(shuffled_ids).keys())

    for source, destination in copy.deepcopy(shuffled_ids).items():
        digraph.add_edges_from([(source, destination)])

    save_graph(digraph, "./static/graph.png")
    del digraph
    rerendernamegraph()  # create the graph with names

    return render_template("success.html", action="Genereeritud", link="./notes")


@app.route("/rerendergraph")
@login_required
def rerender():
    global shuffled_names
    global shuffled_ids
    check = check_if_admin()
    if check is not None:
        return check

    digraph = netx.DiGraph(iterations=100000000, scale=2)
    digraph.add_nodes_from(copy.deepcopy(shuffled_ids).keys())

    for source, destination in copy.deepcopy(shuffled_ids).items():
        digraph.add_edges_from([(source, destination)])

    save_graph(digraph, "./static/graph.png")
    return render_template("success.html", action="Genereeritud", link="./notes")


@app.route("/rerendernamegraph")
@login_required
def rerendernamegraph():
    global shuffled_names
    global shuffled_ids
    check = check_if_admin()
    if check is not None:
        return check

    digraph = netx.DiGraph(iterations=100000000, scale=2)  # This is probably a horrible idea with more nodes

    for shuffled_ids_id in copy.deepcopy(shuffled_ids).keys():
        digraph.add_node(shuffled_ids_id)

    for source, destination in copy.deepcopy(shuffled_ids).items():
        digraph.add_edges_from([(source, destination)])

    save_graph(digraph, "./static/secretgraph.png", colored=True)

    return render_template("success.html", action="Genereeritud", link="./graph")


def save_graph(passed_graph, file_name, colored=False):
    # This function just saves a networkx graph into a .png file without any GUI(!)
    plotlib.figure(num=None, figsize=(10, 10), dpi=60)
    plotlib.axis("off")  # Turn off the axis display
    fig = plotlib.figure(1)
    pos = netx.circular_layout(passed_graph)

    name_id_lookup_dict = {}  # Let's create a name-id mapping

    for name in shuffled_names.keys():
        name_id_lookup_dict[getpersonid(name)] = name

    if colored:  # Try to properly color the nodes
        for node in passed_graph:
            if node in person_colors:
                node_color = person_colors[node]
            else:
                node_color = chistmasy_colors[0]

            netx.draw_networkx_nodes([node], pos, node_size=1500, node_color=node_color)
    else:
        netx.draw_networkx_nodes(passed_graph, pos, node_size=1500, node_color=chistmasy_colors[0])

    netx.draw_networkx_edges(passed_graph, pos)

    if colored:
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
    check = check_if_admin(request)
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

    try:  # Not the prettiest, but tries to display names in the correct form
        return render_template("show_notes.html", notes=currentnotes, target=names_proper[username])
    except Exception:
        return render_template("show_notes.html", notes=currentnotes, target=getpersonname(user_id))


@app.route("/login")
def login():
    if debug:
        try:
            check = check_if_admin(request)
            if check is not None:
                return check
            print("Now", request.authorization.username.lower(), "has a header.")
            return render_template("success.html", action="Sisse logitud", link="./setup")
        except Exception:
            return Response(
                'This setup is in DEBUG MODE!\n'
                'This page only exists to give you a random cookie', 401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'})
    else:
        render_template("error.html", message="Pls no try hax!!")


if __name__ == "__main__":
    load_forms()
    load_mapping()
    load_shuffling()
    load_colors()

    if debug:
        print("Starting in debug!!!")
        app.run(debug=True, use_evalex=False, host="192.168.0.100", port=5000)
    else:
        print("Starting in production.")
        app.run(debug=False, use_evalex=False, host="127.0.0.1")
