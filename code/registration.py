import os
from cerbrus import *


def process_cerm_login_for_new_account(user):
    if user.message.text in clientController.cerm_logins or not user.check_password(user.message.text, 6):
        bot.send_message(user.chat_id, "Данный логин нельзя использовать. Введите логин еще раз.")

    else:
        user.tmp_login = user.message.text

        if user.tmp_password is None:
            bot.send_message(user.chat_id, "Введите пароль вашего аккаунта cerm.ru")


def process_cerm_password_for_new_account(user):
    if user.check_password(user.message.text, 4):
        user.tmp_password = user.message.text

    else:
        bot.send_message(user.chat_id, "Пароль может содержать только английские буквы, цифры и минимум 4 символа")


def create_new_account(user):
    user.config = db.ClientConfig(f"data/newtele/{user.tmp_login}.txt")

    user.config.login = user.tmp_login
    user.config.password = user.tmp_password
    user.config.cerberusLogin = user.login
    user.config.cerberusPassword = user.password
    user.config.chat_id = user.chat_id
    user.config.registration_time = round(time.time())
    user.config.save()

    bot.send_message(user.chat_id, "Проверяю твой аккаунт...")

    user.cerberus = Cerberus(user_config=clientController,
                              lvl_text=user.exercise2do, end_number=0, delay=20)

    user.config.name = user.cerberus.check_this_fish(user.tmp_login, user.tmp_password)

    if len(user.config.name) == 0:
        os.remove(f"data/newtele/{user.tmp_login}.txt")
        user.tmp_login = None
        user.login = None
        user.tmp_password = None
        user.password = None
        bot.send_message(user.chat_id,
                         "Не получилось войти в твой аккаунт на сайте cerm.ru. Введите логин от аккаунта cerm.ru и пароль еще раз. Введите логин от аккаунта cerm.ru.")
    else:
        user.config.save()
        bot.send_message(user.chat_id,
                         f"Проверьте информацию\nВаш логин от церма: {user.tmp_login}\nВаш пароль от церма: {user.tmp_password}\nНапишите да, если все верно, и нет, если есть ошибка")
        user.status = users_statuses.confirm_status


def cerberus_new_account(user):
    if user.tmp_login is None:
        process_cerm_login_for_new_account(user)

    elif user.tmp_password is None:
        process_cerm_password_for_new_account(user)

    if user.tmp_password is not None and user.tmp_login is not None:

        user.login = user.tmp_login
        user.password = user.tmp_password

        create_new_account(user)


def information_confirmed(user):
    clientController.add_user(user.config)

    user.config.save()
    user.authorized = True
    bot.send_message(user.chat_id,
                     f"Вы успешно вошли под вашим аккаунтом {user.config.cerberusLogin}, у вас есть {user.config.paid_answers} слов, у вас установлена точность в {int(user.config.accuracy * 100)}%",
                     reply_markup=standart_keyboard)
    user.status = users_statuses.main_menu


def information_is_not_confirmed(user):
    keyboard = telebot.types.ReplyKeyboardMarkup()
    keyboard.row("Логин церма", "Пароль церма", "Отменить")
    bot.send_message(user.chat_id, "Что вы хотите исправить?", reply_markup=keyboard)
    user.status = users_statuses.correct_status


def confirm_account_creation(user):
    if user.message.text.lower() == "да":
        information_confirmed(user)
    else:
        information_is_not_confirmed(user)


def change_registration_fields(self):
    data = self.message.text.lower()

    if data == "логин церма":
        self.tmp_login = None

    elif data == "пароль церма":
        self.tmp_password = None

    if data == "отменить":
        data = "Хорошо"

    else:
        data = "Напишите исправленную информацию"

    self.status = users_statuses.register_status
    bot.send_message(self.chat_id, data, reply_markup=empty_keyboard)
