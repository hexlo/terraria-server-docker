#!/bin/bash

file=server-config.conf
touch ${file}
echo > ${file}

# user has set the world variable and the world exists. Loads world
if [[ ! -z "${world}" && -f "${world}" ]]; then
    echo "${file}: Loading world: ${world}"
    echo "world=${world}" >> ${file}

# user has set the world variable but it doesnt exists. Creates it. This will bypass the worldname variable.
elif [[ ! -z "${world}" && ! -f "${world}" ]]; then
    echo "${file}: World ${world} doesn't exists. Creating it using:"

    echo "worldname: $(basename "${world}")"
    echo "autocreate: ${autocreate}"
    echo "seed: ${seed}"
    echo "difficulty: ${difficulty}"

    echo "world=${world}" >> ${file}
    echo "autocreate=${autocreate}" >> ${file}
    echo "seed=${seed}" >> ${file}
    echo "worldname=$(basename "${world}")" >> ${file}
    echo "difficulty=${difficulty}" >> ${file}

# user has not set the world variable.
else
    echo "world=${worldpath}/${worldname}.wld" >> ${file}
    echo "autocreate=${autocreate}" >> ${file}
    echo "seed=${seed}" >> ${file}
    echo "worldname=${worldname}" >> ${file}
    echo "difficulty=${difficulty}" >> ${file}
fi

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