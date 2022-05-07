"""
    The file bot.py contains all the actions the telegram bot is capable of as well as some preparations of data:
        - reads specific commands (/help and /start);
        - after being trained by the AI algorithm, reads the message of the user by getting each word and
          understanding what type of request the user has made;
        - searches and prints the information of requested injectors;
        - checks for availability of injectors in case the client is interested in buying:
            - if the needed amount is available, redirects to the site (online shop);
            - if the needed amount is not available, asks for confirmation of the available injectors from the online 
              shop and proposes to send a notification when the remaining amount or the needed amount will be in stock (the check will be 
              done via notifier.py file).
"""

# imports
import imp
from multiprocessing.sharedctypes import Value
import random
import pickle
import json
import numpy as np
import nltk
import sqlite3
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
nltk.download('omw-1.4')
from tensorflow.python import keras
from keras.models import load_model
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import notifier
import logging

# logging 
notifier.setup_logger('log_bot', r'Logs/bot_logs.log')
log_bot = logging.getLogger('log_bot')

# token usage 
token = open('token.txt', 'r')
bot = telebot.TeleBot(token.read())

""" getting example data """
lemmatizer = WordNetLemmatizer()
requests = json.loads(open('Training/example_data.json').read())

""" getting trained model and data """
words = pickle.load(open('Training/words.pkl', 'rb'))
classes = pickle.load(open('Training/classes.pkl', 'rb'))
model = load_model('Training/supportbot_model.h5')

#  making predictions based on users' messages
def clean_up_sentence(sentence):
    """ cleans up the sentence by tokenizing and lemmatizing it """
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


def bag_of_words(sentence):
    """ converts a sentence into a list full of 0s/1s that indicate whether the word is there or not """
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence):
    "" "makes a prediction -> classifies a sentence """
    bag_words = bag_of_words(sentence)
    result = model.predict(np.array([bag_words]))[0]
    ERROR_TRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(result) if r > ERROR_TRESHOLD]
    results.sort(key=lambda x:x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'request': classes[r[0]]})
    return return_list


def get_response(requests_list, requests_json):
    """ get a response based on the users' messages """
    tag = requests_list[0]['request']
    list_of_requests = requests_json['requests']
    for i in list_of_requests:
        if i['tag'] == tag:                
            result = random.choice(i['responses'])
    return result


# ensure data will be loaded beforehand
wn.ensure_loaded()


log_bot.debug('# Bot is running')


# commands
@bot.message_handler(commands=['start'])
def start_message(message):
    """ /start command """
    bot.send_message(message.chat.id, '''
    Welcome and thank you for using this service!
    - To check what the bot can answer to, please write /help
    - Otherwise, please type your request as a normal message.
    ''')


@bot.message_handler(commands=['help'])
def help_command(message):
    """ /help command """
    bot.send_message(message.chat.id, '''
    The bot is able to answer the following requests:
    - Information/Details about a certain Injector (given its serial number);
    - Information about the availability of a certain Injector (given its serial number);
    - Information and contacts of the firm.
    In case you need to make an order, given the availability of the injector, you can be redirected to the online shop.
    If the injector needed is not available/not available in the quantity you want, I, the bot, can notify you as soon as it will be back in stock!
    ''')


# messages
@bot.message_handler(content_types=['text'])
def handle_message(message):
    """ request/number of needed injectors """
    regex = re.compile('^[0-9]*$')
    match = regex.match(message.text)
    chat_id = message.chat.id
    if match is None:
        text = str(message.text).lower()
        request = predict_class(text)
        result = get_response(request, requests)
        if result == "":
            if str(request) == "[{'request': 'injector_information_request'}]":
                id = ''.join(n for n in text if n.isdigit())
                search_injector(message, id)
            elif str(request) == "[{'request': 'injector_availability_request'}]":
                id = ''.join(n for n in text if n.isdigit())
                search_availability(message, id)
        else:
            bot.send_message(chat_id, result)
    order_yes(message, chat_id)

def search_injector(message, id):  
    """ search injector in DB by ID """
    bot.send_message(message.chat.id, f'Searching information of injector {id}')
    id = int(id)
    connection = sqlite3.connect('Database/db.db')
    cursor = connection.cursor()
    cursor.execute("SELECT serial_number, designation, code_number, type_code FROM Injector_Details WHERE code_number = ? ", (id, ))
    data = cursor.fetchone()
    if data is not None:
        information = f'''
        INJECTOR INFORMATION:

    - Serial Number: {str(data[0])}

    - Designation: {data[1]}

    - Code Number: {str(data[2])}

    - Type Code: {data[3]}
        '''
        bot.send_message(message.chat.id, information)
    elif data == None:
        error_message = 'Injector doesn\'t exist! \n(Please, consider checking if the given ID is correct)'
        bot.send_message(message.chat.id, error_message)
        connection.close()
    log_bot.info(f'User {message.chat.id} searched for information of injector 0{id}')


def search_availability(message, id):
    """ search availability of an injector in DB """
    log_bot.info(f'User {message.chat.id} searched for availability of injector {id}')
    bot.send_message(message.chat.id, f'Searching availability of injector {id}')
    id = int(id)
    connection = sqlite3.connect('Database/db.db')
    cursor = connection.cursor()
    cursor.execute("SELECT quantity FROM Injector_Details WHERE code_number = ? ", (id, ))
    data = cursor.fetchone()
    cursor.execute('INSERT INTO User_Injector (chat_id, injector_id) VALUES (?, ?)', (message.chat.id, id, ))
    connection.commit()
    if data is not None and int(data[0]) > 0:
        information = 'This injector is in stock! Would you like to order it?'
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text='Yes', callback_data = 'order_yes'))
        markup.add(telebot.types.InlineKeyboardButton(text='No', callback_data = 'no'))
        bot.send_message(message.chat.id, information, reply_markup = markup)
    else:
        error_message = 'This type of injector is unavailable at the moment. Would you like to be notified when this injector will be back in stock?'
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text='Yes', callback_data = 'notif_yes'))
        markup.add(telebot.types.InlineKeyboardButton(text='No', callback_data = 'no'))
        bot.send_message(message.chat.id, error_message, reply_markup = markup)
    connection.close()


# callback queries for yes/no buttons 
req_answer = ''
@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.data == 'order_yes':
        global req_answer
        answer = 'Please write the amount of injectors you want to purchase'
        req_answer = answer
        bot.send_message(call.message.chat.id, req_answer)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    elif call.data == 'order_not_all_yes':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        answer = 'Great! Please confirm the current available amount on the site (site link)'
        log_bot.info(f'User {call.message.chat.id} is redirected to shop')
        connection = sqlite3.connect('Database/db.db')
        cursor = connection.cursor()
        cursor.execute("SELECT injector_id FROM User_Injector WHERE chat_id = ? ", (call.message.chat.id, ))
        i_id = cursor.fetchone()
        i_id = int(i_id[0])
        cursor.execute('DELETE FROM Remaining_Notifications_NonOrderedInj WHERE chat_id = ? and serial_number = ?', (call.message.chat.id, i_id,  ))
        connection.commit()
        log_bot.debug(f'User {call.message.chat.id} is deleted from Remaining Notifications (non ordered inj.) Table with injector 0{i_id}')
        connection.close()
        bot.send_message(call.message.chat.id, answer)
        waiting_order(call)
    elif call.data == 'order_not_all_no':
        connection = sqlite3.connect('Database/db.db')
        cursor = connection.cursor()
        cursor.execute("SELECT injector_id FROM User_Injector WHERE chat_id = ? ", (call.message.chat.id, ))
        i_id = cursor.fetchone()
        i_id = int(i_id[0])
        cursor.execute('DELETE FROM Remaining_Notifications_OrderedInj WHERE chat_id = ? and serial_number = ?', (call.message.chat.id, i_id,  ))
        connection.commit()
        log_bot.debug(f'User {call.message.chat.id} is deleted from Remaining Notifications (ordered inj.) Table with injector 0{i_id}')
        connection.close()
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        waiting_order(call)
    elif call.data == 'no':
        answer = 'Alright! Thank you for contacting us!'
        bot.send_message(call.message.chat.id, answer)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        connection = sqlite3.connect('Database/db.db')
        cursor = connection.cursor()
        cursor.execute("SELECT injector_id FROM User_Injector WHERE chat_id = ? ", (call.message.chat.id, ))
        i_id = cursor.fetchone()
        i_id = int(i_id[0])
        cursor.execute('DELETE FROM User_Injector WHERE chat_id = ? and injector_id = ? ', (call.message.chat.id, i_id,  ))
        connection.commit()
        log_bot.debug(f'User {call.message.chat.id} is deleted from User-Injector Table')
        connection.close()
        log_bot.info(f'User {call.message.chat.id} did not order the injector')
    elif call.data == 'notif_not_all_no':
        answer = 'Alright! Thank you for contacting us!'
        bot.send_message(call.message.chat.id, answer)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        connection = sqlite3.connect('Database/db.db')
        cursor = connection.cursor()
        cursor.execute("SELECT injector_id FROM User_Injector WHERE chat_id = ? ", (call.message.chat.id, ))
        i_id = cursor.fetchone()
        i_id = int(i_id[0])
        cursor.execute("SELECT serial_number FROM  Remaining_Notifications_NonOrderedInj WHERE chat_id = ? ", (call.message.chat.id, ))
        data=cursor.fetchall()
        if len(data) != 0:
            cursor.execute('DELETE FROM Remaining_Notifications_NonOrderedInj WHERE chat_id = ? and serial_number = ?', (call.message.chat.id, i_id,  ))
            connection.commit()
            log_bot.debug(f'User {call.message.chat.id} is deleted from Remaining Notifications (non ordered inj.) Table with injector 0{i_id}')
        cursor.execute("SELECT serial_number FROM  Remaining_Notifications_OrderedInj WHERE chat_id = ? ", (call.message.chat.id, ))
        data=cursor.fetchall()
        if len(data) != 0:
            cursor.execute('DELETE FROM Remaining_Notifications_OrderedInj WHERE chat_id = ? and serial_number = ?', (call.message.chat.id, i_id,  ))
            connection.commit()
            log_bot.debug(f'User {call.message.chat.id} is deleted from Remaining Notifications (ordered inj.) Table with injector 0{i_id}')
        cursor.execute('DELETE FROM User_Injector WHERE chat_id = ? and injector_id = ? ', (call.message.chat.id, i_id,  ))
        connection.commit()
        log_bot.debug(f'User {call.message.chat.id} is deleted from User-Injector Table')
        connection.close()
        log_bot.info(f'User {call.message.chat.id} did not accept notification arrival')
    elif call.data == 'notif_yes':
        answer = 'Great! You will be notified as soon as this injector will be back in stock'
        bot.send_message(call.message.chat.id, answer)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        notif_yes(call)
    elif call.data == 'notif_not_all_yes':
        answer = 'You will be notified as soon as this injector will be back in stock with the remaining amount needed by you'
        bot.send_message(call.message.chat.id, answer)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        connection = sqlite3.connect('Database/db.db')
        cursor = connection.cursor()
        cursor.execute("SELECT injector_id FROM User_Injector WHERE chat_id = ? ", (call.message.chat.id, ))
        i_id = cursor.fetchone()
        i_id = int(i_id[0])
        cursor.execute('DELETE FROM User_Injector WHERE chat_id = ? and injector_id = ? ', (call.message.chat.id, i_id,  ))
        connection.commit()
        log_bot.debug(f'User {call.message.chat.id} is deleted from User-Injector Table')
        cursor.execute("SELECT serial_number FROM  Remaining_Notifications_NonOrderedInj WHERE chat_id = ? ", (call.message.chat.id, ))
        data=cursor.fetchall()
        if len(data) != 0:
            cursor.execute('UPDATE Remaining_Notifications_NonOrderedInj SET notif_asked = ? WHERE chat_id = ?', (1, call.message.chat.id, ))
            connection.commit()
            log_bot.debug(f'User {call.message.chat.id} in Remaining Notifications (non ordered inj.) Table with injector 0{i_id} is updated')
        cursor.execute("SELECT serial_number FROM  Remaining_Notifications_OrderedInj WHERE chat_id = ? ", (call.message.chat.id, ))
        data=cursor.fetchall()
        if len(data) != 0:
            cursor.execute('UPDATE Remaining_Notifications_OrderedInj SET notif_asked = ? WHERE chat_id = ?', (1, call.message.chat.id, ))
            connection.commit()
            log_bot.debug(f'User {call.message.chat.id} in Remaining Notifications (ordered inj.) Table with injector 0{i_id} is updated')
        connection.close()
        log_bot.info(f'User {call.message.chat.id} accepted notification arrival')


def notif_yes(call):
    """ if user wants to be notified about when injectors will be in-stock """
    connection = sqlite3.connect('Database/db.db')
    cursor = connection.cursor()
    chat_numb = call.message.chat.id
    cursor.execute("SELECT injector_id FROM User_Injector WHERE chat_id = ? ", (chat_numb, ))
    i_id = cursor.fetchone()
    i_id = int(i_id[0])
    cursor.execute('INSERT INTO Injector_Notifications (serial_number, chat_id, notif_asked) VALUES (?, ?, ?)', (i_id, chat_numb, 1, ))
    connection.commit()
    cursor.execute('DELETE FROM User_Injector WHERE chat_id = ? and injector_id = ? ', (chat_numb, i_id,  ))
    connection.commit()
    connection.close()
    log_bot.info(f'User {chat_numb} accepted notification arrival')


def order_yes(message, chat_id):
    """ if user is interested in ordering """
    if message.chat.id == chat_id and req_answer == 'Please write the amount of injectors you want to purchase':
        text = str(message.text).lower()
        regex = re.compile('^[0-9]*$')
        match = regex.match(message.text)
        if match is not None:            
            amount = ''.join(n for n in text if n.isdigit())
            amount = int(amount)
            connection = sqlite3.connect('Database/db.db')
            cursor = connection.cursor()
            cursor.execute("SELECT injector_id FROM User_Injector WHERE chat_id = ? ", (chat_id, ))
            i_id = cursor.fetchone()
            i_id = int(i_id[0])
            cursor.execute("SELECT quantity FROM Injector_Details WHERE code_number = ? ", (i_id, ))
            data = cursor.fetchone()
            if amount > int(data[0]):
                bot.send_message(message.chat.id, f'There are not enough injectors in stock; we have only {str(data[0])} at the moment')
                information = 'Would you like to order anyway?'
                remaining_amount = amount - int(data[0])
                cursor.execute('INSERT INTO Remaining_Notifications_NonOrderedInj (serial_number, chat_id, amount, notif_asked) VALUES (?, ?, ?, ?)', (i_id, chat_id, amount, 0,  ))
                connection.commit()
                log_bot.debug(f'User {chat_id} is added to Remaining Notifications (non ordered inj.) Table')
                cursor.execute('INSERT INTO Remaining_Notifications_OrderedInj (serial_number, chat_id, amount_remaining, notif_asked) VALUES (?, ?, ?, ?)', (i_id, chat_id, remaining_amount, 0,  ))
                connection.commit()
                log_bot.debug(f'User {chat_id} is added to Remaining Notifications (ordered inj.) Table')
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(telebot.types.InlineKeyboardButton(text='Yes', callback_data = 'order_not_all_yes'))
                markup.add(telebot.types.InlineKeyboardButton(text='No', callback_data = 'order_not_all_no'))
                bot.send_message(message.chat.id, information, reply_markup = markup)
                log_bot.info(f'User {chat_id} wants to order injector 0{i_id}, but the amount needed is not in stock')
            else:
                bot.send_message(message.chat.id, 'Great! Here is the link to the shop where you can finalize your purchase (site link)')
                cursor.execute('DELETE FROM User_Injector WHERE chat_id = ? and injector_id = ? ', (chat_id, i_id,  ))
                connection.commit()
                log_bot.debug(f'User {chat_id} is deleted from User-Injector Table')
                log_bot.info(f'User {chat_id} is redirected to shop to order injector 0{i_id}')
            connection.close()
            req_answer == ''

def waiting_order(call):
    """ notification when there are not enough injectors in stock """
    chat_numb = call.message.chat.id
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Yes', callback_data = 'notif_not_all_yes'))
    markup.add(telebot.types.InlineKeyboardButton(text='No', callback_data = 'notif_not_all_no'))
    bot.send_message(chat_numb, 'Would you like to receive a notification when the needed amount of injectors is available?', reply_markup = markup)


# polling
bot.polling(none_stop=True)
