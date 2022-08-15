# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.select import Select
import unittest
import time
import os

from work_with_MailMarge import bd_retail_stations
from dotenv import load_dotenv
from writeExcel import totalTable

load_dotenv('token.env')
LOGIN = os.getenv('LOGIN')
PASS = os.getenv('PASS')
LOGIN_CHAP = os.getenv('LOGIN_CHAP')
PASS_CHAP = os.getenv('PASS_CHAP')


class AppDynamicsJob(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True

    def test_conv(self):
        self.driver.implicitly_wait(10)
        self.driver.get("https://sales.teboil-azs.ru/")
        self.driver.maximize_window()
        self.driver.find_element_by_id("loginFormEmail").clear()
        self.driver.find_element_by_id("loginFormEmail").send_keys(LOGIN)
        self.driver.find_element_by_id("loginFormPassword").clear()
        self.driver.find_element_by_id("loginFormPassword").send_keys(PASS)
        self.driver.find_element_by_xpath(
            u"(.//*[normalize-space(text()) and normalize-space(.)='Забыли пароль?'])[1]/following::button[1]").click()

        # Переход на Магазин
        self.driver.find_element_by_link_text(u"Site Review").click()
        time.sleep(3)

        # получение Словаря ретейлер:станции из MailMerge
        rt_st = bd_retail_stations()
        # rt_st = {'LOL': [11111]}
        ignore_station = []

        # установка даты (месяца и года)
        self.driver.find_element_by_xpath(
            "/html/body/app/ng-component/div/div/div/main/header/div[1]/span/main-filter/div/form/div/div[2]/"
            "datepicker/div/input").click()

        select_mounth = self.driver.find_element_by_class_name("monthselect")
        select_object = Select(select_mounth)
        mounth = 7  # 0-Январь, 1-Февраль..

        # разбивка месяцев по кварталам
        m1_in_quarter = [0, 3, 6, 9]  # первые месяцы в квартале
        m2_in_quarter = [1, 4, 7, 10]  # вторые месяцы в квартале
        m3_in_quarter = [2, 5, 8, 11]  # третьи месяцы в квартале

        select_object.select_by_index(mounth)
        time.sleep(2)

        # выбор года
        # select_yaer = self.driver.find_element_by_class_name("yearselect")
        # select_object = Select(select_yaer)
        # year = 5

        # select_object.select_by_index(year)
        # time.sleep(2)

        select_first_day = self.driver.find_element_by_xpath("(//th[.='Пн'])[1]/../../../tbody/tr/td[text()='1']")
        webdriver.ActionChains(self.driver).click(select_first_day).perform()
        select_last_day = self.driver.find_element_by_xpath("((//th[.='Пн'])[1]/../../../tbody/tr/td[text()='31'])[2]")
        webdriver.ActionChains(self.driver).click(select_last_day).perform()
        self.driver.find_element_by_xpath("//button[text()='Выбрать']").click()
        self.driver.find_element_by_xpath("//button[.='Применить']").click()
        time.sleep(2)

        # новая вкладка: CHAP
        self.driver.execute_script('''window.open("https://chap.teboil-azs.ru/", "_blank");''')
        self.driver.switch_to.window(self.driver.window_handles[1])  # переключение на 2ю вкладку
        self.driver.find_element_by_xpath('//div[@class="form-floating"][1]/input').clear()
        self.driver.find_element_by_xpath('//div[@class="form-floating"][1]/input').send_keys(LOGIN_CHAP)
        self.driver.find_element_by_xpath('//div[@class="form-floating"][2]/input').clear()
        self.driver.find_element_by_xpath('//div[@class="form-floating"][2]/input').send_keys(PASS_CHAP)
        self.driver.find_element_by_xpath("//button").click()

        errors = 0
        base_test = {}
        # Перебор станций на 2х вкладках
        for i in rt_st:
            stations = rt_st[i]
            for station in stations:
                list_test = {}

                if station in ignore_station:
                    continue

                #  1-ая вкладка - сайт Продажи
                self.driver.switch_to.window(self.driver.window_handles[0])  # переключение на 1ую вкладку
                self.driver.find_element_by_xpath("//i[contains(@class,'filter-input-close')]").click()
                self.driver.find_element_by_xpath("//input[contains(@name,'search')]").send_keys(station)
                self.driver.find_element_by_xpath("//div[@class='selected']").click()
                self.driver.find_element_by_xpath("//button[@class='btn']").click()
                time.sleep(2)

                # забираем параметр v-power с сайта Продаж
                # факт
                try:
                    list_test['vpower_fact_sales'] = float(self.driver.find_element_by_xpath(
                        "/html/body/app/ng-component/div/div/div/main/div/ng-component/div/app-site-review/div/div/div"
                        "/div/div[4]/ngb-tabset/div/div/table-grid/table/tfoot/tr/td[2]/span/"
                        "span").text.replace(" ", "").replace(",", "."))
                except:
                    list_test['vpower_fact_sales'] = float(self.driver.find_element_by_xpath(
                        "//span[text()='V-Power + VP-Racing']/../../../td[2]/span/"
                        "span").text.replace(" ", "").replace(",", "."))
                # план
                try:
                    list_test['vpower_plan_sales'] = float(self.driver.find_element_by_xpath(
                        "/html/body/app/ng-component/div/div/div/main/div/ng-component/div/app-site-review/div/div/div"
                        "/div/div[4]/ngb-tabset/div/div/table-grid/table/tfoot/tr/td[3]/span[2]/"
                        "span").text.replace(" ", "").replace(",", "."))
                except:
                    list_test['vpower_plan_sales'] = float(self.driver.find_element_by_xpath(
                        "//span[text()='V-Power + VP-Racing']/../../../td[3]/span[2]/"
                        "span").text.replace(" ", "").replace(",", "."))
                # выполнение
                try:
                    list_test['vpower_explan_sales'] = float(self.driver.find_element_by_xpath(
                        "/html/body/app/ng-component/div/div/div/main/div/ng-component/div/app-site-review/div/div/div"
                        "/div/div[4]/ngb-tabset/div/div/table-grid/table/tfoot/tr/td[3]/span[1]/"
                        "span").text.replace(" ", "").replace(",", "."))
                except:
                    list_test['vpower_explan_sales'] = float(self.driver.find_element_by_xpath(
                        "//span[text()='V-Power + VP-Racing']/../../../td[3]/span[1]/"
                        "span").text.replace(" ", "").replace(",", "."))
                # VP и VPR
                try:
                    list_test['vp_fact_sales'] = float(self.driver.find_element_by_xpath(
                        "/html/body/app/ng-component/div/div/div/main/div/ng-component/div/app-site-review/div/div/div"
                        "/div/div[3]/ngb-tabset/div/div/table-grid/table/tbody[5]/tr/td[2]/span/"
                        "span").text.replace(" ", "").replace(",", "."))
                except:
                    list_test['vp_fact_sales'] = float(self.driver.find_element_by_xpath(
                        "(//span[text()='V-Power'])[2]/../../../td[2]/span/"
                        "span").text.replace(" ", "").replace(",", "."))
                try:
                    list_test['vpr_fact_sales'] = float(self.driver.find_element_by_xpath(
                        "/html/body/app/ng-component/div/div/div/main/div/ng-component/div/app-site-review/div/div"
                        "/div/div/div[3]/ngb-tabset/div/div/table-grid/table/tbody[4]/tr/td[2]/span/"
                        "span").text.replace(" ", "").replace(",", "."))
                except:
                    list_test['vpr_fact_sales'] = float(self.driver.find_element_by_xpath(
                        "(//span[text()='V-Power Racing'])[2]/../../../td[2]/span/"
                        "span").text.replace(" ", "").replace(",", "."))

                # забираем параметр ГН с сайта Продаж
                try:
                    list_test['hotdrink_fact_sales'] = float(self.driver.find_element_by_xpath(
                        "/html/body/app/ng-component/div/div/div/main/div/ng-component/div/app-site-review/div/div/div/"
                        "div/div[6]/ngb-tabset/div/div/shop-conv-table-table/table-grid/table/tbody[1]/"
                        "tr/td[2]/span/span").text.replace(" ", "").replace(",", "."))
                except:
                    list_test['hotdrink_fact_sales'] = float(self.driver.find_element_by_xpath(
                        "(//span[text()='Горячие напитки'])[2]/../../../td[2]/span/"
                        "span").text.replace(" ", "").replace(",", "."))
                try:
                    list_test['hotdrink_plan_sales'] = float(self.driver.find_element_by_xpath(
                        "/html/body/app/ng-component/div/div/div/main/div/ng-component/div/app-site-review/div/div/div/"
                        "div/div[6]/ngb-tabset/div/div/shop-conv-table-table/table-grid/table/tbody[1]/tr/td[3]/"
                        "span[2]/span").text.replace(" ", "").replace(",", "."))
                except:
                    list_test['hotdrink_plan_sales'] = float(self.driver.find_element_by_xpath(
                        "(//span[text()='Горячие напитки'])[2]/../../../td[3]/span[2]/span").text.replace(" ", "").
                                                replace(",", "."))
                try:
                    list_test['hotdrink_explan_sales'] = float(self.driver.find_element_by_xpath(
                        "/html/body/app/ng-component/div/div/div/main/div/ng-component/div/app-site-review/div/div/div/"
                        "div/div[6]/ngb-tabset/div/div/shop-conv-table-table/table-grid/table/tbody[1]/tr/td[3]/"
                        "span[1]/span").text.replace(" ", "").replace(",", "."))
                except:
                    list_test['hotdrink_explan_sales'] = float(self.driver.find_element_by_xpath(
                        "(//span[text()='Горячие напитки'])[2]/../../../td[3]/span[1]/span").text.replace(" ", "").
                                                  replace(",", "."))

                # забираем параметр Омыватель с сайта Продаж
                try:
                    list_test['washer_fact_sales'] = float(self.driver.find_element_by_xpath(
                        "/html/body/app/ng-component/div/div/div/main/div/ng-component/div/app-site-review/div/div/"
                        "div/div/div[6]/ngb-tabset/div/div/shop-conv-table-table/table-grid/table/tbody[3]/tr/td[2]/"
                        "span/span").text.replace(" ", "").replace(",", "."))
                except:
                    list_test['washer_fact_sales'] = float(self.driver.find_element_by_xpath(
                        "//span[text()='Омыватель']/../../../td[2]/span/span").text.replace(" ", "").replace(",", "."))
                try:
                    list_test['washer_plan_sales'] = float(self.driver.find_element_by_xpath(
                        "/html/body/app/ng-component/div/div/div/main/div/ng-component/div/app-site-review/div/div/div/"
                        "div/div[6]/ngb-tabset/div/div/shop-conv-table-table/table-grid/table/tbody[3]/tr/td[3]/"
                        "span[2]/span").text.replace(" ", "").replace(",", "."))
                except:
                    list_test['washer_plan_sales'] = float(self.driver.find_element_by_xpath(
                        "//span[text()='Омыватель']/../../../td[3]/span[2]/"
                        "span").text.replace(" ", "").replace(",", "."))
                try:
                    list_test['washer_explan_sales'] = float(self.driver.find_element_by_xpath(
                        "/html/body/app/ng-component/div/div/div/main/div/ng-component/div/app-site-review/div/div/div/"
                        "div/div[6]/ngb-tabset/div/div/shop-conv-table-table/table-grid/table/tbody[3]/tr/td[3]/"
                        "span[1]/span").text.replace(" ", "").replace(",", "."))
                except:
                    list_test['washer_explan_sales'] = float(self.driver.find_element_by_xpath(
                        "//span[text()='Омыватель']/../../../td[3]/span[1]/"
                        "span").text.replace(" ", "").replace(",", "."))

                # топливные клиенты
                try:
                    list_test['tk_fact_sales'] = float(self.driver.find_element_by_xpath(
                        "/html/body/app/ng-component/div/div/div/main/div/ng-component/div/app-site-review/div/div/"
                        "div/div/div[2]/table-grid/table/tfoot/tr/td[2]/span/"
                        "span").text.replace(" ", "").replace(",", "."))
                except:
                    list_test['tk_fact_sales'] = float(self.driver.find_element_by_xpath(
                        "//span[text()='Всего'][1]/../../../td[2]/span/span").text.replace(" ", "").replace(",", "."))

                # штуки ГН и Омыватель
                self.driver.find_element_by_xpath("//a[contains(text(),'Штуки')]").click()
                time.sleep(1)
                try:
                    list_test['hotdrink_val_fact_sales'] = float(self.driver.find_element_by_xpath(
                        "/html/body/app/ng-component/div/div/div/main/div/ng-component/div/app-site-review/div/div/"
                        "div/div/div[6]/ngb-tabset/div/div/shop-piece-table-table/table-grid/table/tbody[1]/tr/td[2]/"
                        "span/span").text.replace(" ", "").replace(",", "."))
                except:
                    list_test['hotdrink_val_fact_sales'] = float(self.driver.find_element_by_xpath(
                        "(//span[text()='Горячие напитки'])[2]/../../../td[2]/span/"
                        "span").text.replace(" ", "").replace(",", "."))
                try:
                    list_test['washer_val_fact_sales'] = float(self.driver.find_element_by_xpath(
                        "/html/body/app/ng-component/div/div/div/main/div/ng-component/div/app-site-review/div/div/"
                        "div/div/div[6]/ngb-tabset/div/div/shop-piece-table-table/table-grid/table/tbody[3]/tr/td[2]/"
                        "span/span").text.replace(" ", "").replace(",", "."))
                except:
                    list_test['washer_val_fact_sales'] = float(self.driver.find_element_by_xpath(
                        "//span[text()='Омыватель']/../../../td[2]/span/span").text.replace(" ", "").replace(",", "."))

                #  2-ая вкладка - ЧАП
                self.driver.switch_to.window(self.driver.window_handles[1])  # переключение на 2ую вкладку
                self.driver.get(f"https://chap.teboil-azs.ru/indicators/{station}")
                time.sleep(1)

                if mounth in [3, 4, 5]:  # предыдущий квартал, вручную надо менять каждый новый квартал
                    self.driver.find_element_by_xpath('//th[text()="Группа"]/../../../../../div/a/i').click()
                    time.sleep(1)

                # забираем ГН
                self.driver.find_element_by_xpath("//td[text()='Конверсия \"Горячие напитки\"']/../td/i").click()
                time.sleep(1)
                if mounth in m1_in_quarter:
                    list_test['hotdrink_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[3]/'
                        'td[3]').text.replace(" ", "").replace(",", "."))
                    list_test['hotdrink_plan_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[2]/'
                        'td[3]').text.replace(" ", "").replace(",", "."))
                    list_test['hotdrink_explan_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[1]/'
                        'td[3]').text.replace(" ", "").replace("%", "").replace(",", "."))
                    list_test['hotdrink_val_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[5]/'
                        'td[3]').text.replace(" ", "").replace(",", ".").replace(",00", ""))
                    list_test['tk_gn_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[6]/'
                        'td[3]').text.replace(" ", "").replace(",", "."))

                elif mounth in m2_in_quarter:
                    list_test['hotdrink_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[3]/'
                        'td[4]').text.replace(" ", "").replace(",", "."))
                    list_test['hotdrink_plan_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[2]/'
                        'td[4]').text.replace(" ", "").replace(",", "."))
                    list_test['hotdrink_explan_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[1]/'
                        'td[4]').text.replace(" ", "").replace("%", "").replace(",", "."))
                    list_test['hotdrink_val_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[5]/'
                        'td[4]').text.replace(" ", "").replace(",", ".").replace(",00", ""))
                    list_test['tk_gn_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[6]/'
                        'td[4]').text.replace(" ", "").replace(",", "."))

                elif mounth in m3_in_quarter:
                    list_test['hotdrink_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[3]/'
                        'td[5]').text.replace(" ", "").replace(",", "."))
                    list_test['hotdrink_plan_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[2]/'
                        'td[5]').text.replace(" ", "").replace(",", "."))
                    list_test['hotdrink_explan_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[1]/'
                        'td[5]').text.replace(" ", "").replace("%", "").replace(",", "."))
                    list_test['hotdrink_val_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[5]/'
                        'td[5]').text.replace(" ", "").replace(",", ".").replace(",00", ""))
                    list_test['tk_gn_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[6]/'
                        'td[5]').text.replace(" ", "").replace(",", "."))

                # забираем VPower
                self.driver.find_element_by_xpath("//li[2]/a").click()
                time.sleep(1)
                self.driver.find_element_by_xpath("//td[text()='Пенетрация V-Power + V-Power Racing %']/../td"
                                                  "/i").click()
                time.sleep(1)
                if mounth in m1_in_quarter:
                    list_test['vpower_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[3]/'
                        'td[3]').text.replace(" ", "").replace(",", "."))
                    list_test['vpower_plan_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[2]/'
                        'td[3]').text.replace(" ", "").replace(",", "."))
                    list_test['vpower_explan_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[1]/'
                        'td[3]').text.replace(" ", "").replace("%", "").replace(",", "."))
                    list_test['vp_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[5]/'
                        'td[3]').text.replace(" ", "").replace(",", "."))
                    list_test['vpr_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[6]/'
                        'td[3]').text.replace(" ", "").replace(",", "."))

                elif mounth in m2_in_quarter:
                    list_test['vpower_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[3]/'
                        'td[4]').text.replace(" ", "").replace(",", "."))
                    list_test['vpower_plan_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[2]/'
                        'td[4]').text.replace(" ", "").replace(",", "."))
                    list_test['vpower_explan_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[1]/'
                        'td[4]').text.replace(" ", "").replace("%", "").replace(",", "."))
                    list_test['vp_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[5]/'
                        'td[4]').text.replace(" ", "").replace(",", "."))
                    list_test['vpr_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[6]/'
                        'td[4]').text.replace(" ", "").replace(",", "."))

                elif mounth in m3_in_quarter:
                    list_test['vpower_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[3]/'
                        'td[5]').text.replace(" ", "").replace(",", "."))
                    list_test['vpower_plan_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[2]/'
                        'td[5]').text.replace(" ", "").replace(",", "."))
                    list_test['vpower_explan_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[1]/'
                        'td[5]').text.replace(" ", "").replace("%", "").replace(",", "."))
                    list_test['vp_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[5]/'
                        'td[5]').text.replace(" ", "").replace(",", "."))
                    list_test['vpr_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[1]/tr[2]/td/table[1]/tbody/tr[6]/'
                        'td[5]').text.replace(" ", "").replace(",", "."))

                self.driver.find_element_by_xpath(
                    "//td[text()='Пенетрация V-Power + V-Power Racing %']/../td/i").click()
                time.sleep(1)

                # забираем Омыватель
                self.driver.find_element_by_xpath("//td[text()='Омыватель']/../td/i").click()
                time.sleep(1)
                if mounth in m1_in_quarter:
                    list_test['washer_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[2]/tr[2]/td/table[1]/tbody/tr[3]/'
                        'td[3]').text.strip().replace(",", ".").replace(" ", ""))
                    list_test['washer_plan_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[2]/tr[2]/td/table[1]/tbody/tr[2]/'
                        'td[3]').text.strip().replace(",", ".").replace(" ", ""))
                    list_test['washer_explan_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[2]/tr[2]/td/table[1]/tbody/tr[1]/'
                        'td[3]').text.strip().replace(",", ".").replace("%", "").replace(" ", ""))
                    list_test['washer_val_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[2]/tr[2]/td/table[1]/tbody/tr[5]/'
                        'td[3]').text.strip().replace(",", ".").replace(" ", "").replace(",00", ""))
                    list_test['tk_wash_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[2]/tr[2]/td/table[1]/tbody/tr[6]/'
                        'td[3]').text.strip().replace(",", ".").replace(" ", ""))

                elif mounth in m2_in_quarter:
                    list_test['washer_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[2]/tr[2]/td/table[1]/tbody/tr[3]/'
                        'td[4]').text.strip().replace(",", ".").replace(" ", ""))
                    list_test['washer_plan_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[2]/tr[2]/td/table[1]/tbody/tr[2]/'
                        'td[4]').text.strip().replace(",", ".").replace(" ", ""))
                    list_test['washer_explan_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[2]/tr[2]/td/table[1]/tbody/tr[1]/'
                        'td[4]').text.strip().replace(",", ".").replace("%", "").replace(" ", ""))
                    list_test['washer_val_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[2]/tr[2]/td/table[1]/tbody/tr[5]/'
                        'td[4]').text.strip().replace(",", ".").replace(" ", "").replace(",00", ""))
                    list_test['tk_wash_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[2]/tr[2]/td/table[1]/tbody/tr[6]/'
                        'td[4]').text.strip().replace(",", ".").replace(" ", ""))

                elif mounth in m3_in_quarter:
                    list_test['washer_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[2]/tr[2]/td/table[1]/tbody/tr[3]/'
                        'td[5]').text.strip().replace(",", ".").replace(" ", ""))
                    list_test['washer_plan_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[2]/tr[2]/td/table[1]/tbody/tr[2]/'
                        'td[5]').text.strip().replace(",", ".").replace(" ", ""))
                    list_test['washer_explan_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[2]/tr[2]/td/table[1]/tbody/tr[1]/'
                        'td[5]').text.strip().replace(",", ".").replace("%", "").replace(" ", ""))
                    list_test['washer_val_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[2]/tr[2]/td/table[1]/tbody/tr[5]/'
                        'td[5]').text.strip().replace(",", ".").replace(" ", "").replace(",00", ""))
                    list_test['tk_wash_fact_chap'] = float(self.driver.find_element_by_xpath(
                        '/html/body/main/section/div[3]/table/tbody[2]/tr[2]/td/table[1]/tbody/tr[6]/'
                        'td[5]').text.strip().replace(",", ".").replace(" ", ""))

                # вывод результата
                if (list_test['vpower_fact_sales'] != list_test['vpower_fact_chap'])\
                        or (list_test['vpower_plan_sales'] != list_test['vpower_plan_chap']) \
                        or (list_test['hotdrink_fact_sales'] != list_test['hotdrink_fact_chap']) \
                        or (list_test['hotdrink_plan_sales'] != list_test['hotdrink_plan_chap']) \
                        or (list_test['washer_fact_sales'] != list_test['washer_fact_chap']) \
                        or (list_test['washer_plan_sales'] != list_test['washer_plan_chap']) \
                        or (list_test['vpower_explan_sales'] != list_test['vpower_explan_chap']) \
                        or (list_test['hotdrink_explan_sales'] != list_test['hotdrink_explan_chap']) \
                        or (list_test['washer_explan_sales'] != list_test['washer_explan_chap'])\
                        or (list_test['vp_fact_sales'] != list_test['vp_fact_chap'])\
                        or (list_test['vpr_fact_sales'] != list_test['vpr_fact_chap'])\
                        or (list_test['hotdrink_val_fact_sales'] != list_test['hotdrink_val_fact_chap'])\
                        or (list_test['washer_val_fact_sales'] != list_test['washer_val_fact_chap'])\
                        or (list_test['tk_fact_sales'] != list_test['tk_gn_fact_chap'])\
                        or (list_test['tk_fact_sales'] != list_test['tk_wash_fact_chap']):
                    list_test['status'] = 'ERROR'
                    errors += 1
                else:
                    list_test['status'] = 'OK'
                base_test[station] = list_test

        #  Станция: показатель - факт_продажи / факт_чап, план_продажи / план_чап
        print(f'\nКоличество ошибок в сверке: {errors}')

        self.driver.quit()
        totalTable(mounth, base_test)

if __name__ == "__main__":
    unittest.main()
