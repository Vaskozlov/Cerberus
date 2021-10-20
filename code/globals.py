import sys
import enum
from selenium.webdriver import safari
from selenium.webdriver.common import keys
import telebot
import threading as th
import database as db
from selenium.webdriver.firefox.options import Options


class users_statuses(enum.Enum):
    wait_status = 0
    none = -1
    main_menu = -2
    just_logined = -3
    login_status = 1
    enter_password_status = 2
    register_status = 10
    confirm_status = 11
    correct_status = 12
    world_amount_status = 20
    start_execution_status = 21
    accuracy_status = 25
    promocode_status = 30
    promocode_creation_status = 1002
    public_message_status = 2000
    proccessing_exercise_status = 50
    enteringPromo = 3104


class promocode:

    def __init__(self, words, words2creator, creatorLogin):
        self.words = words
        self.words2creator = words2creator
        self.creatorLogin = creatorLogin


promocodes = dict()
invitedUsers = set()
valid = set()
all_users = set()

"""
100 - 50₽
350 - 170₽
500 - 200₽
1200 - 400₽
Безлимит - 1000₽
"""

working_admins = set()
prices = {100: 50, 350: 170, 500: 200, "безлимит": 1000}

gHideBrowsers = False
admins = {"vaskozlov", "Maximosa", "QWERTY", "Bulka"}
publicAdmins = "https://t.me/confidencess"
cardNumbers = "5469 7200 1557 6693"

CermerDatabase = db.DataBase("data/new_base2.txt")
working_users_lock = th.Lock()
promocodes_lock = th.Lock()

standart_keyboard = telebot.types.ReplyKeyboardMarkup()
empty_keyboard = telebot.types.ReplyKeyboardRemove()
promocode_keyboard = telebot.types.ReplyKeyboardMarkup()
first_response_keyboard = telebot.types.ReplyKeyboardMarkup()
cancel_keyboard = telebot.types.ReplyKeyboardMarkup()
add_choise = telebot.types.ReplyKeyboardMarkup()

clientController = db.ClientController("data/newtele")
working_users = dict()
bot = telebot.TeleBot("1463835745:AAEsUMnybJNU5GFzXr_FAqRz7lY6qyEg4Mg")

if sys.platform == "linux":
    ChromeDriverWay = "/usr/bin/geckodriver"
elif sys.platform == "darwin":
    ChromeDriverWay = "/opt/homebrew/bin/geckodriver"
else:
    ChromeDriverWay = "/opt/homebrew/bin/geckodriver"

CermerOptions: Options = Options()

if gHideBrowsers:
    CermerOptions.headless = True

CermerDatabase: db.DataBase = db.DataBase("data/new_base2.txt")
Message4Consumers = f"Вы можете приобрести любой пакет слов из перечисленных:\n"

for elem in prices.keys():
    if isinstance(elem, int):
        Message4Consumers += f"{elem} cлов за {prices[elem]} ₽\n"
    else:
        Message4Consumers += f"{elem} за {prices[elem]} ₽\n"

Message4Consumers += f"Для покупки переведите деньги по этому номеру карты {cardNumbers}, а после напишите админу {publicAdmins}"
help_message_text = ""
with open (data/cerberous_help.txt, mode-'r') as fin:
    help_user_text = fin.read()
