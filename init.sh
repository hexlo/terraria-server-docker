#!/bin/bash

touch server-config.conf
echo > server-config.conf

if [[ ! -z "${world}" ]]; then
    echo "world=${world}" >> server-config.conf
fi

echo "autocreate=${autocreate}" >> server-config.conf
echo "seed=${seed}" >> server-config.conf
echo "worldname=${worldname}" >> server-config.conf
echo "difficulty=${difficulty}" >> server-config.conf
echo "maxplayers=${maxplayers}" >> server-config.conf
echo "port=${port}" >> server-config.conf
echo "password=${password}" >> server-config.conf
echo "motd=${motd}" >> server-config.conf
echo "worldpath=${worldpath}" >> server-config.conf

if [[ -z "${banlist}" || "${banlist}" == "banlist.txt" ]]; then
    touch banlist.txt
fi
echo "banlist=${banlist}" >> server-config.conf

echo "secure=${secure}" >> server-config.conf
echo "language=${language}" >> server-config.conf
echo "upnp=${upnp}" >> server-config.conf
echo "npcstream=${npcstream}" >> server-config.conf
echo "priority=${priority}" >> server-config.conf;

echo "PWD:${PWD}"

ls -al

./TerrariaServer.bin.x86_64 -config server-config.conf
