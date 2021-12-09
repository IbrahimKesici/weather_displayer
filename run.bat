@echo off

echo Scaling down running project containers
call docker-compose down

echo Creating project containers
call docker-compose up -d

echo Starting the application
call docker-compose exec app python3 weather_displayer/main.py