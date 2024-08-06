#!/bin/bash

pls build
./.debug/trivial_dep | tee trivial_dep.txt
[ "$(cat trivial_dep.txt)" == "3+3=6" ]
