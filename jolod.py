#!/usr/bin/python3
# coding=utf-8
from flask import Flask, request, Response, render_template
import json
import matplotlib as pylab
pylab.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import random
import copy

app = Flask(__name__)

admin = {"Admin":0}
fam_1 = {"Fam1_1":0, "Fam1_2":0, "Fam1_3":0, "Fam1_4":0}
fam_2 = {"Fam2_1":0, "Fam2_2":0, "Fam2_3":0}
fam_3 = {"Fam3_1":0, "Fam3_2":0}
fam_4 = {"Fam4_1":0, "Fam4_2":0, "Fam4_3":0, "Fam4_4":0}
fam_5 = {"Fam5_1":0, "Fam5_2":0}

families = [fam_1, fam_2, fam_3, fam_4, fam_5]

names_proper = { # As the software displays messages in estonian it'd be better if names had an genitive form to look up
"Fam1_1":"Fam_1_1i"
}

shuffled_names = {}
shuffled_ids = {}

try:
    print("Trying to load user names in genitive form from file")
    with open("./genitive.json", "r") as file:
        tmp_names_proper = eval(json.load(file))
        print(tmp_names_proper)
        if len(tmp_names_proper) <= 0:
            print(len(tmp_names_proper))
            raise Exception
    names_proper = temp_names_proper
    print("Loaded user names in genitive form from file")
except:
    print("Writing names in genitive form to file")
    with open("./genitive.json", "w") as file:
        file.writelines(json.dumps(str(names_proper)))
        print("Wrote user names in genitive form to file")


try:
    with open("./ids.json", "r") as file:
        tmp_families = eval(json.load(file))
        if len(tmp_families) >= 2:
            if len(tmp_families[1]) <= 1:
                raise Exception
        else:
            raise Exception
    families = tmp_families
    print("Loaded user IDs from file")
except:
    print("Generating user IDs")
    id = 0 # Assign IDs for every person
    for family in families:
        for person in family:
            family[person] = id
            id+=1
    with open("./ids.json", "w") as file:
        file.writelines(json.dumps(str(families)))
        print("Wrote user IDs to file")

try:
    with open("./graph.json", "r") as file:
        [shuffled_names, shuffled_ids_tmp] = json.load(file)
    for key in shuffled_ids_tmp:
        shuffled_ids[int(key)] = shuffled_ids_tmp[key]
    print("Loaded shuffle from file")
except:
    print("No shuffle exists!")

def findpersonid(name):
    for family in families:
        for person in family:
            if person.lower() == name.lower():
                return family[person]

def findpersonname(id):
    id = int(id)
    for family in families:
        for person in family:
            #print(person, family[person], id)
            if family[person] == id:
                #print("Found person with this "+str(id)+" id")
                return person

def getgifttarget(id):
    try:
        print("Found target: ")
        return shuffled_ids[int(id)]
    except:
        print(shuffled_ids)
        print("DID NOT FIND TARGET FOR PERSON!")
        return 0

@app.route("/")
def index(auth=None):
    username = request.authorization.username
    return render_template("index.html", auth=username)

@app.route("/shuffle")
def shuffle():
    print(request.authorization.username)
    gifter = findpersonid(request.authorization.username)
    print(gifter)
    giftee = getgifttarget(gifter)
    print(giftee)
    return render_template("shuffle.html", id=giftee)

@app.route("/notes")
def notes():
    username = request.authorization.username
    useridno = str(findpersonid(username))
    notes = ["Praegu on siin ainult veel tühjus, ei tahagi jõuludeks midagi?"]
    try:
        with open("./notes/"+useridno) as file:
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
    useridno = str(findpersonid(username))
    print("Found user id:", useridno)
    currentnotes = []
    addednote = request.form["note"]

    if len(addednote) > 1000:
        return render_template("error.html", message="Pls no hax "+ request.authorization.username + "!!")
    elif len(addednote) <= 0:
        return render_template("error.html", message="Jõuluvana tühjust tuua ei saa, "+ request.authorization.username + "!")
    print("Trying to add a note:", addednote)
    try:
        print("Opening file", useridno)
        with open("./notes/"+useridno, "r") as file:
            currentnotes = json.load(file)
    except Exception as e:
        print(e)
    if len(currentnotes) == 999:
        return render_template("error.html", message="Soovinimekiri muutuks liiga pikaks, "+ request.authorization.username + "")

    currentnotes.append(addednote)

    with open("./notes/"+useridno, "w") as file:
        file.writelines(json.dumps(currentnotes))
    return render_template("success.html", action="Lisatud")

@app.route("/editnote", methods=["GET"])
def editnote():
    username = request.authorization.username
    useridno = str(findpersonid(username))
    currentnotes = []
    print("Trying to remove a note:", request.args["id"])
    try:
        int(request.args["id"])
    except:
        return render_template("error.html", message="Pls no hax "+ request.authorization.username + "!!")

    try:
        print("Opening file", useridno)
        with open("./notes/"+useridno, "r") as file:
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
    useridno = str(findpersonid(username))
    print("Found user id:", useridno)
    currentnotes = []
    addednote = request.form["note"]
    print("Trying to add a note:", addednote)
    try:
        print("Opening file", useridno)
        with open("./notes/"+useridno, "r") as file:
            currentnotes = json.load(file)
    except Exception as e:
        print(e)

    currentnotes[int(request.args["id"])] = addednote

    with open("./notes/"+useridno, "w") as file:
        file.writelines(json.dumps(currentnotes))
    return render_template("success.html", action="Muudetud")

@app.route("/removenote")
def deletenote():
    username = request.authorization.username
    useridno = str(findpersonid(username))
    currentnotes = []
    print("Trying to remove a note:", request.args["id"])
    try:
        print("Opening file", useridno)
        with open("./notes/"+useridno, "r") as file:
            currentnotes = json.load(file)
    except Exception as e:
        print(e)

    try:
        currentnotes.pop(int(request.args["id"]))
    except:
        return render_template("error.html", message="Ei leidnud seda, mida kustutada tahtsid")
    with open("./notes/"+useridno, "w") as file:
        file.writelines(json.dumps(currentnotes))
    print("Removed", username, "note with ID", request.args["id"])
    return render_template("success.html", action="Eemaldatud")

@app.route("/graph")
def graph():
    return render_template("graph.html", id=str(findpersonid(request.authorization.username)))

@app.route("/dumpinfo")
def dumpinfo():
    check = check_if_admin(request)
    if check != None:
        return check

    return render_template("error.html", message=str([str(shuffled_names), str(families)]))

def check_if_admin(request):
    requester = request.authorization.username.lower()
    if requester  != "admin" and requester != "taavi":
        return render_template("error.html", message="Pls no hax "+ request.authorization.username + "!!")
    else:
        return None


@app.route("/recreategraph")
def regraph():
    check = check_if_admin(request)
    if check != None:
        return check

    families_list_copy = copy.deepcopy(families)
    families_list_copy.pop(0)

    families_give_copy = copy.deepcopy(families) # Does the person need to give a gift
    families_give_copy.pop(0)
    for index, family in enumerate(families_give_copy):
        for person in family:
            families_give_copy[index][person] = True

    families_take_copy = copy.deepcopy(families) # Does the person need to take a gift
    families_take_copy.pop(0)
    for index, family in enumerate(families_take_copy):
        for person in family:
            families_take_copy[index][person] = True

    families_shuf_nam = {}
    families_shuf_ids = {}
#    print("Starting finding matches")
    for index, family in enumerate(families_list_copy):  # For each family among every family
        for person in family: # For each person in given family
            if families_give_copy[index][person] == True: # If person needs to gift
#                print("Looking for a match for:", person, findpersonid(person))
                familynumbers = list(range(0, index))
                familynumbers.extend(range(index+1, len(families)-1))
                random.shuffle(familynumbers)
                for number in familynumbers:
                    receiving_family_index = number
                    receiving_family = families_take_copy[number] # For each receiving family
#                    print("Looking at other families:", receiving_family)

                    for receiving_person in receiving_family: # For each person in other family
                         if families_take_copy[receiving_family_index][receiving_person] == True and families_give_copy[index][person] == True: # If person needs to receive
                             families_take_copy[receiving_family_index][receiving_person] = False#; print("Receiving:", receiving_family_index, receiving_person)
                             families_give_copy[index][person] = False#; print("Giving:", index, person)
                             families_shuf_nam[person] = receiving_person
                             families_shuf_ids[findpersonid(person)] = findpersonid(receiving_person)
#                             print("Breaking")
                             break

    # Store the values globally
    global shuffled_names
    global shuffled_ids
    shuffled_names = copy.deepcopy(families_shuf_nam)
    shuffled_ids = copy.deepcopy(families_shuf_ids)
#    print(shuffled_names)
#    print(shuffled_ids)
    with open("./graph.json", "w") as file:
        file.writelines(json.dumps([shuffled_names, shuffled_ids]))
        print("Wrote shuffle to file")

    #graph=nx.Graph(k=2)
#    print(shuffled_ids)
    graph=nx.DiGraph(iterations=100, scale=2)
    graph.add_nodes_from(copy.deepcopy(shuffled_ids).keys())
    #for number in range(0, 10):
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
    if check != None:
        return check
#    print(shuffled_ids)
    graph=nx.DiGraph(iterations=100000000, scale=2)
    graph.add_nodes_from(copy.deepcopy(shuffled_ids).keys())
#    print(shuffled_ids)
    for source, destination in copy.deepcopy(shuffled_ids).items():
#        print(source, destination)
        graph.add_edges_from([(source, destination)])
    save_graph(graph, "./static/graph.png")

    return render_template("success.html", action="Genereeritud")

def save_graph(graph, file_name):
    #initialze Figure
    print(graph.nodes())
    plt.figure(num=None, figsize=(10, 10), dpi=60)
    plt.axis('off')
    fig = plt.figure(1)
    pos = nx.circular_layout(graph)
    nx.draw_networkx_nodes(graph, pos)
    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_labels(graph, pos)

    cut = 0
    xmax = 2 + cut * max(xx for xx, yy in pos.values())
    ymax = 2 + cut * max(yy for xx, yy in pos.values())
    xmin = -2 + cut * min(xx for xx, yy in pos.values())
    ymin = -2 + cut * min(yy for xx, yy in pos.values())
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)

    fig.savefig(file_name, bbox_inches="tight")
    plt.close()
    print("Saved generated graph to file:", file_name)
    del fig

@app.route("/giftingto")
def giftingto():
    check = check_if_admin(request)
    if check != None:
        if request.args["id"] != str(getgifttarget(findpersonid(request.authorization.username.lower()))):
            return check
    print("Trying to display notes of:", request.args["id"])
    useridno = request.args["id"]
    try:
        value = int(useridno)
        if value < 0:
            raise Exception
    except:
        return render_template("error.html", message="Pls no hax "+ request.authorization.username + "!!")

    currentnotes = ["Praegu on siin ainult veel tühjus"]
    try:
        print("Opening file", useridno)
        with open("./notes/"+useridno, "r") as file:
            currentnotes = json.load(file)
    except Exception as e:
        print(e)
    print(useridno, findpersonname(useridno))
    try:
        return render_template("show_notes.html", notes=currentnotes, target=names_proper[findpersonname(useridno)])
    except:
        return render_template("show_notes.html", notes=currentnotes, target=findpersonname(useridno))

@app.route("/reconfigurefamilies")
def reconfigurefamilies():
    return Null

if __name__ == "__main__":
    app.run(debug=True, use_evalex=False)

