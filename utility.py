# coding=utf-8
# author=Taavi Eomäe
# This file requires database being initialized

# Cython
import warnings
from functools import lru_cache

import pyximport

pyximport.install()
from datetime import datetime

from sqlalchemy import and_

from main import sentry

from models.names_model import Name
from models.shuffles_model import Shuffle
from models.users_families_admins import UserFamilyAdmin
from models.users_model import User
from models.wishlist_model import Wishlist


def get_person_marked(user_id: int) -> list:
    passed_person_id = int(user_id)  # Recast to avoid mistakes
    wishlist_marked = Wishlist.query.filter(Wishlist.purchased_by == passed_person_id).all()
    return wishlist_marked


def get_person_id(name: str) -> int:
    return User.query.filter(User.username == name).first().id


def get_family_id(passed_person_id: int) -> int:
    warnings.warn("The 'get_family_id' method is deprecated, use 'get_families' instead", DeprecationWarning, 2)
    passed_person_id = int(passed_person_id)  # Recast to avoid mistakes
    db_families_user_has_conn = UserFamilyAdmin.query.filter(UserFamilyAdmin.user_id == passed_person_id).all()

    db_family = db_families_user_has_conn[0]
    family_id = db_family.family_id
    return family_id


def get_families(passed_person_id: int) -> int:
    passed_person_id = int(passed_person_id)  # Recast to avoid mistakes
    return UserFamilyAdmin.query.filter(UserFamilyAdmin.user_id == passed_person_id).all()


def get_person_name(passed_person_id: int) -> str:
    return User.query.get(passed_person_id).username


def get_target_id(passed_person_id: int) -> int:
    warnings.warn("The 'get_target_id' method is deprecated, use 'get_target_id_with_group' instead",
                  DeprecationWarning, 2)
    try:
        passed_person_id = int(passed_person_id)  # Recast to avoid mistakes
        return Shuffle.query.filter(and_(Shuffle.giver == passed_person_id,
                                         Shuffle.year == datetime.now().year)).first().getter
    except Exception:
        sentry.captureException()
        return -1


def get_target_id_with_group(passed_person_id: int, passed_group_id: int) -> int:
    try:
        passed_person_id = int(passed_person_id)  # Recast to avoid mistakes
        passed_group_id = int(passed_group_id)  # Recast to avoid mistakes
        return Shuffle.query.filter(and_(Shuffle.giver == passed_person_id,
                                         Shuffle.year == datetime.now().year,
                                         Shuffle.group == passed_group_id)).one().getter
    except Exception:
        sentry.captureException()
        return -1


@lru_cache(maxsize=64)
def get_name_in_genitive(name: str) -> str:
    try:
        return Name.query.get(name).genitive
    except Exception:
        return name


def get_person_language_code(user_id: int) -> str:
    user_id = int(user_id)  # Recast to avoid mistakes
    user = User.query.filter(User.id == user_id).first()
    if user.language is None:
        return "ee"
    else:
        return user.language
