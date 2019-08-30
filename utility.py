# coding=utf-8
# Copyright: Taavi Eomäe 2017-2019
# SPDX-License-Identifier: AGPL-3.0-only
# This file requires database being initialized

# Cython
import operator
from functools import lru_cache

import pyximport

pyximport.install()

from models.family_model import Family, FamilyGroup
from models.groups_model import Group, UserGroupAdmin
from models.names_model import Name
from models.shuffles_model import Shuffle
from models.users_model import User, UserFamilyAdmin
from models.wishlist_model import Wishlist
from datetime import datetime
from sqlalchemy import and_

from main import sentry


def get_person_marked(user_id: int) -> list:
    """
    Get all notes that have been somehow marked by an user
    :param user_id:
    :return:
    """
    passed_person_id = int(user_id)
    wishlist_marked = Wishlist.query.filter(Wishlist.purchased_by == passed_person_id).all()
    return wishlist_marked


def get_families_in_group(group_id: int) -> list:
    return Family.query.filter(
        Family.id.in_(  # TODO: .subquery() instead of .all()
            set([familygroup.family_id for familygroup in FamilyGroup.query.filter(
                FamilyGroup.group_id == group_id
            ).all()])
        )
    ).all()


def get_groups_family_is_in(family_id: int) -> list:
    familygroup_ids = [familygroup.group_id for familygroup in
                       FamilyGroup.query.filter(FamilyGroup.family_id == family_id).all()]
    return Group.query.filter(Group.id.in_(familygroup_ids)).all()


def if_user_is_group_admin(group_id: int, user_id: int) -> bool:
    try:
        return UserGroupAdmin.query.filter(and_(UserGroupAdmin.group_id == group_id,
                                                UserGroupAdmin.user_id == int(user_id)
                                                )).one().admin
    except Exception:
        return False


def get_default_family(passed_person_id: int) -> Family:
    passed_person_id = int(passed_person_id)  # Recast to avoid mistakes
    db_families_user_has_conn = UserFamilyAdmin.query.filter(UserFamilyAdmin.user_id == passed_person_id).all()
    return Family.query.filter(Family.id == sorted(db_families_user_has_conn,
                                                   key=operator.attrgetter("family_id"),
                                                   reverse=False)[0].family_id
                               ).one()


def get_families(passed_person_id: int) -> int:
    passed_person_id = int(passed_person_id)  # Recast to avoid mistakes
    return UserFamilyAdmin.query.filter(UserFamilyAdmin.user_id == passed_person_id).all()


@lru_cache(maxsize=64)
def get_person_name(passed_person_id: int) -> str:
    """
    Returns person's first name based on ID
    :param passed_person_id: Person's ID
    :return: Person's username
    """
    passed_person_id = int(passed_person_id)  # Recast to avoid mistakes
    return User.query.get(passed_person_id).first_name


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
    """
    Get the person's name in Estonian genitive case
    :param name: Name
    :return: Name in Estonian genitive case
    """
    try:
        return Name.query.get(name).genitive
    except Exception:
        return name


def get_person_language_code(user_id: int) -> str:
    """
    Fetches person's language preference from DB

    :param user_id: Person's ID
    :return: Two-letter language code
    """
    user_id = int(user_id)  # Recast to avoid mistakes
    user = User.query.filter(User.id == user_id).first()
    if user.language is None:
        return "ee"
    else:
        return user.language
