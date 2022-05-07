"""
    The file notifier.py checks database every *amount* of minutes/hours/days (can be changed  
    in the scheduled_notifications function) in order to notify the clients that have requested an injector
    of said injector's availability (whether it's > 0 or > *amount needed by the user*)
    
"""

# imports 
import telebot
import schedule
import time
import sqlite3
import logging
from threading import Thread

def setup_logger(logger_name, log_file, level=logging.DEBUG):
    """ logging """
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)    

setup_logger('log_notifier', r'Logs/notifier_logs.log')
log_notifier = logging.getLogger('log_notifier')
    
# token usage
token = open('token.txt', 'r')
bot = telebot.TeleBot(token.read())

def notification():
    """ notifies as soon as inj. quantity > needed amount/0 """
    log_notifier.debug('# Database check')
    connection = sqlite3.connect('Database/db.db')
    cursor = connection.cursor()
    cursor.execute("SELECT code_number, quantity FROM Injector_Details")
    data = cursor.fetchall()
    cursor.execute("SELECT serial_number, amount_remaining, notif_asked FROM Remaining_Notifications_OrderedInj")
    amount = cursor.fetchall()
    for row in data:
        for pending_order in amount:
            if int(row[0]) == int(pending_order[0]):
                if int(row[1]) > int(pending_order[1]):
                    cursor.execute("SELECT chat_id FROM Remaining_Notifications_OrderedInj WHERE serial_number = ?", (int(pending_order[0]), ))
                    chat = cursor.fetchall()
                    for chats in chat:
                        chat_number = int(chats[0])
                        if int(pending_order[2]) == 1:
                            information = f'The injector you looked for previously is now available (0{int(row[0])}). Do you want to purchase it?'
                            cursor.execute("DELETE FROM Remaining_Notifications_OrderedInj WHERE serial_number = ?", (int(pending_order[0]), ))
                            connection.commit()
                            cursor.execute('INSERT INTO User_Injector (chat_id, injector_id) VALUES (?, ?)', (chat_number, int(row[0]), ))
                            connection.commit()
                            markup = telebot.types.InlineKeyboardMarkup()
                            markup.add(telebot.types.InlineKeyboardButton(text='Yes', callback_data = 'order_yes'))
                            markup.add(telebot.types.InlineKeyboardButton(text='No', callback_data = 'no'))
                            bot.send_message(chat_number, information, reply_markup = markup)
    cursor.execute("SELECT serial_number, amount, notif_asked FROM Remaining_Notifications_NonOrderedInj")
    amount = cursor.fetchall()
    for row in data:
        for pending_order in amount:
            if int(row[0]) == int(pending_order[0]):
                if int(row[1]) > int(pending_order[1]):
                    cursor.execute("SELECT chat_id FROM Remaining_Notifications_NonOrderedInj WHERE serial_number = ?", (int(pending_order[0]), ))
                    chat = cursor.fetchall()
                    for chats in chat:
                        chat_number = int(chats[0])
                        if int(pending_order[2]) == 1:
                            information = f'The injector you looked for previously is now available (0{int(row[0])}). Do you want to purchase it?'
                            cursor.execute("DELETE FROM Remaining_Notifications_NonOrderedInj WHERE serial_number = ?", (int(pending_order[0]), ))
                            connection.commit()
                            cursor.execute('INSERT INTO User_Injector (chat_id, injector_id) VALUES (?, ?)', (chat_number, int(row[0]), ))
                            connection.commit()
                            markup = telebot.types.InlineKeyboardMarkup()
                            markup.add(telebot.types.InlineKeyboardButton(text='Yes', callback_data = 'order_yes'))
                            markup.add(telebot.types.InlineKeyboardButton(text='No', callback_data = 'no'))
                            bot.send_message(chat_number, information, reply_markup = markup)
    for row in data:
        if int(row[1]) > 0:
            cursor.execute("SELECT chat_id, notif_asked FROM Injector_Notifications WHERE serial_number = ?", (int(row[0]), ))
            chat = cursor.fetchall()
            for chats in chat:
                chat_number = int(chats[0])
                if int(chats[1]) == 1:
                    information = f'The injector you looked for previously is now available (0{int(row[0])}). Do you want to purchase it?'
                    cursor.execute("DELETE FROM Injector_Notifications WHERE serial_number = ?", (int(row[0]), ))
                    connection.commit()
                    cursor.execute('INSERT INTO User_Injector (chat_id, injector_id) VALUES (?, ?)', (chat_number, int(row[0]), ))
                    connection.commit()
                    markup = telebot.types.InlineKeyboardMarkup()
                    markup.add(telebot.types.InlineKeyboardButton(text='Yes', callback_data = 'order_yes'))
                    markup.add(telebot.types.InlineKeyboardButton(text='No', callback_data = 'no'))
                    bot.send_message(chat_number, information, reply_markup = markup)
    connection.close()


def scheduled_notifications():
    """ schedules the notifier """
    schedule.every(30).seconds.do(notification)
    while True:
        schedule.run_pending()
        time.sleep(1)
        
        

thread_availability_notif = Thread(target=scheduled_notifications)
thread_availability_notif.start()