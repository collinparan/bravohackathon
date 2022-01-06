FROM python:3.8.8-buster

COPY ./requirements.txt ./app/
WORKDIR /app
RUN pip install -r requirements.txt
RUN chmod u+x app.py 

ENTRYPOINT ["python","app.py"]

EXPOSE 80