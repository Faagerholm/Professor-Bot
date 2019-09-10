from telegram import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, \
    InputTextMessageContent, InlineQueryResultArticle

from telegram.utils.helpers import escape_markdown
from Conversations.general import get_joke
from uuid import uuid4
import logging

from studiehandboken_service import alt_parser, course_search, get_course

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


def next_week(update, context):
    keyboard = [[InlineKeyboardButton("Datateknik, magister", callback_data='4349')],
                [InlineKeyboardButton("Datateknik, kandidat", callback_data='5071')],
                [InlineKeyboardButton("Kemi- och precessteknik, kandidat", callback_data='4337')],
                [InlineKeyboardButton("Kemi- och precessteknik, magister", callback_data='6132')],
                [InlineKeyboardButton("Kemi- och precessteknik, energiteknik", callback_data='6020')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("Vilket program söker du efter?", reply_markup=reply_markup)


def callback(update, context):
    query = update.callback_query
    query.edit_message_text("Söker efter dina kurser...")
    table = alt_parser(query.data)
    query.edit_message_text(text="Dina kurser för nästa vecka: \n\n{}".format(table))


def search(update, context):
    query = update.inline_query.query
    if len(query) > 3:
        results = course_search(query)
        answer = []
        for res in sorted(results, key=lambda item: item["name"]):
            answer.append(InlineQueryResultArticle(
                id=uuid4(),
                title=res["name"],
                input_message_content=InputTextMessageContent(get_course(res["id"]))))

        update.inline_query.answer(answer)
