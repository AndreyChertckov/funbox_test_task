FROM python:3.7

RUN mkdir -p /app
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY src/* /app/


CMD [ "bash" , "start.sh"]