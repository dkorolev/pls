#!/bin/bash

pls build
./.debug/use_current | tee use_current.txt
[ "$(cat use_current.txt)" == "[1,2,3]" ]
