FROM alpine:3.10

ENV PYTHONUNBUFFERED=0
ARG TZ=Europe/Amsterdam

WORKDIR /usr/src/app

RUN apk add python3 python3-dev mysql mysql-client mysql-dev gcc g++ musl-dev linux-headers tzdata

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["eddy-backend"]
