from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, ConversationHandler
from telegram import InlineQueryResultArticle, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
import logging

from studiehandboken_service import main_parser
import spreadsheet_service
from Conversations.general import cancel
from Conversations.general import get_joke

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

PROGRAM, LANGUAGE, TIMETABLE, SAVEDATA = range(4)
service = spreadsheet_service.SpreadsheetService()


def get_handler():

        # Add conversation handler with the states PROGRAM and LANGUAGE
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],

            states={
                PROGRAM: [MessageHandler(Filters.regex('^(B.Sc.|M.Sc.|Other)$'), program)],

                LANGUAGE: [MessageHandler(Filters.regex('^(Swedish|English|Finnish)$'), language),
                           CommandHandler('skip', skip_language)],

                TIMETABLE: [MessageHandler(Filters.regex('^(Yes please|No thanks)$'), timetable)],

                SAVEDATA: [MessageHandler(Filters.regex('^(Yes|No)$'), save_data),
                           CommandHandler('skip', skip_save)]
            },

            fallbacks=[CommandHandler('cancel', cancel)]
        )
        return conv_handler


# /start
def start(update, context):
    reply_keyboard = [['B.Sc.', 'M.Sc.']]
    #
    # update.message.reply_text(
    #    'Hi! My name is Professor Bot. Let me try to understand you abit more. '
    #    'Send /cancel to stop talking to me.\nI may collect unnecessary information about you and your family. \n\n'
    #    'At what stage are you studying?',
    #    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    #

    update.message.reply_text('I\'m not fully implemented yet, stay tuned. Meanwhile, check out /help or /scheme')
    return ConversationHandler.END


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
    reply_keyboard = [['Yes', 'No']]
    update.message.reply_text('Thank you, setting {} as your default language. \n'
                              'Can I save your data for later use? you can /skip this.'.format(update.message.text),
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return SAVEDATA


def skip_language(update, context):
    user = update.message.from_user
    logger.info("User %s did not specify a language.", user.first_name)
    context.user_data['language'] = "Swedish"
    reply_keyboard = [['Yes', 'No']]
    update.message.reply_text('I bet you know many languages!\n Setting default language to Swedish.',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return SAVEDATA


def save_data(update, context):
    user = update.message.from_user
    if update.message.text == "Yes":
        logger.info("Saving user information: %d, %s, %s".format(user.id, context.user_data["programme"],
                                                                 context.user_data["language"]))
        update.message.reply_text('Thank you, I will save your information for later use.\n '
                                  'Dont worry, it\'s safe with me.')
        service.insertRow(data=[user.id, context.user_data["programme"], context.user_data["language"]])
        reply_keyboard = [['Yes please', 'No thanks']]
        update.message.reply_text('Let me show you your schedule',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        return TIMETABLE
    else:
        skip_save(update, context)


def skip_save(update, context):
    update.message.reply_text('Ok, I understand you.', reply_markup=ReplyKeyboardRemove())
    reply_keyboard = [['Yes please', 'No thanks']]
    update.message.reply_text('Do you want me to look for your schedule?',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return TIMETABLE


def timetable(update, context):
    user = update.message.from_user
    logger.info("Looking for timetable for %s.", user.first_name)

    # Give timetable
    update.message.reply_text('Give me a minute, I\'m looking for your timetable. '
                              'Let me entertain you with a joke as you wait...\n\n'
                              '{}'.format(get_joke()), reply_markup=ReplyKeyboardRemove())

    table = main_parser(program=context.user_data["programme"], lang=context.user_data["language"], weeks=0)
    if table:
        print(table)
        update.message.reply_text(table, reply_markup=ReplyKeyboardRemove())

    else:
        update.message.reply_text('Nothing scheduled for you, have a nice week!')

    update.message.reply_text('You can always request /more')
    return ConversationHandler.END

