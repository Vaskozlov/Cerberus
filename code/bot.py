import os
import time
from user import *
from globals import CermerOptions
from cerbrus import Cerberus

with open("CerberousStart.log", mode="a", encoding="utf-8") as fin:
    fin.write("Bot pid: " + str(os.getpid()) + "\n")

print("Bot pid: " + str(os.getpid()) + "\n")

first_response_keyboard.row('Войти', 'Зарегистрироваться')
promocode_keyboard.row('100', '200', '300', '1000', '9999999999')
standart_keyboard.row("Упражнение", "Точность", "Пополнить слова")
add_choise.row("Купить слова", "Пригласить друга", "Ввести промокод")
cancel_keyboard.row('Отменить')

if gHideBrowsers:
    CermerOptions.headless = True

with open("data/initedUsers.txt", mode="r", encoding="utf-8") as fin:
    invitedUsers = set(fin.read().split('\n'))

for i in range(ord('A'), ord('Z') + 1):
    valid.add(chr(i))
    valid.add(chr(i + 32))

for i in range(ord('0'), ord('9') + 1):
    valid.add(chr(i))


def starter(usr, message):
    usr.message = message
    usr.loop()


def help_user_message(chat_id: int):
    try:
        help_images = [
            telebot.types.InputMediaPhoto(open(f"data/cerberus_help/cerberus_help_images/{file}", "rb")) for file in
            os.listdir("data/cerberus_help/cerberus_help_images")
        ]
        bot.send_message(chat_id, help_user_text)
        bot.send_media_group(chat_id, help_images)
    except BaseException:
        bot.send_message(chat_id,
                         "Возникла ошибка при отправке примеров использования бота. Попробуйте еще раз или обратитесь "
                         "к администратору https://t.me/confidencess.")


@bot.message_handler(commands=["help"])
def help_user(message):
    th1 = th.Thread(target=help_user_message, args=[message.chat.id])
    th1.start()


@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        chat_id: int = message.chat.id
        working_users_lock.acquire()

        if chat_id in working_users.keys():
            bot.send_message(chat_id, "Вы уже вошли в систему")
        else:
            working_users[chat_id] = user(message)
            usr = working_users[chat_id]
            usr.th = th.Thread(target=starter, args=[usr, message])
            usr.th.start()

    except BaseException:
        pass

    finally:
        working_users_lock.release()


def stop_user(chat_id: int):
    if chat_id in clientController.users_from_chat_id.keys():
        clientController.set_chat_id(clientController.users_from_chat_id[chat_id].cerberusLogin, 0)

    working_users_lock.acquire()

    if chat_id in working_users.keys():
        usr = working_users[chat_id]
        working_users_lock.release()

        if usr.cerberous is not None:
            usr.cerberous.running = False

        usr.lock.acquire()

        if usr.cerberous is not None:
            usr.cerberous.running = False

            while usr.cerberous is not None:
                if usr.status == users_statuses.main_menu:
                    break
                else:
                    time.sleep(0.1)

        usr.lock.release()

        usr.save()

        working_users_lock.acquire()

        if chat_id in working_users.keys():
            try:
                del working_users[chat_id]
            except BaseException:
                pass

    working_users_lock.release()
    bot.send_message(chat_id, "Вы вышли из системы", reply_markup=empty_keyboard)


@bot.message_handler(commands=['stop'])
def stop_message(message):
    try:
        th1 = th.Thread(target=stop_user, args=[message.chat.id])
        th1.start()

    except BaseException:
        return


@bot.message_handler(content_types=['text'])
def send_text(message):
    try:
        chat_id: int = message.chat.id

        if chat_id in working_users.keys():
            usr = working_users[chat_id]
            usr.th = th.Thread(target=starter, args=[usr, message])
            usr.th.start()
        else:
            bot.send_message(chat_id, "Вы не вошли в систему, напишите \"/start\"")

    except BaseException:
        return

bot.infinity_polling((1 << 16), (1 << 16))
print("palling ended")
