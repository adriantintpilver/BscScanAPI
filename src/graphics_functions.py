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

now = datetime.datetime.utcnow()
app = Flask(__name__)

conexion = MySQL(app)


###### GRAPHICS FUNCTIONS ######

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
    n, bins, patches = ax.hist(x, num_bins, density=True, )

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