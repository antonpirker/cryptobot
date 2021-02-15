#
# To build this docker container run this in the root directory of repo:
#
# docker build --tag cryptobot:latest .
#
# To run the docker container:
#
# docker run --rm -p 8000:8000 -it --name cryptobot cryptobot:latest
#

FROM python:3-alpine

WORKDIR /app

COPY *.py ./
COPY *.sql ./
COPY requirements.txt .

# Seed database
RUN \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    apk --purge del .build-deps

RUN PGPASSWORD=$WDPR_DB_PASSWORD psql -v -U $WDPR_DB_USERNAME -h $WDPR_DB_HOST -p $WDPR_DB_PORT -d $WDPR_DB_DATABASE -f database.sql;

# Install requirements
#RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "status.py"]
