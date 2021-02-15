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

ARG WDPR_DB_PASSWORD
ENV WDPR_DB_PASSWORD=$WDPR_DB_PASSWORD

ARG WDPR_DB_USERNAME
ENV WDPR_DB_USERNAME=$WDPR_DB_USERNAME

ARG WDPR_DB_HOST
ENV WDPR_DB_HOST=$WDPR_DB_HOST

ARG WDPR_DB_PORT
ENV WDPR_DB_PORT=$WDPR_DB_PORT

ARG WDPR_DB_DATABASE
ENV WDPR_DB_DATABASE=$WDPR_DB_DATABASE

WORKDIR /app

COPY *.py ./
COPY *.sql ./
COPY requirements.txt .

# Install requirements
RUN \
 apk add --no-cache postgresql-libs postgresql-client && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

# debug
RUN printenv | sort > bla.txt
RUN cat bla.txt

# Seed database
RUN PGPASSWORD=$WDPR_DB_PASSWORD psql -v -U $WDPR_DB_USERNAME -h $WDPR_DB_HOST -p $WDPR_DB_PORT -d $WDPR_DB_DATABASE -f database.sql;


EXPOSE 8000

CMD ["python", "status.py"]
