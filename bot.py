import os
import sys
import logging
from typing import Final, Any
from datetime import datetime, timedelta
from telegram import Update, ChatInviteLink, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

from resources import *
from database_handler import DatabaseHandler

logging.getLogger('httpx').setLevel(logging.WARNING)
logging.basicConfig(filename='bot_log.txt',
    filemode='a',
    level=logging.INFO,
    format="%(levelname)s: %(asctime)s %(message)s")

EXPIRED_CLEANER_JOB: Final = 'expired_users_cleaner'
BOT_USERNAME: Final = '@karedina_ekaterina_bot'
BOT_TOKEN: Final = os.environ.get('BOT_TOKEN')
GROUP_ID: Final = os.environ.get('GROUP_ID')
CARD_NUMBER: Final = os.environ.get('CARD_NUMBER')
if not BOT_TOKEN or not GROUP_ID:
    logging.error("env variables aren't set corectly!")
    sys.exit(1)

databaseHandler = DatabaseHandler()
waiting_for_approve = {}


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(GREETING_MESSAGE, parse_mode="Markdown")
    await set_cleaning_timer(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_MESSAGE)


async def prices_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_message(update, context, custom_text=PRICES_COMMAND)


async def subscription_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_message(update, context, custom_text=PRICES_COMMAND)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f'Update {update} error: {context.error}')


# Internal commands
async def add_user_to_group(user_id: int, period: int, update: Update, context: ContextTypes.DEFAULT_TYPE):
    link: ChatInviteLink = await context.bot.create_chat_invite_link(GROUP_ID)
    expire_time = datetime.now() + timedelta(days=30*period)
    sql_expire_time = expire_time.strftime('%Y-%m-%d %H:%M:%S')
    databaseHandler.add_purchase(user_id, sql_expire_time, period)
    logging.info(f'Invite link was sent to user {user_id}')
    return link.invite_link, expire_time


async def remove_user_from_group(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.ban_chat_member(GROUP_ID, user_id)
    await context.bot.unban_chat_member(GROUP_ID, user_id)
    await context.bot.send_message(user_id, REMOVAL_MESSAGE)
    logging.info(f'User {user_id} removed from group')


# Responses
def handle_response(text: str) -> tuple[str, InlineKeyboardMarkup] | tuple[str, None] | tuple[Any, None]:
    if PRICES_COMMAND in text or SUBSCRIPTION_COMMAND in text:
        response: str = 'Доступные на данный момент варианты:'
        keyboard_variants = []
        for period in PERIODS.items():
            keyboard_variants.append(
                [InlineKeyboardButton(f'{period[1][0]} - {period[1][1]} рублей',
                                      callback_data=period[0])])
        reply_markup = InlineKeyboardMarkup(keyboard_variants)
        return response, reply_markup

    return HELP_MESSAGE, None


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, custom_text: str = ''):
    if update.channel_post is not None:
        return

    text = update.message.text.lower() if custom_text == '' else custom_text
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    username = 'Скрыто' if username is None else username
    logging.info(f'User {user_id}: "{text}"')

    if 'ок' in text:
        keyboard_variants = [
            [InlineKeyboardButton('Подтвердить оплату',
                                  callback_data=f'approve {user_id} {username}')],
            [InlineKeyboardButton('Отклонить',
                                  callback_data=f'decline {user_id} {username}')]
        ]
        paid_period = waiting_for_approve.get(user_id)
        await context.bot.send_message(ADMIN_ID, f'Пользователь {user_id} (Никнейм: {username}) оплатил {paid_period} месяцев подписки',
                                       reply_markup=InlineKeyboardMarkup(keyboard_variants))
        await update.message.reply_text(PAYMENT_CONFIRMATION_REQUEST)
        return

    (response, markup) = handle_response(text)
    if markup is None:
        await update.message.reply_text(response)
    else:
        await update.message.reply_text(response, reply_markup=markup)


async def handle_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith('approve'):
        user_id: int = int(query.data.split(' ')[1])
        paid_period: int = waiting_for_approve.get(user_id)
        (link, expire_time) = await add_user_to_group(user_id, paid_period, update, context)
        waiting_for_approve.pop(user_id)
        await context.bot.send_message(user_id,
                                       f'{PAYMENT_CONFIRMATION}{link}. Ваша подписка действительна до {expire_time}')
        await context.bot.send_message(user_id, RULES, parse_mode='Markdown')
        await query.edit_message_text(f'Пользователю {user_id} выдан доступ до {expire_time}')
    elif query.data.startswith('decline'):
        user_id: int = int(query.data.split(' ')[1])
        waiting_for_approve.pop(user_id)
        await context.bot.send_message(user_id, PAYMENT_REJECT)
        await query.edit_message_text(f'Пользователю {user_id} отказано в доступе')
    else:
        period: int = int(query.data)
        user_id: int = int(query.from_user.id)
        waiting_for_approve[user_id] = period
        await query.edit_message_text(
            f'Для оплаты выбранного периода ({PERIODS[period][0]}) переведите на карту {CARD_NUMBER} {PERIODS[period][1]} рублей. После подтверждения оплаты я вышлю Вам ссылку на добавление в чат.\nВАЖНО! После оплаты отправьте сообщение "ОК"')


async def remove_expired_users(context: ContextTypes.DEFAULT_TYPE) -> None:
    expired_ids = databaseHandler.check_for_expired_users()

    for user_id in expired_ids:
        if user_id != ADMIN_ID:
            await remove_user_from_group(user_id, context)


async def set_cleaning_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    if len(context.job_queue.get_jobs_by_name(EXPIRED_CLEANER_JOB)) == 0:
        context.job_queue.run_repeating(remove_expired_users, first=5, interval=CLEANER_INTERVAL_S, chat_id=chat_id, name=EXPIRED_CLEANER_JOB)
        logging.warning(f'Timer for {EXPIRED_CLEANER_JOB} started')


def main():
    logging.info('Starting bot...')
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('prices', prices_command))
    app.add_handler(CommandHandler('subscription', subscription_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(CommandHandler('error', error))

    # Buttons callbacks
    app.add_handler(CallbackQueryHandler(handle_button_callback))

    # Cleaner of expired users
    app.add_handler(CommandHandler(EXPIRED_CLEANER_JOB, set_cleaning_timer))

    logging.info('Starting polling...')
    app.run_polling(poll_interval=1, allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
