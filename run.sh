#!/bin/bash

echo Scaling down running project containers
docker-compose down

echo Creating project containers
docker-compose up -d

echo Starting the application
docker-compose exec app python3 weather_displayer/main.py