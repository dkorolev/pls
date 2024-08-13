#!/bin/bash

pls build
./.debug/trivial_dep | tee trivial_dep.txt
[ "$(cat trivial_dep.txt)" == "2+2=10004" ]  # With 10'000 added from a `#define`-d symbol set in `pls.json`.
