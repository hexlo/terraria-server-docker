FROM ubuntu:jammy as builder

ARG VERSION=latest

ENV TERRARIA_VERSION=$VERSION \
    LATEST_VERSION="" \
    PATH="/scripts:${PATH}" \
    TERRARIA_DIR=/root/.local/share/Terraria

RUN mkdir -p /scripts ${TERRARIA_DIR}

COPY ./.scripts /scripts

RUN chmod +x /scripts/* && \
    mv /scripts/init-TerrariaServer.sh ${TERRARIA_DIR}/Worlds

RUN apt-get update -y && apt-get install -y unzip curl

WORKDIR ${TERRARIA_DIR}

RUN if [ "${TERRARIA_VERSION:-latest}" = "latest" ]; then \
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

ENV TERRARIA_DIR=/root/.local/share/Terraria \
    autocreate=2 \
    seed='' \
    worldname=TerrariaWorld \
    difficulty=0 \
    maxplayers=16 \
    port=7777 \
    password='' \
    motd="Welcome!" \
    worldpath=${TERRARIA_DIR}/Worlds \
    banlist=banlist.txt \
    secure=1 \
    language=en/US \
    upnp=1 \
    npcstream=1 \
    priority=1

RUN mkdir -p ${TERRARIA_DIR}/Worlds

WORKDIR ${TERRARIA_DIR}

COPY --from=builder ${TERRARIA_DIR}/* ./

VOLUME [`${TERRARIA_DIR}/Worlds`]

ENTRYPOINT [ "./init-TerrariaServer.sh" ]

