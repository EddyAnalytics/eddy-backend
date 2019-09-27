FROM alpine

WORKDIR /usr/src/app

RUN apk update

RUN apk upgrade

RUN apk add python3 mariadb python3-dev mariadb-dev gcc g++ musl-dev  linux-headers tzdata

COPY requirements.txt .

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["eddy-backend"]
