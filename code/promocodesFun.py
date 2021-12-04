from globals import *
import random


def promocodes_level_1(self):
    bot.send_message(self.chat_id, "Сколько слов добавить в промокод?", reply_markup=promocode_keyboard)

    self.status = users_statuses.promocode_creation_status
    return


def promocodes_level_2(self, number):
    global promocodes_lock, promocodes

    promocodes_lock.acquire()
    num = random.randint(1_000_000, 1_0000_0000)

    while num in promocodes.keys():
        num = random.randint(1_000_000, 1_0000_0000)

    if self.message.text.isdecimal():
        promocodes[num] = promocode(int(self.message.text), number, self.login)

    else:
        promocodes_lock.release()
        bot.send_message(self.chat_id, "Введите число")
        return

    promocodes_lock.release()
    bot.send_message(self.chat_id, f"Промокод: {num}", reply_markup=standart_keyboard)

    self.status = users_statuses.main_menu
    return


def enter_promocode(self):
    promocodes_lock.acquire()

    if self.message.text.isdecimal() and int(self.message.text) in promocodes.keys():
        num = int(self.message.text)

        if self.login == promocodes[num].creatorLogin:
            bot.send_message(self.chat_id,
                             "Ты не можешь использовать свой же промокод. Попробуй ввести еще раз или напиши \"отменить\"")
            promocodes_lock.release()
            return

        elif self.login in invitedUsers and promocodes[num].words == 100:
            bot.send_message(self.chat_id,
                             "Ты был уже приглашен другим пользователем. Ты не можешь использовать этот промокод.")
            promocodes_lock.release()
            return

        elif promocodes[num].words == 100:
            invitedUsers.add(self.login)

            with open("data/initedUsers.txt", mode="a", encoding="utf-8") as fin:
                fin.write(self.login + "\n")

        if promocodes[num].creatorLogin not in invitedUsers:
            invitedUsers.add(promocodes[num].creatorLogin)

            with open("data/initedUsers.txt", mode="a", encoding="utf-8") as fin:
                fin.write(promocodes[num].creatorLogin + "\n")

        self.config.add_paid_aswers(promocodes[num].words)

        if promocodes[num].words2creator > 0:
            thread = th.Thread(target=addPromocode, args=[promocodes[num]])
            thread.start()

        with open("data/usedPromocods.txt", mode="a", encoding="utf-8") as fin:
            fin.write(f"{self.login} {promocodes[num].words}\n")

        del promocodes[num]
        promocodes_lock.release()

        bot.send_message(self.chat_id, f"Данный промокод существует. Теперь у вас есть {self.config.paid_answers} слов",
                         reply_markup=standart_keyboard)
        self.status = users_statuses.main_menu

    else:
        bot.send_message(self.chat_id, "Данный промокод не существует.", reply_markup=standart_keyboard)
        self.status = users_statuses.main_menu
        promocodes_lock.release()


def addPromocode(promo: promocode):
    usr = clientController.get_user_from_login(promo.creatorLogin)
    usr.add_paid_aswers(promo.words2creator)
