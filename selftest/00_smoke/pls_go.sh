#!/bin/bash

pls build
./.debug/example | tee example.txt
[ "$(cat example.txt)" == "OK" ]
