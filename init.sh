#!/bin/bash

touch server-config.conf
touch banlist.txt
echo 'world=${world}' > server-config.conf
echo 'autocreate=${autocreate}' >> server-config.conf
echo 'seed=${seed}' >> server-config.conf
echo 'worldname=${worldname}' >> server-config.conf
echo 'difficulty=${difficulty}' >> server-config.conf
echo 'maxplayers=${maxplayers}' >> server-config.conf
echo 'port=${port}' >> server-config.conf
echo 'password=${password}' >> server-config.conf
echo 'motd=${motd}' >> server-config.conf
echo 'worldpath=${worldpath}' >> server-config.conf
echo 'banlist=${banlist}' >> server-config.conf
echo 'secure=${secure}' >> server-config.conf
echo 'language=${language}' >> server-config.conf
echo 'upnp=${upnp}' >> server-config.conf
echo 'npcstream=${npcstream}' >> server-config.conf
echo 'priority=${priority}' >> server-config.conf

cat server-config.conf | envsubst | tee server-config.conf;

./TerrariaServer.bin.x86_64 -config server-config.conf