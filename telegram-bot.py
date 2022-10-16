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
        if not(any([i[1]==str(telegram_id) for i in mas])):
            cursor.execute("INSERT INTO 'users' ('telegram_id') VALUES (?)",(telegram_id,))
            connector.commit()
    except sqlite3.Error as error:
        print("Error",error)
    finally:
        if (connector):
            connector.close()


@bot.message_handler(commands=['start'])
def hello(message):
    bot.send_message(message.chat.id,"Hello bro")
    telegram_id = message.from_user.id
    id_in_sql(telegram_id)


bot.polling()