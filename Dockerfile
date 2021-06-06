FROM ubuntu:focal

#Change 'VERSION','FOLDER_NUMBER' and 'DOWNLOAD_URL' variables for new versions
ENV VERSION=1.4.2.3

ENV FOLDER_NUMBER=1423

ENV DOWNLOAD_URL=https://terraria.org/system/dedicated_servers/archives/000/000/046/original/terraria-server-1423.zip

ENV SERVER_NAME=terraria-server

ENV port=7777

ENV maxplayers=16

ENV password=''

ENV secure=1

ENV language=en/US

ENV worldpath=/root/.local/share/Terraria/Worlds/

RUN apt update && apt install -y wget unzip gettext

RUN mkdir -p ${SERVER_NAME} /root/.local/share/Terraria/Worlds/ \
    && wget -O terraria-server.zip ${DOWNLOAD_URL} \
    && unzip terraria-server.zip -d ${SERVER_NAME} && rm terraria-server.zip && rm -Rf ${SERVER_NAME}/${FOLDER_NUMBER}/Windows ${SERVER_NAME}/${FOLDER_NUMBER}/Mac \
    && chmod +x ${SERVER_NAME}/${FOLDER_NUMBER}/Linux/TerrariaServer.bin.x86_64* \
    && cd ${SERVER_NAME}/${FOLDER_NUMBER}/Linux/ \
    && touch server-config.conf \
    && echo 'world=${world}' >> server-config.conf \
    && echo 'autocreate=${autocreate}' >> server-config.conf \
    && echo 'seed=${seed}' >> server-config.conf \
    && echo 'worldname=${worldname}' >> server-config.conf \
    && echo 'difficulty=${difficulty}' >> server-config.conf \
    && echo 'maxplayers=${maxplayers}' >> server-config.conf \
    && echo 'port=${port}' >> server-config.conf \
    && echo 'password=${password}' >> server-config.conf \
    && echo 'motd=${motd}' >> server-config.conf \
    && echo 'worldpath=${worldpath}' >> server-config.conf \
    && echo 'banlist=${banlist}' >> server-config.conf \
    && echo 'secure=${secure}' >> server-config.conf \
    && echo 'language=${language}' >> server-config.conf \
    && echo 'upnp=${upnp}' >> server-config.conf \
    && echo 'npcstream=${npcstream}' >> server-config.conf \
    && echo 'priority=${priority}' >> server-config.conf \
    && touch init.sh \
    && chmod +x init.sh \
    && echo '#!/bin/sh' >> init.sh \
    && echo 'envsubst < server-config.conf | tee server-config.conf' >> init.sh \
    && echo './TerrariaServer.bin.x86_64 -config server-config.conf' >> init.sh

VOLUME ["/root/.local/share/Terraria/Worlds/"]

WORKDIR ${SERVER_NAME}/${FOLDER_NUMBER}/Linux

CMD ["sh", "-c", "./init.sh"]

