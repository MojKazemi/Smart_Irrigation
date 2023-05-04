import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import time
from MyMQTT_Reqs import MyMQTT, MyRequest
import pprint


class IrrigationBot:

    def __init__(self, broker, port):
        self.my_req = MyRequest()
        _setting = self.my_req.get_telegram_setting()
        self.tokenBot=_setting["telegramToken"]      
        self.list_chat_id = _setting["chat_ids"]
        self.bot = telepot.Bot(self.tokenBot)
        self.init_dict = {}
        for chat_id in self.list_chat_id:
            self.init_dict[chat_id] = {'Firstmsg':False,
                                        'passcheck':False,
                                        'usercheck':False,
                                        'userID':None,
                                        'IDs':{'farm': None,
                                                'section': None},
                                        'user_dict':{}}
        MessageLoop(self.bot, {'chat': self.on_chat_message, 
                                'callback_query': self.on_callback_query}).run_as_thread()
        
        self.client = MyMQTT("telegramBotIoT", broker, port, self)
        self.client.start()
        self.topic = f'{_setting["alarm_topics"]}/#'
        self.client.mySubscribe(self.topic)

    def notify(self, topic, message):
        msg=json.loads(message)
                # self.telegram_message={"alert":"", "farm":"", "section":""}
        alert = msg["alert"]
        farm = msg["farm"]
        section = msg["section"]
        tosend=f"      ⚠️⚠️⚠️ \n ❌❌❌ ATTENTION!!! ❌❌❌\n{alert},\n ➡️   In Farm: {farm}\n ➡️   Section: {section}"
        
        for chat_id, val in self.init_dict.items():
            if val['usercheck']:
                if farm in val['user_dict']['farm_list']:
                    self.bot.sendMessage(chat_id, text=tosend)

    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        if content_type != 'text':
            self.bot.sendMessage(chat_ID, text='Your command is not correct')
        else:
            print(f"Message from: {msg['from']['username']} with chat ID: {chat_ID} the context is: {msg['text']}")
                        
            if chat_ID in self.list_chat_id:
                
                if msg['text'] == "/start":
                    self.start_command(chat_ID)
                    
                elif self.init_dict[chat_ID]['usercheck'] == False:
                    user = msg['text']
                    self.check_user(chat_ID, user)
                    
                elif self.init_dict[chat_ID]['usercheck'] == True and self.init_dict[chat_ID]['passcheck'] == False:

                    if msg['text'] == self.init_dict[chat_ID]['user_dict']['pass']:
                        self.init_dict[chat_ID]['passcheck'] = True
                        self.select_farm(chat_ID)
                    else:
                        self.bot.sendMessage(chat_ID, 'Your password is not correct please try again')
                        
                else:
                    self.command_control(msg['text'], chat_ID)
                    
            else:
                self.bot.sendMessage(chat_ID, text='You are not allow to access to the Smart Irrigation bot please send an email to the admin\n s289864@studenti.polito.it')

    def start_command(self, chat_ID):
        if self.init_dict[chat_ID]['Firstmsg'] ==False:
            self.init_dict[chat_ID]['Firstmsg'] = True
            self.bot.sendMessage(chat_ID, text="Welcome to Irrigation Bot \n Please insert your username: ")
        elif self.init_dict[chat_ID]['passcheck'] == False and self.init_dict[chat_ID]['usercheck'] == True:
            self.bot.sendMessage(chat_ID,'Your password is not correct please try again')
        elif self.init_dict[chat_ID]['usercheck'] == False:
            self.bot.sendMessage(chat_ID,'Please insert your username')
        else:
            self.bot.sendMessage(chat_ID, 'You are already logged in')

    def check_user(self, chat_ID, user):
        users_catalog = self.my_req.get_catalog()
        for _user in users_catalog.values():
            for val in _user.values():
                if user == val['userID']:
                    self.init_dict[chat_ID]['user_dict'] = val
                    self.init_dict[chat_ID]['userID'] = user
                    self.init_dict[chat_ID]['usercheck'] = True
                    self.bot.sendMessage(chat_ID, 'Please insert your password:')
        
        if not self.init_dict[chat_ID]['usercheck']:
            self.bot.sendMessage(chat_ID, 'Your username is not correct please try again')

    def select_farm(self, chat_ID):
        farm_buttons = []
        for farm in self.init_dict[chat_ID]['user_dict']['farm_list']:
            farm_buttons.append(InlineKeyboardButton(text=f'{farm} ✅', callback_data=f'selectfarm-{farm}'))

        buttons = [farm_buttons]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        self.bot.sendMessage(chat_ID, text='Select the farm', reply_markup=keyboard)

    def on_callback_query(self,msg):
        query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')
        
        if 'selectfarm-' in query_data:
            farm = query_data.split('-')[1]
            self.init_dict[chat_ID]['IDs']['farm'] = farm

            farm_dict = self.my_req.get_catalog_farm()

            sec_buttons = []
            for val in farm_dict['Farms'].values():
                if val['farmID'] == farm:
                    for val_sec in val['Sections'].values():
                        _secId = val_sec['sectionID']
                        sec_buttons.append(InlineKeyboardButton(text=f'{_secId} 🧩', callback_data=f'selectsection-{_secId}'))
           
            buttons = [sec_buttons]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text='Select the Section', reply_markup=keyboard)

        elif 'selectsection-' in query_data:
            section = query_data.split('-')[1]
            self.init_dict[chat_ID]['IDs']['section'] = section

            self.main_buttons(chat_ID)
            
        else:
            self.handler_level2(query_data, chat_ID)

    def command_control(self, message, chat_ID):

        if message == "/panel":
            if self.init_dict[chat_ID]['IDs']['section']:
                self.main_buttons(chat_ID)
            else:
                self.select_farm(chat_ID)
                

        elif message =="/logout":
            self.init_dict[chat_ID] = {'Firstmsg':True,
                                        'passcheck':False,
                                        'usercheck':False,
                                        'userID':None,
                                        'IDs':{'farm': None,
                                                'section': None},
                                        'user_dict':{}}
            self.bot.sendMessage(chat_ID, text="You are log out")

        else:
            self.bot.sendMessage(chat_ID, text="Command not supported")
    
    def main_buttons(self, chat_ID):
        
        buttons = [
            [InlineKeyboardButton(text=f'Monitor 🖥', callback_data=f'monitor')], 
            [InlineKeyboardButton(text=f'Switch PUMP 🕹', callback_data=f'switch_pump'),
            InlineKeyboardButton(text=f'Change Mode 🖲', callback_data=f'change_mode')]
                    ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        self.bot.sendMessage(chat_ID, text='What do you want to do', reply_markup=keyboard)
        
    def monitor_buttons(self, chat_ID):
        buttons = [
            [InlineKeyboardButton(text=f'Pump Status', callback_data=f'pump_status')], 
            [InlineKeyboardButton(text=f'Sensor Live', callback_data=f'sensorlive'),
            InlineKeyboardButton(text=f'Threshold', callback_data=f'thresh')],
            [InlineKeyboardButton(text=f'Control Mode', callback_data=f'control_mode')]
                    ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        self.bot.sendMessage(chat_ID, text='What do you want to do', reply_markup=keyboard)

    def handler_level2(self, query_data, chat_ID):

        if query_data == 'monitor':
            self.monitor_buttons(chat_ID)

        elif query_data == 'pump_status':
            pump_status = self.my_req.get_status(self.init_dict[chat_ID]['IDs'])
            self.bot.sendMessage(
                chat_ID,
                text=f"The pump staus of {self.init_dict[chat_ID]['IDs']['farm']}/{self.init_dict[chat_ID]['IDs']['section']}is:\n--> {pump_status} <--"
             )

        elif query_data == 'sensorlive':
            sn_types = ['Temperature','Soil_Moisture']
            _msg = []
            for sn_type in sn_types:
                sen = self.my_req.get_sen_val(self.init_dict[chat_ID]['IDs'],sn_type)
                _msg.append(f'{sn_type} : {sen}')
            self.bot.sendMessage(
                chat_ID,
                text=f"Live value of sensors in {self.init_dict[chat_ID]['IDs']['farm']} - {self.init_dict[chat_ID]['IDs']['section']}\n{_msg[0]} C\n{_msg[1]} %"
                )

        elif query_data == 'thresh': 
            thresh = self.my_req.get_threshold(self.init_dict[chat_ID]['IDs'])
            self.bot.sendMessage(
                chat_ID,
                text=f"Thresholds of {self.init_dict[chat_ID]['IDs']['farm']} - {self.init_dict[chat_ID]['IDs']['section']}\n🌡 Temprature is: {thresh['temp']} C\n💧 Minium Moisture is: {thresh['mois_min']} %\n💧 Maximum Moisture is: {thresh['mois_max']} %"
                )

        elif query_data == 'switch_pump':
            buttons = [[InlineKeyboardButton(text=f'PUMP ON 🟡', callback_data=f'switchPump_on'), 
                    InlineKeyboardButton(text=f'PUMP OFF ⚪', callback_data=f'switchPump_off')]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text='What do you want to do', reply_markup=keyboard)

        elif "switchPump_" in query_data:
            self.my_req.put_status(self.init_dict[chat_ID]['IDs'],status=query_data.split('_')[1])
            self.bot.sendMessage(chat_ID, text=f"The pump of {self.init_dict[chat_ID]['IDs']['farm']} - {self.init_dict[chat_ID]['IDs']['section']}\n is became {query_data.split('_')[1]}")

        elif query_data == "control_mode":
            mode_status = self.my_req.get_control_status(self.init_dict[chat_ID]['IDs'])
            self.bot.sendMessage(chat_ID, text=f"The control mode of {self.init_dict[chat_ID]['IDs']['farm']} - {self.init_dict[chat_ID]['IDs']['section']} is\n  {mode_status}")

        elif query_data == "change_mode":
            buttons = [[InlineKeyboardButton(text=f'Auto', callback_data=f'changeMode_auto'), 
                    InlineKeyboardButton(text=f'Manual', callback_data=f'changeMode_manual')]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text='What do you want to do', reply_markup=keyboard)

        elif 'changeMode_' in query_data:
            self.my_req.put_control_status(self.init_dict[chat_ID]['IDs'],query_data.split('_')[1])
            self.bot.sendMessage(chat_ID, text=f"The control mode of {self.init_dict[chat_ID]['IDs']['farm']} - {self.init_dict[chat_ID]['IDs']['section']} become\n  {query_data.split('_')[1]}")
        
            
if __name__ == "__main__":
    
    my_req = MyRequest()
    broker, port,_ = my_req.get_broker()
    bot=IrrigationBot(broker, port)

    print("Bot started ...")
    while True:
        time.sleep(3)
