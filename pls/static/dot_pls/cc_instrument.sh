#!/bin/bash

# This used to fail silently when `g++` is not present.
# Changed into `clang++` for now.
# Figured this our while experimenting with Alpine.
# TODO(dkorolev): 1) It should not fail silently, 2) perhaps `clang` is an overkill here?
clang++ \
  -I"$2" \
  -D PLS_INSTRUMENTATION \
  -E \
  "$1" 2>/dev/null \
| grep PLS_INSTRUMENTATION_OUTPUT \
| sed 's/^PLS_INSTRUMENTATION_OUTPUT//g'
