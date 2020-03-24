// Copyright: Taavi Eomäe 2017-2020
// SPDX-License-Identifier: AGPL-3.0-only

self.addEventListener("install", function (event) {
    event.waitUntil(
        caches.open("default_cache").then(function (cache) {
            return cache.addAll(
                [
                    "/static/roboto.min.css",
                    "/static/material/lite/material.min.css",
                    "/static/material/lite/material.min.js",
                    "/static/normalize.min.css",
                    "/static/favicon/favicon-no-bg-196x196.png",
                    "/static/custom.css",
                ]
            );
        })
    );
});