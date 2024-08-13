#!/bin/bash

echo 'Attempting `pls build` that should fail.'

if pls build ; then
  echo 'Build succeeded, but it should have failed.'
  exit 1
else
  echo '"Task failed successfully!" (c)'
  exit 0
fi
