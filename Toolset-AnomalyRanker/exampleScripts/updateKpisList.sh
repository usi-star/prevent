#!/bin/bash

curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"kpis":[{"timestamp":1522751098000,"resource":{"name":"Node2"},"metric":{"name":"MEMORY"},"value":48928.6},{"timestamp":1522751098000,"resource":{"name":"Node3"},"metric":{"name":"MEMORY"},"value":48928.6}]}' \
  http://localhost:5000/update_kpi