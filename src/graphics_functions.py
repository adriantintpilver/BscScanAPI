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
import matplotlib.dates as mdates
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
    print("len(data) bar: " + str(len(data)))
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
    cursor2.close() 
    plt.savefig("src/static/graph/bar_"+id_wallet+".jpg", format="jpg")
    return "src/static/graph/bar_"+id_wallet+".jpg"

def graph_histogram_by_wallet(id_wallet, money):
    # call Stores Procedures "transactions_bep20_by_day_money_valuated" 
    print("call histogram store: " + str(id_wallet) + " - " + money)
    cursor6 = conexion.connection.cursor()
    sql = str(sql_querys['sql_transsactions_by_day_money_valuated']).format(str(id_wallet), str(money))
    cursor6.execute(sql)
    conexion.connection.commit()          

    data = cursor6.fetchall()
    #print ("data: " + str(data))
    print("len(data) histogram: " + str(len(data)))
    if (len(data) > 10):
        # call Stores Procedures "transactions_bep20_by_month_money_valuated" 
        sql = str(sql_querys['sql_transsactions_by_month_money_valuated']).format(str(id_wallet), str(money))
        print(sql)
        cursor6.execute(sql)
        conexion.connection.commit()   
        data = cursor6.fetchall()
        print("len(data) histogram: " + str(len(data)))

    
    num_bins = len(data)-1
    fig, ax = plt.subplots()
    y = []
    x = []
    for fila in data:
        #print(str(fila[0]) + " - " +str(fila[1]) + " - " +str(fila[2]) + " - " + str(fila[2]-fila[1]))
        y.append(str(fila[2]-fila[1]))
        x.append(fila[0])
    cursor6.close() 
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

def graph_timeline_by_wallet(id_wallet, money):
    # call Stores Procedures "transactions_bep20_by_day_money_valuated" 
    print("call histogram store: " + str(id_wallet) + " - " + money)
    cursor6 = conexion.connection.cursor()
    sql = str(sql_querys['sql_transsactions_by_day_money_valuated']).format(str(id_wallet), str(money))
    cursor6.execute(sql)
    conexion.connection.commit()          

    data = cursor6.fetchall()
    #print ("data: " + str(data))
    print("len(data) timeline : " + str(len(data)))
    if (len(data) > 10000):
        # call Stores Procedures "transactions_bep20_by_month_money_valuated" 
        sql = str(sql_querys['sql_transsactions_by_month_money_valuated']).format(str(id_wallet), str(money))
        print(sql)
        cursor6.execute(sql)
        conexion.connection.commit()   
        data = cursor6.fetchall()
        print("len(data) timeline : " + str(len(data)))

    
    dates = []
    names = []
    for fila in data:
        #print(str(fila[0]) + " - " +str(fila[1]) + " - " +str(fila[2]) + " - " + str(fila[2]-fila[1]))
        if (float(str(fila[1])) > 0 and float(str(fila[2])) > 0):
            names.append(str(fila[2]-fila[1]))
        else:
            if (float(str(fila[2])) > 0):
                names.append(str(fila[2]))
            else:    
                names.append(str(0))
        dates.append(fila[0])
    dates = [datetime.datetime.strptime(d, "%y-%m-%d") for d in dates]

    # Choose some nice levels
    levels = np.tile([-5, 5, -3, 3, -1, 1],
                    int(np.ceil(len(dates)/6)))[:len(dates)]

    # Create figure and plot a stem plot with the date
    fig, ax = plt.subplots(figsize=(8.8, 4), constrained_layout=True)
    ax.set(title="transactions in out from wallet")

    ax.vlines(dates, 0, levels, color="tab:red")  # The vertical stems.
    ax.plot(dates, np.zeros_like(dates), "-o",
            color="k", markerfacecolor="w")  # Baseline and markers on it.

    # annotate lines
    for d, l, r in zip(dates, levels, names):
        ax.annotate(r, xy=(d, l),
                    xytext=(-3, np.sign(l)*3), textcoords="offset points",
                    horizontalalignment="right",
                    verticalalignment="bottom" if l > 0 else "top")

    # format xaxis with 4 month intervals
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    # remove y axis and spines
    ax.yaxis.set_visible(False)
    ax.spines[["left", "top", "right"]].set_visible(False)

    ax.margins(y=0.1)


    #dates = [datetime.datetime.strptime(d, "%y-%M") for d in dates]
    plt.savefig("src/static/graph/timeline_"+id_wallet+".jpg", format="jpg")
    return "src/static/graph/timeline_"+id_wallet+".jpg"



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