#!/bin/bash

pls build
./.debug/call | tee result.txt
[ "$(cat result.txt)" == "6*2=12; 7+7=14" ]
