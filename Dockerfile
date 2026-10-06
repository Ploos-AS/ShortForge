FROM python:3.13-alpine

RUN apk add --no-cache ffmpeg font-dejavu
WORKDIR /opt/shortforge
COPY . .
RUN pip install --no-cache-dir .

WORKDIR /work
ENTRYPOINT ["shortforge"]
CMD ["--help"]
