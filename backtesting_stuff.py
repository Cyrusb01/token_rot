from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA, GOOG
import pandas as pd
import talib
import tqdm 
from helpers import EMA_Backtesting
import csv

asset_list = ['btc', 'aave', 'ada', 'dot', 'eth', 'sol', 'uni', 'xlm']


#Fetch data from csv and then format is nicely

# print(data)




class tok_rot_tester (Strategy):
    """
    This strategy is meant to test the token rotation on how long each of the assets ema's should be. The variables in this 
    will be the ema length, and how long the asset should be held for. 
    """
    
    n1 = 5
    n2 = 33
    buy_number = 100
    hold_length = 10
    days_since_buy = 0

    def init(self):
        super().init()
        self.ema1 = self.I(EMA_Backtesting, self.data.Close, self.n1)
        self.ema2 = self.I(EMA_Backtesting, self.data.Close, self.n2)
        self.power = (
            100 * self.ema1 / self.ema2
        )  # how fast has the short ema gone above the longer one
        

    def next(self):
        super().next()
        if self.power > self.buy_number and not self.position.is_long:
            self.buy(size = .99) #buy 99% of current liquidity
            #print("Bought")
        
        if self.position.is_long:
            self.days_since_buy += 1

        if self.days_since_buy == self.hold_length and self.position.is_long:
            self.sell()
            #print("Sold")
            self.days_since_buy = 0
        #print(self.days_since_buy)
        

# bt = Backtest(data, tok_rot_tester,
#               cash=1000000, commission=.002,
#               exclusive_orders=True)


years = ['2017-01-01', '2018-01-01', '2019-01-01', '2020-01-01', '2021-01-01', ]
optimization_type = "Sharpe Ratio"
titles = ['In Sample', 'Optimized For', 'Sharpe', 'Win Rate', 'Return', 'Full-Sharpe',	'Full-Win Rate', 'Full-Return', "N1", "N2", "Buy Number", "Hold Number"]


for asset in asset_list:
    data = pd.read_csv(f"datafiles/{asset}.csv")
    data.columns = ['Date', 'Open', "High", "Low", "Close", "Volume"]
    data['Date'] = pd.to_datetime(data['Date'])
    data = data.set_index(data["Date"])
    data = data.drop("Date", axis = 1)
    with open('datafiles/Optimization.csv', 'a', newline= '') as f:
        writer = csv.writer(f) 
        writer.writerow([asset])
        writer.writerow(titles)
        for i in range(len(years)-1):
            #Cut the data into years
            in_sample = data[data.index > years[i]]
            in_sample = in_sample[in_sample.index < years[i+1]]
            if in_sample.empty:
                continue
            print(asset, ": ", years[i])
            #Run strategy with in sample data so we can optimize 
            bt = Backtest(in_sample, tok_rot_tester,
                cash=1000000, commission=.002,
                exclusive_orders=True)

            #Optimize
            stats = bt.optimize(
                        n1 = range(10, 70, 2),
                        n2 = range(20, 80, 2),
                        buy_number = range(100, 110, 1),
                        hold_length = range(9, 10, 1),
                        maximize=optimization_type,
                        constraint=lambda param: param.n1 < param.n2
            )
            #Start creating the csv row
            row = []
            row.append(years[i])
            row.append(optimization_type)
            row.append(stats['Sharpe Ratio'])
            row.append(stats['Win Rate [%]'])
            row.append(stats['Return [%]'])
            
            #This Chunk gets the optimized numbers and puts them into a list optimized nums so we can later use them 
            optimized_nums = str(stats['_strategy']).split(',')
            for i in range(len(optimized_nums)):
                optimized_nums[i] = optimized_nums[i][optimized_nums[i].index('=')+1:]
                optimized_nums[i] = optimized_nums[i].replace(')', '')
                optimized_nums[i] = int(optimized_nums[i])
            
            
            #New strategy with optimized numbers and then we backtest on the full dataset
            class tok_rot_tester_opt (Strategy):
                """
                This strategy is meant to test the token rotation on how long each of the assets ema's should be. The variables in this 
                will be the ema length, and how long the asset should be held for. 
                THIS ONE IS MEANT TO USE OPTIMIZED VALUES TO SEE HOW THEY DO WITH THE FULL DATASET
                """
        
                n1 = optimized_nums[0]
                n2 = optimized_nums[1]
                buy_number = optimized_nums[2]
                hold_length = optimized_nums[3]
                days_since_buy = 0

                def init(self):
                    super().init()
                    self.ema1 = self.I(EMA_Backtesting, self.data.Close, self.n1)
                    self.ema2 = self.I(EMA_Backtesting, self.data.Close, self.n2)
                    self.power = (
                        100 * self.ema1 / self.ema2
                    )  # how fast has the short ema gone above the longer one
                    

                def next(self):
                    super().next()
                    if self.power > self.buy_number and not self.position.is_long:
                        self.buy(size = .99) #buy 99% of current liquidity
                    
                    
                    if self.position.is_long:
                        self.days_since_buy += 1

                    if self.days_since_buy == self.hold_length and self.position.is_long:
                        self.sell()
                        self.days_since_buy = 0
            
            bt_opt = Backtest(data, tok_rot_tester_opt,
                cash=1000000, commission=.002,
                exclusive_orders=True)
            
            output_opt = bt_opt.run()
            row.append(output_opt['Sharpe Ratio'])
            row.append(output_opt['Win Rate [%]'])
            row.append(output_opt['Return [%]'])

            row.append(optimized_nums[0])
            row.append(optimized_nums[1])
            row.append(optimized_nums[2])
            row.append(optimized_nums[3])
            writer.writerow(row)
        writer.writerow("")


            
        




print(stats)
print(stats['SQN'])


# print(stats)
# print(stats['_strategy'])














# stats_skopt, heatmap, optimize_result = bt.optimize(
#     n1=[10, 100],      # Note: For method="skopt", we
#     n2=[20, 200],      # only need interval end-points
#     buy_number = [100, 150],
#     hold_length = [1, 15],
#     constraint=lambda param: param.n1 < param.n2,
#     maximize='Equity Final [$]',
#     method='skopt',
#     max_tries=1000,
#     random_state=0,
#     return_heatmap=True,
#     return_optimization=True)
"""
OPTIMIZED CLASS VARIABLES
-------------------------

BTC 
n1 = 5
n2 = 33
buy_number = 101
hold_length = 10
-------------------------

ETH 
n1 = 5
n2 = 32
buy_number = 103
hold_length = 10
------------------------

ADA
n1 = 3
n2 = 53
buy_number = 101
hold_length = 8
------------------------

DOT 
n1 = 2
n2 = 3
buy_number = 100
hold_length = 10
------------------------

SOL
n1 = 20
n2 = 50
buy_number = 100
hold_length = 10
------------------------

UNI 
n1 = 15
n2 = 69
buy_number = 100
hold_length = 10
------------------------

LINK  #NOT GOOD, LOW SQN AND LESS THAN BUY AND HOLD
n1 = 13
n2 = 27
buy_number = 100
hold_length = 10
------------------------

LTC 
n1 = 6
n2 = 56
buy_number = 100
hold_length = 10
------------------------

MATIC #NOT GOOD 
n1 = 22
n2 = 23
buy_number = 100
hold_length = 10 
------------------------

XLM  #less than 50% win rate
n1 = 6
n2 = 56
buy_number = 100
hold_length = 9
------------------------

AAVE
n1 = 2
n2 = 3
buy_number = 100
hold_length = 10
------------------------

AXS
------------------------

"""