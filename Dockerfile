FROM ubuntu:focal

RUN apt update && apt install -y wget unzip gettext

#Change 'VERSION','FOLDER_NUMBER' and 'DOWNLOAD_URL' variables for new versions
ENV VERSION=1.4.2.3

ENV SERVER_NAME=terraria-server

ENV FOLDER_NUMBER=1423

ENV DOWNLOAD_URL=https://terraria.org/api/download/pc-dedicated-server/terraria-server-1423.zip

ENV SELF_HOSTED_DOWNLOAD_URL=https://raw.githubusercontent.com/Iceoid/FileShare/main/terraria-server-1423.tar

ENV DOCS_URL=https://terraria.fandom.com/wiki/Server

ENV world=/root/.local/share/Terraria/Worlds/newworld.wld

ENV autocreate=2

ENV seed=celebrationmk10

ENV worldname=TerrariaWorld

ENV difficulty=2

ENV maxplayers=16

ENV port=7777

ENV password=''

ENV motd="Welcome!"

ENV worldpath=/root/.local/share/Terraria/Worlds/

ENV banlist=banlist.txt

ENV secure=1

ENV language=en/US

ENV upnp=1

ENV npcstream=5

ENV priority=1

COPY ./init.sh .

RUN mkdir -p ${SERVER_NAME} /root/.local/share/Terraria/Worlds/ \
    && wget -O terraria-server.zip ${DOWNLOAD_URL} \
    && unzip terraria-server.zip -d ${SERVER_NAME} && rm terraria-server.zip && rm -Rf ${SERVER_NAME}/${FOLDER_NUMBER}/Windows ${SERVER_NAME}/${FOLDER_NUMBER}/Mac \
    && cd ${SERVER_NAME}/${FOLDER_NUMBER}/Linux \
    # && wget -O terraria-server.zip ${SELF_HOSTED_DOWNLOAD_URL} \
    # && tar -xf terraria-server.zip -C ${SERVER_NAME} --strip-components=1\
    # && cd ${SERVER_NAME}/${FOLDER_NUMBER}/Linux \
    && chmod +x TerrariaServer.bin.x86_64* 

WORKDIR ${SERVER_NAME}/${FOLDER_NUMBER}/Linux

COPY ./init.sh .

RUN chmod +x init.sh

VOLUME ["/root/.local/share/Terraria/Worlds/"]

ENTRYPOINT [ "./init.sh" ]

