# Start from the official Python base image.
#FROM python:3.11.4
FROM tiangolo/uvicorn-gunicorn:python3.11

# We create our working space
WORKDIR /code

# We copy the requirements file
COPY ./requirements.txt /code/requirements.txt

# We install the dependancies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the source code into the container 
COPY . /code

# Run the application
#CMD uvicorn main:app --reload --port 8000 --host 0.0.0.0
CMD gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT

