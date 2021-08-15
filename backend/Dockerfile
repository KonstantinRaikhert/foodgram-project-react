FROM python:3.8.5
WORKDIR /code
COPY .  .
COPY requirements/ requirements/
RUN pip install -r requirements/develop.txt
CMD gunicorn configuration.wsgi:application --bind 0.0.0.0:8000
