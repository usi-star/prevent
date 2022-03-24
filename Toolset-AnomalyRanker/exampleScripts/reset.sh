#!/bin/bash

curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"reset":true}' \
  http://localhost:5000/reset