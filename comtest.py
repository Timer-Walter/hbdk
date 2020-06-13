import json
import pandas as pd
import time
import talib
from HuobiDMService import HuobiDM


def BuyK(closed,opened,highed,lowed,amounted,ma5,ma60,rsi,id,account_info):
    position = 0

    if ma5[-1] < ma60[-1] and ma5[-2] > ma60[-2]:
        angle = ((ma5[-2] - ma5[-1]) / ma5[-2] + (ma5[-3] - ma5[-2]) / ma5[-3]) * 10000
        if angle>3 and closed[-1]<opened[-1]:
            amountDown = amounted[-1] / float(amounted[-2])
            a = [ma60[-3], ma60[-4], ma60[-5]]
            if amountDown>2 and a == sorted(a):
                position = max(position,0.5)

    if id - account_info['id'] == 1 and closed[-1] < opened[-1] and ma5[-1] < ma60[-1] and 5 > amounted[-1] / float(
            amounted[-2]) > 2:
        position = max(position, 0.6)

    highPointLong = highed[-2] - max(closed[-2], opened[-2])
    highPointLongRate = highPointLong / (highed[-2] - lowed[-2])
    lowPointLong = min(closed[-2], opened[-2]) - lowed[-2]
    lowPointLongRate = lowPointLong / (highed[-2] - lowed[-2])
    if rsi[-2] > 80 and rsi[-2] > rsi[-1] and highPointLong > 30 and highPointLongRate > 0.7 and lowPointLongRate < 0.1:
        position = max(position, 0.3)


    return position


def BuyKoperation(account_info,position,closed,id):
    price = closed[-1] * (1 - 0.001)
    margin_available_use = account_info['margin_available'] * position * 10 * (1 - 0.0003)
    volume_add = margin_available_use / price
    account_info['volume'] += volume_add
    account_info['margin_frozen'] += account_info['margin_available'] * position
    account_info['margin_available'] -= account_info['margin_available'] * position
    account_info['cost_price'] = closed[-1]
    account_info['id'] = id
    account_info['direction'] = 2
    return account_info

def SellKoperation(account_info,position,closed):
    account_info['margin_available'] += account_info['margin_frozen'] * position
    account_info['margin_frozen'] -= account_info['margin_frozen'] * position
    account_info['margin_available'] -= account_info['volume'] * position * closed[-1] * 0.001
    account_info['volume'] -= account_info['volume'] * position
    if position == 1:
        account_info['cost_price'] = 0
        account_info['id'] = 0
        account_info['direction'] = 0
    return account_info

def SellK(closed,opened,amounted,ma5,ma20,ma30,ma60,rsi,id,account_info,macd,signal,hist):
    position = 0

    if (ma5[-1] > ma30[-1] and ma5[-2] <= ma30[-2]) or (ma5[-1] > ma20[-1] and ma5[-2] <= ma20[-2]):
        if closed[-1]>opened[-1]:
            amountUp = amounted[-1] / float(amounted[-2])
            if amountUp>5:
                position = max(position, 1)

    if account_info['cost_price'] != 0 and closed[-1] > account_info['cost_price'] * 1.01:
        position = max(position, 1)

    if account_info['cost_price'] != 0 and closed[-1] < account_info['cost_price'] * 0.96:
        position = max(position, 0.8)

    if account_info['cost_price'] != 0 and closed[-1] < account_info['cost_price'] * 0.97:
        position = max(position, 0.2)

    macdBuy = 0
    if hist[-1] > 0 and macd[-1] > signal[-1] and macd[-2] < signal[-2] and amounted[-1] / amounted[-2] > 3:
        for i in range(1, 6):
            if rsi[-i] < 30:
                macdBuy = 1
                break
    if macdBuy == 1:
        position = max(position, 1)

    if id - account_info['id'] == 1 and amounted[-1] / float(amounted[-2]) > 5:
        position = max(position, 0.2)

    if id - account_info['id'] == 1 and (closed[-1] > ma20[-1] or closed[-1] > ma30[-1] or closed[-1] > ma60[-1]):
        position = max(position, 1)

    return position


def BuyD(closed,opened,highed,lowed,amounted,rsi,ma5,ma10,ma60):
    position = 0
    if ma5[-1] > ma10[-1] and ma5[-2] < ma10[-2]:
        angle = ((ma5[-1] - ma5[-2]) / ma5[-2] + (ma5[-2] - ma5[-3]) / ma5[-3]) * 10000
        kCount = 1
        for i in range(3, 30):
            if (ma5[-i] > ma10[-i]):
                break
            else:
                kCount += 1
        if angle>=8 and kCount>=15 and closed[-1]>opened[-1]:
            position = max(position,0.8)

    lowPointLong = min(closed[-1], opened[-1]) - lowed[-1]
    highPointLong = highed[-1] - max(closed[-1], opened[-1])
    lowPointLongRate = lowPointLong / (highed[-1] - lowed[-1])
    highPointLongRate = highPointLong / (highed[-1] - lowed[-1])
    if lowPointLong > 25 and lowPointLongRate > 0.7 and amounted[-1] / amounted[
        -2] > 3 and ma5[-1] < ma60[-1] and highPointLongRate < 0.1 and rsi[-1] < 30:
        position = max(position, 0.8)

    return position

def SellD(closed,opened,highed,lowed,amounted,rsi,macd,signal,account_info):
    position = 0
    if account_info['cost_price'] != 0 and closed[-1] < account_info['cost_price'] * 0.995:
        position = max(position, 1)

    if rsi[-2] >= 80 and rsi[-2] > rsi[-1]:
        position = max(position, 1)

    if closed[-1] < opened[-1] and amounted[-1] / amounted[-2] >= 6:
        position = max(position, 1)

    if 0 < amounted[-2] / amounted[-3] <= 0.2:
        position = max(position, 1)

    macdSell = 0
    if macd[-1] < signal[-1] and macd[-2] > signal[-2]:
        for i in range(1, 6):
            highPointLong = highed[-i] - max(closed[-i], opened[-i])
            highPointLongRate = highPointLong / (highed[-i] - lowed[-i])
            if highPointLong > 10 and highPointLongRate > 0.6 and rsi[-i] > 70:
                macdSell = 1
                break
    if macdSell == 1:
        position = max(position, 1)
    return position

def BuyDoperation(account_info,position,closed,id):
    price = closed[-1] * 1.001
    margin_available_use = account_info['margin_available'] * position * 20 * (1 - 0.0003)
    volume_add = margin_available_use / price
    account_info['volume'] += volume_add
    account_info['margin_frozen'] += account_info['margin_available'] * position
    account_info['margin_available'] -= account_info['margin_available'] * position
    account_info['cost_price'] = closed[-1]
    account_info['id'] = id
    account_info['direction'] = 1
    return account_info

def SellDoperation(account_info,position,closed):
    account_info['margin_available'] += account_info['margin_frozen'] * position
    account_info['margin_frozen'] -= account_info['margin_frozen'] * position
    account_info['margin_available'] -= account_info['volume'] * position * closed[-1] * 0.001
    account_info['volume'] -= account_info['volume'] * position
    if position == 1:
        account_info['cost_price'] = 0
        account_info['id'] = 0
        account_info['direction'] = 0
    return account_info



with open("test_account_info.json", 'r') as load_f:
    account_info = json.load(load_f)

URL = 'https://www.hbdm.com/'
ACCESS_KEY = ''
SECRET_KEY = ''
count = 0
retryCount =0
while (1):
    try:
        dm = HuobiDM(URL, ACCESS_KEY, SECRET_KEY)
        kline_1min = (dm.get_contract_kline(symbol='BTC_CQ', period='1min'))['data']
    except:
        retryCount += 1
        if(retryCount == 20):
            with open("test_account_info.json", "w") as dump_f:
                json.dump(account_info, dump_f)
            print('connect ws error!')
            break
        continue

    retryCount=0

    kline = (pd.DataFrame.from_dict(kline_1min))[['id', 'close', 'high', 'low', 'open', 'amount']]
    id = kline['id'].values
    id = (id[-1] / 60)
    closed = kline['close'].values
    opened = kline['open'].values
    highed = kline['high'].values
    lowed = kline['low'].values
    amounted = kline['amount'].values
    ma5 = talib.SMA(closed, timeperiod=5)
    ma10 = talib.SMA(closed, timeperiod=10)
    ma20 = talib.SMA(closed, timeperiod=20)
    ma30 = talib.SMA(closed, timeperiod=30)
    ma60 = talib.SMA(closed, timeperiod=60)
    rsi = talib.RSI(closed, timeperiod=14)
    macd, signal, hist = talib.MACD(closed, fastperiod=12, slowperiod=26, signalperiod=9)

    if account_info['direction'] == 2:
        if (account_info['margin_available'] + account_info['margin_frozen'] +
            (account_info['price'] - highed[-1]) * account_info['volume']) <= 0:
            account_info['margin_available'] = 0
            account_info['margin_frozen'] = 0
            account_info['cost_price'] = 0
            account_info['volume'] = 0
            account_info['direction'] =0
        account_info['margin_available'] += (account_info['price'] - closed[-1]) * account_info['volume']
    elif account_info['direction'] == 1:
        if (account_info['margin_available'] + account_info['margin_frozen'] +
            (lowed[-1] - account_info['price']) * account_info['volume']) <= 0:
            account_info['margin_available'] = 0
            account_info['margin_frozen'] = 0
            account_info['cost_price'] = 0
            account_info['volume'] = 0
            account_info['direction'] = 0
        account_info['margin_available'] += (closed[-1] - account_info['price']) * account_info['volume']

    account_info['price'] = closed[-1]

    positionBuyK = BuyK(closed, opened, highed, lowed, amounted, ma5, ma60, rsi, id, account_info)

    positionBuyD = BuyD(closed, opened, highed, lowed, amounted, rsi, ma5, ma10, ma60)

    if positionBuyK > 0 and positionBuyD == 0:
        if account_info['direction'] == 1:
            account_info = SellDoperation(account_info, 1, closed)
        if id != account_info['id'] and account_info['margin_available'] > 0:
            account_info = BuyKoperation(account_info, positionBuyK, closed, id)

    if positionBuyD > 0:
        if account_info['direction'] == 2:
            account_info = SellKoperation(account_info, 1, closed)

        if id != account_info['id'] and account_info['margin_available'] > 0:
            account_info = BuyDoperation(account_info, positionBuyD, closed, id)

    positionSellK = SellK(closed, opened, amounted, ma5, ma20, ma30, ma60, rsi, id, account_info, macd, signal, hist)
    positionSellD = SellD(closed, opened, highed, lowed, amounted, rsi, macd, signal, account_info)

    # sell
    if positionSellK > 0 and account_info['direction'] == 2:
        account_info = SellKoperation(account_info, positionSellK, closed)
    if positionSellD > 0 and account_info['direction'] == 1:
        account_info = SellDoperation(account_info, positionSellD, closed)

    count +=1

    if(count%20==0):
        print(account_info['margin_available'] + account_info['margin_frozen'])
    time.sleep(10)
