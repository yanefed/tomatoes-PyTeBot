import copy
import logging

import telegram
from telegram.ext import *

import config
from SQLighter import SQLighter

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)


def start(bot, update, chat_data):
    ch_id = update.message.chat_id
    db_worker = SQLighter(config.database_name)
    cur_user = (ch_id,)
    print(cur_user)
    exist = db_worker.searh_user()
    print(exist)
    if cur_user in exist:
        print("С возвращением!")
    else:
        db_worker.new_user(update.message.chat_id)

    markup = telegram.ReplyKeyboardMarkup(config.start_keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     text='This is tomato timer. Please, choose any option.',
                     reply_markup=markup)
    dp.add_handler(RegexHandler("^(Work)$", work_timer,
                                pass_chat_data=True,
                                pass_job_queue=True))
    dp.add_handler(RegexHandler("^(Rest)$", rest_timer,
                                pass_chat_data=True,
                                pass_job_queue=True))
    dp.add_handler(RegexHandler("^(Send Feedback)$", feedback_handler,
                                pass_chat_data=True))
    dp.add_handler(RegexHandler("^(Settings)$", settings_handler))
    dp.add_handler(RegexHandler("^(Stop)$", unset, pass_chat_data=True))


def cancel_button(bot, update):
    try:
        dp.remove_handler(text_handler)
    except NameError:
        pass
    bot.send_message(update.message.chat_id,
                     text='Cancel',
                     reply_markup=telegram.ReplyKeyboardMarkup(config.start_keyboard))


def settings_handler(bot, update):
    temp_keyboard = [['Set work timer'], ['Set rest timer'], ['Cancel']]
    markup = telegram.ReplyKeyboardMarkup(temp_keyboard)
    bot.send_message(update.message.chat_id, text='Settings', reply_markup=markup)
    set_work_handler = RegexHandler("^(Set work timer)$", set_work_option)
    set_rest_handler = RegexHandler("^(Set rest timer)$", set_rest_option)
    cancel_work_handler = RegexHandler("^(Cancel)$", cancel_button)
    dp.add_handler(set_work_handler)
    dp.add_handler(set_rest_handler)
    dp.add_handler(cancel_work_handler)


def set_work_option(bot, update):
    global text_handler
    text_handler = MessageHandler(Filters.text, set_work_check)
    dp.add_handler(RegexHandler("^(Cancel)$", cancel_button))
    dp.add_handler(text_handler)
    markup = telegram.ReplyKeyboardMarkup([['Cancel']], one_time_keyboard=True)
    bot.send_message(update.message.chat_id, text='Enter work duration', reply_markup=markup)


def set_work_check(bot, update):
    db_worker = SQLighter(config.database_name)
    try:
        temp = float(update.message.text)
        print('success')
        temp = str(temp)
        db_worker.write_work(time=temp, user_id=update.message.chat_id)
        bot.send_message(chat_id=update.message.chat_id, text='Done',
                         reply_markup=telegram.ReplyKeyboardMarkup(config.start_keyboard))
        dp.remove_handler(text_handler)
    except ValueError:
        bot.send_message(update.message.chat_id, text='Wrong value. Try again.')
        set_work_option(bot, update)


def set_rest_option(bot, update):
    global text_handler
    text_handler = MessageHandler(Filters.text, set_rest_check)
    dp.add_handler(RegexHandler("^(Cancel)$", cancel_button))
    dp.add_handler(text_handler)
    markup = telegram.ReplyKeyboardMarkup([['Cancel']], one_time_keyboard=True)
    bot.send_message(update.message.chat_id, text='Enter rest duration', reply_markup=markup)


def set_rest_check(bot, update):
    db_worker = SQLighter(config.database_name)
    try:
        temp = float(update.message.text)
        print('success')
        temp = str(temp)
        db_worker.write_rest(time=temp, user_id=update.message.chat_id)
        bot.send_message(chat_id=update.message.chat_id, text='Done',
                         reply_markup=telegram.ReplyKeyboardMarkup(config.start_keyboard))
        dp.remove_handler(text_handler)
    except ValueError:
        set_rest_option(bot, update)


def feedback_handler(bot, update, chat_data):
    """Catch user feedback"""
    global text_handler
    dp.add_handler(RegexHandler("^(Cancel)$", cancel_button))
    markup = telegram.ReplyKeyboardMarkup([['Cancel']])
    bot.send_message(update.message.chat_id,
                     text='Enter your feedback message',
                     reply_markup=markup)
    text_handler = MessageHandler(Filters.text, send_feedback,
                                  pass_user_data=True)
    dp.add_handler(text_handler)


def send_feedback(bot, update, user_data):
    """Send feedback to admins"""
    markup = telegram.ReplyKeyboardMarkup(config.start_keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     text='Done!', reply_markup=markup)
    for guy in config.admins:
        bot.send_message(guy, str(update.message.from_user.username) + ' sent feedback: ' + update.message.text)
    dp.remove_handler(text_handler)


def alarm(bot, job):
    """Send the alarm message."""
    config.start_keyboard = copy.deepcopy(config.return_keyboard)
    markup = telegram.ReplyKeyboardMarkup(config.start_keyboard)
    bot.send_message(job.context, text='Beep-beep! Time is up!', reply_markup=markup)


def work_timer(bot, update, job_queue, chat_data):
    config.start_keyboard[0][0] = 'Stop'
    markup = telegram.ReplyKeyboardMarkup(config.start_keyboard)
    chat_id = update.message.chat_id
    db_worker = SQLighter(config.database_name)
    due = float(db_worker.select_work(update.message.chat_id).fetchone()[0])
    job = job_queue.run_once(alarm, due * 60, context=chat_id)
    chat_data['job'] = job
    bot.send_message(text='Start work now! You have {:.7g} minutes.'.format(float(due)), chat_id=chat_id,
                     reply_markup=markup)


def rest_timer(bot, update, job_queue, chat_data):
    config.start_keyboard[0][1] = 'Stop'
    markup = telegram.ReplyKeyboardMarkup(config.start_keyboard)
    chat_id = update.message.chat_id
    db_worker = SQLighter(config.database_name)
    due = float(db_worker.select_rest(update.message.chat_id).fetchone()[0])
    job = job_queue.run_once(alarm, due * 60, context=chat_id)
    chat_data['job'] = job
    bot.send_message(text='Now you can rest {:.7g} minutes.'.format(float(due)), chat_id=chat_id, reply_markup=markup)


def unset(bot, update, chat_data):
    """Remove the job if the user changed their mind."""
    if 'job' not in chat_data:
        update.message.reply_text('You have no active timer')
        return
    job = chat_data['job']
    job.schedule_removal()
    del chat_data['job']
    config.start_keyboard = copy.deepcopy(config.return_keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     text='Timer successfully unset',
                     reply_markup=telegram.ReplyKeyboardMarkup(config.start_keyboard))


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Run bot."""
    global dp

    updater = Updater(config.token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start, pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
