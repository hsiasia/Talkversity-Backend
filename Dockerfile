FROM python:3.9.7
LABEL maintainer jeanshan
ENV PYTHONUNBUFFERED 1
RUN apt-get update && \
    apt-get upgrade -y && apt-get install -y ffmpeg \
    libprotobuf-dev protobuf-compiler \
    cmake 
RUN mkdir /docker_api
WORKDIR /docker_api
COPY . /docker_api/
RUN pip install -r requirements.txt