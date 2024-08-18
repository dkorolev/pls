#!/bin/bash

pls build
./.debug/use_current_2 | tee use_current_2.txt
[ "$(cat use_current_2.txt)" == "[4,5,6]" ]
