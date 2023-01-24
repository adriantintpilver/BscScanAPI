FROM python:3

RUN mkdir /BscScanAPI

WORKDIR /BscScanAPI

COPY requirements.txt /BscScanAPI

RUN pip install -r requirements.txt

COPY . /BscScanAPI

EXPOSE 5000

CMD [ "python", ".\src\app.py" ]