# coding=utf-8
# Copyright: Taavi Eomäe 2017-2020
# SPDX-License-Identifier: AGPL-3.0-only
"""
Utility functions that aren't super specific to Loosindus
"""
import re

import pyximport
from flask import session

pyximport.install()

from functools import lru_cache
from datetime import datetime
from sys import setrecursionlimit
from base64 import urlsafe_b64decode
from binascii import Error as BinasciiError
from hashlib import sha3_512
from random import Random
from logging import getLogger

from config import Config

getLogger().setLevel(Config.LOGLEVEL)
logger = getLogger()

shuffler = Random(Config.SHUFFLE_SEED)
christmasy_emojis = ["🎄", "🎅", "🤶", "🦌", "🍪", "🌟", "❄️", "☃️", "⛄", "🎁", "🎶", "🕯️", "🔥", "🥶", "🧣", "🧥",
                     "🌲", "🌁", "🌬️", "🎿", "🏔️", "🌨️", "🏂", "⛷️"]
christmasy_emojis_len = len(christmasy_emojis)
shuffler.shuffle(christmasy_emojis)  # Shuffle them based on each instance


@lru_cache(maxsize=128)
def get_christmasy_emoji(user_id: int) -> str:
    """
    Returns a christmasy emoji based on user ID
    """
    if user_id is not None:
        emoji = christmasy_emojis[user_id % christmasy_emojis_len]
    else:
        emoji = ""
    return emoji


estonian_id_regex = re.compile("([3-6][0-9]{10})")


@lru_cache(maxsize=128)
def get_id_code(dn: str):
    """
    Parses out ID code from DN
    """
    result = estonian_id_regex.search(dn)
    if not result:
        raise Exception
    else:
        return result.group(0)


@lru_cache(maxsize=2)  # Keep last hash in memory
def get_sha3_512_hash(input_string: str) -> str:
    """
    Returns the SHA3-512 hash of the input string
    """
    return sha3_512(input_string.encode("utf-8")).hexdigest()


def auto_pad_urlsafe_b64(input_base64: str) -> str:
    """
    Tries to guess if people forgot to copy the entire string
    """
    for i in range(5):  # Let's hope that's all the padding needed
        try:
            urlsafe_b64decode(input_base64 + "=" * i)
            return input_base64 + "=" * i
        except BinasciiError:
            pass  # This padding didn't work
    raise Exception("Beyond messed up, maybe it's a not base64?")


def get_timestamp() -> str:
    """
    @return: Returns the current timestamp
    """
    return str(datetime.isoformat(datetime.now()))


def get_user_id() -> int:
    """
    @return: Returns the user ID from session as int
    """
    return int(session["user_id"])


def set_recursion_limit() -> None:
    """
    Sets the recustion limit required by shuffling
    """
    setrecursionlimit(2000)
