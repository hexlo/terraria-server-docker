FROM ubuntu:jammy as builder

ARG VERSION=1441-fixed

ENV TERRARIA_VERSION=$VERSION

ENV LATEST_VERSION=""

ENV PATH="/scripts:${PATH}"

ENV TERRARIA_DIR=/root/.local/share/Terraria

RUN mkdir -p /scripts ${TERRARIA_DIR}

COPY ./.scripts /scripts

RUN chmod +x /scripts/*

RUN mv /scripts/init-TerrariaServer.sh ${TERRARIA_DIR}

RUN apt update -y && apt install -y unzip curl

WORKDIR ${TERRARIA_DIR}

RUN if [ "${TERRARIA_VERSION}" = "latest" ]; then \
        echo "using latest version." \
    &&  export LATEST_VERSION=$(get-terraria-version.sh) \
    &&  export TERRARIA_VERSION=${LATEST_VERSION}; fi \
    && echo "TERRARIA_VERSION=${TERRARIA_VERSION}" \
    && echo "${TERRARIA_VERSION}" > ${TERRARIA_DIR}terraria-version.txt \
    && curl https://terraria.org/api/download/pc-dedicated-server/terraria-server-${TERRARIA_VERSION}.zip --output terraria-server.zip \  
    && unzip terraria-server.zip -d ${TERRARIA_DIR} && mv ${TERRARIA_DIR}/*/* ${TERRARIA_DIR} \
    && rm -rf terraria-server.zip ${TERRARIA_DIR}/Mac ${TERRARIA_DIR}/Windows ${TERRARIA_DIR}/${TERRARIA_VERSION} \
    && mv ${TERRARIA_DIR}/Linux/* ${TERRARIA_DIR}/ \
    && rm -rf ${TERRARIA_DIR}/Linux \
    && cd ${TERRARIA_DIR} \
    && chmod +x TerrariaServer.bin.x86_64*

####################################################################

FROM ubuntu:jammy

ENV TERRARIA_DIR=/root/.local/share/Terraria

RUN mkdir -p ${TERRARIA_DIR}/Worlds

ENV autocreate=2

ENV seed=

ENV worldname=TerrariaWorld

ENV difficulty=0

ENV maxplayers=16

ENV port=7777

ENV password=''

ENV motd="Welcome!"

ENV worldpath=${TERRARIA_DIR}/Worlds

ENV banlist=banlist.txt

ENV secure=1

ENV language=en/US

ENV upnp=1

ENV npcstream=1

ENV priority=1

WORKDIR ${TERRARIA_DIR}

COPY --from=builder ${TERRARIA_DIR}/* ./

VOLUME ["/root/.local/share/Terraria/Worlds"]

ENTRYPOINT [ "./init-TerrariaServer.sh" ]

