#!/usr/bin/python3
# coding=utf-8
# author=Taavi Eomäe

#####
# TODO:
# * Add marking gifts as bougth
#
# Known flaws:
# * SecretSanta can't match less than two people or people from less than one family
####

# Plotting
import matplotlib as pylab
from flask_wtf import RecaptchaField

pylab.use("Agg")  # Because we won't have a GUI on the server itself
import matplotlib.pyplot as plotlib
import networkx as netx

# Graphing
import secretsanta

# Utilities
import copy
import datetime
import random

# Flask
from flask import request, render_template, session, redirect
from flask_security import login_required, logout_user, SQLAlchemyUserDatastore, forms, Security
from flask_login import current_user
from flask_mail import Message

# App specific config
from config import Config, db, app, mail  # , celery

# Database models
from models import notes_model, family_model, shuffles_model, groups_model, users_groups_admins_model, \
    users_families_admins_model, names_model

import sys

sys.setrecursionlimit(2000)

# Setup Flask-Security
userroles = db.Table(
    "roles_users",
    db.Column("id", db.Integer(), db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer(), db.ForeignKey("role.id"))
)

from models import users_model

user_datastore = SQLAlchemyUserDatastore(db,
                                         users_model.User,
                                         users_model.Role)


class ExtendedRegistrerForm(forms.RegisterForm):
    username = forms.StringField("Eesnimi", [forms.Required()])
    recaptcha = RecaptchaField("Captcha")


class ExtendedResetForm(forms.ResetPasswordForm):
    recaptcha = RecaptchaField("Captcha")


class ExtendedConfirmationForm(forms.SendConfirmationForm):
    recaptcha = RecaptchaField("Captcha")


class ExtendedForgotPasswordForm(forms.ForgotPasswordForm):
    recaptcha = RecaptchaField("Captcha")


security = Security(app, user_datastore,
                    confirm_register_form=ExtendedRegistrerForm,
                    reset_password_form=ExtendedResetForm,
                    send_confirmation_form=ExtendedConfirmationForm,
                    forgot_password_form=ExtendedForgotPasswordForm)

# Just for assigning members_to_families a few colors
chistmasy_colors = ["#B3000C", "#DC3D2A", "#0DEF42", "#00B32C", "#0D5901"]


def getpersonid(name):
    return users_model.User.query.filter(users_model.User.username == name).first().id


def getfamilyid(passed_person_id):
    passed_person_id = int(passed_person_id)
    db_families_user_has_conn = users_families_admins_model.UFARelationship.query.filter(
        users_families_admins_model.UFARelationship.user_id == passed_person_id).all()

    db_family = db_families_user_has_conn[0]
    family_id = db_family.family_id
    return family_id


def getpersonname(passed_person_id):
    return users_model.User.query.get(passed_person_id).username


def gettargetid(passed_person_id):
    try:
        return shuffles_model.Shuffle.query.get(passed_person_id).getter
    except Exception:
        return -1


def getnameingenitive(name):
    try:
        return names_model.Name.query.get(name).genitive
    except Exception:
        return name


# Views
@app.route("/test")
@login_required
def test():
    return render_template("error.html", message="Here you go!", title="Error")


def index():
    user_id = session["user_id"]
    username = getpersonname(user_id)
    no_shuffle = False
    if gettargetid(user_id) == -1:
        no_shuffle = True
    return render_template("index.html", auth=username, no_shuffle=no_shuffle, uid=user_id, title="Kodu")


@app.route("/about")
def about():
    return render_template("home.html", no_sidebar=True)


@app.route("/")
def home():
    if current_user.is_authenticated:
        return index()
    else:
        return about()


@app.route("/contact")
def contact():
    return render_template("contact.html", no_sidebar=True)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/shuffle")
@login_required
def shuffle():
    user_id = session["user_id"]
    username = getpersonname(user_id)
    print(username)
    gifter = getpersonid(username)
    print(gifter)
    giftee = gettargetid(gifter)
    print(giftee)
    return render_template("shuffle.html", title="Loosimine", id=giftee)


@app.route("/notes")
@login_required
def notes():
    user_id = session["user_id"]
    username = getpersonname(user_id)
    notes_from_file = []
    empty = False
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
        empty = True
    return render_template("notes.html", list=notes_from_file, empty=empty, title="Minu jõulusoovid")


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
        return render_template("error.html", message="Pls no hax " + username + "!!", title="Error")
    elif len(addednote) <= 0:
        return render_template("error.html",
                               message="Jõuluvana tühjust tuua ei saa, " + username + "!", title="Error")
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
                               message="Soovinimekiri muutuks liiga pikaks, " + username + "", title="Error")

    currentnotes.append(addednote)

    #    with open("./notes/" + useridno, "w") as file:
    #        file.write(json.dumps(currentnotes))
    db_entry_notes = notes_model.Notes(
        user_id=user_id,
        notes=currentnotes,
    )
    try:
        db.session.add(db_entry_notes)
        db.session.commit()
    except:
        db.session.rollback()
        row = notes_model.Notes.query.get(user_id)
        row.notes = currentnotes
        db.session.commit()
    return render_template("success.html", action="Lisatud", link="./notes", title="Lisatud")


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
        return render_template("error.html", message="Pls no hax " + username + "!!", title="Error")

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
        return render_template("error.html", message="Ei leidnud seda, mida muuta tahtsid 🤔", title="Error")
    return render_template("createnote.html", action="Muuda", title="Muuda",
                           placeholder=currentnotes[int(request.args["id"])])


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
    try:
        db.session.add(db_entry_notes)
        db.session.commit()
    except:
        db.session.rollback()
        row = notes_model.Notes.query.get(user_id)
        row.notes = currentnotes
        db.session.commit()

    return render_template("success.html", action="Muudetud", link="./notes", title="Muudetud")


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
        return render_template("error.html", message="Ei leidnud seda, mida kustutada tahtsid", title="Error")

    #    with open("./notes/" + useridno, "w") as file:
    #        file.write(json.dumps(currentnotes))
    db_entry_notes = notes_model.Notes(
        user_id=user_id,
        notes=currentnotes,
    )
    try:
        db.session.add(db_entry_notes)
        db.session.commit()
    except:
        db.session.rollback()
        row = notes_model.Notes.query.get(user_id)
        row.notes = currentnotes
        db.session.commit()

    print("Removed", username, "note with ID", request.args["id"])
    return render_template("success.html", action="Eemaldatud", link="./notes", title="Eemaldatud")


@app.route("/graph")
@login_required
def graph():
    user_id = session["user_id"]
    try:
        family_id = getfamilyid(user_id)
        family_obj = family_model.Family.query.get(family_id)
        family_group = family_obj.group
        return render_template("graph.html",
                               id="number " + str(session["user_id"]),
                               image="graph" + str(family_group) + ".png")
    except:
        return render_template("error.html", message="Loosimist ei ole administraatori poolt tehtud", title="Error")


@app.route("/settings")
@login_required
def settings():
    user_id = session["user_id"]
    user_obj = users_model.User.query.get(user_id)
    is_in_group = False
    is_in_family = False

    db_families_user_has_conn = users_families_admins_model.UFARelationship.query.filter(
        users_families_admins_model.UFARelationship.user_id == user_id).all()

    user_families = {}
    for family_relationship in db_families_user_has_conn:
        family = family_model.Family.query.get(family_relationship.family_id)
        user_families[family.name] = (family.id, family_relationship.admin)
        is_in_family = True

    db_groups_user_has_conn = users_groups_admins_model.UGARelationship.query.filter(
        users_groups_admins_model.UGARelationship.user_id == user_id).all()

    user_groups = {}
    for group_relationship in db_groups_user_has_conn:
        group = groups_model.Groups.query.get(group_relationship.group_id)
        user_groups[group.description] = (group.id, group_relationship.admin)
        is_in_group = True

    return render_template("settings.html",
                           user_id=user_id,
                           user_name=user_obj.username,
                           family_admin=is_in_family,
                           group_admin=is_in_group,
                           families=user_families,
                           groups=user_groups,
                           title="Seaded")


@app.route("/editfam")
@login_required
def editfamily():
    user_id = session["user_id"]
    user_obj = users_model.User.query.get(user_id)

    db_families_user_has_conn = users_families_admins_model.UFARelationship.query.filter(
        users_families_admins_model.UFARelationship.user_id == user_id).all()

    family = []
    db_family = db_families_user_has_conn[int(request.args["id"])]
    family_id = db_family.family_id
    db_family_members = users_families_admins_model.UFARelationship.query.filter(
        users_families_admins_model.UFARelationship.family_id == family_id).all()

    for member in db_family_members:
        family.append((getpersonname(member.user_id), member.user_id))

    return render_template("editfam.html", family=family, title="Muuda perekonda")


@app.route("/editfam", methods=["POST"])
@login_required
def editfamily_with_action():
    user_id = session["user_id"]
    user_obj = users_model.User.query.get(user_id)
    try:
        action = request.args["action"]
    except Exception:
        return render_template("error.html", message="Tekkis viga, kontrolli linki", title="Error")

    return None


@app.route("/editgroup")
@login_required
def editgroup():
    user_id = session["user_id"]
    user_obj = users_model.User.query.get(user_id)
    return render_template("editgroup.html", title="Muuda gruppi")


@app.route("/editgroup", methods=["POST"])
@login_required
def editgroup_with_action():
    user_id = session["user_id"]
    user_obj = users_model.User.query.get(user_id)
    return None


@app.route("/secretgraph")
@login_required
def secretgraph():
    check = check_if_admin()
    if check is not None:
        return check
    return render_template("graph.html",
                           id=str(getpersonname(session["user_id"])),
                           image="s" + str(request.args["id"]) + ".png",
                           title="Salajane graaf")


def check_if_admin():
    user_id = session["user_id"]
    requester = getpersonname(user_id)
    if requester != "admin" and requester != "taavi":
        return render_template("error.html", message="Pls no hax " + requester + "!!", title="Error")
    else:
        return None


"""@app.route("/family")
@login_required
def family():
    user_id = session["user_id"]
    family_id = users_model.User.query.get(user_id).family_id
    family_members = users_model.User.query.filter(users_model.User.family_id == family_id).all()
    family_member_names = []
    for member in family_members:
        family_member_names.append(member.username)
    return render_template("show_family.html", names=family_member_names, title="Perekond")
"""


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
        raise Exception("Coloring nodes is not yet supported")
        # name_id_lookup_dict = {}  # Let's create a admin-user_id mapping

        # for name in shuffled_names.keys():
        #    name_id_lookup_dict[getpersonid(name)] = name

        # netx.draw_networkx_labels(passed_graph, pos, labels=name_id_lookup_dict)
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


@app.route("/recreategraph")
@login_required
def regraph():
    #    check = check_if_admin()
    #    if check is not None:
    #        return check

    user_id = session["user_id"]
    family_id = getfamilyid(user_id)
    family_obj = family_model.Family.query.get(family_id)
    family_group = family_obj.group

    database_families = family_model.Family.query.filter(family_model.Family.group == family_group).all()
    database_all_families_with_members = []
    for db_family in database_families:
        database_family_members = users_families_admins_model.UFARelationship.query.filter(
            users_families_admins_model.UFARelationship.family_id == db_family.id).all()
        database_all_families_with_members.append(database_family_members)

    families = []
    family_ids_map = {}
    for family_index, list_family in enumerate(database_all_families_with_members):
        families.insert(family_index, {})
        for person_index, person in enumerate(list_family):
            family_ids_map[family_index] = getfamilyid(person.user_id)
            families[family_index][getpersonname(person.user_id)] = person.user_id

    families_shuf_nam = {}
    families_shuf_ids = {}
    #    print("Starting finding matches")
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

    save_graph(digraph, "./static/graph" + str(family_group) + ".png")
    del digraph
    #    rerendernamegraph()  # create the graph with names

    return render_template("success.html", action="Genereeritud", link="./notes", title="Genereeritud")


@app.route("/testmail")
@login_required
def test_mail():
    with mail.connect() as conn:
        print(conn.configure_host().vrfy)
        msg = Message(recipients=["root@localhost"],
                      body="test",
                      subject="test2")

        conn.send(msg)
    return render_template("success.html", action="Sent", link="./testmail", title="Saadetud")


@app.route("/rerendergraph")
@login_required
def rerender():
    check = check_if_admin()
    if check is not None:
        return check

    digraph = netx.DiGraph(iterations=100000000, scale=2)
    #    digraph.add_nodes_from(copy.deepcopy(families_shuf_ids).keys())

    #    for source, destination in copy.deepcopy(families_shuf_ids).items():
    #        digraph.add_edges_from([(source, destination)])

    save_graph(digraph, "./static/graph"".png")
    return render_template("success.html", action="Genereeritud", link="./notes", title="Genereeritud")


@app.route("/rerendernamegraph")
@login_required
def rerendernamegraph():
    check = check_if_admin()
    if check is not None:
        return check

    digraph = netx.DiGraph(iterations=100000000, scale=2)  # This is probably a horrible idea with more nodes

    # for shuffled_ids_id in copy.deepcopy(families_shuf_ids).keys():
    #    digraph.add_node(shuffled_ids_id)

    # for source, destination in copy.deepcopy(families_shuf_ids).items():
    #    digraph.add_edges_from([(source, destination)])

    save_graph(digraph, "./static/secretgraph.png", colored=True)

    return render_template("success.html", action="Genereeritud", link="./graph")


@app.route("/giftingto")
@login_required
def giftingto():
    check = check_if_admin()
    user_id = session["user_id"]
    username = getpersonname(user_id)

    try:
        request_id = int(request.args["id"])
    except Exception:
        request_id = gettargetid(user_id)

    if check is not None:  # Let's not let everyone read everyone's lists
        if request_id != gettargetid(user_id):
            return check

    try:  # Yeah, only valid IDs please
        value = int(request_id)
        if value == -1:
            return render_template("error.html", message="Loosimist ei ole veel administraatori poolt tehtud",
                                   title="Error")
        elif value < 0:
            raise Exception()
    except Exception:
        return render_template("error.html", message="Pls no hax " + username + "!!", title="Error")

    currentnotes = ["Praegu on siin ainult veel tühjus"]

    try:
        print("Opening file:", user_id)
        row = notes_model.Notes.query.get(request_id)
        currentnotes = row.notes
    except Exception as e:
        print("Error displaying notes, there might be none:", e)

    # try:  # Not the prettiest, but tries to display names in the correct form
    #    return render_template("show_notes.html", notes=currentnotes, target=names_proper[username])
    # except Exception:
    return render_template("show_notes.html",
                           notes=currentnotes,
                           target=getnameingenitive(getpersonname(request_id)),
                           title="Kingisoovid")


"""
@app.route("/login", methods=["GET"])
def login():
    render_template("security/login_user.html", title="Logi sisse")


@app.route("/register", methods=["GET"])
def register():
    render_template("security/register_user.html", title="Registreeru")


@app.route("/change", methods=["GET"])
@login_required
def change():
    render_template("security/change_password.html", title="Muuda parooli")


@app.route("/reset", methods=["GET"])
def reset():
    render_template("security/reset_password.html", title="Lähtesta parool")


@app.route("/confirm", methods=["GET"])
def confirmation():
    render_template("security/send_confirmation.html", title="Kinnita e-mail")
"""

if __name__ == "__main__":
    if Config.DEBUG:
        print("Starting in debug!")
        app.run(debug=Config.DEBUG, use_evalex=False, host="0.0.0.0", port=5000)
    else:
        print("Starting in production.")
        app.run(debug=Config.DEBUG, use_evalex=False, host="127.0.0.1")
