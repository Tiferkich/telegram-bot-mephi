import sqlite3
import telebot
from tokens import token


bot=telebot.TeleBot(token)
def id_in_sql(telegram_id):
    try:
        connector=sqlite3.connect("telegram.db")
        cursor=connector.cursor()
        cursor.execute("SELECT * FROM 'users'")
        mas=cursor.fetchall()
        if not(any([i[0]==str(telegram_id) for i in mas])):
            cursor.execute("INSERT INTO users VALUES (?, ?)", (telegram_id, 1))
        else:
            cursor.execute("UPDATE users SET status = ? WHERE telegram = ?", (1, telegram_id))
        connector.commit()
    except sqlite3.Error as error:
        print("Error:",error)    
    finally:
        cursor.close()
        connector.close()

def get_status(message):
    try:
        connector=sqlite3.connect("telegram.db")
        cursor=connector.cursor()
        telegram_id = message.chat.id
        cursor.execute("SELECT status FROM users WHERE telegram = ?", telegram_id)
        return cursor.fetchone()
    except sqlite3.Error as error:
        print("Error:",error)    
    finally:
        cursor.close()
        connector.close()

def update_status(telegram_id, new_status):
    try:
        connector=sqlite3.connect("telegram.db")
        cursor=connector.cursor()
        cursor.execute("UPDATE users SET status = ? WHERE telegram = ?", (2, telegram_id))
        connector.commit()
    except sqlite3.Error as error:
        print("Error:",error)    
    finally:
        cursor.close()
        connector.close()

def add_word(telegram_id, new_word):
    try:
        connector=sqlite3.connect("telegram.db")
        cursor=connector.cursor()
        cursor.execute("SELECT * FROM 'words'")
        mas=cursor.fetchall()
        if not(any([i[0]==str(telegram_id) for i in mas])):
            cursor.execute("INSERT INTO words VALUES (?, ?)", (telegram_id, new_word))
        else:
            cursor.execute("UPDATE words SET user_word = ? WHERE telegram = ?", (new_word, telegram_id))
        connector.commit()
    except sqlite3.Error as error:
        print("Error:",error)    
    finally:
        cursor.close()
        connector.close()

@bot.message_handler(commands=['start'])
def hello(message):
    telegram_id = message.from_user.id
    bot.send_message(telegram_id, "Hello bro! Now send your keywords")
    
    id_in_sql(telegram_id)
    

@bot.message_handler(content_types=['audio', 'video', 'document', 'text', 'location', 'contact', 'sticker', 'photo'])
def handle_adding_word(message):
    if message.content_type == 'text':
        telegram_id = message.chat.id
        add_word(telegram_id, message.text)
        update_status(telegram_id, 2)
        bot.send_message(telegram_id, "Your word is added")

    else:
        bot.send_message(message.chat.id, text='This is not a text message. Please try again')


bot.polling()