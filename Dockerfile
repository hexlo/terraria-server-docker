FROM rockylinux:9 as builder

ARG VERSION=latest

ENV TERRARIA_VERSION=$VERSION

ENV LATEST_VERSION=""

ENV PATH="/scripts:${PATH}"

RUN mkdir -p /scripts /terraria-server

COPY ./.scripts /scripts

RUN chmod +x /scripts/*

RUN mv /scripts/init-TerrariaServer.sh /terraria-server

RUN dnf update -y && dnf install -y unzip curl

WORKDIR /terraria-server

RUN if [ "${TERRARIA_VERSION}" = "latest" ]; then \
        echo "using latest version." \
    &&  export LATEST_VERSION=$(/scripts/get-terraria-version.sh) \
    &&  export TERRARIA_VERSION=${LATEST_VERSION}; fi \
    && echo "TERRARIA_VERSION=${TERRARIA_VERSION}" \
    && echo "${TERRARIA_VERSION}" > /terraria-server/terraria-version.txt \
    && curl https://terraria.org/api/download/pc-dedicated-server/terraria-server-${TERRARIA_VERSION}.zip --output terraria-server.zip \  
    && unzip terraria-server.zip -d /terraria-server && mv /terraria-server/*/* /terraria-server \
    && rm -rf terraria-server.zip /terraria-server/Mac /terraria-server/Windows /terraria-server/${TERRARIA_VERSION} \
    && mv /terraria-server/Linux/* /terraria-server/ \
    && rm -rf /terraria-server/Linux \
    && cd /terraria-server \
    && chmod +x TerrariaServer.bin.x86_64*

####################################################################

FROM rockylinux:9-minimal

RUN mkdir -p /terraria-server/Worlds

ENV autocreate=2

ENV seed=

ENV worldname=TerrariaWorld

ENV difficulty=0

ENV maxplayers=16

ENV port=7777

ENV password=''

ENV motd="Welcome!"

ENV worldpath=/terraria-server/Worlds

ENV banlist=banlist.txt

ENV secure=1

ENV language=en/US

ENV upnp=1

ENV npcstream=1

ENV priority=1

WORKDIR /terraria-server

COPY --from=builder /terraria-server/* ./

VOLUME ["/terraria-server/Worlds"]

ENTRYPOINT [ "./init-TerrariaServer.sh" ]

