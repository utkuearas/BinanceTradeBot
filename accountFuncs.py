import asyncio
async def marketEnterOrder(self,symbol,side,quantity):

    try:
        self.bot.new_order(symbol = symbol, side = side, type = "MARKET", quantity = quantity)
    except Exception as e:
        print(e)
        await asyncio.sleep(3)
        await marketEnterOrder(self,symbol,side,quantity)

    return

async def closePosition(self,symbol,side,quantity):

    try:
        self.bot.new_order(symbol = symbol, side = side , type = "MARKET", quantity = quantity,reduceOnly = True)
    except Exception as e:
        print(e)
        await asyncio.sleep(3)
        await closePosition(self,symbol,side,quantity)
    return 



async def stopLossOrder(self,symbol,side,price):

    try:
        order = self.bot.new_order(symbol = symbol, side = side, type = "STOP_MARKET", stopPrice = price, closePosition = True)
        print(order)
    except Exception as e:
        print(e)
        await asyncio.sleep(3)
        await stopLossOrder(self,symbol,side,price)

    return 

async def get_index_klines(self,symbol,interval,limit):

    try:
        return self.bot.index_price_klines(pair = symbol,interval = interval,limit=limit)
    except Exception as e:
        print(e)
        await asyncio.sleep(3)
        return await get_index_klines(self,symbol,interval,limit)
    
async def getTime(self):
    try:
        return self.bot.time()["serverTime"]
    except Exception as e:
        print(e)
        await asyncio.sleep(3)
        return await getTime(self)

async def markPrice(self):

    try:
        return self.bot.mark_price(self.symbol)
    except Exception as e:
        print(e)
        await asyncio.sleep(3)
        return await markPrice(self)

async def stopProfitOrder2(self,symbol,side,price):

    try:
        order = self.bot.new_order(symbol = symbol, side = side, type = "TAKE_PROFIT_MARKET", stopPrice = price, closePosition = True)
        print(order)
    except Exception as e:
        print(e)
        await asyncio.sleep(3)
        await stopLossOrder(self,symbol,side,price)

    return 

async def filterPositionsWithSymbol(self,symbol,force = False):

    try:
        accountData = self.bot.account()
        positions = accountData["positions"]
        position = list(filter(lambda position: position["symbol"] == symbol,positions))[0]

        if position["entryPrice"] == "0.0":
            if force:
                await asyncio.sleep(3)
                await filterPositionsWithSymbol(self,symbol,force)
            else:
                return 0
        return position

    except Exception as e:
        print(e)
        await asyncio.sleep(3)
        await filterPositionsWithSymbol(self,symbol,force)

async def cancelAllOrders(self,symbol):

    try:
        self.bot.cancel_open_orders(symbol = symbol)
    except Exception as e:
        print(e)
        await asyncio.sleep(3)
        await cancelAllOrders(self,symbol)
