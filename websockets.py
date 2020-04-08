# coding=utf-8
# Copyright: Taavi Eomäe 2020
# SPDX-License-Identifier: AGPL-3.0-only
"""
Contains websocket related code
"""
from eventlet import monkey_patch
from flask import Flask
from flask_login import current_user
from flask_socketio import SocketIO, emit

from config import Config
from socketio_helper import authenticated_only

# Do eventlet monkey patching
monkey_patch()

app = Flask(__name__)
app.config.from_object(Config)

socketio = SocketIO(app, message_queue=Config.MESSAGE_QUEUE_URI)
