# Start from the official Python base image.
FROM python:3.11.4

# We create our working space
WORKDIR /code

# We copy the requirements file
COPY ./requirements.txt /code/requirements.txt

# We install the dependancies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# We copy the current dir 
COPY . /code

# 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]