import hashlib

from django.contrib.auth.hashers import BasePasswordHasher
from collections import OrderedDict
import base64
from django.utils.translation import gettext_noop as _
import hmac

from passlib.hash import pbkdf2_sha512

from SecretSanta.settings import PASSWORD_SALT


def mask_hash(hash, show=6, char="*"):
    """
    Return the given hash, with only the first ``show`` number shown. The
    rest are masked with ``char`` for security reasons.
    """
    masked = hash[:show]
    masked += char * len(hash[show:])
    return masked


def get_hmac(password):
    """Returns a Base64 encoded HMAC+SHA512 of the password signed with
    the salt specified by ``SECURITY_PASSWORD_SALT``.
    :param password: The password to sign
    """
    salt = PASSWORD_SALT
    sha512_hash = hmac.new(encode_string(salt), encode_string(password), hashlib.sha512)
    return base64.b64encode(sha512_hash.digest())


def encode_string(string):
    """Encodes a string to bytes, if it isn"t already.
    :param string: The string to encode"""

    if isinstance(string, str):
        string = string.encode("utf-8")
    return string


class PBKDF2SHA512PasswordHasher(BasePasswordHasher):
    """
    Secure password hashing using the PBKDF2 algorithm (recommended)

    Configured to use PBKDF2 + HMAC + SHA512.
    The result is a 64 byte binary string.  Iterations may be changed
    safely but you must rename the algorithm if you change SHA512.
    """
    algorithm = "pbkdf2-sha512"
    iterations = 25000
    digest = hashlib.sha512

    def encode(self, password, salt, iterations=None):
        return pbkdf2_sha512.hash(get_hmac(password).decode("ascii"))

    def verify(self, password, encoded):
        return pbkdf2_sha512.verify(get_hmac(password), encoded)

    def safe_summary(self, encoded):
        if encoded[0] is "$":
            encoded = encoded[1:]
        algorithm, iterations, salt, hash = encoded.split("$", 3)
        assert algorithm == self.algorithm
        return OrderedDict([
            (_("algorithm"), algorithm),
            (_("iterations"), iterations),
            (_("salt"), mask_hash(salt)),
            (_("hash"), mask_hash(hash)),
        ])

    def must_update(self, encoded):
        if encoded[0] is "$":
            encoded = encoded[1:]
        algorithm, iterations, salt, hash = encoded.split("$", 3)
        return int(iterations) != self.iterations

    def harden_runtime(self, password, encoded):
        if encoded[0] is "$":
            encoded = encoded[1:]
        algorithm, iterations, salt, hash = encoded.split("$", 3)
        extra_iterations = self.iterations - int(iterations)
        if extra_iterations > 0:
            self.encode(password, salt, extra_iterations)
