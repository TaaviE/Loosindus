# coding=utf-8
# Copyright: Taavi Eomäe 2017-2019
# SPDX-License-Identifier: AGPL-3.0-only

# Cython
import pyximport

pyximport.install()

from functools import lru_cache
import datetime
import sys
from base64 import urlsafe_b64decode
import binascii
from hashlib import sha3_512

from config import Config
from logging import getLogger

getLogger().setLevel(Config.LOGLEVEL)
logger = getLogger()

from random import Random

shuffler = Random(Config.SHUFFLE_SEED)
christmasy_emojis = ["🎄", "🎅", "🤶", "🦌", "🍪", "🌟", "❄️", "☃️", "⛄", "🎁", "🎶", "🕯️", "🔥", "🥶", "🧣", "🧥",
                     "🌲", "🌁", "🌬️", "🎿", "🏔️", "🌨️", "🏂", "⛷️"]
shuffler.shuffle(christmasy_emojis)


@lru_cache(maxsize=128)
def get_christmasy_emoji(user_id: int) -> str:
    if user_id is not None:
        emoji = christmasy_emojis[int(user_id) % len(christmasy_emojis)]
    else:
        emoji = ""
    return emoji


@lru_cache(maxsize=2)  # Keep last hash in memory
def get_sha3_512_hash(input_dn: str) -> str:
    return sha3_512(input_dn.encode("utf-8")).hexdigest()


# Tries to guess if people forgot to copy the entire string
def auto_pad_urlsafe_b64(input_base64: str) -> str:
    for i in range(5):  # Let's hope that's all the padding needed
        try:
            urlsafe_b64decode(input_base64 + "=" * i)
            return input_base64 + "=" * i
        except binascii.Error:
            pass  # This padding didn't work
    raise Exception("Beyond messed up, maybe it's a not base64?")


def get_timestamp() -> str:
    return str(datetime.datetime.isoformat(datetime.datetime.now()))


def set_recursionlimit() -> None:
    sys.setrecursionlimit(2000)
