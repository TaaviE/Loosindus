# coding=utf-8
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
