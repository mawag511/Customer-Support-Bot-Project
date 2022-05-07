"""
    Testing of the commands and messages the bot will have to answer to
"""
from telethon import TelegramClient
from telethon.tl.custom.message import Message
from telethon.sessions import StringSession
from api_secrets import api_id, api_hash
import time
from pytest import mark
import logging 

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

setup_logger('log_test', r'logs.log')
log_test = logging.getLogger('log_test')

# credentials and login
api_id = api_id
api_hash = api_hash
with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("Your session string is:", client.session.save())

# commands
@mark.asyncio
async def test_start(client: TelegramClient):
    """ test of the /start command """
    async with client.conversation("@ClientSupport_Bot", timeout=5) as conv:
        await conv.send_message("/start")
        resp: Message = await conv.get_response()
        time.sleep(5)
        start_text = '''Welcome and thank you for using this service!
    - To check what the bot can answer to, please write /help
    - Otherwise, please type your request as a normal message.
    '''
        start_text = start_text.split()
        resp = resp.raw_text.split()
        log_test.debug(f'Bot {resp}')
        log_test.debug(f' Assertion {start_text}')
        assert resp == start_text


@mark.asyncio
async def test_help(client: TelegramClient):
    """ test of the /help command """
    async with client.conversation("@ClientSupport_Bot", timeout=5) as conv:
        await conv.send_message("/help")
        resp: Message = await conv.get_response()
        time.sleep(5)
        help_text = '''The bot is able to answer the following requests:
    - Information/Details about a certain Injector (given its serial number);
    - Information about the availability of a certain Injector (given its serial number);
    - Information and contacts of the firm.
    In case you need to make an order, given the availability of the injector, you can be redirected to the online shop.
    If the injector needed is not available/not available in the quantity you want, I, the bot, can notify you as soon as it will be back in stock!
    '''
        help_text = help_text.split()
        resp = resp.raw_text.split()
        log_test.debug(f'Bot {resp}')
        log_test.debug(f' Assertion {help_text}')
        assert resp == help_text

# messages
@mark.asyncio
async def test_hello(client: TelegramClient):
    """ test of a Greeting """
    async with client.conversation("@ClientSupport_Bot", timeout=5) as conv:
        await conv.send_message("Hello")
        resp: Message = await conv.get_response()
        time.sleep(5)
        hello_text1 = 'Good day! How can i help you?' 
        hello_text2 = 'Hello! How may i help?'
        hello_text3 = 'Greetings, how can i help?'
        hello_text1 = hello_text1.split()
        hello_text2 = hello_text2.split()
        hello_text3 = hello_text3.split()
        resp = resp.raw_text.split()
        log_test.debug(f'Bot {resp}')
        log_test.debug(f' Assertion 1 {hello_text1}')
        log_test.debug(f' Assertion 2 {hello_text2}')
        log_test.debug(f' Assertion 3 {hello_text3}')
        assert resp == hello_text1 or resp == hello_text2 or resp == hello_text3

@mark.asyncio
async def test_goodbye(client: TelegramClient):
    """ test of a Farewell """
    async with client.conversation("@ClientSupport_Bot", timeout=5) as conv:
        await conv.send_message("Thank you, goodbye!")
        resp: Message = await conv.get_response()
        time.sleep(5)
        farewell_text = 'Thank you for using our service!'
        resp = resp.raw_text.split()
        farewell_text = farewell_text.split()
        log_test.debug(f'Bot {resp}')
        log_test.debug(f' Assertion {farewell_text}')
        assert resp == farewell_text

@mark.asyncio
async def test_unidentified(client: TelegramClient):
    """ test of an unidentified text """
    async with client.conversation("@ClientSupport_Bot", timeout=5) as conv:
        await conv.send_message("wfedgfhhgfds")
        resp: Message = await conv.get_response()
        time.sleep(5)
        unidentified_text = 'I\'m sorry, i think i didn\'t quite get what you\'re trying to say. Please word your sentence differently, so that i can understand a bit better!'
        resp = resp.raw_text.split()
        unidentified_text = unidentified_text.split()
        log_test.debug(f'Bot {resp}')
        log_test.debug(f' Assertion {unidentified_text}')
        assert resp == unidentified_text

@mark.asyncio
async def test_company_information(client: TelegramClient):
    """ test of the Company Contacts request """
    async with client.conversation("@ClientSupport_Bot", timeout=5) as conv:
        await conv.send_message("Could i get the contacts of the firm?")
        resp: Message = await conv.get_response()
        time.sleep(5)
        answer = 'All the information of the firm is available on the site (site link)'
        answer = answer.split()
        resp = resp.raw_text.split()
        log_test.debug(f'Bot {resp}')
        log_test.debug(f' Assertion {answer}')
        assert resp == answer

@mark.asyncio
async def test_existing_injector_information(client: TelegramClient):
    """ test of the Injector Information request """
    async with client.conversation("@ClientSupport_Bot", timeout=5) as conv:
        await conv.send_message("Can i get information on the injector 0445110002")
        messages_array = []
        time.sleep(5)
        chat = await client.get_entity('@ClientSupport_Bot')
        messages = await client.get_messages(chat, limit=2)
        for message in messages:
            messages_array.append(message.raw_text)
        messages_array.reverse()
        
        answer_one = 'Searching information of injector 0445110002'
        answer_two = '''
        INJECTOR INFORMATION:

    - Serial Number: 0 445 110 002

    - Designation: Injector, CR system

    - Code Number: 445110002

    - Type Code: CRI1-13
        '''
        full_answer = []
        answer_one = answer_one.split()
        answer_two = answer_two.split()
        full_answer.append(answer_one)
        full_answer.append(answer_two)

        full_message = []
        for word in messages_array:
            word = word.split()
            full_message.append(word)
        
        log_test.debug(f'Bot {full_message}')
        log_test.debug(f' Assertion {full_answer}')
        assert full_message == full_answer

@mark.asyncio
async def test_nonexisting_injector_information(client: TelegramClient):
    """ test of the Injector Information request """
    async with client.conversation("@ClientSupport_Bot", timeout=5) as conv:
        await conv.send_message("Can i get information on the injector 0445110001")
        messages_array = []
        time.sleep(5)
        chat = await client.get_entity('@ClientSupport_Bot')
        messages = await client.get_messages(chat, limit=2)
        for message in messages:
            messages_array.append(message.raw_text)
        messages_array.reverse()
        
        answer_one = 'Searching information of injector 0445110001'
        answer_two = 'Injector doesn\'t exist! \n(Please, consider checking if the given ID is correct)'
        full_answer = []
        answer_one = answer_one.split()
        answer_two = answer_two.split()
        full_answer.append(answer_one)
        full_answer.append(answer_two)

        full_message = []
        for word in messages_array:
            word = word.split()
            full_message.append(word)
        
        log_test.debug(f'Bot {full_message}')
        log_test.debug(f' Assertion {full_answer}')
        assert full_message == full_answer
    
@mark.asyncio
async def test_existing_injector_availability_yes(client: TelegramClient):
    """ test of the Injector Availability request """
    async with client.conversation("@ClientSupport_Bot") as conv:
        await conv.send_message("Is injector 0445110002 available?")
        messages_array = []
        time.sleep(10)
        chat = await client.get_entity('@ClientSupport_Bot')
        messages = await client.get_messages(chat, limit=2)
        for message in messages:
            messages_array.append(message.raw_text)
        messages_array.reverse()
        
        answer_one = 'Searching availability of injector 0445110002'
        answer_two = 'This injector is in stock! Would you like to order it?'
        full_answer = []
        answer_one = answer_one.split()
        answer_two = answer_two.split()
        full_answer.append(answer_one)
        full_answer.append(answer_two)

        full_message = []
        for word in messages_array:
            word = word.split()
            full_message.append(word)
        
        log_test.debug(f'Bot {full_message}')
        log_test.debug(f' Assertion {full_answer}')
        assert full_message == full_answer

        messages = await client.get_messages(chat)
        await messages[0].click(data=b'order_yes')

        await conv.send_message("1")
        resp: Message = await conv.get_response()
        time.sleep(2)
        order_text = 'Great! Here is the link to the shop where you can finalize your purchase (site link)'
        resp = resp.raw_text.split()
        order_text = order_text.split()
        log_test.debug(f'Bot {resp}')
        log_test.debug(f' Assertion {order_text}')
        assert resp == order_text

@mark.asyncio
async def test_existing_injector_availability_no(client: TelegramClient):
    """ test of the Injector Availability request """
    async with client.conversation("@ClientSupport_Bot") as conv:
        await conv.send_message("Is injector 0445110002 available?")
        messages_array = []
        time.sleep(10)
        chat = await client.get_entity('@ClientSupport_Bot')
        messages = await client.get_messages(chat, limit=2)
        for message in messages:
            messages_array.append(message.raw_text)
        messages_array.reverse()
        
        answer_one = 'Searching availability of injector 0445110002'
        answer_two = 'This injector is in stock! Would you like to order it?'
        full_answer = []
        answer_one = answer_one.split()
        answer_two = answer_two.split()
        full_answer.append(answer_one)
        full_answer.append(answer_two)

        full_message = []
        for word in messages_array:
            word = word.split()
            full_message.append(word)
        
        log_test.debug(f'Bot {full_message}')
        log_test.debug(f' Assertion {full_answer}')
        assert full_message == full_answer

        messages = await client.get_messages(chat)
        await messages[0].click(data=b'no')

        msg_array = []
        time.sleep(10)
        message = await client.get_messages(chat, limit=1)
        for message in message:
            msg_array.append(message.raw_text)
        full_msg = []
        for word in msg_array:
            word = word.split()
            full_msg.append(word)
        order_text = []
        order = 'Alright! Thank you for contacting us!'
        order = order.split()
        order_text.append(order)
        log_test.debug(f'Bot {full_msg}')
        log_test.debug(f' Assertion {order_text}')
        assert full_msg == order_text      

@mark.asyncio
async def test_nonexisting_injector_availability_yes(client: TelegramClient):
    """ test of the Injector Availability request (accepting notification)"""
    async with client.conversation("@ClientSupport_Bot") as conv:
        await conv.send_message("Is injector 0445110001 available?")
        time.sleep(10)
        chat = await client.get_entity('@ClientSupport_Bot')
        messages_array = []
        messages = await client.get_messages(chat, limit=2)
        for message in messages:
            messages_array.append(message.raw_text)
        messages_array.reverse()
        
        answer_one = 'Searching availability of injector 0445110001'
        answer_two = 'This type of injector is unavailable at the moment. Would you like to be notified when this injector will be back in stock?'
        full_answer = []
        answer_one = answer_one.split()
        answer_two = answer_two.split()
        full_answer.append(answer_one)
        full_answer.append(answer_two)

        full_message = []
        for word in messages_array:
            word = word.split()
            full_message.append(word)
      
        log_test.debug(f'Bot {full_message}')
        log_test.debug(f' Assertion {full_answer}')
        assert full_message == full_answer

        messages = await client.get_messages(chat)
        await messages[0].click(data=b'notif_yes')
        time.sleep(10)

        msg_array = []
        message = await client.get_messages(chat, limit=1)
        for message in message:
            msg_array.append(message.raw_text)
        full_msg = []
        for word in msg_array:
            word = word.split()
            full_msg.append(word)
        notif_answer = []
        notif = 'Great! You will be notified as soon as this injector will be back in stock'
        notif = notif.split()
        notif_answer.append(notif)
        log_test.debug(f'Bot {full_msg}')
        log_test.debug(f' Assertion {notif_answer}')
        assert full_msg == notif_answer  

@mark.asyncio
async def test_nonexisting_injector_availability_no(client: TelegramClient):
    """ test of the Injector Availability request (not accepting notification)"""
    async with client.conversation("@ClientSupport_Bot") as conv:
        await conv.send_message("Is injector 0445110001 available?")
        time.sleep(10)
        chat = await client.get_entity('@ClientSupport_Bot')
        messages_array = []
        messages = await client.get_messages(chat, limit=2)
        for message in messages:
            messages_array.append(message.raw_text)
        messages_array.reverse()
        
        answer_one = 'Searching availability of injector 0445110001'
        answer_two = 'This type of injector is unavailable at the moment. Would you like to be notified when this injector will be back in stock?'
        full_answer = []
        answer_one = answer_one.split()
        answer_two = answer_two.split()
        full_answer.append(answer_one)
        full_answer.append(answer_two)

        full_message = []
        for word in messages_array:
            word = word.split()
            full_message.append(word)
      
        log_test.debug(f'Bot {full_message}')
        log_test.debug(f' Assertion {full_answer}')
        assert full_message == full_answer

        messages = await client.get_messages(chat)
        await messages[0].click(data=b'no')
        time.sleep(10)

        msg_array = []
        message = await client.get_messages(chat, limit=1)
        for message in message:
            msg_array.append(message.raw_text)
        full_msg = []
        for word in msg_array:
            word = word.split()
            full_msg.append(word)
        notif_answer = []
        notif = 'Alright! Thank you for contacting us!'
        notif = notif.split()
        notif_answer.append(notif)
        log_test.debug(f'Bot {full_msg}')
        log_test.debug(f' Assertion {notif_answer}')
        assert full_msg == notif_answer      

@mark.asyncio
async def test_existing_injector_availability_insufficient_all_yes(client: TelegramClient):
    """ test of the Injector Availability request (requesting too many items, accepting both buttons)"""
    async with client.conversation("@ClientSupport_Bot") as conv:
        await conv.send_message("Is injector 0445110002 available?")
        messages_array = []
        time.sleep(10)
        chat = await client.get_entity('@ClientSupport_Bot')
        messages = await client.get_messages(chat, limit=2)
        for message in messages:
            messages_array.append(message.raw_text)
        messages_array.reverse()
        
        answer_one = 'Searching availability of injector 0445110002'
        answer_two = 'This injector is in stock! Would you like to order it?'
        full_answer = []
        answer_one = answer_one.split()
        answer_two = answer_two.split()
        full_answer.append(answer_one)
        full_answer.append(answer_two)

        full_message = []
        for word in messages_array:
            word = word.split()
            full_message.append(word)
        
        log_test.debug(f'Bot {full_message}')
        log_test.debug(f' Assertion {full_answer}')
        assert full_message == full_answer

        messages = await client.get_messages(chat)
        await messages[0].click(data=b'order_yes')

        await conv.send_message("100")
        time.sleep(10)
        new_messages_array = []
        new_messages = await client.get_messages(chat, limit=2)
        for message in new_messages:
            new_messages_array.append(message.raw_text)
        new_messages_array.reverse()
        new_answer_one = 'There are not enough injectors in stock; we have only 5 at the moment'
        new_answer_two = 'Would you like to order anyway?'
        new_full_answer = []
        new_answer_one =  new_answer_one.split()
        new_answer_two =  new_answer_two.split()
        new_full_answer.append( new_answer_one)
        new_full_answer.append( new_answer_two)

        new_full_message = []
        for word in new_messages_array:
            word = word.split()
            new_full_message.append(word)
        
        log_test.debug(f'Bot {new_full_message}')
        log_test.debug(f' Assertion {new_full_answer}')
        assert new_full_message == new_full_answer

        messages = await client.get_messages(chat)
        await messages[0].click(data=b'order_not_all_yes')

        msg_array = []
        message = await client.get_messages(chat, limit=2)
        for message in message:
            msg_array.append(message.raw_text)
        msg_array.reverse()
        full_msg = []
        for word in msg_array:
            word = word.split()
            full_msg.append(word)
        conf_answer = []
        conf1 = 'Great! Please confirm the current available amount on the site (site link)'
        conf2 = 'Would you like to receive a notification when the needed amount of injectors is available?'
        conf1 = conf1.split()
        conf2 = conf2.split()
        conf_answer.append(conf1)
        conf_answer.append(conf2)
        log_test.debug(f'Bot {full_msg}')
        log_test.debug(f' Assertion {conf_answer}')
        assert full_msg == conf_answer  

        messages = await client.get_messages(chat)
        await messages[0].click(data=b'notif_not_all_yes') 

        msg_array = []
        message = await client.get_messages(chat, limit=1)
        for message in message:
            msg_array.append(message.raw_text)
        full_msg = []
        for word in msg_array:
            word = word.split()
            full_msg.append(word)
        notif_answer = []
        notif = 'You will be notified as soon as this injector will be back in stock with the remaining amount needed by you'
        notif = notif.split()
        notif_answer.append(notif)
        log_test.debug(f'Bot {full_msg}')
        log_test.debug(f' Assertion {notif_answer}')
        assert full_msg == notif_answer  

@mark.asyncio
async def test_existing_injector_availability_insufficient_all_no(client: TelegramClient):
    """ test of the Injector Availability request (requesting too many items, not accepting any buttons)"""
    async with client.conversation("@ClientSupport_Bot") as conv:
        await conv.send_message("Is injector 0445110008 available?")
        messages_array = []
        time.sleep(10)
        chat = await client.get_entity('@ClientSupport_Bot')
        messages = await client.get_messages(chat, limit=2)
        for message in messages:
            messages_array.append(message.raw_text)
        messages_array.reverse()
        
        answer_one = 'Searching availability of injector 0445110008'
        answer_two = 'This injector is in stock! Would you like to order it?'
        full_answer = []
        answer_one = answer_one.split()
        answer_two = answer_two.split()
        full_answer.append(answer_one)
        full_answer.append(answer_two)

        full_message = []
        for word in messages_array:
            word = word.split()
            full_message.append(word)
        
        log_test.debug(f'Bot {full_message}')
        log_test.debug(f' Assertion {full_answer}')
        assert full_message == full_answer

        messages = await client.get_messages(chat)
        await messages[0].click(data=b'order_yes')

        await conv.send_message("100")
        time.sleep(10)
        new_messages_array = []
        new_messages = await client.get_messages(chat, limit=2)
        for message in new_messages:
            new_messages_array.append(message.raw_text)
        new_messages_array.reverse()
        new_answer_one = 'There are not enough injectors in stock; we have only 10 at the moment'
        new_answer_two = 'Would you like to order anyway?'
        new_full_answer = []
        new_answer_one =  new_answer_one.split()
        new_answer_two =  new_answer_two.split()
        new_full_answer.append( new_answer_one)
        new_full_answer.append( new_answer_two)

        new_full_message = []
        for word in new_messages_array:
            word = word.split()
            new_full_message.append(word)
        
        log_test.debug(f'Bot {new_full_message}')
        log_test.debug(f' Assertion {new_full_answer}')
        assert new_full_message == new_full_answer

        messages = await client.get_messages(chat)
        await messages[0].click(data=b'order_not_all_no')

        msg_array = []
        message = await client.get_messages(chat, limit=1)
        for message in message:
            msg_array.append(message.raw_text)
        msg_array.reverse()
        full_msg = []
        for word in msg_array:
            word = word.split()
            full_msg.append(word)
        conf_answer = []
        conf = 'Would you like to receive a notification when the needed amount of injectors is available?'
        conf = conf.split()
        conf_answer.append(conf)
        log_test.debug(f'Bot {full_msg}')
        log_test.debug(f' Assertion {conf_answer}')
        assert full_msg == conf_answer  

        messages = await client.get_messages(chat)
        await messages[0].click(data=b'notif_not_all_no') 

        msg_array = []
        message = await client.get_messages(chat, limit=1)
        for message in message:
            msg_array.append(message.raw_text)
        full_msg = []
        for word in msg_array:
            word = word.split()
            full_msg.append(word)
        notif_answer = []
        notif = 'Alright! Thank you for contacting us!'
        notif = notif.split()
        notif_answer.append(notif)
        log_test.debug(f'Bot {full_msg}')
        log_test.debug(f' Assertion {notif_answer}')
        assert full_msg == notif_answer      
   
@mark.asyncio
async def test_existing_injector_availability_insufficient_Nyes(client: TelegramClient):
    """ test of the Injector Availability request (requesting too many items, accepting only notifs)"""
    async with client.conversation("@ClientSupport_Bot") as conv:
        await conv.send_message("Is injector 0445110083 available?")
        messages_array = []
        time.sleep(10)
        chat = await client.get_entity('@ClientSupport_Bot')
        messages = await client.get_messages(chat, limit=2)
        for message in messages:
            messages_array.append(message.raw_text)
        messages_array.reverse()
        
        answer_one = 'Searching availability of injector 0445110083'
        answer_two = 'This injector is in stock! Would you like to order it?'
        full_answer = []
        answer_one = answer_one.split()
        answer_two = answer_two.split()
        full_answer.append(answer_one)
        full_answer.append(answer_two)

        full_message = []
        for word in messages_array:
            word = word.split()
            full_message.append(word)
        
        log_test.debug(f'Bot {full_message}')
        log_test.debug(f' Assertion {full_answer}')
        assert full_message == full_answer

        messages = await client.get_messages(chat)
        await messages[0].click(data=b'order_yes')

        await conv.send_message("100")
        time.sleep(10)
        new_messages_array = []
        new_messages = await client.get_messages(chat, limit=2)
        for message in new_messages:
            new_messages_array.append(message.raw_text)
        new_messages_array.reverse()
        new_answer_one = 'There are not enough injectors in stock; we have only 3 at the moment'
        new_answer_two = 'Would you like to order anyway?'
        new_full_answer = []
        new_answer_one =  new_answer_one.split()
        new_answer_two =  new_answer_two.split()
        new_full_answer.append( new_answer_one)
        new_full_answer.append( new_answer_two)

        new_full_message = []
        for word in new_messages_array:
            word = word.split()
            new_full_message.append(word)
        
        log_test.debug(f'Bot {new_full_message}')
        log_test.debug(f' Assertion {new_full_answer}')
        assert new_full_message == new_full_answer

        messages = await client.get_messages(chat)
        await messages[0].click(data=b'order_not_all_no')

        msg_array = []
        message = await client.get_messages(chat, limit=1)
        for message in message:
            msg_array.append(message.raw_text)
        msg_array.reverse()
        full_msg = []
        for word in msg_array:
            word = word.split()
            full_msg.append(word)
        conf_answer = []
        conf = 'Would you like to receive a notification when the needed amount of injectors is available?'
        conf = conf.split()
        conf_answer.append(conf)
        log_test.debug(f'Bot {full_msg}')
        log_test.debug(f' Assertion {conf_answer}')
        assert full_msg == conf_answer  

        messages = await client.get_messages(chat)
        await messages[0].click(data=b'notif_not_all_yes') 

        msg_array = []
        message = await client.get_messages(chat, limit=1)
        for message in message:
            msg_array.append(message.raw_text)
        full_msg = []
        for word in msg_array:
            word = word.split()
            full_msg.append(word)
        notif_answer = []
        notif = 'You will be notified as soon as this injector will be back in stock with the remaining amount needed by you'
        notif = notif.split()
        notif_answer.append(notif)
        log_test.debug(f'Bot {full_msg}')
        log_test.debug(f' Assertion {notif_answer}')
        assert full_msg == notif_answer  
   
@mark.asyncio
async def test_existing_injector_availability_insufficient_Oyes(client: TelegramClient):
    """ test of the Injector Availability request (requesting too many items, accepting only order)"""
    async with client.conversation("@ClientSupport_Bot") as conv:
        await conv.send_message("Is injector 0445120002 available?")
        messages_array = []
        time.sleep(10)
        chat = await client.get_entity('@ClientSupport_Bot')
        messages = await client.get_messages(chat, limit=2)
        for message in messages:
            messages_array.append(message.raw_text)
        messages_array.reverse()
        
        answer_one = 'Searching availability of injector 0445120002'
        answer_two = 'This injector is in stock! Would you like to order it?'
        full_answer = []
        answer_one = answer_one.split()
        answer_two = answer_two.split()
        full_answer.append(answer_one)
        full_answer.append(answer_two)

        full_message = []
        for word in messages_array:
            word = word.split()
            full_message.append(word)
        
        log_test.debug(f'Bot {full_message}')
        log_test.debug(f' Assertion {full_answer}')
        assert full_message == full_answer

        messages = await client.get_messages(chat)
        await messages[0].click(data=b'order_yes')

        await conv.send_message("100")
        time.sleep(10)
        new_messages_array = []
        new_messages = await client.get_messages(chat, limit=2)
        for message in new_messages:
            new_messages_array.append(message.raw_text)
        new_messages_array.reverse()
        new_answer_one = 'There are not enough injectors in stock; we have only 2 at the moment'
        new_answer_two = 'Would you like to order anyway?'
        new_full_answer = []
        new_answer_one =  new_answer_one.split()
        new_answer_two =  new_answer_two.split()
        new_full_answer.append( new_answer_one)
        new_full_answer.append( new_answer_two)

        new_full_message = []
        for word in new_messages_array:
            word = word.split()
            new_full_message.append(word)
        
        log_test.debug(f'Bot {new_full_message}')
        log_test.debug(f' Assertion {new_full_answer}')
        assert new_full_message == new_full_answer

        messages = await client.get_messages(chat)
        await messages[0].click(data=b'order_not_all_yes')

        msg_array = []
        message = await client.get_messages(chat, limit=2)
        for message in message:
            msg_array.append(message.raw_text)
        msg_array.reverse()
        full_msg = []
        for word in msg_array:
            word = word.split()
            full_msg.append(word)
        conf_answer = []
        conf1 = 'Great! Please confirm the current available amount on the site (site link)'
        conf2 = 'Would you like to receive a notification when the needed amount of injectors is available?'
        conf1 = conf1.split()
        conf2 = conf2.split()
        conf_answer.append(conf1)
        conf_answer.append(conf2)
        log_test.debug(f'Bot {full_msg}')
        log_test.debug(f' Assertion {conf_answer}')
        assert full_msg == conf_answer  

        messages = await client.get_messages(chat)
        await messages[0].click(data=b'notif_not_all_no') 

        msg_array = []
        message = await client.get_messages(chat, limit=1)
        for message in message:
            msg_array.append(message.raw_text)
        full_msg = []
        for word in msg_array:
            word = word.split()
            full_msg.append(word)
        notif_answer = []
        notif = 'Alright! Thank you for contacting us!'
        notif = notif.split()
        notif_answer.append(notif)
        log_test.debug(f'Bot {full_msg}')
        log_test.debug(f' Assertion {notif_answer}')
        assert full_msg == notif_answer      
   

with client:
    client.loop.run_until_complete(test_start(client))
    time.sleep(2)
    client.loop.run_until_complete(test_help(client))
    time.sleep(2)
    client.loop.run_until_complete(test_hello(client))
    time.sleep(2)
    client.loop.run_until_complete(test_company_information(client))
    time.sleep(2)
    client.loop.run_until_complete(test_existing_injector_information(client))
    time.sleep(2)
    client.loop.run_until_complete(test_nonexisting_injector_information(client))
    time.sleep(2)
    client.loop.run_until_complete(test_existing_injector_availability_yes(client))
    time.sleep(2)
    client.loop.run_until_complete(test_existing_injector_availability_no(client))
    time.sleep(2)
    client.loop.run_until_complete(test_nonexisting_injector_availability_yes(client))
    time.sleep(2)
    client.loop.run_until_complete(test_nonexisting_injector_availability_no(client))
    time.sleep(2)
    client.loop.run_until_complete(test_existing_injector_availability_insufficient_all_yes(client))
    time.sleep(2)
    client.loop.run_until_complete(test_existing_injector_availability_insufficient_all_no(client))
    time.sleep(2)
    client.loop.run_until_complete(test_existing_injector_availability_insufficient_Nyes(client))
    time.sleep(2)
    client.loop.run_until_complete(test_existing_injector_availability_insufficient_Oyes(client))
    time.sleep(2)
    client.loop.run_until_complete(test_unidentified(client))
    time.sleep(2)
    client.loop.run_until_complete(test_goodbye(client))
    time.sleep(2)
