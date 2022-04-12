from globals import *


def log_message(message):
    with open("data/messages.txt", mode="a", encoding="utf-8") as fin:
        fin.write(message)


def public_message(self):
    bot.send_message(self.chat_id, "Введите сообщение, которое хотите отправить всем пользователям")
    self.status = users_statuses.public_message_status


def send_public_message(self):
    clientController.login_lock.acquire()

    for chat_id in clientController.users_from_chat_id.keys():
        try:
            bot.send_message(chat_id, self.message.text)
        except BaseException:
            pass

    self.status = users_statuses.main_menu
    clientController.login_lock.release()


def show_user(self):
    data = []
    clientController.login_lock.acquire()

    for elem in clientController.users_from_clogin.keys():
        usr = clientController.users_from_clogin[elem]
        data.append(f"{usr.name} - {usr.chat_id}, {usr.cerberusLogin}\n")

    log_message(
        f"To all, from {self.config.cerberusLogin}, data = {data}\n")

    clientController.login_lock.release()
    data.sort()
    bot.send_message(self.chat_id, "".join(data))


def send_private_message(self):
    info = self.message.text.split(' ')

    try:
        chat_id = int(info[1])

        if chat_id not in clientController.users_from_chat_id.keys():
            bot.send_message(self.chat_id, "Данный пользователь не обнаружен")
            return

        data = info[2]

        for elem in info[3:]:
            data += " " + elem

        log_message(
            f"To {clientController.get_user_from_id(chat_id).cerberusLogin}, from {self.config.cerberusLogin}, data = {data}\n")

        bot.send_message(chat_id, data)

    except BaseException:

        if info[1] not in clientController.users_from_clogin.keys():
            bot.send_message(self.chat_id, "Данный пользователь не обнаружен")
            return

        try:
            data = info[2]
            for elem in info[3:]:
                data += " " + elem

            with open("data/messages.txt", mode="a", encoding="utf-8") as fin:
                fin.write(
                    f"To {clientController.get_user_from_login(info[1]).cerberusLogin}, from {self.config.cerberusLogin}, data = {data}\n")

            bot.send_message(clientController.get_user_from_login(info[1]).chat_id, data)
        except BaseException:
            pass

    bot.send_message(self.chat_id, "Сообщение отправлено получателю")


def get_fish_info(self):
    info = self.message.text.split(' ')

    try:
        usr = clientController.get_user_from_login(info[1])
        data = f"name: {usr.name}, clogin: {usr.cerberusLogin}, cpassword: {usr.cerberusPassword}, login: {usr.login}, password: {usr.password}, paid_answers: {usr.paid_answers}"
        bot.send_message(self.chat_id, data)

    except BaseException:
        bot.send_message(self.chat_id, "Возникла ошибка")
