#!/bin/bash

pls build
./.debug/call | tee result.txt
[ "$(cat result.txt)" == "UNIQUE=42" ]
