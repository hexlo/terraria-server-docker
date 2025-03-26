FROM debian:10-slim AS base

ARG VERSION=latest

ENV TERRARIA_VERSION=$VERSION
ENV LATEST_VERSION=""
ENV TERRARIA_DIR=/root/.local/share/Terraria
ENV PATH="${TERRARIA_DIR}:${PATH}"

RUN mkdir -p ${TERRARIA_DIR}

WORKDIR ${TERRARIA_DIR}

COPY ./.scripts/* .

RUN chmod +x \
    create-server-config.sh \
    get-terraria-version.sh \
    init-TerrariaServer-amd64.sh \
    init-TerrariaServer-arm64.sh

RUN apt-get update -y && apt-get install -y unzip wget

RUN if [ "${TERRARIA_VERSION:-latest}" = "latest" ]; then \
    echo "using latest version." \
    &&  export LATEST_VERSION=$(bash get-terraria-version.sh) \
    &&  export TERRARIA_VERSION=${LATEST_VERSION}; fi \
    && echo "TERRARIA_VERSION=${TERRARIA_VERSION}" \
    && echo "${TERRARIA_VERSION}" > ${TERRARIA_DIR}/terraria-version.txt \
    && wget https://terraria.org/api/download/pc-dedicated-server/terraria-server-${TERRARIA_VERSION}.zip -O terraria-server.zip \  
    && unzip terraria-server.zip -d ${TERRARIA_DIR} && mv ${TERRARIA_DIR}/*/* ${TERRARIA_DIR} \
    && rm -rf terraria-server.zip ${TERRARIA_DIR}/Mac ${TERRARIA_DIR}/Windows ${TERRARIA_DIR}/${TERRARIA_VERSION} \
    && mv ${TERRARIA_DIR}/Linux/* ${TERRARIA_DIR}/ \
    && rm -rf ${TERRARIA_DIR}/Linux \
    && cd ${TERRARIA_DIR}

ENV autocreate=1 \
    seed='' \
    worldname=TerrariaWorld \
    difficulty=1 \
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

RUN mkdir -p ${TERRARIA_DIR}

WORKDIR ${TERRARIA_DIR}

RUN mkdir -p ${TERRARIA_DIR}/Worlds

### amd-64 ###

FROM base AS build-amd64

RUN chmod +x TerrariaServer.bin.x86_64

ENTRYPOINT [ "./init-TerrariaServer-amd64.sh" ]

### arm-64 ###

FROM mono:latest AS build-arm64

ENV TERRARIA_DIR=/root/.local/share/Terraria

ENV PATH="${TERRARIA_DIR}:${PATH}" \
    autocreate=1 \
    seed='' \
    worldname=TerrariaWorld \
    difficulty=1 \
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

RUN mkdir -p ${TERRARIA_DIR}

WORKDIR ${TERRARIA_DIR}

COPY --from=base ${TERRARIA_DIR}/* ./

RUN chmod +x TerrariaServer.exe

RUN rm System* Mono* monoconfig mscorlib.dll

ENTRYPOINT [ "./init-TerrariaServer-arm64.sh" ]