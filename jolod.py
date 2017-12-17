#!/usr/bin/python3
# coding=utf-8
# author=Taavi Eomäe
import json
import matplotlib as pylab
pylab.use("Agg")
from flask import Flask, request, render_template, Response
import matplotlib.pyplot as plotlib
import networkx as netx
import random
import copy

app = Flask(__name__)
debug = True  # If debugging is enabled

# Contains placeholder names and families that are going to 
# be written into a file on first launch, after that it's
# going to be loaded from there and these lines could be removed
fam_1 = {"Fam1_1": 0, "Fam1_2": 0, "Fam1_3": 0, "Fam1_4": 0}
fam_2 = {"Fam2_1": 0, "Fam2_2": 0, "Fam2_3": 0}
fam_3 = {"Fam3_1": 0, "Fam3_2": 0}
fam_4 = {"Fam4_1": 0, "Fam4_2": 0, "Fam4_3": 0, "Fam4_4": 0}
fam_5 = {"Fam5_1": 0, "Fam5_2": 0}

families = [fam_1, fam_2, fam_3, fam_4, fam_5]

names_proper = {
    # As the software displays messages in estonian it'd be
    # better if names had an genitive form to look up, feel free
    # to remove this list, it is saved into a file on first launch
    # and then loaded from there on future launches
    "Fam1_1": "Fam_1_1i"
}

shuffled_names = {}  # Will contain the shuffled names and IDs
shuffled_ids = {}

# Just for assigning families a few colors, if you have more than five families, add more
chistmasy_colors = ["#B3000C", "#DC3D2A", "#0DEF42", "#00B32C", "#0D5901"]


def load_forms():
    global names_proper
    try:  # Load user names in genitive form from file
        print("Trying to load user names in genitive form from file")
        tmp_names_proper = {}
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
            file.write(json.dumps(str(names_proper)))
            print("Wrote user names in genitive form to file")


load_forms()


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
                raise Exception("Not enough families!")
        families = tmp_families
        print("Loaded user IDs from file")
    except Exception as e:
        print("Loading failed:", e)
        print("Generating user IDs")
        person_id = 1  # Assign IDs for every person, let admin user keep it's 0
        for family in families:
            for person in family:
                family[person] = person_id
                person_id += 1
        with open("./ids.json", "w") as file:
            file.write(json.dumps(str(families)))
            print("Wrote user IDs to file")


load_mapping()

def load_shuffling():
    global shuffled_ids
    global shuffled_names

    try:  # Load the shuffling mapping from file
        with open("./graph.json", "r") as file:
            [shuffled_names, shuffled_ids_tmp] = json.load(file)
        for key in shuffled_ids_tmp:  # Need to fix json not storing integers
            shuffled_ids[int(key)] = shuffled_ids_tmp[key]
        print("Loaded shuffle from file")
    except:
        print("No shuffle exists! Generate one!")


load_shuffling()

person_colors = {}
for family_id, family in enumerate(families):
    for person, person_id in family.items():
        person_colors[person_id] = chistmasy_colors[family_id]


def getpersonid(name):
    for family in families:
        for person in family:
            if person.lower() == name.lower():
                return family[person]


def getfamilyid(person_person_id):
    person_id = int(person_person_id)
    for family_id, family in enumerate(families):
        for person in family:
            # print(person, family[person], person_person_id)
            if family[person] == person_id:
                # print(person_id, family[person])
                # print("Found person with this "+str(person_person_id)+" person_id")
                return family_id


def getpersonname(person_person_id):
    person_id = int(person_person_id)
    for family in families:
        for person in family:
            # print(person, family[person], person_person_id)
            if family[person] == person_id:
                # print("Found person with this "+str(person_person_id)+" person_id")
                return person


def gettargetname(person_person_id):
    try:
        print("Found target: ")
        return shuffled_ids[int(person_person_id)]
    except:
        print(shuffled_ids)
        print("DID NOT FIND TARGET FOR PERSON!")
        return 0


@app.route("/")
def index():
    username = request.authorization.username
    return render_template("index.html", auth=username)


@app.route("/shuffle")
def shuffle():
    print(request.authorization.username)
    gifter = getpersonid(request.authorization.username)
    print(gifter)
    giftee = gettargetname(gifter)
    print(giftee)
    return render_template("shuffle.html", id=giftee)


@app.route("/notes")
def notes():
    username = request.authorization.username
    useridno = str(getpersonid(username))
    notes = ["Praegu on siin ainult veel tühjus, ei tahagi jõuludeks midagi?"]
    try:
        with open("./notes/" + useridno) as file:
            notes = json.load(file)
    except Exception as e:
        print(e)

    if len(notes) <= 0:
        notes = ["Praegu on siin ainult veel tühjus, ei tahagi jõuludeks midagi?"]
    return render_template("notes.html", list=notes)


@app.route("/createnote", methods=["GET"])
def createnote():
    return render_template("createnote.html", title="Lisa uus")


@app.route("/createnote", methods=["POST"])
def createnote_add():
    print("Got a post request to add a note")
    username = request.authorization.username
    print("Found user:", username)
    useridno = str(getpersonid(username))
    print("Found user id:", useridno)
    currentnotes = []
    addednote = request.form["note"]

    if len(addednote) > 1000:
        return render_template("error.html", message="Pls no hax " + request.authorization.username + "!!")
    elif len(addednote) <= 0:
        return render_template("error.html",
                               message="Jõuluvana tühjust tuua ei saa, " + request.authorization.username + "!")
    print("Trying to add a note:", addednote)
    try:
        print("Opening file", useridno)
        with open("./notes/" + useridno, "r") as file:
            currentnotes = json.load(file)
    except Exception as e:
        print(e)
    if len(currentnotes) == 999:
        return render_template("error.html",
                               message="Soovinimekiri muutuks liiga pikaks, " + request.authorization.username + "")

    currentnotes.append(addednote)

    with open("./notes/" + useridno, "w") as file:
        file.write(json.dumps(currentnotes))
    return render_template("success.html", action="Lisatud")


@app.route("/editnote", methods=["GET"])
def editnote():
    username = request.authorization.username
    useridno = str(getpersonid(username))
    currentnotes = []
    print("Trying to remove a note:", request.args["id"])
    try:
        int(request.args["id"])
    except:
        return render_template("error.html", message="Pls no hax " + request.authorization.username + "!!")

    try:
        print("Opening file", useridno)
        with open("./notes/" + useridno, "r") as file:
            currentnotes = json.load(file)
    except Exception as e:
        print(e)

    if int(request.args["id"]) >= len(currentnotes):
        return render_template("error.html", message="Ei leidnud seda, mida muuta tahtsid 🤔")
    return render_template("createnote.html", action="Muuda", placeholder=currentnotes[int(request.args["id"])])


@app.route("/editnote", methods=["POST"])
def editnote_edit():
    print("Got a post request to edit a note")
    username = request.authorization.username
    print("Found user:", username)
    useridno = str(getpersonid(username))
    print("Found user id:", useridno)
    currentnotes = []
    addednote = request.form["note"]
    print("Trying to add a note:", addednote)
    try:
        print("Opening file", useridno)
        with open("./notes/" + useridno, "r") as file:
            currentnotes = json.load(file)
    except Exception as e:
        print(e)

    currentnotes[int(request.args["id"])] = addednote

    with open("./notes/" + useridno, "w") as file:
        file.write(json.dumps(currentnotes))
    return render_template("success.html", action="Muudetud")


@app.route("/removenote")
def deletenote():
    username = request.authorization.username
    useridno = str(getpersonid(username))
    currentnotes = []
    print("Trying to remove a note:", request.args["id"])
    try:
        print("Opening file", useridno)
        with open("./notes/" + useridno, "r") as file:
            currentnotes = json.load(file)
    except Exception as e:
        print(e)

    try:
        currentnotes.pop(int(request.args["id"]))
    except:
        return render_template("error.html", message="Ei leidnud seda, mida kustutada tahtsid")

    with open("./notes/" + useridno, "w") as file:
        file.write(json.dumps(currentnotes))
    print("Removed", username, "note with ID", request.args["id"])
    return render_template("success.html", action="Eemaldatud")


@app.route("/graph")
def graph():
    return render_template("graph.html", id=str(getpersonid(request.authorization.username)))


@app.route("/dumpinfo")
def dumpinfo():
    check = check_if_admin(request)
    if check is not None:
        return check

    return render_template("error.html", message=str([str(shuffled_names), str(families)]))


def check_if_admin(request):
    requester = request.authorization.username.lower()
    if requester != "admin" and requester != "taavi":
        return render_template("error.html", message="Pls no hax " + request.authorization.username + "!!")
    else:
        return None


@app.route("/recreategraph")
def regraph():
    check = check_if_admin(request)
    if check is not None:
        return check

    families_list_copy = copy.deepcopy(families)

    families_give_copy = copy.deepcopy(families)  # Does the person need to give a gift
    for index, family in enumerate(families_give_copy):
        for person in family:
            families_give_copy[index][person] = True

    families_take_copy = copy.deepcopy(families)  # Does the person need to take a gift
    for index, family in enumerate(families_take_copy):
        for person in family:
            families_take_copy[index][person] = True

    families_shuf_nam = {}
    families_shuf_ids = {}
    #    print("Starting finding matches")
    for index, family in enumerate(families_list_copy):  # For each family among every family
        for person in family:  # For each person in given family
            if families_give_copy[index][person] == True:  # If person needs to gift
                #                print("Looking for a match for:", person, getpersonid(person))
                familynumbers = list(range(0, index))
                familynumbers.extend(range(index + 1, len(families) - 1))
                random.shuffle(familynumbers)
                for number in familynumbers:
                    receiving_family_index = number
                    receiving_family = families_take_copy[number]  # For each receiving family
                    #                    print("Looking at other families:", receiving_family)

                    for receiving_person in receiving_family:  # For each person in other family
                        if families_take_copy[receiving_family_index][receiving_person] == True and \
                                families_give_copy[index][person] == True:  # If person needs to receive
                            families_take_copy[receiving_family_index][
                                receiving_person] = False  # ; print("Receiving:", receiving_family_index, receiving_person)
                            families_give_copy[index][person] = False  # ; print("Giving:", index, person)
                            families_shuf_nam[person] = receiving_person
                            families_shuf_ids[getpersonid(person)] = getpersonid(receiving_person)
                            #                             print("Breaking")
                            break

    # Store the values globally
    global shuffled_names
    global shuffled_ids
    shuffled_names = copy.deepcopy(families_shuf_nam)
    shuffled_ids = copy.deepcopy(families_shuf_ids)
    shuffled_ids_str = {}
    for key, value in shuffled_ids.items():
        shuffled_ids_str[key] = value
    #    print(shuffled_names)
    #    print(shuffled_ids)
    with open("./graph.json", "w") as file:
        file.write(json.dumps([shuffled_names, shuffled_ids_str]))
        print("Wrote shuffle to file")

    # graph=nx.Graph(k=2)
    #    print(shuffled_ids)
    graph = netx.DiGraph(iterations=100, scale=2)
    graph.add_nodes_from(copy.deepcopy(shuffled_ids).keys())
    # for number in range(0, 10):
    #    graph.remove_node(number)
    #    print(shuffled_ids)
    for source, destination in copy.deepcopy(shuffled_ids).items():
        #        print("Source:", source, ", side:", destination)
        graph.add_edges_from([(source, destination)])
    save_graph(graph, "./static/graph.png")
    #    print(shuffled_ids)
    return render_template("success.html", action="Genereeritud")


@app.route("/rerendergraph")
def rerender():
    global shuffled_names
    global shuffled_ids
    check = check_if_admin(request)
    if check is not None:
        return check
    #    print(shuffled_ids)
    digraph = netx.DiGraph(iterations=100000000, scale=2)
    digraph.add_nodes_from(copy.deepcopy(shuffled_ids).keys())
    #    print(shuffled_ids)
    for source, destination in copy.deepcopy(shuffled_ids).items():
        #        print(source, destination)
        digraph.add_edges_from([(source, destination)])
    save_graph(digraph, "./static/graph.png")
    return render_template("success.html", action="Genereeritud")


@app.route("/rerendernamegraph")
def rerendernamegraph():
    global shuffled_names
    global shuffled_ids
    check = check_if_admin(request)
    if check is not None:
        return check
    #    print(shuffled_ids)
    graph = netx.DiGraph(iterations=100000000, scale=2)
    
    for person_id in copy.deepcopy(shuffled_ids).keys():
        graph.add_node(person_id)
        # graph.add_nodes_from(copy.deepcopy(shuffled_ids).keys())
        # print(shuffled_ids)
    for source, destination in copy.deepcopy(shuffled_ids).items():
        #        print(source, destination)
        graph.add_edges_from([(source, destination)])
    save_graph(graph, "./static/graph.png")

    return render_template("success.html", action="Genereeritud")


def save_graph(passed_graph, file_name):
    # initialze Figure
    # print(graph.nodes())
    plotlib.figure(num=None, figsize=(10, 10), dpi=60)
    plotlib.axis('off')
    fig = plotlib.figure(1)
    pos = netx.circular_layout(passed_graph)

    name_id_lookup_dict = {}  # Let's create a name-id mapping
    for name in shuffled_names.keys():
        name_id_lookup_dict[getpersonid(name)] = name


    for node in passed_graph:
        node_color = person_colors[node]
        print(node_color)
        netx.draw_networkx_nodes([node], pos, node_size=1000, node_color=node_color)
    netx.draw_networkx_edges(passed_graph, pos)
    netx.draw_networkx_labels(passed_graph, pos, labels=name_id_lookup_dict)


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
def giftingto():
    check = check_if_admin(request)
    if check is not None:
        if request.args["id"] != str(gettargetname(getpersonid(request.authorization.username.lower()))):
            return check
    print("Trying to display notes of:", request.args["id"])
    useridno = request.args["id"]
    try:
        value = int(useridno)
        if value < 0:
            raise Exception
    except:
        return render_template("error.html", message="Pls no hax " + request.authorization.username + "!!")

    currentnotes = ["Praegu on siin ainult veel tühjus"]
    try:
        print("Opening file:", useridno)
        with open("./notes/" + useridno, "r") as file:
            currentnotes = json.load(file)
    except Exception as e:
        print(e)
    print(useridno, getpersonname(useridno))
    try:
        return render_template("show_notes.html", notes=currentnotes, target=names_proper[getpersonname(useridno)])
    except:
        return render_template("show_notes.html", notes=currentnotes, target=getpersonname(useridno))


@app.route("/reconfigurefamilies")
def reconfigurefamilies():
    return None


if __name__ == "__main__":
    if debug:
        print("Starting in debug!!!")
        app.run(debug=True, use_evalex=False, host="192.168.0.100", port=5000)
    else:
        print("Starting in production.")
        app.run(debug=False, use_evalex=False, host="127.0.0.1")
