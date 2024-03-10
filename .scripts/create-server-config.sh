#!/bin/bash

file=server-config.conf
touch ${file}
echo > ${file}

if [[ ! -z "${world}" ]]; then
    echo "world=${world}" >> ${file}
fi

echo "autocreate=${autocreate}" >> ${file}
echo "seed=${seed}" >> ${file}
echo "worldname=${worldname}" >> ${file}
echo "difficulty=${difficulty}" >> ${file}
echo "maxplayers=${maxplayers}" >> ${file}
echo "port=${port}" >> ${file}
echo "password=${password}" >> ${file}
echo "motd=${motd}" >> ${file}
echo "worldpath=${worldpath}" >> ${file}

if [[ -z "${banlist}" || "${banlist}" == "banlist.txt" ]]; then
    touch banlist.txt
fi
echo "banlist=${banlist}" >> ${file}

echo "secure=${secure}" >> ${file}
echo "language=${language}" >> ${file}
echo "upnp=${upnp}" >> ${file}
echo "npcstream=${npcstream}" >> ${file}
echo "priority=${priority}" >> ${file};