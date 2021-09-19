FROM python:3.8.5
WORKDIR /code
COPY .  .
COPY requirements/ requirements/
RUN python -m pip install --upgrade pip
RUN pip install -r requirements/production.txt
CMD gunicorn configuration.wsgi:application --bind 0.0.0.0:8000
