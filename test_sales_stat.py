# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, os
import datetime


class AppDynamicsJob(unittest.TestCase):
    def setUp(self):
        self.drivers = [webdriver.Chrome(), webdriver.Firefox()]
        # ниже пример для удалённого запуска
        # self.driver = webdriver.Remote("http://192.168.1.43:4444/wd/hub",
        #                                desired_capabilities={"browserName": "chrome"})
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True

    def test_app_dynamics_job(self):
        for driver in self.drivers:
            driver.implicitly_wait(30)
            driver.get("https://sales.shell-azs.ru/")
            driver.maximize_window()
            driver.find_element_by_id("loginFormEmail").clear()
            driver.find_element_by_id("loginFormEmail").send_keys("vk@forifelse.com")
            driver.find_element_by_id("loginFormPassword").clear()
            driver.find_element_by_id("loginFormPassword").send_keys("12qwaszx")
            driver.find_element_by_xpath(
                u"(.//*[normalize-space(text()) and normalize-space(.)='Забыли пароль?'])[1]/following::button[1]").click()
            # Объявление переменных
            date = datetime.datetime.today().strftime("%Y-%m-%d-%H%M%S")
            da_te = datetime.datetime.today().strftime("%Y-%m-%d")
            try:
                os.mkdir(f'./stat/{da_te}')
            except:
                None
            if 'chrome' in str(driver.name):
                brauz = 'cr'
            elif 'firefox' in str(driver.name):
                brauz = 'ff'

            # Работа с Начальной страницей
            all_fuel = driver.find_element_by_xpath("//div[text()='Продажи топлива, л.']/../div[3]/div").text
            all_shop = driver.find_element_by_xpath("//div[@id='block-shop']/div[2]/div[2]/div[3]/div").text
            time.sleep(3)
            driver.save_screenshot(f'./stat/{da_te}/{date}-1start_{brauz}.png')

            # Переход на пенетрацию и конверсию
            driver.find_element_by_link_text(u"Пенетрация").click()
            time.sleep(1)  # Хром почему-то тупит, если нет паузы между кликами
            driver.find_element_by_link_text(u"Конверсии").click()
            all_pen = driver.find_element_by_xpath("//div[text()='Пенетрация бензинов, %']/../div[3]/div").text
            all_konv = driver.find_element_by_xpath("//div[text()='Конверсия по магазину']/../div[3]/div").text
            time.sleep(3)
            driver.save_screenshot(f'./stat/{da_te}/{date}-2konv_{brauz}.png')

            # Переход на трафик
            driver.find_element_by_link_text(u"Трафик").click()
            all_traf = driver.find_element_by_xpath(
                "//div[text()='Траффик (все сорта), шт.']/../div[3]/div").text
            time.sleep(3)
            driver.save_screenshot(f'./stat/{da_te}/{date}-3traf_{brauz}.png')

            # Переход на Топливо
            driver.find_element_by_link_text(u"Топливо").click()
            time.sleep(3)
            driver.save_screenshot(f'./stat/{da_te}/{date}-4fuel_{brauz}.png')

            # Переход на Магазин
            driver.find_element_by_link_text(u"Магазин").click()
            time.sleep(3)
            driver.save_screenshot(f'./stat/{da_te}/{date}-5shop_{brauz}.png')

            # Переход на Site Review
            driver.find_element_by_link_text(u"Site Review").click()
            time.sleep(3)
            driver.save_screenshot(f'./stat/{da_te}/{date}-6sr_{brauz}.png')

            # Переход на Планы
            driver.find_element_by_link_text(u"Планы").click()
            time.sleep(3)
            driver.save_screenshot(f'./stat/{da_te}/{date}-7plans_{brauz}.png')

            file_log = './stat/stat_log.txt'
            with open(file_log, 'a+') as f:
                f.seek(0)
                f.write(
                    f"{date}-{brauz} fuel: {all_fuel} shop: {all_shop} pen: {all_pen} konv: {all_konv} traf: {all_traf}\n")

            driver.quit()

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e:
            return False
        return True

    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException as e:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True

    def tearDown(self):
        # To know more about the difference between verify and assert,
        # visit https://www.seleniumhq.org/docs/06_test_design_considerations.jsp#validating-results
        self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittest.main()
