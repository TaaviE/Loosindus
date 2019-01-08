# coding=utf-8
# author=Taavi Eomäe
# This file requires database being initialized
from datetime import datetime

from sqlalchemy import and_

from main import sentry
from models.names_model import Name
from models.shuffles_model import Shuffle
from models.users_families_admins import UserFamilyAdmin
from models.users_model import User
from models.wishlist_model import Wishlist


def get_person_marked(user_id: int) -> list:
    passed_person_id = int(user_id)
    wishlist_marked = Wishlist.query.filter(Wishlist.purchased_by == passed_person_id).all()
    return wishlist_marked


def get_person_id(name: str) -> int:
    return User.query.filter(User.username == name).first().id


def get_family_id(passed_person_id: int) -> int:
    passed_person_id = int(passed_person_id)
    db_families_user_has_conn = UserFamilyAdmin.query.filter(UserFamilyAdmin.user_id == passed_person_id).all()

    db_family = db_families_user_has_conn[0]  # TODO: User might have more than one family
    family_id = db_family.family_id
    return family_id


def get_person_name(passed_person_id: int) -> str:
    return User.query.get(passed_person_id).username


def get_target_id(passed_person_id: int) -> int:
    try:
        return Shuffle.query.filter(and_(Shuffle.giver == passed_person_id,
                                         Shuffle.year == datetime.now().year)).one().getter
    except Exception:
        sentry.captureException()
        return -1


def get_name_in_genitive(name: str) -> str:
    try:
        return Name.query.get(name).genitive
    except Exception:
        return name


def get_person_language_code(user_id: int) -> str:
    user = User.query.filter(User.id == int(user_id)).first()
    if user.language is None:
        return "ee"
    else:
        return user.language
