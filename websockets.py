# coding=utf-8
# Copyright: Taavi Eomäe 2020
# SPDX-License-Identifier: AGPL-3.0-only
"""
Contains websocket related code
"""
import eventlet
from flask import Flask
from flask_socketio import SocketIO

from config import Config

eventlet.monkey_patch()

app = Flask(__name__)
app.config.from_object(Config)

socketio = SocketIO(app, message_queue=Config.MESSAGE_QUEUE_URI)
