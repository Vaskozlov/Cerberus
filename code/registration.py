import os
from globals import *
from cerbrus import *


def cerberus_new_account(self):
    if self.tmp_login == None:

        if self.message.text in clientController.cerm_logins or self.check_password(self.message.text, 6) == False:
            bot.send_message(self.chat_id, "Данный логин нельзя использовать. Введите логин еще раз.")

        else:
            self.tmp_login = self.message.text

            if self.tmp_password == None:
                bot.send_message(self.chat_id, "Введите пароль вашего аккаунта cerm.ru")

    elif self.tmp_password == None:

        if self.check_password(self.message.text, 3):
            self.tmp_password = self.message.text

            if self.login == None:
                bot.send_message(self.chat_id, "Придумайте логин для аккаунта цербера")

        else:
            bot.send_message(self.chat_id, "Пароль может содержать только английские буквы и цифры и минимум 4 символы")

    elif self.login == None:

        if self.message.text in clientController.users_from_clogin.keys() or self.check_password(self.message.text,
                                                                                                 5) == False:
            bot.send_message(self.chat_id,
                             "Данный логин нельзя использовать. Также логин должен содержать как минимум 6 символов и состоять из букв и цифр")
        else:
            self.login = self.message.text

            if self.password == None:
                bot.send_message(self.chat_id, "Придумайте пароль от аккаунта цербера")

    elif self.password == None:
        if self.check_password(self.message.text, 5):
            self.password = self.message.text
        else:
            bot.send_message(self.chat_id, "Пароль содержит запрщенные символы или короче 6 символов")

    if self.password is not None and self.tmp_password is not None and self.tmp_login is not None and self.login is not None:

        self.config = db.ClientConfig(f"data/newtele/{self.tmp_login}.txt")

        self.config.login = self.tmp_login
        self.config.password = self.tmp_password
        self.config.cerberusLogin = self.login
        self.config.cerberusPassword = self.password
        self.config.chat_id = self.chat_id
        self.config.save()

        bot.send_message(self.chat_id, "Проверяю твой аккаунт...")

        self.cerberous = Cerberus(user_config=clientController,
                                  lvl_text=self.exercise2do, end_number=0, delay=8)

        self.config.name = self.cerberous.check_this_fish(self.tmp_login, self.tmp_password)

        if len(self.config.name) == 0:
            os.remove(f"data/newtele/{self.tmp_login}.txt")
            self.tmp_login = None
            self.tmp_password = None
            bot.send_message(self.chat_id,
                             "Не получилось войти в твой аккаунт на сайте cerm.ru. Введите логин от церма и пароль еще раз. Введите логин от церма.")
        else:
            self.config.save()
            bot.send_message(self.chat_id,
                             f"Проверьте информацию\nВаш логин от церма: {self.tmp_login}\nВаш пароль от церма: {self.tmp_password}\nВаш логин для цербера: {self.login}\nВаш пароль для цербреа: {self.password}\nНапишите да, если все верно и нет, если есть ошибика")
            self.status = users_statuses.confirm_status


def confirm_account_creation(self):
    if self.message.text.lower() == "да":
        clientController.add_user(self.config)

        self.config.save()
        self.logined = True
        bot.send_message(self.chat_id,
                         f"Вы успешно вошли под вашим аккаунтом {self.config.cerberusLogin}, у вас есть {self.config.paid_answers} слов, у вас установлена точность в {int(self.config.accuracy * 100)}%",
                         reply_markup=standart_keyboard)
        self.status = users_statuses.main_menu

    else:
        keyboard = telebot.types.ReplyKeyboardMarkup()
        keyboard.row("Логин церма", "Пароль церма", "Логин цербера", "Пароль цербера", "Отменить")
        bot.send_message(self.chat_id, "Что вы хотите исправить?", reply_markup=keyboard)
        self.status = users_statuses.correct_status


def change_registration_fields(self):
    data = self.message.text.lower()

    if data == "логин церма":
        self.tmp_login = None

    elif data == "пароль церма":
        self.tmp_password = None

    elif data == "логин цербера":
        self.login = None

    elif data == "пароль цербера":
        self.password = None

    if data == "отменить":
        data = "Хорошо"
    else:
        data = "Напишите исправленную информацию"

    self.status = users_statuses.register_status
    bot.send_message(self.chat_id, data, reply_markup=empty_keyboard)
