import telebot
from telegram import Message

TOKEN = "885275180:AAGDMJcATEbqQWwIiKb-zpAwvR8hkM-N3xs"
bot = telebot.TeleBot(TOKEN)

USERS = {}


@bot.message_handler(commands=['start', 'help'])
def welcome_message(message: Message):
    bot.send_message(message.chat.id, "Привет!")


bot.polling(timeout=60)
