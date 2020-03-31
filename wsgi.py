# coding=utf-8
# Copyright: Taavi Eomäe 2018-2020
# SPDX-License-Identifier: AGPL-3.0-only
"""
Helps with starting a wsgi worker
"""
import logging
from logging import basicConfig, getLogger

from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from main import app

getLogger().setLevel(logging.DEBUG)
logger = getLogger()
logger.debug("Started with proxyfix")

# Assume one proxy using provided NGINX config
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    if Config.DEBUG:
        logger.warning("Starting in debug!")
        app.run(debug=True, use_evalex=True, host="0.0.0.0", port=5000)
    else:
        logger.info("Starting in production")
        app.run(debug=True, use_evalex=False, host="127.0.0.1")
