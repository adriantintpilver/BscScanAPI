FROM python:3.10.7

WORKDIR /

COPY ./requirements.txt /requirements.txt

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "./src/app.py"]
#CMD [ "python", "view.py" ]