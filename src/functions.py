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
from accessdata import sql_querys 
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

now = datetime.datetime.utcnow()
app = Flask(__name__)

conexion = MySQL(app)

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
                if (len(str(field_dict['value'])) >= 18):
                    value = str(field_dict['value'][0:-18]+"."+field_dict['value'][-18])
                else:
                    value = str("0."+field_dict['value'])
                cursor = conexion.connection.cursor()
                sql = str(sql_querys['sql_insert_bep20_token_transfer_events_by_address']).format(field_dict['blockHash'],
                                                                    field_dict['blockNumber'],field_dict['confirmations'],field_dict['contractAddress'],field_dict['cumulativeGasUsed'],field_dict['from'],field_dict['gas'],field_dict['gasPrice'],field_dict['gasUsed'],field_dict['hash'],field_dict['input'],field_dict['nonce'],field_dict['timeStamp'],field_dict['to'],field_dict['tokenDecimal'],field_dict['tokenName'],field_dict['tokenSymbol'],field_dict['transactionIndex'],value)
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

# Function that insert_coins_history data into DB
def insert_coins_history(coin, price, market_cap, date_price, money):
    try:
        coinresp = read_coins_history(coin, date_price, money)
        if (coinresp == None):
            cursor = conexion.connection.cursor()
            sql = str(sql_querys['sql_insert_coins_history_db']).format(coin,
                                                               price, market_cap, date_price,money)
            cursor.execute(sql)
            conexion.connection.commit()
        return None
    except Exception as ex:
        raise ex 

# Function that returns coins_history by coin, date and money
def read_coins_history(coin, date, money):
    try:
        cursor = conexion.connection.cursor()
        sql = str(sql_querys['sql_read_coins_history_db']).format(coin, date, money)
        cursor.execute(sql)
        data = cursor.fetchone()
        if data != None:
            resp = [data[0],data[1],data[2],data[3],data[4]]
            return resp
        else:
            return None
    except Exception as ex:
        raise ex 

# Function that log one txt file by day
def LogFile(text):
    now = datetime.datetime.now()
    try:
        f = open("logs/log_" + now.strftime("%m-%d-%Y")+".txt", "a")
        f.write("\n")
        f.write(now.strftime("%m-%d-%Y-%H-%M-%S")+ " : " + str(text))
        f.close()
        return "log OK"
    except Exception as ex:
        raise ex