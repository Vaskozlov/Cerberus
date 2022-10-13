from loginIN import *
from adminFunctionality import *
from cerberPro import *
from promocodesFun import *
from registration import *


class user:

    def __init__(self, message):
        self.lock = th.Lock()
        self.th = None
        self.running = False
        self.status = users_statuses.just_logined
        self.authorized = False
        self.cerberus = None
        self.chat_id = message.chat.id
        self.login = None
        self.password = None
        self.exercise_amount = 0
        self.exercise2do = None
        self.message = None
        self.tmp_login = None
        self.tmp_password = None
        self.config: db.ClientConfig = None
        self.callback_message = None

    def callback(self, a, b):
        try:
            bot.edit_message_text(chat_id=self.chat_id, message_id=self.callback_message.message_id,
                                  text=f"Упражнение выполняется... Прогресс: {a}, ошибок: {b}")
        except BaseException:
            pass

    def check_password(self, data, size):
        global valid

        if len(data) < size:
            return False

        for elem in data:
            if elem not in valid:
                return False

        return True

    def default_choice(self):
        data = self.message.text.lower()

        if data == "упражнение":
            bot.send_message(self.chat_id, "Подождите загрузки активных упражнений.", reply_markup=empty_keyboard)
            self.status = users_statuses.world_amount_status
            process_exercise_loading(self)

        elif data == "точность":
            bot.send_message(self.chat_id,
                             f"Введите новую точность в процентах %, текущая {int(self.config.accuracy * 100)}%",
                             reply_markup=cancel_keyboard)
            self.status = users_statuses.accuracy_status

        elif data == "пополнить слова":
            bot.send_message(self.chat_id,
                             "Выберите вариант пополнения слов. При приглашении друга вы получите 200 слов, а ваш друг 100 слов.",
                             reply_markup=add_choise)
            self.status = users_statuses.promocode_status

    def change_accuracy(self):
        try:
            data = float(self.message.text.strip(" %"))

            if data < 75 or data > 100:
                raise BaseException

            self.config.change_accuracy(data / 100.0)
            self.status = users_statuses.main_menu

            bot.send_message(self.chat_id, "Вы успешно установили точность: " + str(int(data)) + "%",
                             reply_markup=standart_keyboard)

        except BaseException:
            bot.send_message(self.chat_id,
                             f"Введите число в диапозоне от 75 до 100. Если у вас возникла ошибка, то обратитесь к администратору {publicAdmins}.")

    def cancel_action(self):

        if self.config != None:
            self.config.running = False

        self.lock.acquire()

        try:

            if self.status == users_statuses.correct_status:
                self.login = ""
                self.password = ""
                self.tmp_login = ""
                self.tmp_password = ""

            if self.authorized:

                while self.cerberus != None:
                    if self.status == users_statuses.main_menu:
                        break
                    else:
                        time.sleep(0.2)

                self.status = users_statuses.main_menu
                bot.send_message(self.chat_id, "Хорошо", reply_markup=standart_keyboard)
            else:
                bot.send_message(self.chat_id, "Привет, что ты хочешь сделать? Если нужна помощь, то напиши /help.",
                                 reply_markup=first_response_keyboard)
                self.status = users_statuses.none

        except BaseException:
            pass

        finally:
            self.lock.release()

    def send_message_to_admin(self):
        chat_id = 664322462  # Maximosa
        data = f"support request from {self.config.cerberusLogin} \nmessage: {' '.join(self.message.text.split(' ')[1:])}"
        bot.send_message(chat_id, data)
        bot.send_message(self.chat_id, "Сообщение в поддержку отправлено")

    def loop(self):
        global bot, user_configs
        self.message.text = self.message.text.strip(" \n")
        lowercase = self.message.text.lower()
        first_word = lowercase.split(' ')[0]

        if lowercase == "отменить" or lowercase == "cancel":
            self.cancel_action()
            return

        if self.lock.locked():
            bot.send_message(self.chat_id, "Подождите выполнения команды")
            return

        self.lock.acquire()

        try:

            if lowercase == "admin" and self.login in admins:
                if self.login not in working_admins:
                    working_admins.add(self.login)
                    bot.send_message(self.chat_id, "Вы вошли в качестве админа")
                else:
                    working_admins.remove(self.login)
                    bot.send_message(self.chat_id, "Теперь вы больше не админ")

            if self.status == users_statuses.public_message_status:
                send_public_message(self)

            elif self.login in working_admins:
                if lowercase == "пополнить слова":
                    promo_codes_level_1(self)

                elif lowercase == "рассылка" or lowercase == "public":
                    public_message(self)

                elif lowercase == "пользователи" or lowercase == "users":
                    show_users(self)

                elif first_word == "новые" or first_word == "new":
                    show_users_with_time(self)

                elif first_word == "лично" or first_word == "private":
                    send_private_message(self)

                elif first_word == "fish":
                    get_fish_info(self)

                elif first_word == "zero":
                    zero_chat_id(self)

                elif lowercase == "использованные" or lowercase == "used":
                    with open("data/usedPromocods.txt", mode="r", encoding="utf-8") as fin:
                        data = fin.read()

                    bot.send_message(self.chat_id, data)

                elif lowercase == "сообщения" or lowercase == "messages":
                    with open("data/messages.txt", mode="r", encoding="utf-8") as fin:
                        bot.send_message(self.chat_id, fin.read())

            if first_word == "поддержка" or first_word == "support":
                self.send_message_to_admin()

            if self.status == users_statuses.main_menu:
                self.default_choice()

            elif self.status == users_statuses.login_status:
                bot.send_message(self.chat_id, "Напишите ваш пароль")
                self.login = self.message.text
                self.status = users_statuses.enter_password_status

            elif self.status == users_statuses.enter_password_status:
                cerberus_login(self)

            elif self.status == users_statuses.register_status:
                cerberus_new_account(self)

            elif self.status == users_statuses.confirm_status:
                confirm_account_creation(self)

            elif self.status == users_statuses.correct_status:
                change_registration_fields(self)

            elif self.status == users_statuses.world_amount_status:
                worlds_amount_quastion(self)

            elif self.status == users_statuses.start_execution_status:
                do_exercise(self)

            elif self.status == users_statuses.accuracy_status:
                self.change_accuracy()

            elif self.status == users_statuses.promocode_status:

                if lowercase == "купить слова":
                    bot.send_message(self.chat_id, Message4Consumers, reply_markup=standart_keyboard)
                    self.status = users_statuses.main_menu

                elif lowercase == "пригласить друга":
                    self.message.text = "100"
                    promo_codes_level_2(self, 200)
                    self.status = users_statuses.main_menu
                    bot.send_message(self.chat_id,
                                     "Этот промокод должен ввести твой друг, чтобы ты и он получили слова.")

                elif lowercase == "ввести промокод":
                    bot.send_message(self.chat_id, "Введите ваш промокод", reply_markup=empty_keyboard)
                    self.status = users_statuses.enteringPromo

            elif self.status == users_statuses.enteringPromo:
                enter_promocode(self)

            elif self.status == users_statuses.just_logined:
                bot.send_message(self.chat_id, "Привет, что ты хочешь сделать? Если нужна помощь, то напиши /help.",
                                 reply_markup=first_response_keyboard)
                self.status = users_statuses.wait_status

            elif self.status == users_statuses.promocode_creation_status:
                promo_codes_level_2(self, 10)

            elif self.message is not None:
                first_response(self)

        except BaseException as e:
            print(e)

        finally:
            self.lock.release()

    def save(self):
        if self.config is not None and self.config.updated:
            self.config.save()
