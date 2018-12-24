import datetime
import sys
from base64 import urlsafe_b64decode, urlsafe_b64encode, b64decode, b64encode
from json import dumps, loads
from logging import info

from Cryptodome.Cipher.AES import new, MODE_GCM

from config import Config
from models.familiy_user_admin_model import UserFamilyAdmin
from models.names_model import Name
from models.shuffles_model import Shuffle
from models.users_model import User
from models.wishlist_model import Wishlist


def get_person_marked(user_id):
    passed_person_id = int(user_id)
    wishlist_marked = Wishlist.query.filter(Wishlist.purchased_by == passed_person_id).all()
    return wishlist_marked


def get_person_id(name):
    return User.query.filter(User.username == name).first().id


def get_family_id(passed_person_id):
    passed_person_id = int(passed_person_id)
    db_families_user_has_conn = UserFamilyAdmin.query.filter(UserFamilyAdmin.user_id == passed_person_id).all()

    db_family = db_families_user_has_conn[0]
    family_id = db_family.family_id
    return family_id


def get_person_name(passed_person_id):
    return User.query.get(passed_person_id).username


def get_target_id(passed_person_id):
    try:
        return Shuffle.query.get(passed_person_id).getter
    except Exception:
        return -1


def get_name_in_genitive(name):
    try:
        return Name.query.get(name).genitive
    except Exception:
        return name


def decrypt_id(encrypted_user_id):
    base64_raw_data = urlsafe_b64decode(encrypted_user_id).decode()
    data = loads(base64_raw_data)
    ciphertext = b64decode(data[0])
    nonce = b64decode(data[1])
    tag = b64decode(data[2])
    cipher = new(Config.AES_KEY, MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext).decode()

    try:
        cipher.verify(tag)
        info("The message is authentic: {}", plaintext)
    except ValueError:
        info("Key incorrect or message corrupted!")

    return plaintext


def encrypt_id(user_id):
    cipher = new(Config.AES_KEY, MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(bytes(str(user_id), encoding="utf8"))
    nonce = b64encode(cipher.nonce).decode()
    ciphertext = b64encode(ciphertext).decode()
    tag = b64encode(tag).decode()
    json_package = dumps([ciphertext, nonce, tag])
    packed = urlsafe_b64encode(bytes(json_package, "utf8")).decode()
    return packed


def get_timestamp():
    return str(datetime.datetime.isoformat(datetime.datetime.now()))


def get_person_language_code(user_id):
    user = User.query.filter(User.id == int(user_id)).first()
    if user.language is None:
        return "ee"
    else:
        return user.language


def set_recursionlimit():
    sys.setrecursionlimit(2000)
