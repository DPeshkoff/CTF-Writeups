FROM python:3.9
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD rm database.db
CMD python -m flask run --host=0.0.0.0
