import asyncio
from bscscan import BscScan
from flask import Flask, jsonify, request, render_template
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
import ast
import requests
from datetime import datetime
from csv import reader
import os
import copy
import json
import pandas as pd
import pandavro as pdx
from AccessData import sql_querys 

import base64
from io import BytesIO

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

from config import config
from config import (YOUR_API_KEY)
from validations import *

now = datetime.now()
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
    image_name_hist = graph_histogram_by_wallet(id_wallet)
    return render_template('events_by_address.html', id_wallet = id_wallet, image_name = image_name, image_name_hist = image_name_hist)

# API Function that returns all employees
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

# asynchronous call to get_bep20_token_transfer_events_by_address method of BscScan
async def get_bep20_token_transfer_events_by_address(id_wallet):
    try:
        async with BscScan(YOUR_API_KEY) as client:
            return ( await client.get_bep20_token_transfer_events_by_address(
                    address= id_wallet,
                    startblock=0,
                    endblock=999999999,
                    sort="asc"
            ))
    except AssertionError:
        return None     
# asynchronous call to get_bep20_token_transfer_events_by_address method of BscScan
async def get_bep721_token_transfer_events_by_address(id_wallet):
    try: 
        async with BscScan(YOUR_API_KEY) as client:
            return ( await client.get_bep721_token_transfer_events_by_address(
                    address= id_wallet,
                    startblock=0,
                    endblock=999999999,
                    sort="asc"
                        
            ))
    except AssertionError:
        return None
# asynchronous call to get_bnb_balance method of BscScan
async def get_bnb_balance(id_wallet):
    try:
        async with BscScan(YOUR_API_KEY) as client:
            return ( await client.get_bnb_balance(
                    address= id_wallet
            ))
    except AssertionError:
        return None

# asynchronous call to get_bnb_balance method of BscScan
async def get_bnb_balance(id_wallet):
    async with BscScan(YOUR_API_KEY) as client:
        return ( await client.get_bnb_balance(
                address= id_wallet
        ))


# Function that save bep20_token_transfer_events_by_address data into DB
def insert_bep20_token_transfer_events(var_json,id_wallet):
    try:
        max_timestamp = read_bep20_token_transfer_events_by_address_db(id_wallet)
        for field_dict in var_json:
            if (field_dict['timeStamp'] > str(max_timestamp) or max_timestamp == None):
                cursor = conexion.connection.cursor()
                sql = str(sql_querys['sql_insert_bep20_token_transfer_events_by_address']).format(field_dict['blockHash'],
                                                                    field_dict['blockNumber'],field_dict['confirmations'],field_dict['contractAddress'],field_dict['cumulativeGasUsed'],field_dict['from'],field_dict['gas'],field_dict['gasPrice'],field_dict['gasUsed'],field_dict['hash'],field_dict['input'],field_dict['nonce'],field_dict['timeStamp'],field_dict['to'],field_dict['tokenDecimal'],field_dict['tokenName'],field_dict['tokenSymbol'],field_dict['transactionIndex'],field_dict['value'])
                cursor.execute(sql)
                conexion.connection.commit()
        return None
    except Exception as ex:
        raise ex 

# Function that save bep721_token_transfer_events_by_address data into DB
def insert_bep721_token_transfer_events(var_json,id_wallet):
    try:
        max_timestamp = read_bep721_token_transfer_events_by_address_db(id_wallet)
        for field_dict in var_json:
            if (field_dict['timeStamp'] > str(max_timestamp) or max_timestamp == None):
                cursor = conexion.connection.cursor()
                sql = str(sql_querys['sql_insert_bep721_token_transfer_events_by_address']).format(field_dict['blockHash'],
                                                                    field_dict['blockNumber'],field_dict['confirmations'],field_dict['contractAddress'],field_dict['cumulativeGasUsed'],field_dict['from'],field_dict['gas'],field_dict['gasPrice'],field_dict['gasUsed'],field_dict['hash'],field_dict['input'],field_dict['nonce'],field_dict['timeStamp'],field_dict['to'],field_dict['tokenDecimal'],field_dict['tokenName'],field_dict['tokenSymbol'],field_dict['transactionIndex'],field_dict['tokenID'])
                cursor.execute(sql)
                conexion.connection.commit()
        return None
    except Exception as ex:
        raise ex 

# Function that returns last time stamp save from a wallet in table bep721_token_transfer_events_by_address
def read_bep721_token_transfer_events_by_address_db(id_wallet):
    try:
        cursor = conexion.connection.cursor()
        sql = str(sql_querys['sql_from-to_read_bep721_token_transfer_events_by_address_db']).format(id_wallet)
        cursor.execute(sql)
        data = cursor.fetchone()
        if data != None:
            timestamp = data[0]
            return timestamp
        else:
            return None
    except Exception as ex:
        raise ex 

# Function that returns last time stamp save from a wallet in table bep20_token_transfer_events_by_address
def read_bep20_token_transfer_events_by_address_db(id_wallet):
    try:
        cursor = conexion.connection.cursor()
        sql = str(sql_querys['sql_from-to_read_bep20_token_transfer_events_by_address_db']).format(id_wallet)
        cursor.execute(sql)
        data = cursor.fetchone()
        if data != None:
            timestamp = data[0]
            return timestamp
        else:
            return None
    except Exception as ex:
        raise ex 

# Function that log one txt file by day
def LogFile(text):
    now = datetime.now()
    try:
        f = open("logs/log_" + now.strftime("%m-%d-%Y")+".txt", "a")
        f.write("\n")
        f.write(now.strftime("%m-%d-%Y-%H-%M-%S")+ " : " + str(text))
        f.close()
        return "log OK"
    except Exception as ex:
        raise ex

def graph_bars_transsaction_from_to_day_by_wallet(id_wallet):
    # call Stores Procedures "transsaction_from_to_day_by_wallet" 
    cursor2 = conexion.connection.cursor()
    cursor2.callproc('transsaction_from_to_day_by_wallet', [str(id_wallet)])
    data = cursor2.fetchall()
    cut=8
    print("len(data): " + str(len(data)))
    if (len(data) > 10):
        cursor2.close() 
        # call Stores Procedures "transsaction_from_to_month_by_wallet" 
        cursor2 = conexion.connection.cursor()
        cursor2.callproc('transsaction_from_to_month_by_wallet', [str(id_wallet)])
        data = cursor2.fetchall()
        cut=6

    fig, ax = plt.subplots()
    labels = []
    fromwallet = []
    towallet = []
    for fila in data:
        labels.append(str(fila[0])[:cut])
        fromwallet.append(fila[1])
        towallet.append(fila[2])

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, fromwallet, width, label='From', color='red')
    rects2 = ax.bar(x + width/2, towallet, width, label='To', color='green')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('how many transactions')
    ax.set_title('transaction from and to')
    ax.set_xticks(x, labels)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    plt.savefig("src/static/graph/bar_"+id_wallet+".jpg", format="jpg")
    return "src/static/graph/bar_"+id_wallet+".jpg"

def graph_histogram_by_wallet(id_wallet):
    # call Stores Procedures "transsaction_from_to_day_by_wallet"
    num_bins = 11
    fig, ax = plt.subplots()

    y = [115.73956466,112.99148762,108.267019,125.92116686,90.26067825,92.82370635,116.16827658,114.53215499,87.8598281,81.43916344,127.90174814,95.37521144]
    x = ['01/02/2021','01/03/2021','01/04/2021','01/05/2021','01/06/2021','01/07/2021','01/08/2021','01/09/2021','01/10/2021','01/11/2021','01/12/2021','11/12/2021']

    # the histogram of the data
    n, bins, patches = ax.hist(x, num_bins, density=True)

    ax.plot(bins, y, '--')
    ax.set_xlabel('Dates')
    ax.set_ylabel('USD')
    ax.set_title('Histogram of USD in wallet')

    # Tweak spacing to prevent clipping of ylabel
    fig.tight_layout()
    plt.savefig("src/static/graph/histogram_"+id_wallet+".jpg", format="jpg")
    return "src/static/graph/histogram_"+id_wallet+".jpg"


def graph_bars_generated(name):
    fig, ax = plt.subplots()

    fruits = ['apple', 'blueberry', 'cherry', 'orange']
    counts = [40, 100, 30, 55]
    bar_labels = ['red', 'blue', '_red', 'orange']
    bar_colors = ['tab:red', 'tab:blue', 'tab:red', 'tab:orange']

    ax.bar(fruits, counts, label=bar_labels, color=bar_colors)

    ax.set_ylabel('fruit supply')
    ax.set_title('Fruit supply by kind and color')
    ax.legend(title='Fruit color')

    plt.savefig("src/static/graph/bar_"+name+".jpg", format="jpg")
    return "src/static/graph/"+name+".jpg"

def page_not_found(error):
    LogFile("Page not found!, sorry. Error success: False")
    return "<h1>Page not found!, sorry d:-D </h1>", 404


if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404, page_not_found)
    app.run()
