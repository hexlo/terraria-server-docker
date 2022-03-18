FROM ubuntu:focal

ARG VERSION=latest

ENV VER=$VERSION

ENV LATEST_VERSION=""

ENV DOCS_URL=https://terraria.fandom.com/wiki/Server

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
        https://terraria.fandom.com/wiki/Server#Downloads 2>&1 | grep -o 'https://terraria.org/api/download/pc-dedicated-server/[^"]*' \
        | sed 's#.*/terraria-server-##' | sed 's/.zip//' | tail -1) \
    &&  export VER=${LATEST_VERSION}; fi \
    && echo "VERSION=${VER}" \
    && echo "${VER}" > /terraria-server/info/version.txt \
    && curl https://terraria.org/api/download/pc-dedicated-server/terraria-server-${VER}.zip --output terraria-server.zip \  
    && unzip terraria-server.zip -d /terraria-server && mv /terraria-server/*/* /terraria-server \
    && rm terraria-server.zip && rm -rf /terraria-server/Mac && rm -rf /terraria-server/Windows \
    && cd /terraria-server/Linux \
    && chmod +x TerrariaServer.bin.x86_64*

# RUN mkdir -p /terraria-server /root/.local/share/Terraria/Worlds/ \
#     && wget -O terraria-server.zip ${DOWNLOAD_URL} \
#     && unzip terraria-server.zip -d /terraria-server && rm terraria-server.zip && rm -Rf /terraria-server/*/Windows /terraria-server/*/Mac \
#     && cd /terraria-server/*/Linux \
#     # && wget -O terraria-server.zip ${SELF_HOSTED_DOWNLOAD_URL} \
#     # && tar -xf terraria-server.zip -C /terraria-server --strip-components=1\
#     # && cd /terraria-server/*/Linux \
#     && chmod +x TerrariaServer.bin.x86_64* 

COPY ./init.sh /terraria-server/Linux/

RUN chmod +x /terraria-server/Linux/init.sh

VOLUME ["/root/.local/share/Terraria/Worlds/"]

WORKDIR /terraria-server/Linux

ENTRYPOINT [ "./init.sh" ]

