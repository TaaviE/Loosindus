# coding=utf-8
# Copyright: Taavi Eomäe 2020
# SPDX-License-Identifier: AGPL-3.0-only
"""
Contains all the views used in Loosindus
"""
from views.edit.blueprint import edit_page as edit
from views.login import login_page as login
from views.static import static_page as static
from views.test import test_page as test
from views.user_specific_static import user_specific as user_specific
from views.views import main_page as views
