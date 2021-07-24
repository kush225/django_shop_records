#pull official base image
FROM python:3.7

#setting up the directory
WORKDIR /server



##installing python-dev
RUN apt-get update -y && \
   apt-get upgrade -y && \
   apt-get dist-upgrade -y && \
   apt-get -y autoremove && \
   apt-get clean
#   && apt-get install python3-dev -y

#COPYING requirements
COPY ./requirements.txt ./requirements.txt

#installing dependencies
RUN pip3 install --upgrade pip \
    && pip3 install -r ./requirements.txt 

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

RUN echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | tee /etc/apt/sources.list.d/google-chrome.list

RUN apt-get update -y && \
    apt-get install google-chrome-stable -y

#COPYING server files
COPY ./ ./

#run entrypoint.sh
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]