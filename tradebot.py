import gdax,time,os
from datetime import datetime, timedelta

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


    def trade(self):
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


def main():
    client=Gdax("ETH-USD")
    bot = Trader(client)
    bot.gather_data()
    bot.calculate_emas()
    bot.trade()




main()
