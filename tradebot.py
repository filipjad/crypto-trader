import gdax,time,os
from datetime import datetime, timedelta
import requests
import json

class Gdax():
    def __init__(self,pair):
        self.client=gdax.PublicClient()
        self.trading_pair=pair

    ### Fetches current price for the given trading-pair ###
    def getPrice(self):
        return float(self.client.get_product_ticker(product_id=self.trading_pair)['price'])

    ### API is bugged out... don't use!  ###
    def getHistoricalPrice(self,start):
        now = datetime.now()
        start = datetime.now() - timedelta(days=start)
        #minutes=60*minutes
        return self.client.get_product_historic_rates(self.trading_pair,start=start.isoformat(),end=now.isoformat(), granularity=60*60*24)

class Trader():
    def __init__(self,client):
        self.past_prices=[]
        self.ema=0

        self.shortEma=0
        self.longEma=0
        self.shortEmaIsLower=False

        self.weight=0
        self.client=client
        self.fiat_balance=1000
        self.eth_balance=0


    def gather_data(self):
        os.system("say 'Initiating systems'")
        os.system("say 'Please wait while I fetch crypto data'")
        while len(self.past_prices)<10:
            time.sleep(60)
            self.past_prices.append(self.client.getPrice())
        os.system("say 'I am done Mother fucker let us trade some Ethereum'")
        print(self.past_prices)

    def fetch_data(self,long,short):
        resp = requests.get("https://etherchain.org/api/statistics/price")
        robj = json.loads(resp.text)

        nrOfDays = long
        shortDays = short
        data = robj["data"][-nrOfDays*24:] #Get the last nrOfDays elements in list

        nrOfElements = len(data)

        longEma=[]  #Length of list 200 days*24
        shortEma=[] #Length of list 50 days*24

        for i in range(nrOfElements):
            element = data[i]
            longEma.append(element["usd"])
            if(i>=shortDays*24):
                shortEma.append(element["usd"])

        return shortEma, longEma

    def calculate_emas(self,prices):
        window = len(prices)
        weight = 2/(window+1)
        ### Reversed list or not? ###
        for i in range(window):
            if i == 0:
                ema=prices[i]
            else:
                ema = ((prices[i]-ema)*weight)+ema
        return ema

    def buy(self,price,amount):
        self.eth_balance = self.eth_balance + amount/price
        self.fiat_balance = self.fiat_balance - amount

    def sell(self,current_price):
        self.fiat_balance= self.fiat_balance + current_price * self.eth_balance
        self.eth_balance=0

    def setShortEma(self, ema):
        self.shortEma = ema

    def setLongEma(self, ema):
        self.longEma = ema

    def setShortEmaIsLower(self, bool):
        self.shortEmaIsLower=bool

    #Old trade func
    def minuteTrade(self):
        active_trade = False
        i = 0
        while (i==0):
            time.sleep(60)
            current_price = self.client.getPrice()
            self.ema = ((current_price-self.ema)*self.weight)+self.ema
            if (current_price>self.ema):
                self.buy(current_price,10)
                print("BUY")
                active_trade = True
            if (current_price<self.ema and active_trade):
                print("SELL")
                self.sell(current_price)
                print(self.fiat_balance/1000)
                active_trade = False

    def trade(self,interval):
        print("init trading")
        active_trade = False
        init=True

        while(True):
            time.sleep(interval)
            shortEmaPrices, longEmaPrices = self.fetch_data()
            shortEma = self.calculate_emas(shortEmaPrices)
            longEma = self.calculate_emas(longEmaPrices)

            if (init):
                self.setShortEma(shortEma)
                self.setLongEma(longEma)

                if(shortEma<longEma):
                    self.setShortEmaIsLower(True)
                else:
                    self.setShortEmaIsLower(False)

                init=False

            #No trade is made on the first round
            else:
                if(self.heuristicFunc(shortEma,longEma)== 1):
                    self.buy(current_price,10)
                    print("BUY")
                    active_trade = True
                elif(self.heuristicFunc(shortEma,longEma)== -1 and active_trade):
                    print("SELL")
                    self.sell(current_price)
                    print(self.fiat_balance/1000)
                    active_trade = False

    def heuristicFunc(self,newShortEma,newLongEma):
        #If shortEma crosses longEma from beneath = BUY
        heuristic=0
        if(newShortEma>newLongEma and self.shortEmaIsLower==True):
            heuristic=1

        #If shortEma crosses longEma from above = SELL
        elif(newLongEma>newShortEma and self.shortEmaIsLower==False):
            heuristic=-1

        self.setShortEma(newShortEma)
        self.setLongEma(newLongEma)
        if(newShortEma<newLongEma):
            self.setShortEmaIsLower(True)
        else:
            self.setShortEmaIsLower(False)

        print("Heuristic=",heuristic)
        return heuristic


def main():
    client=Gdax("ETH-USD")
    bot = Trader(client)
    time = int(input("Please enter trading interval: "))
    bot.trade(time)




main()
