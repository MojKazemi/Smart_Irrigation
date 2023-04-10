#!/usr/bin/env python
# coding: utf-8


import telepot
from telepot.loop import MessageLoop
import json    #help converting the datastructures to JSON strings
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from MyMQTT_Reqs import MyMQTT
import time
import requests

class IrrigationBot:
    
    def __init__(self, broker, port, topic):
        # Local token
        self.pwdProcedure = False
        # self.tokenbot = "6178145800:AAFSEDMqPd4KOffrq6P30hslfNkhWJORi-o"
        # Catalog token
        self.tokenBot=requests.get("http://catalogIP/telegram_token").json() #["telegramToken"]
        
        self.bot = telepot.Bot(self.tokenBot)
        self.client = MyMQTT("telegramBot", broker, port, self)
#        self.client = MyMQTT("telegramBot", broker, port, self)
        self.client.start()
        self.topic = topic
        self.__message = {'bn': "telegramBot",
                          'e':[
                              {'n': 'switch', 'v': '', 't': '', 'u': 'bool'},
                          ]
                         }

        MessageLoop(self.bot, {'chat': self.on_chat_message}).run_as_thread()
        
                          
    def start(self):
        self.client.start()
    
    def subscribe(self, topic):
        self.client.mysubscribe(topic) #mysubscribe comes from MQTT file
    
    def stop(self):
        self.client.stop()
    
    def notify(self, topic, msg):
        d = json.loads(msg)
        self.value = d['e']['v']
        timestamp = d['e']['t']
        id = topic.split('/')
        userID = id[1]
        farmID = id[2]
        sectionID=id[3]
        
        # this message will tell us the status of the system
        print(f"The alarm of {userID}\'s{farmID}\'s section{sectionID} is measuring {self.value} at time {timestamp}") #this notify could be for example finishing the irrigation or the number of irrigation which has done in a week
        if self.value:
            self.send_message(self.value, userID, farmID, sectionID)
            
            
    def send_message(self, msg, user, farm, section):
        chat_IDs = ((requests.get("http://127.0.0.1:8080/catalog/chatID/"+user+'/'+farm)).json())["chatID"] #the information of this part comes from catalog
        username = ((requests.get('http://127.0.0.1:8080/catalog/chatID/'+user+'/'+farm)).json())["username"]
        sections = ((requests.get('http://127.0.0.1:8080/catalog/chatID/'+user+'/'+farm+'/'+section)).json())["section"]
        for chat_ID in chat_IDs:
            self.bot.sendMessage(chatID, text=f'The {username}\'s has sent a message')
            

    def on_chat_message(self, msg):
        content_type, chat_type ,chat_ID = telepot.glance(msg)
        message=msg['text']
        
        if self.pwdProcedure == False:
            if message == "/start":
                all_chatIDs = (requests.get('http://127.0.0.1:8080/catalog/all_chatIDs').json())["all_chatIDs"]
                if chat_ID in all_chatIDs:
                    self.bot.sendMessage(chat_ID, text="Welcome. The Contact already registered,"
                                    " if you want to add a new farm, type corresponding password")
                    self.pwdProcedure = True
                    
                else :
                    self.bot.sendMessage(chat_ID, text="Type the current password to register a new farm")
                    self.pwdProcedure = True
            else:
                self.bot.sendMessage(chat_ID, text="Oooopps, I don't understand")
        else:
            dict_result = requests.get('http://127.0.0.1:8080/catalog/evaluate_password?password='+message).json()
            password_correct, user, farm = dict_result["correct"], dict_result["user"], dict_result["farm"]
            
            if password_correct == True :
                requests.post('http://127.0.0.1:8080/catalog/chatID/'+user+'/'+farm,json.dumps({"chatID":chat_ID}))
                username = ((requests.get('http://127.0.0.1:8080/catalog/chatID/'+user+'/'+farm)).json())["username"]
                self.bot.sendMessage(chat_ID, text="Procedure of identification completed ! "
                                                    "You will be alerted in case of your "
                                                    + username + "'s farm status")
                
            else:
                self.bot.sendMessage(chat_ID, text="Wrong password, type /start to retry")
            self.pwdProcedure = False
            
    def bottons(self, chat_ID, currentUser = 1):
        if(currentUser):
            buttons = [[InlineKeyboardButton(text='Farms', callback_data='get_list'),
                    InlineKeyboardButton(text='Turn off the notifications', callback_data='unsubscribe')]]
        else:
                
            bottons = [[InlineKeyboardButton(text="Farms", callback_data='get_list'), 
                    InlineKeyboardButton(text="Turn on the notifications", callback_data='currenctUser')]]
        
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        self.bot.sendMessage(chat_ID, text='Please select one option:', reply_markup=keyboard)
        
        
    

    
'''    def bottons1(self, chat_ID):
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        # Define a button
        button = InlineKeyboardButton("Button Text", callback_data="button_data")

        # Define a keyboard containing the button
        keyboard = [[button]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the keyboard to the user
        bot.send_message(chat_id=chat_id, text='Please choose:', reply_markup=reply_markup)'''

        

if __name__=="__main__":
    mqtt_details = (requests.get('http://127.0.0.1:8080/catalog/broker_details')).json()
    broker = mqtt_details["broker"]
    port = int(mqtt_details["port"])
    topics = (requests.get('http://127.0.0.1:8080/catalog/all_topics?program=controller&type=infraction').json())["value"]
    
    irr_b = IrrigationBot(broker, port, topics)
    for topic in topics:
        irr_b.subscribe(topic)

    print("Bot started ...")
    counter=0
    while True:
        time.sleep(5)
        
