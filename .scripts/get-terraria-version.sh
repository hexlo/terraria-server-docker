#!/bin/sh
curl -v -L --silent \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36" \
  https://terraria.wiki.gg/wiki/Server#Downloads 2>&1 \
  | grep -o 'https://terraria.org/api/download/pc-dedicated-server/[^"]*' \
  | sed 's#.*/terraria-server-##' | sed 's/\.zip//' | tail -1
