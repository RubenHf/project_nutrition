# Start from the fastapi image
FROM tiangolo/uvicorn-gunicorn:python3.11
#FROM python:3.11-slim

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# We create our working space
WORKDIR /code

# We copy the requirements file
COPY ./requirements.txt /code/requirements.txt

# We upgrade pip
RUN pip install --upgrade pip

# We install the dependancies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the source code into the container 
COPY . /code

# Run the application
CMD gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
