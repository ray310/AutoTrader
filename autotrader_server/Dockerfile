# setting base image
FROM python:3.8

# arguments are passed in from CLI
ARG KEY_BUCKET
ARG AT_BUCKET

# setting environment variables from arguments passed from CLI
ENV AT_KEYS_BUCKET=$KEY_BUCKET
ENV AT_BUCKET=$AT_BUCKET

# set the working directory in the container
WORKDIR /server

# copy the requirements file from context to the working directory
COPY requirements.txt .

# install Python dependencies
RUN pip install -r requirements.txt

# copy the context working directory to the image working directory
COPY . .

# command to run on container start
CMD [ "python", "server.py" ]