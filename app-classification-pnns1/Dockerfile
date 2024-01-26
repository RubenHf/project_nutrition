# Start from the official Python base image.
FROM python:3.11.4

# We create our working space
WORKDIR /code

# We copy the requirements file
COPY ./requirements.txt /code/requirements.txt

# We install the dependancies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the source code into the container 
COPY . /code

# Expose the port that the application listens on.

EXPOSE 8000

# Run the application
CMD uvicorn main:app --reload --port 8000 --host 0.0.0.0
