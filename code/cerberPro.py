from globals import *
from cerbrus import *


def process_exercise_loading(user):
    if user.status == users_statuses.world_amount_status:

        user.cerberus = Cerberus(
            user_config=user.config,
            lvl_text=user.exercise2do, end_number=user.exercise_amount, delay=8
        )

        keyb = telebot.types.ReplyKeyboardMarkup()

        try:
            data = user.cerberus.load_exercise()

        except BaseException:
            data = []

        for elem in data:
            keyb.add(elem[0])

        keyb.add("Отменить")
        if len(data) > 0:
            info = [f"{elem[0]} прогресс {elem[1]}\n" for elem in data]
            bot.send_message(user.chat_id,
                             f"Выберите активное упражнение из списка. Если вам требуется выполнить неактивное упражнение, то напишите его номер вручную.\n" + "".join(info),
                             reply_markup=keyb)
        else:
            bot.send_message(user.chat_id, "Нет активных упражнений. Если вам требуется выполнить неактивное упражнение, то напишите его номер вручную", reply_markup=keyb)

        user.cerberus = None

    else:
        bot.send_message(user.chat_id, "Начните делать упражнение, чтобы просмотреть список доступных заданий")


def worlds_amount_quastion(user):
    user.exercise2do = user.message.text
    bot.send_message(user.chat_id, "Сколько слов вы хотите сделать?", reply_markup=empty_keyboard)
    user.status = users_statuses.start_execution_status


def do_exercise(user):
    user.status = users_statuses.proccessing_exercise_status

    if user.message.text.isdecimal():
        user.exercise_amount = int(user.message.text)

        if user.config.paid_answers < user.exercise_amount:
            bot.send_message(user.chat_id,
                             f"Вы не можете сделать столько слов, потому что у вас есть всего {user.config.paid_answers} слов",
                             reply_markup=standart_keyboard)
            user.status = users_statuses.main_menu
            return

        else:
            user.callback_message = bot.send_message(user.chat_id, "Упражнение выполняется... Прогресс: 0, ошибок: 0",
                                                     reply_markup=None)

            try:
                user.cerberus = Cerberus(user_config=user.config,
                                          lvl_text=user.exercise2do, end_number=user.exercise_amount, delay=8)
                result = user.cerberus.start(callback=user.callback)
                bot.send_message(user.chat_id,
                                 f"Упражнение выполнено: {result[0]}/{user.exercise_amount}, ошибок: {result[1]}, у вас есть {user.config.paid_answers} слов",
                                 reply_markup=standart_keyboard)
                user.status = users_statuses.main_menu
                user.cerberus = None
                user.callback_message = None

                if user.config.paid_answers <= 0:
                    bot.send_message(user.chat_id, f"У вас закончились слова. {Message4Consumers}")

            except BaseException as e:
                print(e)
                bot.send_message(user.chat_id, "Возникла ошибка, убедитесь в правильности номера упражнения",
                                 reply_markup=standart_keyboard)
                user.status = users_statuses.main_menu

    else:
        bot.send_message(user.chat_id, "Введите только число. Попробуйте еще раз", reply_markup=cancel_keyboard)
        user.status = users_statuses.start_execution_status
