from globals import *
from cerbrus import *


def process_exercise_loading(self):
    if self.status == users_statuses.world_amount_status:

        self.cerberous = Cerberus(
            user_config=self.config,
            lvl_text=self.exercise2do, end_number=self.exercise_amount, delay=8
        )

        keyb = telebot.types.ReplyKeyboardMarkup()

        try:
            data = self.cerberous.load_exercise()

        except BaseException:
            data = []

        for elem in data:
            keyb.add(elem[0])

        if len(data) > 0:
            info = [f"{elem[0]} прогресс {elem[1]}\n" for elem in data]
            keyb.add("Отменить")
            bot.send_message(self.chat_id,
                             f"Выберите упражнение из списка или напишите номер любого.\n" + "".join(info),
                             reply_markup=keyb)
        else:
            bot.send_message(self.chat_id, "Нет активных упражнений.", reply_markup=standart_keyboard)
            self.status = users_statuses.main_menu

        self.cerberous = None

    else:
        bot.send_message(self.chat_id, "Начните делать упражнение, чтобы просмотреть список доступных заданий")


def worlds_amount_quastion(self):
    self.exercise2do = self.message.text
    bot.send_message(self.chat_id, "Сколько слов вы хотите сделать?", reply_markup=empty_keyboard)
    self.status = users_statuses.start_execution_status


def do_exercise(self):
    self.status = users_statuses.proccessing_exercise_status

    if self.message.text.isdecimal():
        self.exercise_amount = int(self.message.text)

        if self.config.paid_answers < self.exercise_amount:
            bot.send_message(self.chat_id,
                             f"Вы не можете сделать столько слов, потому что у вас есть всего {self.config.paid_answers} слов",
                             reply_markup=standart_keyboard)
            self.status = users_statuses.main_menu
            return

        else:
            self.callback_message = bot.send_message(self.chat_id, "Упражнение выполняется... Прогресс: 0, ошибок: 0",
                                                     reply_markup=None)

            try:

                self.cerberous = Cerberus(user_config=self.config,
                                          lvl_text=self.exercise2do, end_number=self.exercise_amount, delay=8)

                result = self.cerberous.start(callback=self.callback)

                bot.send_message(self.chat_id,
                                 f"Упражнение выполнено: {result[0]}/{self.exercise_amount}, ошибок: {result[1]}, у вас есть {self.config.paid_answers} слов",
                                 reply_markup=standart_keyboard)
                self.status = users_statuses.main_menu
                self.cerberous = None
                self.callback_message = None

                if self.config.paid_answers <= 0:
                    bot.send_message(self.chat_id, f"У вас закончились слова. {Message4Consumers}")

            except BaseException as e:
                bot.send_message(self.chat_id, "Возникла ошибка, убедитесь в правильности номера упражнения",
                                 reply_markup=standart_keyboard)
                self.status = users_statuses.main_menu

    else:
        bot.send_message(self.chat_id, "Введите только число. Попробуйте еще раз", reply_markup=cancel_keyboard)
        self.status = users_statuses.start_execution_status
