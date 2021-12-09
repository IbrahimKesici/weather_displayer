FROM python:3.9

WORKDIR /weather-displayer
COPY . .

RUN pip3.9 install -r requirements.txt

ENTRYPOINT ["python3"]
#CMD ["weather_displayer/main.py"]