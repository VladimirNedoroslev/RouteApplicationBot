import logging

from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

from db_operations import save_user, user_exists, update_user
from settings import USER_DATA_REGISTRATION_FORM


class RegistrationForm:
    def __init__(self):
        self.pin = None
        self.full_name = None
        self.phone_number = None

    def is_complete(self) -> bool:
        return all([self.pin, self.full_name, self.phone_number])

    def reset(self):
        self.__init__()

    def __str__(self):
        return 'pin = {}, name = {}, phone number = {}'.format(self.pin, self.full_name,
                                                               self.phone_number)


PIN = 1
FULL_NAME = 2
PHONE_NUMBER = 3


def start_registration(update, context):
    user = update.message.from_user
    if user_exists(str(user.id)):
        update.message.reply_text(
            'Вы начали процесс изменения своих данных. Для отмены используйте команду /cancel')
    else:
        update.message.reply_text(
            'Вы начали процесс регистрации. Для отмены используйте команду /cancel.')

    update.message.reply_text('Пожалуйста введите Ваше ФИО.')
    context.user_data[USER_DATA_REGISTRATION_FORM] = RegistrationForm()

    logging.info("User has started registration process %s (id = %s)", user.first_name, user.id)

    return FULL_NAME


def full_name(update, context):
    message_text = update.message.text
    if message_text == '/cancel':
        return cancel(update, context)

    context.user_data[USER_DATA_REGISTRATION_FORM].full_name = message_text

    user = update.message.from_user
    logging.info("Full name of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(
        'Хорошо, {}, Теперь введите ваш ПИН (персональный идентификационный номер) он указан в паспорте (14 цифр)'.format(
            message_text))

    return PIN


def pin(update, context):
    message_text = update.message.text
    if message_text == '/cancel':
        return cancel(update, context)
    if len(message_text) != 14:
        update.message.reply_text('Персональный номер должен быть длиной 14 символов. Попробуйте ещё раз')
        return PIN
    if not message_text.isnumeric():
        update.message.reply_text('Ваш персональный номер содержит недопустимые символы. Попробуйте ещё раз ')
        return PIN

    context.user_data[USER_DATA_REGISTRATION_FORM].pin = message_text

    user = update.message.from_user
    logging.info("Pin of %s (id = %s): %s", user.first_name, user.id, message_text)

    send_contact_button = KeyboardButton(text="Отправить свой номер телефона", request_contact=True)
    update.message.reply_text(
        'Мне осталось узнать Ваш номер телефона - для этого нажмите на кнопку "Отправить свой номер телефона".\nЕсли '
        'Вы не видите кнопку, то нажмите на иконку слева от скрепки в поле ввода сообщений.',
        reply_markup=ReplyKeyboardMarkup([[send_contact_button]]))

    return PHONE_NUMBER


def phone_number(update, context):
    user_phone_number = update.effective_message.contact.phone_number

    context.user_data[USER_DATA_REGISTRATION_FORM].phone_number = user_phone_number

    update.message.reply_text(
        'Отлично, всё готово! Теперь Вы можете создавать маршрутные листы через команды:\n/create_app - для '
        'физических лиц\n/create_org_app - для юридических лиц', reply_markup=ReplyKeyboardRemove())

    user = update.message.from_user
    logging.info("Phone number of %s (id = %s): %s", user.first_name, user.id, user_phone_number)

    if context.user_data[USER_DATA_REGISTRATION_FORM].is_complete():
        user_id = str(update.message.from_user.id)
        if user_exists(user_id):
            update_user(user_id, context.user_data[USER_DATA_REGISTRATION_FORM])
        else:
            chat_id = update.effective_chat.id
            save_user(user_id, chat_id, context.user_data[USER_DATA_REGISTRATION_FORM])

    else:
        update.message.reply_text('При Вашей регистрации произошла ошибка. Попробуйте позже.')
    return ConversationHandler.END


def cancel(update, context):
    if user_exists(str(update.message.from_user.id)):
        update.message.reply_text(
            'Вы прервали процесс изменения своих данных. Запустить его снова можно через команду /change_info',
            reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text(
            'Вы прервали регистрацию. Пока Вы не заполните все данные, Вы не сможете заполнять заявки. Начать '
            'регистрацию можно через команду /register',
            reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def get_registration_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('register', start_registration),
                      CommandHandler('change_info', start_registration)],
        states={
            PIN: [MessageHandler(Filters.text, pin)],
            FULL_NAME: [MessageHandler(Filters.text, full_name)],
            PHONE_NUMBER: [MessageHandler(Filters.contact, phone_number)],
        },
        fallbacks={CommandHandler('cancel', cancel)}
    )
