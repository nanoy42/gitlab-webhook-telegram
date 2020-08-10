FROM python:3-alpine

WORKDIR /code

RUN apk --update add openssl libffi

COPY requirements.txt .
RUN apk --update add --virtual /tmp/build-deps --no-cache alpine-sdk \
    libffi-dev openssl-dev && pip3 install --no-cache-dir -r requirements.txt \
    && apk del /tmp/build-deps

COPY . .

CMD [ "python3", "main.py", "test" ]
