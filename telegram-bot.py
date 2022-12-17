import psycopg2
import telebot
from tokens import token,URL
from telebot import types


bot=telebot.TeleBot(token)

OPTION_BUTTONS = {'ADD NEW KEY WORD': 'WORDS',
                  'VIEW KEY WORDS': 'VIEW_KEY_WORDS', 'DELETE ALL KEY WORDS': 'DELETE_KEY_WORDS',
                 }

def con_to_bs():
    connector = psycopg2.connect(URL)
    return connector


def id_in_sql(telegram_id):
    try:
        connector=con_to_bs()
        cursor=connector.cursor()
        cursor.execute('SELECT * FROM users')
        mas=cursor.fetchall()
        if not(any([i[1]==str(telegram_id) for i in mas])):
            cursor.execute("INSERT INTO users (telegram_id,status) VALUES (%s, %s)", (telegram_id, "START",))
        else:
            cursor.execute("UPDATE users SET status = %s WHERE telegram_id = %s", (str("START"), [telegram_id]))
        connector.commit()
    except psycopg2.Error as error:
        print("Error:",error)    
    finally:
        connector.commit()
        cursor.close()
        connector.close()

def get_status(message):
    try:
        connector=con_to_bs()
        cursor = connector.cursor()
        query = "SELECT * FROM users WHERE telegram_id=%s"
        id = str(message.chat.id)
        cursor.execute(query, [id])
        user_state = cursor.fetchone()[2]
        cursor.close()
        connector.close()
        return user_state
    except:
        pass

def update_status(telegram_id, new_status):
    try:
        connector=con_to_bs()
        cursor=connector.cursor()
        cursor.execute("UPDATE users SET status = %s WHERE telegram_id = %s", (str(new_status),str(telegram_id)))
        connector.commit()
    except psycopg2.Error as error:
        print("Error:",error)    
    finally:
        connector.commit()
        cursor.close()
        connector.close()

def add_word(telegram_id, new_word):
    try:
        connector=con_to_bs()
        cursor=connector.cursor()
        cursor.execute("SELECT * FROM words")
        mas=cursor.fetchall()
        if not(any([i[0]==str(telegram_id) for i in mas])):
            cursor.execute("INSERT INTO words (telegram_id,user_word) VALUES (%s, %s)", (telegram_id, new_word))
        else:
            cursor.execute("SELECT user_word FROM words WHERE telegram_id=%s", ([str(telegram_id)]))
            mas = list(cursor.fetchone())
            mas+=[new_word]
            cursor.execute("DELETE FROM words WHERE telegram_id=%s", ([str(telegram_id)]))
            cursor.execute("INSERT INTO words (telegram_id,user_word) VALUES (%s, %s)", (telegram_id, ",".join(mas),))
        connector.commit()
    except psycopg2.Error as error:
        print("Error:",error)
    finally:
        connector.commit()
        cursor.close()
        connector.close()

def delete_users_key_words(message):
    try:
        connector=con_to_bs()
        cursor = connector.cursor()
        queue="DELETE FROM words WHERE telegram_id=%s"
        id = str(message.chat.id)
        cursor.execute(queue,[id])
    except psycopg2.Error as error:
        print("Error:", error)
    finally:
        connector.commit()
        cursor.close()
        connector.close()

def list_of_words(telegram_id):
    try:
        connector=con_to_bs()
        cursor = connector.cursor()
        cursor.execute("SELECT * FROM words WHERE telegram_id=%s", (str(telegram_id)))
        mas=cursor.fetchall()[1]
        return mas
    except psycopg2.Error as error:
        print("Error:", error)
    finally:
        connector.commit()
        cursor.close()
        connector.close()




@bot.message_handler(commands=['start'])
def handle_confirmation(message):
    try:
        telegram_id = message.from_user.id

        id_in_sql(telegram_id)
        update_status(telegram_id, "START")
    except:
        pass
    finally:
        bot.send_message(message.chat.id, text="I can help you to find information based "
                                               "on your keywords on Chinese sites. \n"
                                           'You can manage me by sending these commands:\n'
                                           '\n'
                                           '/options - display options\n'
                     )


def create_options_keyboard():
    button1 = types.InlineKeyboardButton(text="ADD NEW KEY WORD", callback_data="WORDS")
    button2 = types.InlineKeyboardButton(text="VIEW KEY WORD", callback_data="VIEW_KEY_WORDS")
    button3 = types.InlineKeyboardButton(text="DELETE ALL KEY WORDS", callback_data="DELETE_KEY_WORDS")
    keyboard=types.InlineKeyboardMarkup(row_width=1).add(button1,button2,button3)
    return keyboard

@bot.message_handler(commands=['options'])
def handle_help(message):
    telegram_id = message.chat.id
    update_status(telegram_id, "WORDS")
    keyboard = create_options_keyboard()
    bot.send_message(message.chat.id, text="I can help you to find information based "
                                               "on your keywords on Chinese sites. \n"
                                               'You can manage me by using buttons below\n',
                         reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in [str(value) for key, value in OPTION_BUTTONS.items()])
def options_callback_handler(callback_query):
    message = callback_query.message
    text = callback_query.data
    telegram_id=message.chat.id
    current_state = get_status(message)
    if current_state=="START" or current_state=="WORDS" and text=='WORDS':
        bot.send_message(message.chat.id, text='Write new key word')
    elif text=="VIEW_KEY_WORDS" and (current_state=="START" or current_state=="WORDS"):
        bot.send_message(message.chat.id, text="LIST OF WORDS:  "+list_of_words(telegram_id))
        bot.send_message(message.chat.id, text="LIST IS EMPTY")
    elif text=="DELETE_KEY_WORDS" and current_state=="START" or current_state=="WORDS":
        delete_users_key_words(message)
        bot.send_message(message.chat.id, text='WORDS WERE DELETED')


@bot.message_handler(content_types=['audio', 'video', 'document', 'text', 'location', 'contact', 'sticker', 'photo'])
def handle_adding_word(message):
    if message.content_type == 'text':
        telegram_id = message.chat.id
        add_word(telegram_id, message.text)
        update_status(telegram_id, "WORDS")
        bot.send_message(telegram_id, "Your word is added")

    else:
        bot.send_message(message.chat.id, text='This is not a text message. Please try again')



bot.polling()