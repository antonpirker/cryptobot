#
# To build this docker container run this in the root directory of repo:
#
# docker build --tag cryptobot:latest .
#
# To run the docker container:
#
# docker run --rm -p 8000:8000 -it --name cryptobot cryptobot:latest
#

FROM python:3

WORKDIR /app

RUN mkdir -p /root/.jupyter && pip install jupyter -U && pip install jupyterlab -U

COPY jupyter_notebook_config.py /root/.jupyter/jupyter_notebook_config.py

COPY *.py ./
COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8000

#CMD ["jupyter", "lab","--ip=0.0.0.0","--allow-root"]
CMD ["python", "status.py"]
