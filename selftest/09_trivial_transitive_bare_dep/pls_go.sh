#!/bin/bash

pls build
./.debug/call | tee result.txt
[ "$(cat result.txt)" == "7*2=14; 8+8=16" ]
