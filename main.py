from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import logging

# Not so be shared with git
import client_secrets_telegram

from Conversations.start import get_handler as start_conv
from Conversations.more import get_handler as more_conv
import commands


API_TOKEN = client_secrets_telegram.BOT_TOKEN
URL = "https://api.telegram.org/bot{}/".format(API_TOKEN)

PROGRAM, LANGUAGE, TIMETABLE, SAVEDATA = range(4)
MORE, WEEKS, ADDITION = range(3)


# setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def button(update, context):
    query = update.callback_query

    query.edit_message_text(text="Selected option: {}".format(query.data))


def main():
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(start_conv())
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(more_conv())
    dispatcher.add_handler(CommandHandler('Magister', commands.get_msc))
    dispatcher.add_handler(CommandHandler('Kandi', commands.get_bsc))
    dispatcher.add_handler(CommandHandler('Joke', commands.tell_joke))
    dispatcher.add_handler(CommandHandler('Help', commands.get_help))
    dispatcher.add_handler(CommandHandler('Developer', commands.get_dev))

    # log all errors
    dispatcher.add_error_handler(error)

    print("Listening..")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
