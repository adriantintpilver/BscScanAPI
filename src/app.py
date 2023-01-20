import asyncio
from bscscan import BscScan
from flask import Flask, jsonify, request, render_template
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
import ast
import requests
import time

#from datetime import datetime
import datetime

from csv import reader
import os
import copy
import json
import pandas as pd
import pandavro as pdx
from AccessData import sql_querys 
import calendar
from urllib.request import urlopen


import base64
from io import BytesIO

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

from config import config
from config import (YOUR_API_KEY)
from validations import *
from functions import *
from graphics_functions import *

now = datetime.datetime.utcnow()
app = Flask(__name__)

conexion = MySQL(app)

# WEB Function home
@app.route("/")
def index():
    return render_template('index.html')

# WEB Function events_by_address
@app.route('/events_by_address/', methods=['POST'])
def events_by_address():
    id_wallet = request.form.get('id_wallet')
    #print(id_wallet)
    #respt = asyncio.run(get_bnb_balance(id_wallet))
    #print("respt: " + str(respt))
    respt = asyncio.run(get_bep721_token_transfer_events_by_address(id_wallet))
    if respt != None: insert_bep721_token_transfer_events(respt,id_wallet)
    # Call bscScan to bring the new data into DB
    resp = asyncio.run(get_bep20_token_transfer_events_by_address(id_wallet))
    if resp != None: insert_bep20_token_transfer_events(resp,id_wallet)
    image_name = graph_bars_transsaction_from_to_day_by_wallet(id_wallet)
    #image_name = 'feo.jpj'
    #image_name_hist = graph_timeline_by_wallet(id_wallet,'usd')
    image_name_value = graph_stock_by_dates_2(id_wallet)
    return render_template('events_by_address.html', id_wallet = id_wallet, image_name = image_name, image_name_value = image_name_value)

# API Function that bep20_token_transfer_events
@app.route('/get_bep20_token_transfer_events_by_address', methods=['POST'])
def list_get_bep20_token_transfer_events_by_address():
    print (request.json)
    id_wallet = request.json['id_wallet']
    if (wallet_id_validation(id_wallet)):
        resp = asyncio.run(get_bep20_token_transfer_events_by_address(id_wallet))
        insert_bep20_token_transfer_events(resp,id_wallet)
        LogFile("method: API: get_bep20_token_transfer_events_by_address. status.status.200 OK INPUT ->" + str(request.json))
        return jsonify({'message': resp, 'status': 'status.200 OK'})
    else:
        LogFile("method: API: get_bep20_token_transfer_events_by_address . Error Invalid parameters. status.HTTP_400_BAD_REQUEST INPUT ->" + str(request.json))
        return jsonify({'method': 'get_bep20_token_transfer_events_by_address', 'message': "Error Invalid parameters....", 'status': 'status.HTTP_400_BAD_REQUEST'})

@app.route('/add_coins_history', methods=['POST'])
def add_coins_history():
    try:
        date_itinerate = datetime.datetime.utcnow()
        count = 0
        while True:
            coinresp = read_coins_history(request.json['coin'], date_itinerate.strftime("%Y-%m-%d"), request.json['money'])
            if (coinresp == None):
                url = "https://api.coingecko.com/api/v3/coins/"+request.json['coin']+"/history?date="+date_itinerate.strftime("%d-%m-%Y")
                response = urlopen(url)
                data = json.loads(response.read())
                if 'market_data' in data:
                    if 'current_price' in data['market_data']:
                        if request.json['money'] in data['market_data']['current_price']:
                            count = count + 1
                            print( " count:" + str(count) + " fecha: " + str(date_itinerate.strftime("%Y-%m-%d")))
                            insert_coins_history(request.json['coin'], data["market_data"] ["current_price"][request.json['money']], data["market_data"] ["market_cap"][request.json['money']], date_itinerate.strftime("%Y-%m-%d"), request.json['money'])
                            time.sleep(5)
                else:
                    break  
            date_itinerate = date_itinerate - datetime.timedelta(days=1) 
        return jsonify({'para la moneda '+ request.json['coin'] + ' en ' + request.json['money'] + ' se insertaron: ': count, 'status': 'status.200 OK'})
    except Exception as ex:
        raise ex 

def page_not_found(error):
    LogFile("Page not found!, sorry. Error success: False")
    return "<h1>Page not found!, sorry d:-D </h1>", 404


if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404, page_not_found)
    app.run()
