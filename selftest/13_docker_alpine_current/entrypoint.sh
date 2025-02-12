#!/bin/sh

(cd demo; pls build)
(cd demo; ./.debug/example | tee /out/example.txt)
