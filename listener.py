import asyncio
import math
from re import T
from accountFuncs import marketEnterOrder , stopLossOrder , stopProfitOrder2 , filterPositionsWithSymbol , cancelAllOrders , closePosition , get_index_klines, getTime, markPrice
from mathCalcs import taMath
import pandas as pd
import pathlib


path = str(pathlib.Path().resolve())

class listener:

    def __init__(self,bot,symbol,almaParameters,hmaParameter,interval,dolar,margin,stopLoss,stopProfit,message = None):

        self.message = message
        self.bot = bot
        self.symbol = symbol
        self.almaParameters = almaParameters
        self.hmaParameter = hmaParameter
        self.interval = interval
        self.hmaDatas = []
        self.almaDatas = []
        self.taCalc = taMath()
        self.dolar = dolar
        self.margin = margin
        self.stopLoss = stopLoss
        self.position = False
        self.closeDatas = []
        self.stopListener = False
        self.profitsAndLosses = []
        self.stopProfit = stopProfit
        self.precision = list(filter(lambda symbol: symbol["symbol"] == self.symbol,self.bot.exchangeInfo["symbols"]))[0]["quantityPrecision"]
        self.precisionPrice = list(filter(lambda symbol: symbol["symbol"] == self.symbol,self.bot.exchangeInfo["symbols"]))[0]["pricePrecision"]
        


    async def stop(self):

        self.stopListener = True

        position = await filterPositionsWithSymbol(self,self.symbol)

        try:

            state = self.state

        except:
            state = self.oldState

        if position != 0:

            quantity = abs(float(position["positionAmt"]))

            if state:

                await closePosition(self,self.symbol,"SELL",quantity)

            else:

                await closePosition(self,self.symbol,"BUY",quantity)

            await cancelAllOrders(self,self.symbol)

    async def getDatas(self):

        if "window" in self.almaParameters:
            almaWindow = self.almaParameters["window"] 
        else:
            almaWindow = 9

        if "window" in self.hmaParameter:
            parameter = self.hmaParameter["window"]
            hmaWindow = parameter + int(math.sqrt(parameter)) - 1
        else:
            hmaWindow = 11

        if(almaWindow > hmaWindow):
            limit = almaWindow + 1
        else:
            limit = hmaWindow + 1

        return await get_index_klines(self,self.symbol,self.interval,limit)

    async def runListener(self,first = False):

        if self.stopListener:
            return 
        if first:
            datas = await self.getDatas()
            closeDatas = [float(i[4]) for i in datas][:len(datas) - 1]
            self.closeDatas = closeDatas
            openTime = datas[-1][0]
            closeTime = datas[-1][6]
            currentTime = await getTime(self)
            sleepTime = (closeTime - currentTime) / 1000
            self.interval = (closeTime - openTime) 
            if sleepTime < 0:
                sleepTime += self.interval / 1000 
            self.nextCloseTime = closeTime + self.interval
        else:
            del self.closeDatas[0]
            data = await markPrice(self)
            self.closeDatas.append(float(data["indexPrice"]))
            closeDatas = self.closeDatas

        self.hma = self.taCalc.calcHMA(closeDatas,self.hmaParameter)
        self.alma = self.taCalc.calcALMA(closeDatas,self.almaParameters)

        self.bot.telBot.reply_to(self.message,f"HMA: {self.hma}\nALMA: {self.alma}")

        if self.hma < self.alma:

            if first:
                self.oldState = 0
            else:
                self.state = 0
        else:
            if first:
                self.oldState = 1
            else:
                self.state = 1

        print(self.alma,self.hma)
        print()

        if(first):
            await asyncio.sleep(sleepTime)
            return await self.runListener()

        if self.state != self.oldState:

            self.oldState = self.state
            await self.positionTask()

        
        currentTime = await getTime(self)
        sleepTime = (self.nextCloseTime - currentTime) / 1000
        if sleepTime < 0:
            sleepTime += self.interval / 1000 
        self.nextCloseTime += self.interval

        await asyncio.sleep(sleepTime)
        return await self.runListener()

    async def positionTask(self):

        await cancelAllOrders(self,self.symbol)

        if self.position:

            position = await filterPositionsWithSymbol(self,self.symbol)

            if position != 0:

                quantity = abs(float(position["positionAmt"]))

                if self.state:

                    await closePosition(self,self.symbol,"BUY",quantity)

                else:

                    await closePosition(self,self.symbol,"SELL",quantity)

                await cancelAllOrders(self,self.symbol)

            else:

                self.position = False

        if self.state:

            print("Long Position")
            self.bot.telBot.reply_to(self.message,"Long position has been opened")

            quantity = math.floor(self.dolar * self.margin / (float(self.closeDatas[-1])) * 10 ** self.precision) / 10 ** self.precision
            await marketEnterOrder(self,self.symbol,"BUY",quantity)

            await asyncio.sleep(3)

            position = await filterPositionsWithSymbol(self,self.symbol,True)
            entryPrice = float(position["entryPrice"])

            stopPrice = round(entryPrice * (100 - self.stopLoss) / 100 * 10 ** self.precisionPrice) / 10 ** self.precisionPrice
            stopProfitPrice = round(entryPrice * (100 + self.stopProfit) / 100 * 10 ** self.precisionPrice) / 10 ** self.precisionPrice

            await stopLossOrder(self,self.symbol,"SELL",stopPrice)
            await asyncio.sleep(3)
            await stopProfitOrder2(self,self.symbol,"SELL",stopProfitPrice)

        else:

            print("Short Position")

            self.bot.telBot.reply_to(self.message,"Short position has been opened")

            quantity = math.floor(self.dolar * self.margin / (float(self.closeDatas[-1])) * 10 ** self.precision) / 10 ** self.precision
            await marketEnterOrder(self,self.symbol,"SELL",quantity)

            await asyncio.sleep(3)

            position = await filterPositionsWithSymbol(self,self.symbol,True)
            entryPrice = float(position["entryPrice"])

            stopPrice = round(entryPrice * (100 + self.stopLoss) / 100 * 10 ** self.precisionPrice) / 10 ** self.precisionPrice
            stopProfitPrice = round(entryPrice * (100 - self.stopProfit) / 100 * 10 ** self.precisionPrice) / 10 ** self.precisionPrice

            await stopLossOrder(self,self.symbol,"BUY",stopPrice)
            await asyncio.sleep(3)
            await stopProfitOrder2(self,self.symbol,"BUY",stopProfitPrice)

        self.position = True

            

        




