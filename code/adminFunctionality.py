from globals import *


def log_message(message):
    with open("data/messages.txt", mode="a", encoding="utf-8") as fin:
        fin.write(message)


def public_message(user):
    bot.send_message(user.chat_id, "Введите сообщение, которое хотите отправить всем пользователям")
    user.status = users_statuses.public_message_status


def send_public_message(user):
    clientController.login_lock.acquire()

    for chat_id in clientController.users_from_chat_id.keys():
        try:
            bot.send_message(chat_id, user.message.text)
        except BaseException:
            pass

    log_message(
        f"To all, from {user.config.cerberusLogin}, data = {user.message.text}\n")

    user.status = users_statuses.main_menu
    clientController.login_lock.release()


def show_users(user):
    data = []
    clientController.login_lock.acquire()

    for elem in clientController.users_from_clogin.keys():
        usr = clientController.users_from_clogin[elem]
        data.append(f"{usr.name} - {usr.chat_id}, {usr.cerberusLogin}\n")

    clientController.login_lock.release()
    data.sort()
    bot.send_message(user.chat_id, "".join(data))


def send_private_message(user):
    split_text = user.message.text.split(' ')

    try:
        try_to_send_private_message_by_id(split_text, user)
    except BaseException:
        try_to_send_private_message_by_login(split_text, user)

    bot.send_message(user.chat_id, "Сообщение отправлено получателю (наверное)")


def try_to_send_private_message_by_id(split_text, user):
    chat_id = int(split_text[1])

    if chat_id not in clientController.users_from_chat_id.keys():
        bot.send_message(user.chat_id, "Данный пользователь не обнаружен")
        return

    data = split_text[2]

    for elem in split_text[3:]:
        data += " " + elem

    log_message(
        f"To {clientController.get_user_from_id(chat_id).cerberusLogin}, from {user.config.cerberusLogin}, data = {data}\n")

    bot.send_message(chat_id, data)


def try_to_send_private_message_by_login(split_text, user):
    if split_text[1] not in clientController.users_from_clogin.keys():
        bot.send_message(user.chat_id, "Данный пользователь не обнаружен")
        return

    try:
        data = split_text[2]

        for elem in split_text[3:]:
            data += " " + elem

        log_message(
            f"To {clientController.get_user_from_login(split_text[1]).cerberusLogin}, from {user.config.cerberusLogin}, data = {data}\n")

        bot.send_message(clientController.get_user_from_login(split_text[1]).chat_id, data)
    except BaseException:
        pass


def get_fish_info(self):
    info = self.message.text.split(' ')

    try:
        usr = clientController.get_user_from_login(info[1])
        data = f"name: {usr.name}, clogin: {usr.cerberusLogin}, cpassword: {usr.cerberusPassword}, login: {usr.login}, password: {usr.password}, paid_answers: {usr.paid_answers}"
        bot.send_message(self.chat_id, data)

    except BaseException:
        bot.send_message(self.chat_id, "Возникла ошибка")


def zero_chat_id(user):
    name = user.message.text.split(' ')[1]
    if name not in clientController.users_from_clogin.keys():
        bot.send_message(user.chat_id, "Данный пользователь не обнаружен")
        return

    clientController.set_chat_id(name, 0)
    bot.send_message(user.chat_id, f"chat_id {name} теперь 0")



