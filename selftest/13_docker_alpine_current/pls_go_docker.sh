#!/bin/bash

DIR="$(dirname "$(realpath "$0")")"

rm -rf pls_into_docker
mkdir pls_into_docker

(cd ../..; cp -rv pls "$DIR/_pls")

docker build .
mkdir -p _out
time docker run -t -v "$PWD/_out:/out" $(docker build -q .)

[ "$(cat _out/example.txt)" == "[1,2,3]" ]
