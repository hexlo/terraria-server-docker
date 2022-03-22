FROM ubuntu:focal

ARG VERSION=latest

ENV VER=$VERSION

ENV LATEST_VERSION=""

ENV autocreate=2

ENV seed=

ENV worldname=TerrariaWorld

ENV difficulty=0

ENV maxplayers=16

ENV port=7777

ENV password=''

ENV motd="Welcome!"

ENV worldpath=/root/.local/share/Terraria/Worlds/

ENV banlist=banlist.txt

ENV secure=1

ENV language=en/US

ENV upnp=1

ENV npcstream=1

ENV priority=1

RUN apt update && apt install -y wget unzip gettext curl

ARG CACHE_DATE=''

RUN mkdir -p /terraria-server/info /root/.local/share/Terraria/Worlds/ \
    && if [ "$VER" = "latest" ]; then \
        echo "using latest version." \
    &&  export LATEST_VERSION=$(curl -v -L --silent \
        -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36" \
        https://terraria.wiki.gg/wiki/Server#Downloads 2>&1 | grep -o 'https://terraria.org/api/download/pc-dedicated-server/[^"]*' \
        | sed 's#.*/terraria-server-##' | sed 's/.zip//' | tail -1) \
    &&  export VER=${LATEST_VERSION}; fi \
    && echo "VERSION=${VER}" \
    && echo "${VER}" > /terraria-server/info/version.txt \
    && curl https://terraria.org/api/download/pc-dedicated-server/terraria-server-${VER}.zip --output terraria-server.zip \  
    && unzip terraria-server.zip -d /terraria-server && mv /terraria-server/*/* /terraria-server \
    && rm -rf terraria-server.zip /terraria-server/Mac /terraria-server/Windows /terraria-server/${VER} \
    && mv /terraria-server/Linux/* /terraria-server/ \
    && cd /terraria-server \
    && chmod +x TerrariaServer.bin.x86_64*

COPY ./init.sh /terraria-server/

RUN chmod +x /terraria-server/init.sh

VOLUME ["/root/.local/share/Terraria/Worlds/"]

WORKDIR /terraria-server

ENTRYPOINT [ "./init.sh" ]

