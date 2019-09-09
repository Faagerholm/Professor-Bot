from telegram import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from Conversations.general import get_joke
import logging

from studiehandboken_service import main_parser, alt_parser

# setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def get_help(update, context):
    update.message.reply_text('I\'m the professor Bot , soon I\'ll know alot about your school. '
                              'Stay tuned, for the time these are the commands I understand.\n'
                              '/Start\n/Scheme\n/Joke\n/Help\n\n'
                              'Stay tuned for reminders and other cool stuff.'
                              ' /Developer\n'
                              'If something is wrong, give my creator a heads up!'
                              '\n @Faagerholm')


def get_dev(update, context):
    update.message.reply_text('You will find the project at\n'
                              'https://github.com/Faagerholm/Professor-Bot.git')


def tell_joke(update, context):
    update.message.reply_text(get_joke(), reply_markup=ReplyKeyboardRemove())


def get_msc(update, context):
    user = update.message.from_user
    logger.info("User %s looking for his masters courses.", user.first_name)
    update.message.reply_text('Looking for this weeks masters schedule.. \n\n'
                              'Here\'s a joke for now.\n'
                              '{}'.format(get_joke()))
    table = main_parser(program="M.Sc.", lang='Swedish')
    context.user_data["programme"] = "M.Sc."
    if table:
        update.message.reply_text('This weeks schedule, \n{}'.format(table), reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text('I didn\'t find anything scheduled for you, you can always request /more',
                                  reply_markup=ReplyKeyboardRemove())


def get_bsc(update, context):
    user = update.message.from_user
    logger.info("User %s looking for his bachelor\'s courses.", user.first_name)
    update.message.reply_text('Looking for this weeks bachelor\'s schedule.. \n\n'
                              'Here\'s a joke for now.\n'
                              '{}'.format(get_joke()))
    table = main_parser(program="B.Sc.", lang='Swedish')
    context.user_data["programme"] = "B.Sc."
    if table:
        update.message.reply_text('This weeks schedule, \n{}'.format(table), reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text('Looks like nothing scheduled for this week, you can always request /more')


def next_week(update, context):
    keyboard = [[InlineKeyboardButton("Datateknik, magister", callback_data='4349')],
                [InlineKeyboardButton("Datateknik, kandidat", callback_data='5071')],
                [InlineKeyboardButton("Kemi- och precessteknik, kandidat", callback_data='4337')],
                [InlineKeyboardButton("Kemi- och precessteknik, magister", callback_data='6132')],
                [InlineKeyboardButton("Kemi- och precessteknik, energiteknik", callback_data='6020')],
                [InlineKeyboardButton("Utbildningslinjen för kultur, historia och filosofi, KH2018", callback_data='7226')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("Vilket program söker du efter?", reply_markup=reply_markup)


def callback(update, context):
    query = update.callback_query
    query.edit_message_text("Söker efter dina kurser...")
    table = alt_parser(query.data)
    query.edit_message_text(text="Dina kurser för nästa vecka: \n\n{}".format(table))
