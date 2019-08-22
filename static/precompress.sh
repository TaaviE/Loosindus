#!/bin/bash
# This script precompressess all resources for faster serving and
# to reduce load on the server
cd static # Just in case we already weren't in the folder

find . -type f -name "*.br" -not -path '*/\.*' -exec sh -c "rm '{}'" \;
find . -type f -name "*.gz" -not -path '*/\.*' -exec sh -c "rm '{}'" \;

find . -type f -name "*.css" -not -path '*/\.*' -exec sh -c "touch '{}' && brotli --quality=11 < {} > {}.br" \;
find . -type f -name "*.css" -not -path '*/\.*' -exec sh -c "touch '{}' && gzip -9 < {} > {}.gz" \;

find . -type f -name "*.woff2" -not -path '*/\.*' -exec sh -c "touch '{}' && brotli --quality=11 < {} > {}.br" \;
find . -type f -name "*.woff2" -not -path '*/\.*' -exec sh -c "touch '{}' && gzip -9 < {} > {}.gz" \;

find . -type f -name "*.png" -not -path '*/\.*' -exec sh -c "touch '{}' && brotli --quality=11 < {} > {}.br" \;
find . -type f -name "*.png" -not -path '*/\.*' -exec sh -c "touch '{}' && gzip -9 < {} > {}.gz" \;

find . -type f -name "*.svg" -not -path '*/\.*' -exec sh -c "touch '{}' && brotli --quality=11 < {} > {}.br" \;
find . -type f -name "*.svg" -not -path '*/\.*' -exec sh -c "touch '{}' && gzip -9 < {} > {}.gz" \;

find . -type f -name "*.js" -not -path '*/\.*' -exec sh -c "touch '{}' && brotli --quality=11 < {} > {}.br" \;
find . -type f -name "*.js" -not -path '*/\.*' -exec sh -c "touch '{}' && gzip -9 < {} > {}.gz" \;

find . -type f -name "*.map" -not -path '*/\.*' -exec sh -c "touch '{}' && brotli --quality=11 < {} > {}.br" \;
find . -type f -name "*.map" -not -path '*/\.*' -exec sh -c "touch '{}' && gzip -9 < {} > {}.gz" \;

find . -type f -name "*.xml" -not -path '*/\.*' -exec sh -c "touch '{}' && brotli --quality=11 < {} > {}.br" \;
find . -type f -name "*.xml" -not -path '*/\.*' -exec sh -c "touch '{}' && gzip -9 < {} > {}.gz" \;

find . -type f -name "*.txt" -not -path '*/\.*' -exec sh -c "touch '{}' && brotli --quality=11 < {} > {}.br" \;
find . -type f -name "*.txt" -not -path '*/\.*' -exec sh -c "touch '{}' && gzip -9 < {} > {}.gz" \;

brotli --quality=11 < manifest.json > manifest.json.br
gzip -9 < manifest.json> manifest.json.gz
