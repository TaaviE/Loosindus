#!/usr/bin/env bash
# This script precompressess all resources for faster serving and
# to reduce load on the server
cd static # Just in case we already weren't in the folder

find . -type f -name "*.br" -exec sh -c "rm {}" \;
find . -type f -name "*.gz" -exec sh -c "rm {}" \;

find . -type f -name "*.css" -exec sh -c "touch {} && brotli --quality=11 < {} > {}.br" \;
find . -type f -name "*.css" -exec sh -c "touch {} && gzip -9 < {} > {}.gz" \;

find . -type f -name "*.woff2" -exec sh -c "touch {} && brotli --quality=11 < {} > {}.br" \;
find . -type f -name "*.woff2" -exec sh -c "touch {} && gzip -9 < {} > {}.gz" \;

find . -type f -name "*.png" -exec sh -c "touch {} && brotli --quality=11 < {} > {}.br" \;
find . -type f -name "*.png" -exec sh -c "touch {} && gzip -9 < {} > {}.gz" \;

find . -type f -name "*.svg" -exec sh -c "touch {} && brotli --quality=11 < {} > {}.br" \;
find . -type f -name "*.svg" -exec sh -c "touch {} && gzip -9 < {} > {}.gz" \;

find . -type f -name "*.js" -exec sh -c "touch {} && brotli --quality=11 < {} > {}.br" \;
find . -type f -name "*.js" -exec sh -c "touch {} && gzip -9 < {} > {}.gz" \;

brotli --quality=11 < sitemap.xml > sitemap.xml.br
gzip -9 < sitemap.xml > sitemap.xml.gz

brotli --quality=11 < robots.txt > sitemap.xml.br
gzip -9 < robots.txt > sitemap.xml.gz

brotli --quality=11 < manifest.json > sitemap.xml.br
gzip -9 < manifest.json> sitemap.xml.gz
