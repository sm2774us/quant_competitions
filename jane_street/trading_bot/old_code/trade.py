#!/usr/bin/python
from __future__ import print_function

import sys
import socket
import json
import datetime
import time

currentPosition = {}
currentBuyOrders = {}
currentSellOrders = {}

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("production", 25000)) #test-exch-PMPPLUSPLUS
    return s.makefile('rw', 1)

def write(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read(exchange):
    return json.loads(exchange.readline())

def buySingleBond(exchange, output):
    #if 'sell' in output and output['symbol'] == 'BOND' and currentPosition['BOND'] == 0 and len(currentBuyOrders) < 1:
    if currentPosition['BOND'] == 0 and currentBuyOrders['BOND'] == 0:
        sizeToAdd = 30- currentPosition['BOND']
        timeid = str(datetime.datetime.now()).split(" ")[1].replace(":","").split(".")[0]
        print("Placing a single buy order")
        write(exchange, {"type": "add", "order_id": int(timeid) , "symbol": 'BOND', "dir": "BUY", "price": 999, "size": sizeToAdd})
        currentBuyOrders['BOND'] = sizeToAdd
        print(currentBuyOrders['BOND'])
        time.sleep(1)
def sellSingleBond(exchange,output):
    if currentPosition['BOND'] == 30 and currentSellOrders['BOND'] == 0:
        timeid = str(datetime.datetime.now()).split(" ")[1].replace(":","").split(".")[0]
        print("Placing a single sell order")
        write(exchange,{"type": "add" , "order_id": int(timeid) , "symbol" : 'BOND' , "dir": "SELL" , "price": 1001, "size":30 })
        currentSellOrders['BOND'] = 30
        print(currentSellOrders['BOND'])
        time.sleep(1)

def getBuyOrders(output):
    if 'buy' in output and output['symbol'] == 'BOND':
        symbol = str(output['symbol'])
        buyOrders = output['buy']
        bondBuyPricePoints = [997,998,999]
        print(str(output['buy']) + " " + str(output['symbol']))
    return 1

def getSellOrders(output):
    # LOOK for which exchange reads are for sell/buy orders
    if 'sell' in output and output['symbol'] == 'BOND':
        symbol = str(output['symbol'])
        sellOrders = output['sell']
        print("The sell orders are: ")
        print(str(output['sell']))
    return 1

def updatePosition(output):
    if 'position' in output and 'symbols' in output: #checks for the output from the jsonString
        print(json['symbols'])
    return 1
def createPosition(output):
    for symbol in output['symbols']:
        currentPosition[symbol['symbol']]= symbol['position']
        currentSellOrders[symbol['symbol']] = symbol['position']
        currentBuyOrders[symbol['symbol']] = symbol['position']
    return 1
def printPosition():
    print(currentPosition)

def checkFill(output):
        if output['type'] == 'fill':
            print("FILL")
            time.sleep(1)
            if output['dir'] == "BUY":
                currentPosition[output['symbol']] = currentPosition[output['symbol']] + output['size']
                currentBuyOrders["BOND"] = 0
            if output['dir'] == "SELL":
                currentPosition[output['symbol']] = currentPosition[output['symbol']] - output['size']
                currentSellOrders["BOND"] = 0


def main():
    timeid = str(datetime.datetime.now()).split(" ")[1].replace(":","").split(".")[0]
    exchange = connect()
    print(timeid)
    write(exchange, {"type": "hello", "team": "PMPPLUSPLUS"})
    hello_from_exchange = read(exchange)
    print("the exchange replied" , hello_from_exchange,file=sys.stderr)
    createPosition(hello_from_exchange)
    print(currentPosition)
    #write(exchange, {"type": "add", "order_id": int(timeid) , "symbol": 'BOND', "dir": "SELL", "price": 1002, "size": 1})
    while True:
        hello_from_exchange = read(exchange)
        '''getBuyOrders(hello_from_exchange)
        getSellOrders(hello_from_exchange)
        print("The exchange replied:", hello_from_exchange, file=sys.stderr)'''
        buySingleBond(exchange,hello_from_exchange)
        sellSingleBond(exchange,hello_from_exchange)
        #getSellOrders(hello_from_exchange)
        checkFill(hello_from_exchange)
        printPosition()
        #print(hello_from_exchange)
        #time.sleep(3)
if __name__ == "__main__":
    main()
