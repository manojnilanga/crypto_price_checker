import tkinter as tk
import json
import win32api
import requests
from btcturk_api.client import Client
from threading import Thread
import winsound
import time



coins_list_text_file= open("coins.text","r").read().split("\n")
coins_list_text_file = list(filter(None, coins_list_text_file))


window = tk.Tk()
window.geometry("700x160")
window.title("Crypto Value Checker")
label_threshold = tk.Label(text="Threshold")
label_threshold.place(x=10,y=10)
ent_threshold = tk.Entry(width=5)
ent_threshold.place(x=70,y=10)
label_percentage = tk.Label(text="%")
label_percentage.place(x=100,y=10)

check_box_result =[]
for i in range(0,30):
    check_box_result.append(tk.IntVar())

is_run = True
def start_press():
    global is_run
    is_run = True

    t = Thread(target=start_checking)
    t.start()

def stop_checking():
    global is_run
    is_run = False

def start_alert(alert_message):
    duration = 600  # milliseconds
    freq = 500  # Hz
    winsound.Beep(freq, duration)

    wait_time = 10000
    top = tk.Toplevel()
    top.title('Alert ! from Crypto')
    top.geometry("280x80")
    tk.Message(top, text=alert_message,padx=0, pady=20, width=250).pack()
    top.after(wait_time, top.destroy)

    # win32api.MessageBox(0, alert_message, 'ALERT !')

def start_checking():
    threshold = float(ent_threshold.get())
    coin_list=[]
    for i in range(0,30):
        if(check_box_result[i].get()==1):
            coin_list.append(coins_list_text_file[i])

    while (True):
        if is_run==False:
            break
        for i in range(0, len(coin_list)):
            print("COIN -----> "+coin_list[i])
            max_bid_val = 0
            max_bid_place = "max_place"
            min_ask_val = 1000000000000
            min_ask_place = "min_place"

            # binance
            print("binance ->")
            symbol = coin_list[i] + "USDT"
            response = requests.get('https://api.binance.com/api/v3/ticker/24hr', params={"symbol": symbol})
            binance_dic = json.loads(response.content)
            if "bidPrice" in binance_dic:
                binance_bid_price = float(binance_dic["bidPrice"])
                print("binance_bid_price "+str(binance_bid_price))
                binance_askPrice = float(binance_dic["askPrice"])
                print("binance_askPrice " + str(binance_askPrice))
                max_bid_val = binance_bid_price
                max_bid_place = "binance"
                min_ask_val = binance_askPrice
                min_ask_place = "binance"
            else:
                print(coin_list[i] + " not in binance")

            if is_run == False:
                break

            # btcturk
            print("btcturk ->")
            btcturk_client = Client()
            btcturk_dic = btcturk_client.tick(symbol)
            if len(btcturk_dic) > 0 and "bid" in btcturk_dic[0]:
                turk_bid_price = btcturk_dic[0]["bid"]
                print("turk_bid_price "+str(turk_bid_price))
                turk_ask_price = btcturk_dic[0]["ask"]
                print("turk_ask_price " + str(turk_ask_price))
                if (max_bid_val < turk_bid_price):
                    max_bid_val = turk_bid_price
                    max_bid_place = "btcturk"
                if (min_ask_val > turk_ask_price):
                    min_ask_val = turk_ask_price
                    min_ask_place = "btcturk"
            else:
                print(coin_list[i] + " not in turk")

            if is_run == False:
                break

            # paribu
            print("paribu ->")
            paribu_response = requests.get('https://www.paribu.com/ticker')
            symbol_paribu = coin_list[i] + "_TL"
            symbol_usdt_tl = "USDT_TL"
            paribu_dic = json.loads(paribu_response.content)
            if "lowestAsk" in paribu_dic[symbol_paribu]:
                paribu_bid_price = paribu_dic[symbol_paribu]['highestBid']/paribu_dic[symbol_usdt_tl]['lowestAsk']
                print("paribu_bid_price "+str(paribu_bid_price))
                paribu_ask_price = paribu_dic[symbol_paribu]['lowestAsk'] / paribu_dic[symbol_usdt_tl]['highestBid']
                print("paribu_ask_price " + str(paribu_ask_price))
                if (max_bid_val < paribu_bid_price):
                    max_bid_val = paribu_bid_price
                    max_bid_place = "paribu"
                if (min_ask_val > paribu_ask_price):
                    min_ask_val = paribu_ask_price
                    min_ask_place = "paribu"
            else:
                print(coin_list[i] + " not in paribu")

            if is_run == False:
                break

            current_threshold = (max_bid_val - min_ask_val) * 100 / min_ask_val

            if (current_threshold > threshold):
                alert_message = "Buy " + coin_list[i] + " on " + min_ask_place + " website for " + str(
                    min_ask_val) + " price and Sell on " + max_bid_place + " for " + str(max_bid_val) + " price."
                print(alert_message)
                start_alert(alert_message)
                time.sleep(10)






for i in range(0, 10):
    cbx = tk.Checkbutton(text=coins_list_text_file[i],variable=check_box_result[i])
    cbx.place(x=i*70+10,y=50)
for i in range(10, 20):
    cbx = tk.Checkbutton(text=coins_list_text_file[i],variable=check_box_result[i])
    cbx.place(x=(i-10)*70+10,y=80)
for i in range(20, 30):
    cbx = tk.Checkbutton(text=coins_list_text_file[i],variable=check_box_result[i])
    cbx.place(x=(i-20)*70+10,y=110)

btn_start = tk.Button(text="Start", command=start_press)
btn_start.place(x=150,y=8)
btn_stop = tk.Button(text="Stop",command=stop_checking)
btn_stop.place(x=190,y=8)
window.mainloop()