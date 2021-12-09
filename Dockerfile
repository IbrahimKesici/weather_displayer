FROM cpa.docker.itcm.oneadr.net/ubi8-python39:1.0.0

WORKDIR /weather-displayer
COPY . .

RUN pip3.9 install -r requirements.txt

ENTRYPOINT ["python3"]
#CMD ["weather_displayer/main.py"]