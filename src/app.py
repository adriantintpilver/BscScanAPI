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
    return render_template('events_by_address.html', id_wallet = id_wallet, image_name = image_name)

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

    print("data: " + str(data))

    fig, ax = plt.subplots()

    fruits = ['apple', 'blueberry', 'cherry', 'orange']
    counts = [40, 100, 30, 55]
    bar_labels = ['red', 'blue', '_red', 'orange']
    bar_colors = ['tab:red', 'tab:blue', 'tab:red', 'tab:orange']

    ax.bar(fruits, counts, label=bar_labels, color=bar_colors)

    ax.set_ylabel('fruit supply')
    ax.set_title('Fruit supply by kind and color')
    ax.legend(title='Fruit color')

    plt.savefig("src/static/graph/bar_"+id_wallet+".jpg", format="jpg")
    return "src/static/graph/"+id_wallet+".jpg"

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
