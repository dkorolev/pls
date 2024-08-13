#!/bin/bash

pls build
./.debug/call | tee result.txt
[ "$(cat result.txt)" == "2+2=4" ]
