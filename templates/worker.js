self.addEventListener("install", function(event) {
  event.waitUntil(
    caches.open("default_cache").then(function(cache) {
      return cache.addAll(
        [
          "/static/roboto.min.css",
          "/static/material.min.css",
          "/static/normalize.min.css",
          "/static/normalize.min.js",
          "/static/custom.css",
        ]
      );
    })
  );
});