# coding=utf-8
# Copyright: Taavi Eomäe 2017-2020
# SPDX-License-Identifier: AGPL-3.0-only
"""
Contains functions that abstracts a few queries
This file requires database being initialized
"""
# Cython
from functools import lru_cache

import pyximport

from utility_standalone import get_user_id

pyximport.install()

from models.family_model import Family, FamilyGroup
from models.names_model import Name
from models.shuffles_model import Shuffle
from models.users_model import User
from datetime import datetime
from sqlalchemy import and_

import sentry_sdk


def get_user() -> User:
    """
    @return: Returns the user from session as User
    """
    return User.query.get(get_user_id())


def get_person(user_id: int) -> User:
    """
    :return: Just the user based on the ID
    """
    return User.query.get(user_id)


def get_families_in_group(group_id: int) -> list:
    return Family.query.filter(
        Family.id.in_(  # TODO: .subquery() instead of .all()
            set([familygroup.family_id for familygroup in FamilyGroup.query.filter(
                FamilyGroup.group_id == group_id
            ).all()])
        )
    ).all()


def get_target_id_with_group(passed_person_id: int, passed_group_id: int) -> int:
    try:
        passed_person_id = int(passed_person_id)  # Recast to avoid mistakes
        passed_group_id = int(passed_group_id)  # Recast to avoid mistakes
        return Shuffle.query.filter(and_(Shuffle.giver == passed_person_id,
                                         Shuffle.year == datetime.now().year,
                                         Shuffle.group == passed_group_id)).one().getter
    except Exception as e:
        sentry_sdk.capture_exception(e)
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
