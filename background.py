# coding=utf-8
# Copyright: Taavi Eomäe 2017-2019
# SPDX-License-Identifier: AGPL-3.0-only

# Background tasks

from main import mail
from models.wishlist_model import NoteState
from utility import *
from utility_standalone import *

getLogger().setLevel(Config.LOGLEVEL)
logger = getLogger()


def remind_to_add(rate_limit=True):
    logger.info("Started sending adding reminders")
    now = datetime.datetime.now()
    try:
        with open("remind_to_add", "r+") as timer_file:
            lastexec = timer_file.read()
            lastexec = datetime.datetime(*map(int, reversed(lastexec.split("/"))))

            if now - lastexec < datetime.timedelta(days=30):
                logger.info(" Adding reminders were rate-limited")
                if rate_limit:
                    return
            else:
                timer_file.seek(0)
                timer_file.write(get_timestamp())
    except Exception:
        logger.info(" Adding reminders rate-limit file was not found")
        with open("remind_to_add", "w") as timer_file:
            timer_file.write(get_timestamp())

    for user in User.query:
        if user.last_activity_at:
            if now - datetime.datetime(*map(int, user.last_activity_at.split("/"))) < datetime.timedelta(days=15):
                continue

        email_to_send = "Tere,\n"
        email_to_send += "Tegemist on väikese meeldetuletusega enda nimekirja koostamisele hakata mõtlema\n"
        email_to_send += "\n"
        email_to_send += "Kirja saavad kõik kasutajad kes ei ole vähemalt 15 päeva sisse loginud\n"
        email_to_send += "Jõulurakendus 🎄"

        mail.send_message(subject="Meeldetuletus kinkide kohta",
                          body=email_to_send,
                          recipients=[user.email])

    logger.info("Finished sending adding reminders")


def remind_to_buy(rate_limit=True):
    logger.info("Started sending purchase reminders")
    now = datetime.datetime.now()
    try:
        with open("remind_to_buy", "r+") as timer_file:
            lastexec = timer_file.read()
            lastexec = datetime.datetime(*map(int, reversed(lastexec.split("/"))))

            if now - lastexec < datetime.timedelta(days=15):
                logger.info("Buying reminders were rate-limited")
                if rate_limit:
                    return
            else:
                timer_file.seek(0)
                timer_file.write(get_timestamp())
    except Exception:
        logger.info(" Reminder to buy timer file was not found")
        with open("remind_to_buy", "w") as timer_file:
            timer_file.write(get_timestamp())

    for user in User.query:
        marked_entries = get_person_marked(user.id)
        items_to_purchase = []
        for entry in marked_entries:
            if entry.status == NoteState.PLANNING_TO_PURCHASE.value["id"] or \
                    entry.status == NoteState.MODIFIED.value["id"]:
                items_to_purchase.append((entry.item, get_person_name(entry.user_id)))

        if len(items_to_purchase) == 0:
            continue

        email_to_send = "Tere,\n"
        email_to_send += "Olete märkinud, et plaanite osta allpool loetletud kingitused kuid ei ole vastavate kingituste staatust uuendanud vähemalt viisteist päeva eelnevast meeldetuletusest:\n"
        email_to_send += "\n"
        email_to_send += "Kingitus | Kellele\n"
        for item in items_to_purchase:
            email_to_send += "\""
            email_to_send += item[0]
            email_to_send += "\" - "
            email_to_send += item[1]
            email_to_send += "\n"
        email_to_send += "\n"
        email_to_send += "Palun mitte unustada\n"
        email_to_send += "Jõulurakendus🎄"

        mail.send_message(subject="Meeldetuletus kinkide kohta",
                          body=email_to_send,
                          recipients=[user.email])

    logger.info("Finished sending purchase reminders")


def remind_about_change(rate_limit=True):
    logger.info(" Started sending change reminders")
    now = datetime.datetime.now()
    try:
        with open("remind_about_change", "r+") as timer_file:
            lastexec = timer_file.read()
            lastexec = datetime.datetime(*map(int, reversed(lastexec.split("/"))))

            if now - lastexec < datetime.timedelta(hours=6):
                logger.info(" Changing reminders were rate-limited")
                if rate_limit:
                    return
            else:
                timer_file.seek(0)
                timer_file.write(get_timestamp())
    except Exception:
        logger.info(" Change reminder timer file was not found")
        with open("remind_about_change", "w") as timer_file:
            timer_file.write(get_timestamp())

    for user in User.query:
        marked_entries = get_person_marked(user.id)
        items_to_purchase = []
        for entry in marked_entries:
            if entry.status == NoteState.MODIFIED.value["id"]:
                items_to_purchase.append((entry.item, get_person_name(entry.user_id)))

        if len(items_to_purchase) == 0:
            continue

        email_to_send = "Tere,\n"
        email_to_send += "Viimase päeva jooksul on muudetud allpool loetletud soove, on oluline, et otsustaksite kas soovite ikka kinki osta või vabastate selle teistele:\n"
        email_to_send += "\n"
        email_to_send += "Kingitus | Kellele\n"
        for item in items_to_purchase:
            email_to_send += "\""
            email_to_send += item[0]
            email_to_send += "\" - "
            email_to_send += item[1]
            email_to_send += "\n"
        email_to_send += "\n"
        email_to_send += "Palume päeva jooksul enda otsus uuesti süsteemi sisestada\n"
        email_to_send += "Jõulurakendus 🎄"

        mail.send_message(subject="Meeldetuletus kinkide kohta",
                          body=email_to_send,
                          recipients=[user.email])

    logger.info("Finished sending change reminders")
