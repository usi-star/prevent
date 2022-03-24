#!/bin/bash

mkdir -p log
mkdir -p cached
docker-compose pull
docker-compose up