from MyMQTT_Reqs import *
from datetime import datetime
import requests

tok = requests.get("http://127.0.0.1:8080/catalog/telegram_token").json()#["telegramToken"]
print(tok)

my_req = MyRequest()

IDs = {
    "user":"Moj",
    "farm":"Farm1",
    "section":"Section1"
}

# _sc = my_req.get_manual_schedul(IDs)
# if _sc["timers"] != []:
#     for period in _sc["timers"]:
#      print(period["days"])
# days_list = my_req.get_days(IDs)
# if datetime.now().weekday() in days_list:
#     print('hi')

# tt = 1680260340000/1000

# datetime.fromtimestamp(tt)
# print(datetime.fromtimestamp(tt).hour)

# print(datetime.now().weekday())


# for key,val in catalog['Farms'][selected_farm]['Sections'].items():
#     section_list.append(val["sectionID"])