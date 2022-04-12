from globals import *


def try_to_login(user):
    if user.chat_id in clientController.users_from_chat_id.keys():
        user.config = clientController.get_user_from_id(user.chat_id)
        bot.send_message(user.chat_id,
                         f"Вы успешно вошли под вашим аккаунтом {user.config.cerberusLogin}, у вас есть {user.config.paid_answers} слов, у вас установлена точность в {int(user.config.accuracy * 100)}%",
                         reply_markup=standart_keyboard)
        user.login = user.config.cerberusLogin
        user.password = user.config.cerberusPassword
        user.status = users_statuses.main_menu
        user.logined = True

        if user.config.paid_answers == 0:
            bot.send_message(user.chat_id, f"У вас закончились слова. {Message4Consumers}")

    else:
        user.status = users_statuses.login_status
        bot.send_message(user.chat_id, "Напишите ваш логин от цербера", reply_markup=empty_keyboard)


def register(user):
    user.tmp_login = None
    user.tmp_password = None
    user.login = None
    user.password = None
    bot.send_message(user.chat_id, "Напишите ваш логин от аккаунта cerm.ru", reply_markup=empty_keyboard)
    user.status = users_statuses.register_status


def first_response(user):
    global clientController, bot

    data = user.message.text.lower()

    if data == "войти":
        try_to_login(user)

    elif data == "зарегистрироваться":
        register(user)

    user.message = None


def cerberus_login(self):
    self.password = self.message.text

    try:
        if self.login in clientController.users_from_clogin.keys() and clientController.get_user_from_login(
                self.login).cerberusPassword == self.password:
            usr = clientController.get_user_from_login(self.login)

            if usr.chat_id != self.chat_id and usr.chat_id != 0:
                bot.send_message(self.chat_id, "Другой телеграмм аккаунт уже работает с этим аккаунтом")
                del working_users[self.chat_id]
                return

            else:
                self.config = clientController.get_user_from_login(self.login)
                bot.send_message(self.chat_id,
                                 f"Вы успешно вошли под вашим аккаунтом {self.config.cerberusLogin}, у вас есть {self.config.paid_answers} слов, у вас установлена точность в {int(self.config.accuracy * 100)}%",
                                 reply_markup=standart_keyboard)

                clientController.set_chat_id(self.login, self.chat_id)

                self.status = users_statuses.main_menu
                self.logined = True

        else:
            bot.send_message(self.chat_id, "Неверный логин или пароль, попробуйте еще раз")
            self.status = users_statuses.login_status

    except BaseException:
        pass
