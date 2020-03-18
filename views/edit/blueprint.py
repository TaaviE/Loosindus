# coding=utf-8
"""
Initializes the blueprint so pages can register themselves
"""
from flask import Blueprint

edit_page = Blueprint("edit_page",
                      __name__,
                      url_prefix="/edit",
                      template_folder="templates")
