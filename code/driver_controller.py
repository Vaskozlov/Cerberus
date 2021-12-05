import sys
from globals import *
import multiprocessing as ml
from collections import deque
from selenium import webdriver


class driver_controller:
    def __init__(self):
        self.add_lock: ml.Lock = ml.Lock()
        self.take_lock: ml.Lock = ml.Lock()
        self.drivers: deque = deque()
        self.add_driver()
        self.add_driver()

    def add_driver(self):
        self.add_lock.acquire()

        if sys.platform == "linux" or sys.platform == "darwin":
            server_log_path = "/dev/null"
            self.drivers.append(webdriver.Firefox(executable_path=ChromeDriverWay,
                                                  options=CermerOptions, service_log_path=server_log_path))
        else:
            self.drivers.append(webdriver.Firefox(executable_path=ChromeDriverWay,
                                                  options=CermerOptions))

        self.add_lock.release()

    def get_driver(self) -> webdriver:
        self.take_lock.acquire()

        if len(self.drivers) == 0:
            self.add_driver()

        driver = self.drivers.popleft()

        self.take_lock.release()

        return driver

    def release_driver(self, driver: webdriver) -> None:
        if driver is None:
            return

        self.add_lock.acquire()
        self.drivers.append(driver)
        self.add_lock.release()

    def __del__(self):
        for driver in self.drivers:
            try:
                driver.quit()
                driver.close()
            except BaseException:
                pass


DriverController: driver_controller = driver_controller()
