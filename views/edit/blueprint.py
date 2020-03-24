# coding=utf-8
# Copyright: Taavi Eomäe 2018-2020
# SPDX-License-Identifier: AGPL-3.0-only
"""
Initializes the blueprint so pages can register themselves
"""
from flask import Blueprint

edit_page = Blueprint("edit_page",
                      __name__,
                      url_prefix="/edit",
                      template_folder="templates")
