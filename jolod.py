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
import base64
import json
import itertools
from Cryptodome.Cipher import AES

# Flask
from flask import request, render_template, session, redirect, send_from_directory
from flask_security import login_required, logout_user, SQLAlchemyUserDatastore, forms, Security
from flask_login import current_user
from flask_mail import Message

# App specific config
from config import Config, db, app, mail

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
chistmasy_colors = ["#E5282A", "#DC3D2A", "#0DEF42", "#00B32C", "#0D5901"]


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


def send_graph(filename):
    return send_from_directory("./generated_graphs", filename)


def decrypt_id(encrypted_user_id):
    base64_raw_data = base64.urlsafe_b64decode(encrypted_user_id).decode()
    data = json.loads(base64_raw_data)
    ciphertext = base64.b64decode(data[0])
    nonce = base64.b64decode(data[1])
    tag = base64.b64decode(data[2])

    cipher = AES.new(Config.AES_KEY, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext).decode()

    try:
        cipher.verify(tag)
        print("The message is authentic:", plaintext)
    except ValueError:
        print("Key incorrect or message corrupted!")

    return plaintext


def encrypt_id(user_id):
    cipher = AES.new(Config.AES_KEY, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(bytes(str(user_id), encoding="utf8"))
    nonce = base64.b64encode(cipher.nonce).decode()
    ciphertext = base64.b64encode(ciphertext).decode()
    tag = base64.b64encode(tag).decode()
    json_package = json.dumps([ciphertext, nonce, tag])
    packed = base64.urlsafe_b64encode(bytes(json_package, "utf8")).decode()

    return packed


app.add_url_rule("/generated_graphs/<filename>", endpoint="generated_graphs", view_func=send_graph)

if not Config.DEBUG:
    @app.errorhandler(500)
    def error_500():
        return render_template("error.html", message="Päringu töötlemisel tekkis viga!", title="Error")


    @app.errorhandler(404)
    def error_404():
        return render_template("error.html", message="Lehte ei leitud!", title="Error")


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


@app.route("/robots.txt")
def robots():
    return send_from_directory(app.static_folder, "robots.txt")


@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(app.static_folder, "sitemap.xml")


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
    # username = getpersonname(user_id)
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
    notes_purchased = []
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
            notes_purchased = db_notes.notes_purchased
    except Exception as e:
        print(e)

    if len(currentnotes) >= 999:
        return render_template("error.html",
                               message="Soovinimekiri muutuks liiga pikaks, " + username + "", title="Error")

    currentnotes.append(addednote)
    notes_purchased.append(False)

    #    with open("./notes/" + useridno, "w") as file:
    #        file.write(json.dumps(currentnotes))
    db_entry_notes = notes_model.Notes(
        user_id=user_id,
        notes=currentnotes,
        notes_purchased=notes_purchased
    )

    try:
        db.session.add(db_entry_notes)
        db.session.commit()
    except Exception:
        db.session.rollback()
        row = notes_model.Notes.query.get(user_id)
        row.notes = currentnotes
        row.notes_purchased = notes_purchased
        db.session.commit()

    return render_template("success.html", action="Lisatud", link="./notes", title="Lisatud")


@app.route("/editnote", methods=["GET"])
@login_required
def editnote():
    user_id = session["user_id"]
    username = getpersonname(user_id)
    currentnotes = []

    try:
        request_id = request.args["id"]
        request_id = int(decrypt_id(request_id))

        print(user_id, "is trying to remove a note", request_id)
    except Exception:
        return render_template("error.html", message="Pls no hax " + username + "!!", title="Error")

    try:
        print(user_id, " is pening notes of ", request_id)
        db_notes = notes_model.Notes.query.get(user_id)
        if db_notes is not None:  # Don't want to display None
            currentnotes = db_notes.notes
    except Exception as e:
        print(e)

    if int(request_id) >= len(currentnotes):
        return render_template("error.html", message="Ei leidnud seda, mida muuta tahtsid 🤔", title="Error")

    return render_template("createnote.html", action="Muuda", title="Muuda",
                           placeholder=currentnotes[request_id])


@app.route("/editnote", methods=["POST"])
@login_required
def editnote_edit():
    print("Got a post request to edit a note")
    user_id = session["user_id"]
    # username = getpersonname(user_id)
    print("Found user id:", user_id)
    currentnotes = []
    notes_purchased = []

    addednote = request.form["note"]
    try:
        request_id = request.args["id"]
        request_id = int(decrypt_id(request_id))
    except Exception:
        request_id = -1

    if request_id < 0:
        return None

    try:
        print("Trying to add a note:", addednote)
        print("Opening file", user_id)
        #        with open("./notes/" + user_id, "r") as file:
        #            currentnotes = json.load(file)
        db_notes = notes_model.Notes.query.get(user_id)
        if db_notes is not None:  # Don't want to display None
            currentnotes = db_notes.notes
            notes_purchased = db_notes.notes_purchased
    except Exception as e:
        print(e)

    currentnotes[request_id] = addednote

    #    with open("./notes/" + user_id, "w") as file:
    #        file.write(json.dumps(currentnotes))
    db_entry_notes = notes_model.Notes(
        user_id=user_id,
        notes=currentnotes,
        notes_purchased=notes_purchased
    )

    try:
        db.session.add(db_entry_notes)
        db.session.commit()
    except Exception:
        db.session.rollback()
        row = notes_model.Notes.query.get(user_id)
        row.notes = currentnotes
        row.notes_purchased = notes_purchased
        db.session.commit()

    return render_template("success.html", action="Muudetud", link="./notes", title="Muudetud")


@app.route("/removenote")
@login_required
def deletenote():
    user_id = session["user_id"]
    username = getpersonname(user_id)
    currentnotes = []
    notes_purchased = []

    try:
        request_id = request.args["id"]
        request_id = int(request_id)
        print(user_id, " is trying to remove a note", request_id)
    except Exception:
        return render_template("error.html", message="Viga lingis", title="Error")

    try:
        print("Opening file", user_id)
        #        with open("./notes/" + useridno, "r") as file:
        #            currentnotes = json.load(file)
        db_notes = notes_model.Notes.query.get(user_id)
        if db_notes is not None:  # Don't want to display None
            currentnotes = db_notes.notes
            notes_purchased = db_notes.notes_purchased
    except Exception as e:
        print(e)

    try:
        currentnotes.pop(request_id)
        notes_purchased.pop(request_id)
    except Exception:
        return render_template("error.html", message="Ei leidnud seda, mida kustutada tahtsid", title="Error")

    #    with open("./notes/" + useridno, "w") as file:
    #        file.write(json.dumps(currentnotes))
    db_entry_notes = notes_model.Notes(
        user_id=user_id,
        notes=currentnotes,
        notes_purchased=notes_purchased
    )

    try:
        db.session.add(db_entry_notes)
        db.session.commit()
    except Exception:
        db.session.rollback()
        row = notes_model.Notes.query.get(user_id)
        row.notes = currentnotes
        row.notes_purchased = notes_purchased
        db.session.commit()

    print("Removed", username, "note with ID", request_id)
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
                               id=str(session["user_id"]),
                               image="graph_" + str(family_group) + ".png",
                               title="Graaf")
    except Exception:
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
    db_groups_user_has_conn = []
    for family_relationship in db_families_user_has_conn:
        family = family_model.Family.query.get(family_relationship.family_id)
        user_families[family.name] = (encrypt_id(family.id), family_relationship.admin)
        is_in_family = True
        db_groups_user_has_conn += (groups_model.Groups.query.filter(family_model.Family.group == family.group).all())

    user_groups = {}
    for group_relationship in db_groups_user_has_conn:
        uga_relationship = users_groups_admins_model.UGARelationship.query.filter(
            users_groups_admins_model.UGARelationship.user_id == user_id
            and
            users_groups_admins_model.UGARelationship.group_id == group_relationship.id).first()

        if not uga_relationship:
            user_groups[group_relationship.description] = (encrypt_id(group_relationship.id), False)
        else:
            user_groups[group_relationship.description] = (encrypt_id(group_relationship.id), uga_relationship.admin)
        is_in_group = True

    return render_template("settings.html",
                           user_id=user_id,
                           user_name=user_obj.username,
                           family_admin=is_in_family,
                           group_admin=is_in_group,
                           families=user_families,
                           groups=user_groups,
                           title="Seaded",
                           back_link="/")


@app.route("/editfam")
@login_required
def editfamily():
    user_id = session["user_id"]

    try:
        request_id = request.args["id"]
        request_id = int(decrypt_id(request_id))
    except Exception:
        return render_template("error.html", message="Tekkis viga, kontrolli linki", title="Error")

    if request_id < 0:
        return render_template("error.html", message="Tekkis viga, kontrolli linki", title="Error")

    db_family_members = users_families_admins_model.UFARelationship.query.filter(
        users_families_admins_model.UFARelationship.family_id == request_id).all()

    family = []
    show_admin_column = False
    for member in db_family_members:
        is_admin = False
        is_person = False
        if member.user_id == user_id:
            is_person = True

        family.append((getpersonname(member.user_id), encrypt_id(member.user_id), is_admin, is_person))

    return render_template("editfam.html",
                           family=family,
                           title="Muuda perekonda",
                           admin=show_admin_column,
                           back=False,
                           back_link="/settings")


@app.route("/editfam", methods=["POST"])
@login_required
def editfamily_with_action():
    # user_id = session["user_id"]

    # try:
    # action = request.args["action"]
    # request_id = request.args["id"]
    # request_id = int(decrypt_id(request_id))
    # except Exception:
    # return render_template("error.html", message="Tekkis viga, kontrolli linki", title="Error")

    return None


@app.route("/editgroup")
@login_required
def editgroup():
    user_id = session["user_id"]
    # user_obj = users_model.User.query.get(user_id)

    try:
        request_id = request.args["id"]
        request_id = int(decrypt_id(request_id))
    except Exception:
        request_id = 0

    db_groups_user_is_admin = users_groups_admins_model.UGARelationship.query.filter(
        users_groups_admins_model.UGARelationship.user_id == user_id).all()

    db_groups_user_has_conn = family_model.Family.query.filter(family_model.Family.group == request_id).all()

    db_group = db_groups_user_has_conn[request_id]

    db_families_in_group = family_model.Family.query.filter(family_model.Family.group == db_group.group).all()

    families = []
    for family in db_families_in_group:
        admin = False

        if family in db_groups_user_is_admin:
            admin = True

        families.append((family.name, encrypt_id(family.id), admin))

    is_admin = False
    if len(db_groups_user_is_admin) > 0:
        is_admin = True

    return render_template("editgroup.html", title="Muuda gruppi", families=families, admin=is_admin)


@app.route("/editgroup", methods=["POST"])
@login_required
def editgroup_with_action():
    # user_id = session["user_id"]
    # user_obj = users_model.User.query.get(user_id)
    return None


@app.route("/secretgraph")
@login_required
def secretgraph():
    check = check_if_admin()
    if check is not None:
        return check

    request_id = str(request.args["id"])

    return render_template("graph.html",
                           id=str(getpersonname(session["user_id"])),
                           image="s" + request_id + ".png",
                           title="Salajane graaf")


def check_if_admin():
    user_id = session["user_id"]
    requester = getpersonname(user_id)
    requester = requester.lower()

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


def save_graph(passed_graph, file_name, colored=False, id_to_id_mapping={}):
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
        name_id_lookup_dict = {}  # Let's create a admin-user_id mapping

        for name in id_to_id_mapping.keys():
            name_id_lookup_dict[getpersonid(name)] = name

        netx.draw_networkx_labels(passed_graph, pos, labels=name_id_lookup_dict, font_size=18)
    else:
        netx.draw_networkx_labels(passed_graph, pos, font_size=18)
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
        except Exception:
            db.session.rollback()
            row = shuffles_model.Shuffle.query.get(giver)
            row.getter = getter
            db.session.commit()

    digraph = netx.DiGraph(iterations=10000, scale=2)
    digraph.add_nodes_from(copy.deepcopy(families_shuf_ids).keys())

    for source, destination in copy.deepcopy(families_shuf_ids).items():
        digraph.add_edges_from([(source, destination)])

    save_graph(digraph, "./generated_graphs/graph_" + str(family_group) + ".png")
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
    #    check = check_if_admin()
    #    if check is not None:
    #        return check

    user_id = session["user_id"]
    family_id = getfamilyid(user_id)
    family_obj = family_model.Family.query.get(family_id)
    family_group = family_obj.group

    digraph = netx.DiGraph(iterations=100000000, scale=2)

    database_all_families_with_members = []
    database_families = family_model.Family.query.filter(family_model.Family.group == family_group).all()
    for db_family in database_families:
        database_family_members = users_families_admins_model.UFARelationship.query.filter(
            users_families_admins_model.UFARelationship.family_id == db_family.id).all()
        database_all_families_with_members.append(database_family_members)

    families_shuf_ids = {}
    for family in database_all_families_with_members:
        for member in family:
            families_shuf_ids[member.user_id] = gettargetid(member.user_id)

    digraph.add_nodes_from(families_shuf_ids.keys())

    for source, destination in copy.deepcopy(families_shuf_ids).items():
        digraph.add_edges_from([(source, destination)])

    save_graph(digraph, "./generated_graphs/graph_" + str(family_group) + ".png")

    return render_template("success.html", action="Genereeritud", link="./notes", title="Genereeritud")


@app.route("/rerendernamegraph")
@login_required
def rerendernamegraph():
    check = check_if_admin()
    if check is not None:
        return check

    digraph = netx.DiGraph(iterations=100000000, scale=2)  # This is probably a horrible idea with more nodes

    user_id = session["user_id"]
    family_id = getfamilyid(user_id)
    family_obj = family_model.Family.query.get(family_id)
    family_group = family_obj.group

    database_all_families_with_members = []
    database_families = family_model.Family.query.filter(family_model.Family.group == family_group).all()
    for db_family in database_families:
        database_family_members = users_families_admins_model.UFARelationship.query.filter(
            users_families_admins_model.UFARelationship.family_id == db_family.id).all()
        database_all_families_with_members.append(database_family_members)

    families_shuf_ids = {}
    for family in database_all_families_with_members:
        for member in family:
            families_shuf_ids[member.user_id] = gettargetid(member.user_id)

    for shuffled_ids_id in copy.deepcopy(families_shuf_ids).keys():
        digraph.add_node(shuffled_ids_id)

    for source, destination in copy.deepcopy(families_shuf_ids).items():
        digraph.add_edges_from([(source, destination)])

    save_graph(digraph, "./static/secretgraph.png", colored=True, id_to_id_mapping=families_shuf_ids)

    return render_template("success.html", action="Genereeritud", link="./graph")


@app.route("/giftingto", methods=["POST"])
@login_required
def updatenotestatus():
    user_id = session["user_id"]
    username = getpersonname(user_id)
    currentnotes = []
    notes_purchased = []

    try:
        request_id = request.form["id"]
        request_id = int(decrypt_id(request_id))
        print(user_id, " is trying to mark a note bought", request_id)
    except Exception as e:
        print("Failed decrypting", e)
        return render_template("error.html", message="Viga lingis", title="Error")

    try:
        print("Opening file", user_id)
        #        with open("./notes/" + useridno, "r") as file:
        #            currentnotes = json.load(file)
        db_notes = notes_model.Notes.query.get(request_id)
        if db_notes is not None:  # Don't want to display None
            currentnotes = db_notes.notes
            notes_purchased = db_notes.notes_purchased
    except Exception as e:
        print("Failed opening", e)
        return render_template("error.html", message="Ei saanud staatusemuudatusega hakkama", title="Error", back=True)

    try:
        try:
            boolean = request.form["checkbox"]
        except Exception as e:
            print("Checkbox not found:", e)
            boolean = "off"

        if boolean == "on":
            notes_purchased[int(request.form["index"])] = True
        elif boolean == "off":
            notes_purchased[int(request.form["index"])] = False
        else:
            raise Exception
    except Exception as e:
        print("Failed toggling:", e)
        return render_template("error.html", message="Ei saanud staatusemuudatusega hakkama", title="Error", back=True)

    #    with open("./notes/" + useridno, "w") as file:
    #        file.write(json.dumps(currentnotes))
    db_entry_notes = notes_model.Notes(
        user_id=request_id,
        notes=currentnotes,
        notes_purchased=notes_purchased
    )

    try:
        db.session.add(db_entry_notes)
        db.session.commit()
    except Exception:
        db.session.rollback()
        row = notes_model.Notes.query.get(request_id)
        row.notes = currentnotes
        row.notes_purchased = notes_purchased
        db.session.commit()

    print(username, " updated note with ID", request_id, "made by", user_id)
    return redirect("/giftingto?id=" + request.form["id"] + "&back=-2", code=303)


@app.route("/giftingto")
@login_required
def giftingto():
    check = check_if_admin()
    user_id = session["user_id"]
    username = getpersonname(user_id)
    invalid_notes = False
    try:
        back_count = request.args["back"]
    except Exception:
        back_count = -1

    try:
        request_id = request.args["id"]
        request_id = int(decrypt_id(request_id))
    except Exception as e:
        print("Failed decrypting:", e)
        request_id = gettargetid(user_id)

    try:  # Yeah, only valid IDs please
        if request_id == -1:
            return render_template("error.html", message="Loosimist ei ole veel administraatori poolt tehtud",
                                   title="Error")
        elif request_id < 0:
            raise Exception()
        elif request_id == int(user_id):
            return render_template("error.html", message="Sellele nimekirjale on ligipääs keelatud", title="Keelatud")
    except Exception:
        return render_template("error.html", message="Pls no hax " + username + "!!", title="Error")

    if check is not None:  # Let's not let everyone read everyone's lists
        if request_id != gettargetid(user_id):
            family_id = getfamilyid(user_id)
            family_obj = family_model.Family.query.get(family_id)
            family_group = family_obj.group

            database_all_families_with_members = []
            database_families = family_model.Family.query.filter(family_model.Family.group == family_group).all()
            for db_family in database_families:
                database_family_members = users_families_admins_model.UFARelationship.query.filter(
                    users_families_admins_model.UFARelationship.family_id == db_family.id).all()
                database_all_families_with_members.append(database_family_members)

            found = False
            for family in database_all_families_with_members:
                for member in family:
                    if member.user_id == request_id:
                        found = True

            if not found:
                return check

    currentnotes = ["Praegu on siin ainult veel tühjus"]
    boughtnotes = [False]

    try:
        print(user_id, "is opening file:", request_id)
        row = notes_model.Notes.query.get(request_id)
        currentnotes = row.notes
        boughtnotes = row.notes_purchased
    except Exception as e:
        invalid_notes = True
        print("Error displaying notes, there might be none:", e)

    # try:  # Not the prettiest, but tries to display names in the correct form
    #    return render_template("show_notes.html", notes=currentnotes, target=names_proper[username])
    # except Exception:

    passednotes = []
    for note, bought in list(itertools.zip_longest(currentnotes, boughtnotes, fillvalue=False)):
        passednotes.append((note, bought))

    return render_template("show_notes.html",
                           notes=passednotes,
                           target=getnameingenitive(getpersonname(request_id)),
                           id=encrypt_id(request_id),
                           title="Kingisoovid",
                           invalid=invalid_notes,
                           back=True,
                           back_count=back_count)


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
