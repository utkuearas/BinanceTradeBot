import telebot
import sys 
import os
import json
import asyncio
from threading import Thread
from core import myBot

#MAIN_URL = "https://testnet.binancefuture.com"
MAIN_URL = "https://fapi.binance.com"

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)



TOKEN = "YOUR TOKEN"
telBot = telebot.TeleBot(TOKEN)


try:
    file = open(current+"/data/account.txt","r")
    accountData = json.loads(file.read())
    print(accountData)
    telBot.biAccount = myBot(accountData["api"],accountData["secret"],accountData["telAccount"],MAIN_URL,telBot)
    print("Binance account is loaded successfully")
except Exception as e:
    print(e)


telBot.first = True

@telBot.message_handler(commands=['start'])
def startCommand(message):
    
    if telBot.first:
        telBot.first = False
        userName = message.from_user.first_name
        return telBot.reply_to(message, f'Welcome {userName}')

    if telBot.biAccount.auth != message.from_user.username:
        return 

    req = message.text.split()

    if len(req) != 9:
        return telBot.reply_to(message, "Wrong request")
    
    symbol = req[1]
    interval = req[2]

    if interval not in telBot.biAccount.intervals:
        return telBot.reply_to(message, "Wrong request")

    almaParams = req[3].split(',')
    for param in almaParams:
        try:
            float(param)
        except:
            return telBot.reply_to(message, "Wrong request")

    almaParameters = {"window" : int(almaParams[0]) , "offset": float(almaParams[1]), "sigma": int(almaParams[2])}

    hmaParam = req[4]
    if hmaParam.isdigit() == False:
        return telBot.reply_to(message, "Wrong request")

    hmaParam = {"window":int(hmaParam)}

    dolar = req[5]
    try:
        dolar = float(dolar)
    except:
        return telBot.reply_to(message, "Wrong request")

    margin = req[6]
    try:
        margin = float(margin)
    except:
        return telBot.reply_to(message, "Wrong request")

    stopLoss = req[7]
    try:
        stopLoss = float(stopLoss)
    except:
        return telBot.reply_to(message, "Wrong request")

    stopProfit = req[8]
    try:
        stopProfit = float(stopProfit)
    except:
        return telBot.reply_to(message, "Wrong request")

    telBot.reply_to(message, "Listener is working")
    
    currentPrice = telBot.biAccount.getPrice(symbol)

    telBot.reply_to(message, f'Current Price:\n{symbol} : {currentPrice}')

    arg = telBot.biAccount.startListener(symbol,almaParameters,hmaParam,interval,dolar,margin,stopLoss,stopProfit,message)

    task = Thread(target = asyncio.run , args=[arg])
    task.start()

    

@telBot.message_handler(commands=['listeners'])
def startCommand(message):

    listeners = telBot.biAccount.listeners

    messageContent = ""
    if len(listeners) == 0:
        messageContent = "There are no listeners"

    for index,listener in enumerate(listeners):

        symbol = listener.symbol
        messageContent += f"{index+1}) {symbol}"

    telBot.reply_to(message, messageContent)

@telBot.message_handler(commands=['stop'])
def startCommand(message):

    split = message.text.split()

    if len(split) != 2:
        return telBot.reply_to(message, "Wrong request")
    
    index = int(split[1]) - 1

    asyncio.run(telBot.biAccount.stopListener(index))

    telBot.reply_to(message, "Successfully stopped and closed positions")


@telBot.message_handler(commands=['create'])
def startCommand(message):

    userName = message.from_user.username

    try:
        if telBot.biAccount.auth != userName:
            return
    except:
        print("DEBUG")

    req = message.text.split()
    if len(req) != 3:
        telBot.reply_to(message, "Wrong request")

    api = req[1]
    secret = req[2]

    file = open(current+"/data/account.txt","w")
    
    file.write("{"+"\"api\" : \"{}\", \"secret\" : \"{}\", \"telAccount\" : \"{}\"".format(api,secret,userName)+"}")
    file.close()

    biBot = myBot(api,secret,userName,MAIN_URL,telBot)
    telBot.biAccount = biBot

    telBot.reply_to(message, "Account has been created")

telBot.infinity_polling()