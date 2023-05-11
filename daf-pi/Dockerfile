FROM debian:latest

RUN apt-get update 
RUN apt-get -y install sudo
USER root

RUN set -xe \
    && sudo apt install -y python3 python3-venv socat \
    && apt-get install -y python3-pip
RUN python3 -m venv venv
RUN . venv/bin/activate

RUN rm -rf /daf-pi
COPY /. /daf-pi

RUN pip3 install --upgrade pip
RUN pip install -r /daf-pi/requirements.txt

#RUN socat -d -d pty,raw,echo=0 pty,raw,echo=0
#RUN python3 app.py


EXPOSE 9000