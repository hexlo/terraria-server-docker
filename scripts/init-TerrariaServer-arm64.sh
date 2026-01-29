#!/bin/bash

./create-server-config.sh;

mono --server --gc=sgen -O=all ./TerrariaServer.exe -config server-config.conf
