#!/bin/bash

CPP=$(g++ --version >/dev/null && echo g++ || echo clang++)

# NOTE(dkorolev): Unfortunately, this next line _may_fail, which is as expected.
# As long as `#include "pls.h"` comes before the `#include`-s of modules which may not yet be present.

$CPP \
  -I"$2" \
  -D PLS_INSTRUMENTATION \
  -E \
  "$1" 2>/dev/null \
| grep PLS_INSTRUMENTATION_OUTPUT \
| sed 's/^PLS_INSTRUMENTATION_OUTPUT//g'
