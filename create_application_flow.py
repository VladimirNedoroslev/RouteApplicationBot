import logging
from datetime import datetime
from io import BytesIO

import psycopg2
import qrcode
import telegram
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from application_form import ApplicationForm
from db_operations import user_exists_in_users
from settings import USER_DATA_APPLICATION_FORM, TELEGRAM_BOT_TOKEN, DB_SETTINGS


class CreateApplicationFlow:
    REASON = 1
    START_LOCATION = 2
    DESTINATION = 3
    START_TIME = 4
    END_TIME = 5
    CHECK_APPLICATION = 6


def create_application(update, context):
    user = update.message.from_user
    connection = psycopg2.connect(**DB_SETTINGS)
    user_id = str(update.message.from_user.id)
    if not user_exists_in_users(connection, user_id):
        update.message.reply_text(
            'Вы не можете составлять маршрутные листы пока не закончите регистрацию.'
            'Для этого выполните команду /register.')
        return ConversationHandler.END
    else:
        logging.info("User %s (id = %s) has started a new application", user, user.id)
        update.message.reply_text(
            'Вы начали создание заявки. Опишите кратко причину выхода. Для отмены используйте команду /cancel')

        context.user_data[USER_DATA_APPLICATION_FORM] = ApplicationForm()
        return CreateApplicationFlow.REASON


def application_reason(update, context):
    if update.message.text == '/cancel':
        return cancel_application(update, context)
    user = update.message.from_user
    context.user_data[USER_DATA_APPLICATION_FORM].reason = update.message.text
    logging.info("Reason of %s (id = %s): %s", user.first_name, user.id, update.message.text)

    update.message.reply_text(
        'Укажите геолокацию, где Вы находитесь. (Нажмите на скрепку, выберите "Геолокация" и укажите на карте Ваше местоположение)', )
    return CreateApplicationFlow.START_LOCATION


def application_start_location(update, context):
    user = update.message.from_user
    start_location = update.message.location
    context.user_data[USER_DATA_APPLICATION_FORM].start_location = start_location

    logging.info("Start location of %s (id = %s): %s", user.first_name, user.id, start_location)
    update.message.reply_text(
        'Теперь укажите геолокацию места, куда Вы направлятесь. (так же, как и в предыдущем шаге)', )
    return CreateApplicationFlow.DESTINATION


def application_destination(update, context):
    user = update.message.from_user
    destination = update.message.location
    context.user_data[USER_DATA_APPLICATION_FORM].destination = destination

    logging.info("Destination of %s (id = %s): %s", user.first_name, user.id, destination)

    update.message.reply_text(
        'Когда Вы планируете выйти? (Укажите в формате ЧЧ.ММ, например <b>23.45</b> или <b>15.20</b>)',
        parse_mode=ParseMode.HTML)
    return CreateApplicationFlow.START_TIME


def application_start_time(update, context):
    user = update.message.from_user
    try:
        input_time = datetime.strptime(update.message.text, "%H.%M")
        start_time = datetime.now().replace(hour=input_time.hour, minute=input_time.minute, second=0, microsecond=0)
        context.user_data[USER_DATA_APPLICATION_FORM].start_time = start_time

        logging.info("Start time of %s (id = %s): %s", user.first_name, user.id, update.message.text)

        update.message.reply_text(
            'Когда Вы планируете вернуться? (Укажите в формате ЧЧ.ММ, например <b>23.45</b> или <b>15.20</b>)',
            parse_mode=ParseMode.HTML)
        return CreateApplicationFlow.END_TIME
    except ValueError as exception:
        update.message.reply_text('Вы ввели неверное время. Попробуйте ещё раз.')
        return CreateApplicationFlow.START_TIME


def application_end_time(update, context):
    user = update.message.from_user
    try:
        input_time = datetime.strptime(update.message.text, "%H.%M")
        end_time = datetime.now().replace(hour=input_time.hour, minute=input_time.minute, second=0, microsecond=0)
        context.user_data[USER_DATA_APPLICATION_FORM].end_time = end_time
        logging.info("End time of %s (id = %s): %s", user.first_name, user.id, update.message.text)

        registration_form = context.user_data[USER_DATA_APPLICATION_FORM]

        reply_keyboard = [['Да', 'Нет']]
        update.message.reply_text(
            'Ваш маршрутный лист почти готов. Проверьте Ваши данные. Всё верно?\n'
            '<b>Причина</b>: {},\n<b>Дата выхода</b>: {},\n<b>Дата возвращения</b>: {}'.format(registration_form.reason,
                                                                                               registration_form.start_time,
                                                                                               registration_form.end_time),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard),
            parse_mode=ParseMode.HTML)
        return CreateApplicationFlow.CHECK_APPLICATION
    except ValueError as exception:
        update.message.reply_text('Вы ввели неверное время. Попробуйте ещё раз.')
        return CreateApplicationFlow.END_TIME


def application_check(update, context):
    if update.message.text.lower() == 'да':
        update.message.reply_text('Ваша заявка создана. Ваш QR-код:',
                                  reply_markup=ReplyKeyboardRemove()
                                  )
        context.user_data[USER_DATA_APPLICATION_FORM].user_id = str(update.message.from_user.id)
        # save_application(context.user_data[USER_DATA_APPLICATION_FORM])

        image = qrcode.make('Some QR code')
        chat_id = update.effective_chat.id
        qr_code = BytesIO()
        qr_code.name = 'qr_code.jpeg'
        image.save(qr_code, 'JPEG')
        qr_code.seek(0)
        bot = telegram.Bot(TELEGRAM_BOT_TOKEN)
        bot.send_photo(chat_id, photo=qr_code)

        user = update.message.from_user
        logging.info("User %s (id = %s) has finished application_form.", user.first_name, user.id)
    else:
        update.message.reply_text(
            'Ваша заявка составлена неправильно. Создайте её снова через команду /create_app',
            reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END


def cancel_application(update, context):
    update.message.reply_text(
        'Вы прервали создание заяки. Для того чтобы заполнить заявку введите команду /create_app.',
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
