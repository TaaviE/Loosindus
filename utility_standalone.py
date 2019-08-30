# coding=utf-8
# Copyright: Taavi Eomäe 2017-2019
# SPDX-License-Identifier: AGPL-3.0-only

# Cython
import pyximport

pyximport.install()

from functools import lru_cache
import datetime
import sys
from base64 import urlsafe_b64decode, urlsafe_b64encode, b64decode, b64encode
from json import dumps, loads
import binascii
from Cryptodome.Cipher.AES import new, MODE_GCM
from hashlib import sha3_512

from config import Config
from logging import getLogger

getLogger().setLevel(Config.LOGLEVEL)
logger = getLogger()


@lru_cache(maxsize=64)
def decrypt_id(encrypted_user_id: str) -> str:
    base64_raw_data = urlsafe_b64decode(encrypted_user_id).decode()
    data = loads(base64_raw_data)
    ciphertext = b64decode(data[0])
    nonce = b64decode(data[1])
    tag = b64decode(data[2])
    cipher = new(Config.AES_KEY, MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext).decode()

    try:
        cipher.verify(tag)
        logger.info("The message is authentic: {}".format(plaintext))
    except ValueError:
        logger.info("Key incorrect or message corrupted!")

    return plaintext


# Replayable, but we don't care anything other than just hiding the data
@lru_cache(maxsize=128)
def encrypt_id(user_id: int) -> str:
    cipher = new(Config.AES_KEY, MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(bytes(str(user_id), encoding="utf8"))
    nonce = b64encode(cipher.nonce).decode()
    ciphertext = b64encode(ciphertext).decode()
    tag = b64encode(tag).decode()
    json_package = dumps([ciphertext, nonce, tag])
    packed = urlsafe_b64encode(bytes(json_package, "utf8")).decode()
    return packed


christmasy_emojis = ["🎄", "🎅", "🤶", "🦌", "🍪", "🌟", "❄️", "☃️", "⛄", "🎁", "🎶", "🕯️", "🔥", "🥶", "🧣", "🧥",
                     "🌲", "🌁", "🌬️", "🎿", "🏔️", "🌨️", "🏂", "⛷️"]


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
