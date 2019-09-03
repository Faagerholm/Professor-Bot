from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, ConversationHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardMarkup, ReplyKeyboardRemove
import logging
import requests

from studiehandboken_parser import main_parser

API_TOKEN = "968319027:AAEDy-A2R6ZMWxyF5OtQWbgmt6FbQqQMfes"
URL = "https://api.telegram.org/bot{}/".format(API_TOKEN)

# setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

PROGRAM, LANGUAGE, TIMETABLE = range(3)


def start(update, context):
    reply_keyboard = [['B.Sc.', 'M.Sc.', 'Other']]
    update.message.reply_text(
        'Hi! My name is Professor Bot. I will try to understand you plebiands. '
        'Send /cancel to stop talking to me.\nI may collect unnecessary information about you and your family. \n\n'
        'At what stage are you studying?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return PROGRAM


def program(update, context):
    context.user_data['programme'] = update.message.text
    user = update.message.from_user
    logger.info("Program of %s: %s", user.first_name, update.message.text)

    reply_keyboard = [['Swedish', 'English', 'Finnish']]
    update.message.reply_text('I see! What language do you want to display, \n'
                              'send /skip if you don\'t want to tell me.',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return LANGUAGE


def language(update, context):
    context.user_data['language'] = update.message.text
    user = update.message.from_user
    logger.info("User %s did specify %s as his language.", user.first_name, update.message.text)
    update.message.reply_text('Thank you, setting {} as your language.'.format(update.message.text))
    # Give timetable
    update.message.reply_text('Give me a minute, I\'m looking for your timetable. '
                              'Let me entertain you with a joke as you wait...\n\n'
                              '{}'.format(get_joke()))

    timetable(update, context)
    return ConversationHandler.END


def skip_language(update, context):
    user = update.message.from_user
    logger.info("User %s did not specify a language.", user.first_name)
    update.message.reply_text('I bet you know many languages!\n Setting default language to Swedish.')

    timetable(update, context)
    return ConversationHandler.END


def timetable(update, context):
    user = update.message.from_user
    logger.info("Looking for timetable for %s.", user.first_name)

    table = main_parser(program=context.user_data["programme"], lang=context.user_data["language"])
    print(table)
    update.message.reply_text(table)
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def get_msc(update, context):
    user = update.message.from_user
    logger.info("User %s looking for his masters courses.", user.first_name)
    update.message.reply_text('Looking for masters schedule.. \n\n'
                              'Here\'s a joke for now.\n'
                              '{}'.format(get_joke()))
    table = main_parser(program="M.Sc.", lang='Swedish')
    update.message.reply_text('This weeks schedule, \n{}'.format(table))


def get_bsc(update, context):
    user = update.message.from_user
    logger.info("User %s looking for his bachelors courses.", user.first_name)
    table = main_parser(program="B.Sc.", lang='Swedish')
    update.message.reply_text('This weeks schedule, \n{}'.format(table))


def tell_joke(update, context):
    update.message.reply_text(get_joke())


def get_joke():
    # Get joke, check for bad request
    r = requests.get("https://geek-jokes.sameerkumar.website/api")
    joke = r.json() if r.status_code == 200 else "No joke for today."
    return joke


def get_help(update, context):
    update.message.reply_text('I\'m the professor Bot , soon I\'ll know alot about your school. '
                              'Stay tuned, for the time these are the commands I understand.\n'
                              '/start\n/Magister\n/Kandi\n/Joke\n/Help\n\n'
                              'Stay tuned for reminders and other cool stuff.'
                              '/Developer')


def get_dev(update, context):
    update.message.reply_text('You will find the project at\n'
                              '')

def main():
    updater = Updater(token=API_TOKEN, use_context=True)
    # Stopping any old updater
    updater.stop()
    dispatcher = updater.dispatcher

    # Add conversation handler with the states PROGRAM and LANGUAGE
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            PROGRAM: [MessageHandler(Filters.regex('^(B.Sc.|M.Sc.|Other)$'), program)],

            LANGUAGE: [MessageHandler(Filters.regex('^(Swedish|English|Finnish)$'), language),
                       CommandHandler('skip', skip_language)],

            TIMETABLE: [MessageHandler(None, timetable)],

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler('Magister', get_msc))
    dispatcher.add_handler(CommandHandler('Kandi', get_bsc))
    dispatcher.add_handler(CommandHandler('Joke', tell_joke))
    dispatcher.add_handler(CommandHandler('Help', get_help))
    dispatcher.add_handler(CommandHandler('Developer'), get_dev)
    # log all errors
    dispatcher.add_error_handler(error)

    print("Listening..")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
