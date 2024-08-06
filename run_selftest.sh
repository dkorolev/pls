#!/bin/bash

set -e

pls version || (echo 'Need the `pls` tool installed.' && exit 1)
echo

SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")

# Figure out we are in the right dir.
[ -d "$SCRIPT_DIR/selftest" ] || (echo 'Need the `./selftest` dir.' && exit 1)

# Clean up the previous run and set up a new one.
(cd "$SCRIPT_DIR"; rm -rf .selftest)
(cd "$SCRIPT_DIR"; cp -r selftest .selftest)

# Run all the tests.
(
  N_RUN=0
  N_PASSED=0
  N_FAILED=0
  cd "$SCRIPT_DIR/.selftest"
  for T in $(find . -name pls_go.sh | sort); do
    N_RUN=$((N_RUN+1))
    TN="$(dirname "$T")"
    echo 'Running the test from  `'$TN'/`.'
    (cd "$TN"; ./pls_go.sh) && N_PASSED=$((N_PASSED+1)) || N_FAILED=$((N_FAILED+1))
    echo
  done
  echo "Total tests run: $N_RUN, passed: $N_PASSED, failed: $N_FAILED."
  [ "$N_FAILED" == 0 ]
)
