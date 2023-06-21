# set the kernel to use
FROM python:3.8.10
# FROM nodered/node-red

# WORKDIR /app
# RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
# RUN apt-get install -y nodejs
# # RUN npm install npm@latest -g
# RUN npm install -g --unsafe-perm node-red

# RUN npm install node-red-dashboard
# RUN npm install npm install node-red-contrib-python-function-ps
# RUN npm install node-red-contrib-ui-time-scheduler

# copy the requirements file
COPY requirements.txt requirements.txt
# install the needed requirements
RUN pip3 install -r requirements.txt
# copy the all the file in the container
COPY . .

# COPY package.json /app/package.json
# COPY IoT_Dashboard.json /data/flows.json

# the command that will be executed when the container will start
CMD ["python3","./catalog_API.py"]


#sudo docker save irrigation_iot -o irrigation_iot.tar