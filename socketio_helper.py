# coding=utf-8
# Copyright: Flask-SocketIO contributors 2020
# SPDX-License-Identifier: MIT
"""
Functions from Flask-SocketIO example
"""
from typing import Any, Callable

from flask_login import current_user
from flask_socketio import disconnect


def authenticated_only(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """
    @param func: function to decorate
    @return: wrapped function
    """

    def wrapped(*args, **kwargs):
        """
        @param args: that are meant to be passed to the route
        @param kwargs: that are meant to be passed to the route
        """
        if not current_user.is_authenticated:
            disconnect()
        else:
            return func(*args, **kwargs)

    return wrapped
