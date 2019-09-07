from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, ConversationHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardMarkup, ReplyKeyboardRemove
import logging

from studiehandboken_service import main_parser
from Conversations.general import cancel

# setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

MORE, WEEKS, ADDITION = range(3)


class ConversationMore:

    def __init__(self):
        more_conv = ConversationHandler(
            entry_points=[CommandHandler('more', more_timetable)],

            states={
                WEEKS: [MessageHandler(None, show_weeks)],

                ADDITION: [MessageHandler(Filters.regex('^(Bachelor\'s|Masters)$'), add_information)]

            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )


def more_timetable(update, context):
    print(update.message.text)
    if not context.user_data:
        reply_keyboard = [["Bachelor's", "Masters"]]
        update.message.reply_text('I have not saved any information about what you study, '
                                  'what degree are you looking for?',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return ADDITION
    else:
        update.message.reply_text('How many weeks ahead are you looking?', reply_keyboard=ReplyKeyboardRemove())

    return WEEKS


def add_information(update, context):
    if update.message.text == "Bachelor's":
        context.user_data["programme"] = "B.Sc."
    elif update.message.text == "Masters":
        context.user_data["programme"] = "M.Sc."

    return more_timetable(update, context)


def show_weeks(update, context):
    logger.info('User %s is looking for %s weeks', update.message.from_user.first_name, update.message.text)
    weeks = int(update.message.text)

    update.message.reply_text("looking for the next " + str(weeks) + " weeks schedule")

    if "language" in context.user_data:
        table = main_parser(program=context.user_data["programme"], lang=context.user_data["language"], weeks=weeks)
    elif "programme" in context.user_data:
        table = main_parser(program=context.user_data["programme"], lang="Swedish", weeks=weeks)
    else:
        table = main_parser(program="M.Sc.", lang="Swedish", weeks=weeks)

    if table:
        update.message.reply_text(table)
    else:
        update.message.reply_text('Sorry didn\'t find anything..')

    return ConversationHandler.END
