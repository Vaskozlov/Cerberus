import os
import unicodedata
from io import TextIOWrapper
import multiprocessing as ml


def add_user(path: TextIOWrapper, user):
    path.write(f"{user.id}\n")


def remove_accents(input_str: str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


def new_remove_accents(input_str: str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    answer = [c for c in nfkd_form if not unicodedata.combining(c)]

    for i in range(min(len(answer), len(input_str))):

        if (input_str[i] == 'й'):
            answer[i] = input_str[i]

        elif input_str[i] == 'Й':
            answer[i] = input_str[i]

        elif input_str[i] == 'ё':
            answer[i] = input_str[i]

        elif input_str == 'Ё':
            answer[i] = input_str[i]

    return "".join(answer)


class DataBase:

    def __init__(self, path: str):
        self.path = path
        self.base = set()
        self.file = open(self.path, "r+")
        self.lock = ml.Lock()
        self.read_base()
        self.available = True

    def __del__(self):
        print("CLOSE")

        self.available = False
        self.file.close()

    def fix(self, wrong, right):
        self.lock.acquire()

        if wrong is self.base:
            self.base.remove(wrong)
        else:
            self.lock.release()
            return

        self.base.add(right)

        if self.available:
            self.file.close()

        self.file = open(self.path, "w")

        for elem in self.base:
            self.file.write(elem + "\n")

        self.file.close()
        self.file = open(self.path, "r+")
        self.available = True

        self.lock.release()

    def add_answer(self, answer: str):
        self.lock.acquire()

        if not self.available:
            self.file = open(self.path, "r+")

        if answer not in self.base and answer is not None:
            self.base.add(answer)
            self.file.write(answer + "\n")

        self.lock.release()

    def read_base(self):
        self.lock.acquire()

        for elem in self.file.readlines():
            self.base.add(elem.strip(" \n"))

        self.lock.release()

    def find_raw(self, word: str):
        return word in self.base

    def find_in_base(self, word: str):
        return remove_accents(word) in self.base


class ClientConfig:

    def __init__(self, path: str):
        self.mistakes: int = 0
        self.answered: int = 0
        self.paid_answers: int = 100
        self.login: str = ""
        self.password: str = ""
        self.accuracy: float = 0.98
        self.informed = False
        self.cerberusLogin: str = ""
        self.cerberusPassword: str = ""
        self.name: str = ""
        self.chat_id: int = 0
        self.path = path
        self.load_config()
        self.updated = False
        self.running = False

    def null(self):
        self.mistakes = 0
        self.answered = 0

    def load_config(self):

        try:
            file = open(self.path, mode="r+")

        except BaseException:
            return

        info = file.readlines()

        for elem in info:
            elem = elem.split(":")
            elem[0] = elem[0].strip(" \n")
            elem[1] = elem[1].strip(" \n")

            if (len(elem) != 2):
                continue

            if elem[0] == 'login':
                self.login = elem[1]

            elif elem[0] == 'password':
                self.password = elem[1]

            elif elem[0] == 'paid_answers':
                self.paid_answers = int(elem[1])

            elif elem[0] == 'accuracy':
                self.accuracy = float(elem[1])

            elif elem[0] == 'informed':
                self.informed = "True" in elem[1]

            elif elem[0] == 'clogin':
                self.cerberusLogin = elem[1]

            elif elem[0] == 'cpassword':
                self.cerberusPassword = elem[1]

            elif elem[0] == 'chat_id':
                self.chat_id = int(elem[1])

            elif elem[0] == 'name':
                self.name = elem[1]

        file.close()

    def add_answer(self, correct: bool):

        if (correct == False):
            self.mistakes += 1

        self.answered += 1
        self.add_paid_aswers(-1)
        self.updated = True

    def add_paid_aswers(self, answers: int):
        self.paid_answers += answers
        self.save()

    def change_accuracy(self, new_accuracy: float):
        self.accuracy = new_accuracy
        self.save()

    def save(self):
        file = open(self.path, mode="w")

        data = f"login: {self.login}\npassword: {self.password}\npaid_answers: {self.paid_answers}\naccuracy: {self.accuracy}\ninformed: {self.informed}\nclogin: {self.cerberusLogin}\ncpassword: {self.cerberusPassword}\nchat_id: {self.chat_id}\nname: {self.name}\n"
        self.updated = False

        file.write(data)
        file.close()


class ClientController:

    def __init__(self, path):
        self.users_from_chat_id = dict()
        self.users_from_clogin = dict()
        self.cerm_logins = set()
        self.id_lock = ml.Lock()
        self.login_lock = ml.Lock()
        self.cerm_logins_lock = ml.Lock()

        for elem in os.listdir(path):
            if elem[0] == '.':
                continue

            conf = ClientConfig(f"{path}/{elem}")

            if conf.chat_id != 0:
                self.users_from_chat_id[conf.chat_id] = conf

            self.users_from_clogin[conf.cerberusLogin] = conf
            self.cerm_logins.add(conf.login)

    def add_cerm_login(self, cerm_login: str) -> None:
        self.cerm_logins_lock.acquire()
        self.cerm_logins.add(cerm_login)
        self.cerm_logins_lock.release()

    def add_user(self, user: ClientConfig):
        self.login_lock.acquire()

        self.users_from_clogin[user.cerberusLogin] = user
        self.add_cerm_login(user.login)

        self.login_lock.release()
        self.set_chat_id(user.cerberusLogin, user.chat_id)

    def get_user_from_id(self, user_id: int) -> ClientConfig:
        self.id_lock.acquire()
        user = None

        try:
            user = self.users_from_chat_id[user_id]

        except KeyError:
            pass

        finally:
            self.id_lock.release()
            return user

    def set_chat_id(self, login: str, chat_id: int):
        self.id_lock.acquire()
        self.login_lock.acquire()

        try:
            if chat_id != 0:
                self.users_from_chat_id[chat_id] = self.users_from_clogin[login]
                self.users_from_clogin[login].chat_id = chat_id
                self.users_from_clogin[login].save()

            else:
                if self.users_from_clogin[login].chat_id in self.users_from_chat_id.keys():
                    del self.users_from_chat_id[self.users_from_clogin[login].chat_id]

                self.users_from_clogin[login].chat_id = chat_id
                self.users_from_clogin[login].save()

        except BaseException:
            pass

        finally:
            self.id_lock.release()
            self.login_lock.release()

    def get_user_from_login(self, login: str) -> ClientConfig:
        self.login_lock.acquire()
        user = None

        try:
            user = self.users_from_clogin[login]

        except KeyError:
            pass

        finally:
            self.login_lock.release()
            return user

    def __del__(self):
        for elem in self.users_from_clogin.keys():
            if self.users_from_clogin[elem].updated == True:
                self.users_from_clogin[elem].save()

        print("Saving files...")
