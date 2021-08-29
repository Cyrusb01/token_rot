"""
In Backtesting_stuff we use backtesting.py to optomize the indivual EMAs for each asset, but in this script we are going to build a backtesting engine to 
see how the token rotation works all together. 
"""
from helpers import data_fetch_and_format
import pandas as pd
import talib


optomized_vals = {}
optomized_vals['btc'] = [5, 33, 101]
optomized_vals['eth'] = [5, 32, 103]
optomized_vals['ada'] = [3, 53, 101]
optomized_vals['dot'] = [2, 3, 100]
optomized_vals['sol'] = [20, 50, 100]
optomized_vals['uni'] = [15, 69, 100]
optomized_vals['link'] = [13, 27, 100]
optomized_vals['ltc'] = [6, 56, 100]
optomized_vals['matic'] = [22, 23, 100]
optomized_vals['xlm'] = [6, 56, 100]
optomized_vals['aave'] = [2, 3, 100]


data = "dataframe with all datas"

asset_list = ['ltc', 'btc', 'aave', 'ada', 'dot', 'eth', 'sol', 'uni', 'xlm']

df_dict = {}

data = pd.DataFrame()

#create a dict with the asset mapped to its data
for asset in asset_list:
    df = pd.read_csv(f"datafiles/{asset}.csv")
    df["N1"] = talib.EMA(df["Close"], timeperiod=optomized_vals[asset][0])
    df["N2"] = talib.EMA(df["Close"], timeperiod=optomized_vals[asset][1])
    df["Power"] = df["N1"] / df["N2"]
    df.columns = ["Date", "Open", "High", "Low", "Close", "Volume", "N1", "N2", "Power"]
    
    df["Date"] = pd.to_datetime(df["Date"], infer_datetime_format = True)
    df["Date"] = df["Date"].dt.strftime('%m/%d/%Y')
    df = df[["Date","Close", "Power"]]
    df = df.rename(columns={"Close":f"Close-{asset}", "Power":f"Power-{asset}"})
    df = df.set_index("Date")
    data = pd.merge(data, df, left_index=True, right_index=True, how='outer')

#huge dataframe with all the closes and powers
data.index = pd.to_datetime(data.index, infer_datetime_format = True)
data = data.sort_index()
data = data.dropna()


asset_power_ratio = {}
asset_allocations = {'ltc':0, 'btc':0, 'aave':0, 'ada':0, 'dot':0, 'eth':0, 'link':0, 'matic':0, 'sol':0, 'uni':0, 'xlm':0}
days_since_trade = 10
cash = 1000
hold_btc = (1000 / data["Close-btc"][0]) * data["Close-btc"][-1]
hold_eth = (1000 / data["Close-eth"][0]) * data["Close-eth"][-1]
hold_ltc = (1000 / data["Close-ltc"][0]) * data["Close-ltc"][-1]
hold_uni = (1000 / data["Close-uni"][0]) * data["Close-uni"][-1]
hold_xlm = (1000 / data["Close-xlm"][0]) * data["Close-xlm"][-1]
# hold_matic = (1000 / data["Close-matic"][0]) * data["Close-matic"][-1]
for i in range(len(data)):
    #make dictionary of each power ratios
    for asset in asset_list: 
        asset_power_ratio[asset] = 100*data[f"Power-{asset}"][i]/optomized_vals[asset][2]
        asset_power_ratio[asset] = asset_power_ratio[asset] - 1  #Want the ones closest to thier optimization number, 0 is the best
        if asset_power_ratio[asset] < 0:
            asset_power_ratio[asset] = 10 #we dont want anything negative, so if it is we will make it large to make sorting easier

    
    #sort power ratios 
    sorted_dict = dict(sorted(asset_power_ratio.items(), key=lambda item: item[1]))
    list_dict = list(sorted_dict)
    
    #print(sorted_dict)
    positive_top = []
    for asset in list_dict[:5]:
        if asset_power_ratio[asset] >= 0:
            positive_top.append(asset)

    #print(positive_top)
    #get the top 5 and check if they are all positive
    # positive_top = []
    # for asset in list_dict[6:]:
    #     if asset_power_ratio[asset] > 1:
    #         positive_top.append(asset)
    
    #Every ten days we need to revaluate which are the assets we want to invest in 
    if days_since_trade == 10:
        number_of_assets_investing = 5
        


        #Selling 
        print("Holding: ", end = "")
        for asset in asset_list:
            #if we already own it from last week, and its top again, just keep  (MAYBE sell so we can distribute profits more evenly?)
            if asset_allocations[asset] != 0 and asset in positive_top:
                print(asset, " ", end = "")
                number_of_assets_investing -= 1 #now we are only investing in one less newer asset
                positive_top.remove(asset)
            
            elif asset_allocations[asset] != 0:
                cash += asset_allocations[asset] * data[f"Close-{asset}"][i]
                asset_allocations[asset] = 0
        print()


        print("Investing:", positive_top)
        
        if number_of_assets_investing != 0:
            buy_amount = cash/number_of_assets_investing
        else:
            buy_amount = 0
        for asset in positive_top:
            asset_allocations[asset] = buy_amount / data[f"Close-{asset}"][i]
            cash -= buy_amount

        hypo_cash = 0
        for asset in asset_list:
            hypo_cash += asset_allocations[asset] * data[f"Close-{asset}"][i] 
        print("Cash Value: ", hypo_cash + cash)
        print('\n')
        days_since_trade = 0
    days_since_trade += 1 


print("BTC-Hold: ", hold_btc)
print("ETH-Hold: ", hold_eth)
print("LTC-Hold: ", hold_ltc)
print("UNI-Hold: ", hold_uni)
print("XLM-Hold: ", hold_xlm)
# print("MATIC-Hold: ", hold_matic)

