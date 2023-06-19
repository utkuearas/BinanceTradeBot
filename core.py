
from binance.um_futures import UMFutures
from listener import listener
import json
import asyncio
import time

MAIN_URL = "https://fapi.binance.com"

class myBot(UMFutures):

    def __init__(self,apiKey,apiSecret,auth,url,telBot = None):
        
        super().__init__(key = apiKey, secret = apiSecret,base_url = url)

        self.telBot = telBot
        self.auth = auth

        self.intervals = ["1m","3m","5m","15m","30m","1h","2h",
        "4h","6h","8h","12h","1d","1d","3d","1w","1M"]

        self.listeners = []

        self.getExchangeInfo()

    async def stopListener(self,index):

        listener = self.listeners[index]

        await listener.stop()

        del listener

        del self.listeners[index]


    def getExchangeInfo(self):

        try:
            self.exchangeInfo = self.exchange_info()
            print("Exchange info loaded successfully")
        except Exception as e:
            print(e)
            time.sleep(3)
            self.getExchangeInfo()
        

    async def startListener(self,symbol,almaParameters,hmaParameter,interval,dolar,margin,stopLoss,stopProfit,message):

        l = listener(self,symbol,almaParameters,hmaParameter,interval,dolar,margin,stopLoss,stopProfit,message)

        self.listeners.append(l)

        await l.runListener(True)

    def testParameter(self,symbol,almaParameters,hmaParameter,interval,dolar,margin,stopLoss,stopProfit):

        l = listener(self,symbol,almaParameters,hmaParameter,interval,dolar,margin,stopLoss,stopProfit)

        l.runBackTest()

    def getPrice(self,symbol):

        data = float(self.mark_price(symbol)["indexPrice"])

        return data


        

