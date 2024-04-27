# syntax=docker/dockerfile:1
FROM puppet/puppetserver
#ENV FLASK_APP=app.py
#ENV FLASK_RUN_HOST=0.0.0.0
RUN apt-get update && apt upgrade -y
RUN apt-get install -y \
    strace
EXPOSE 8140