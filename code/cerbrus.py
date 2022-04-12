import time
import random
import selenium
from globals import *
import database as db
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from driver_controller import DriverController


class Cerberus:

    def __init__(self, user_config, lvl_text, end_number, delay):
        self.last_answer = ""
        self.correct: str = ""
        self.user_config = user_config
        self.page_status = "out"
        self.statistics = {"In database": 0, "In internet": 0, "Not found": 0}
        self.lvl_text = lvl_text
        self.end_number = end_number
        self.delay = delay
        self.right = False
        self.running = False
        self.driver: webdriver.Firefox = DriverController.get_driver()

    def check_this_fish(self, login, password):  # возвращает Фамиялия Имя Отчество владельца аккаунта 
        try:
            self.driver.get("https://login.cerm.ru/")
            log = self.driver.find_element_by_name("simora_login")
            log.send_keys(login)
            pas = self.driver.find_element_by_name("simora_pass")
            pas.send_keys(password)
            pas.send_keys(Keys.ENTER)
            time.sleep(1)
            info = self.driver.find_element_by_class_name("header_content_label_ufio").text
            return info

        except BaseException:
            return ""

    def can_commit_mistake(self, n: int) -> bool:

        if self.user_config.answered == 0:
            return False

        if n > 12 and 1 - (
                (self.user_config.mistakes + 1) / (self.end_number - 1)) > self.user_config.accuracy and 1 - (
                self.user_config.mistakes / self.user_config.answered) > self.user_config.accuracy:
            return True

        return False

    def correct_mistake(self):
        elem = self.driver.find_element_by_id("trainer_rno_right")
        correct_string = db.new_remove_accents(elem.text)

        self.correct = correct_string
        self.right = False

        for _ in range(3):
            WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.ID, "prno")))
            time.sleep(1.1)
            rno_string = self.driver.find_element_by_id("prno")
            self.page_status = 'rno'
            rno_string.send_keys(correct_string)

        print(correct_string)

    def from_login_to_questions(self):
        time.sleep(0.75)
        self.page_status = 'login'
        WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.NAME, 'simora_login')))

        self.login()
        self.driver.get("https://login.cerm.ru/_user/user_app.php?mod=pwg")

        WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.TAG_NAME, 'td')))
        self.page_status = 'before_lvl'

        elem = self.driver.find_element_by_tag_name("button")

        if elem.location['x'] != 0:
            elem.click()

        tolvl = self.driver.find_elements_by_tag_name("td")

        if self.lvl_text.isdecimal():
            number = int(self.lvl_text)

            for i in range(0, len(tolvl), 1):  # при первом открытии после загрузки нового упражнения
                if tolvl[i].text.split("Упражнение")[-1].strip(' #').isdecimal():
                    if int(tolvl[i].text.split("Упражнение")[-1].strip(' #')) == number:
                        tolvl[i].click()  # ищет "Упражнение n" и нажимает
                        break  # после того, как он нажмет, нас перекинет на вопросы

        else:
            self.lvl_text = self.lvl_text.lower()

            for i in range(0, len(tolvl), 1):  # при первом открытии после загрузки нового упражнения
                if self.lvl_text in tolvl[i].text.lower():
                    tolvl[i].click()  # ищет "Упражнение n" и нажимает
                    break  # после того, как он нажмет, нас перекинет на вопросы

        time.sleep(0.5)

        button = self.driver.find_element_by_class_name("btn_yellow")

        if button.text == "Поехали":
            self.page_status = 'bad_yellow_button'
            button.click()
            time.sleep(0.5)

        elem = self.driver.find_elements_by_id("trainer_rno_right");

        if len(elem) > 0:
            self.correct_mistake()
            time.sleep(0.2)

        complete_button = self.driver.find_elements_by_class_name("button btn_yellow")

        if len(complete_button) != 0:
            self.page_status = 'lvl_complete_button'
            complete_button.click()

        time.sleep(1)
        self.page_status = 'lvl'

    def login(self):
        name_input = self.driver.find_element_by_name("simora_login")
        password_input = self.driver.find_element_by_name("simora_pass")
        name_input.send_keys(self.user_config.login)
        password_input.send_keys(self.user_config.password)
        self.driver.find_element_by_name('login_button').click()

    def logout(self):
        out_from_question = WebDriverWait(self.driver, self.delay).until(
            EC.presence_of_element_located((By.ID, 'savequit')))
        out_from_question.click()

        time.sleep(1)

        self.page_status = 'before_lvl'
        time.sleep(round(random.uniform(0.1, 1), 2))
        out_from_login = WebDriverWait(self.driver, self.delay).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'ntoast-exit-button')))

        out_from_login.click()
        self.driver.get("https://login.cerm.ru/")

    def rebuild_variant(self, massiv: list):
        for i in range(len(massiv)):

            if str(massiv[i]) == "(раздельно)":
                massiv[i] = " "
            elif str(massiv[i]) == "(слитно)" or massiv[i] == "(ничего)":
                massiv[i] = ""
            elif str(massiv[i]) == "(дефис)":
                massiv[i] = "-"

        return massiv

    def try_login(self):
        self.driver.get("https://login.cerm.ru/")
        self.from_login_to_questions()

    def start(self, callback=None):
        begin = time.time()
        question_number = 0
        self.running = True

        self.try_login()

        while question_number < self.end_number and self.running:
            if question_number & 15 == 0:
                status = "Page status: %s" % self.page_status
                print(question_number, status, self.statistics, sep='; ')

            self.right = True

            question = WebDriverWait(self.driver, self.delay).until(
                EC.presence_of_element_located((By.ID, "trainer_question")))

            reply = self.driver.execute_script("return arguments[0].lastChild.textContent;", question)
            second_text: str = reply
            all_text: str = question.text
            first_text = ''

            for i in range(len(all_text) + 1):
                first_text: str = all_text[:i]
                if first_text + second_text == all_text:
                    break

            WebDriverWait(self.driver, self.delay).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'trainer_variant')))
            variants = self.driver.find_elements_by_class_name("trainer_variant")

            button1 = variants[0]
            button2 = variants[1]

            variants = [variants[0].text, variants[1].text]
            variants = self.rebuild_variant(variants)
            variant1 = db.new_remove_accents(first_text + variants[0] + second_text)
            variant2 = db.new_remove_accents(first_text + variants[1] + second_text)

            if CermerDatabase.find_raw(variant1):
                self.page_status = "lvl"
                self.correct = variant1
                self.statistics["In database"] += 1
                self.last_answer = "db"

            elif CermerDatabase.find_raw(variant2):
                self.page_status = "lvl"
                self.correct = variant2
                self.statistics["In database"] += 1
                self.last_answer = "db"

            else:
                self.correct = variant1
                self.statistics["Not found"] += 1

            can_commit: bool = self.can_commit_mistake(min(len(variant1), len(variant2)))

            if self.correct is None:
                self.statistics["Not found"] += 1
                self.logout()
                self.from_login_to_questions()

            if self.correct == variant1:
                question_number += 1
                if can_commit:
                    button2.click()
                else:
                    button1.click()

            elif self.correct == variant2:
                question_number += 1

                if can_commit:
                    button1.click()
                else:
                    button2.click()

            try:
                time.sleep(0.5)
                for i in range(50):
                    test_element = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.ID, "trainer_question")))
                    if test_element == question:
                        time.sleep(0.1)
                    else:
                        break

            except selenium.common.exceptions.TimeoutException:

                time.sleep(1)
                try:
                    self.correct_mistake()

                except BaseException:
                    self.logout()
                    self.from_login_to_questions()

            except UnexpectedAlertPresentException:
                CermerDatabase.add_answer(self.correct)
                continue

            CermerDatabase.add_answer(self.correct)
            self.user_config.add_answer(self.right)

            if callback is not None:
                callback(self.user_config.answered, self.user_config.mistakes)

        out_from_question = WebDriverWait(self.driver, self.delay).until(
            EC.presence_of_element_located((By.ID, 'savequit'))
        )

        out_from_question.click()
        answer = [self.user_config.answered, self.user_config.mistakes]
        self.user_config.null()

        time.sleep(1)
        elapsed_time = time.time() - begin

        for key in self.statistics:
            print(key, ": ", self.statistics[key])

        print("Elapsed time: ", elapsed_time)

        DriverController.release_driver(self.driver)
        self.driver = None

        self.user_config.save()
        self.running = False
        return answer

    def __del__(self):
        DriverController.release_driver(self.driver)
        self.driver = None

    def load_exercise(self) -> list:
        exercise_information = []

        try:
            self.driver.get("https://login.cerm.ru/")
            time.sleep(0.1)
            self.page_status = 'login'
            WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.NAME, 'simora_login')))

            self.login()
            self.driver.get("https://login.cerm.ru/_user/user_app.php?mod=pwg")

            WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.TAG_NAME, 'td')))
            opened_exercises = self.driver.find_elements_by_class_name(
                "exerciseOpen")  # содержит всю инфу про упражнениях

            for j in range(len(opened_exercises)):

                information = opened_exercises[j].text.split('\n')

                if " с " in information[0]:
                    index = information[0].index(" с ")
                else:
                    index = len(information[0]) + 1

                exercise_information.append([
                    information[0][
                    information[0].index(" - ") + 3:
                    index
                    ],  # Берет назание и номер упражнения из 1 строчки
                    information[-1]  # Берет прогресс из 3 строчки целиком
                ])

        except BaseException:
            self.user_config.null()

        DriverController.release_driver(self.driver)
        self.driver = None

        self.user_config.save()
        return exercise_information
