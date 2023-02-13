from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from openpyxl import Workbook
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC

s = Service("C:\chromedriver.exe")
chromedriver_path = r'C:/chromedriver.exe'
url = 'https://pa.drweb.com/static/web_price/web/'

license_mas = ['Новая лицензия', 'Продление']    # типы лицензий
data_mas = ['12', '24', '36']     # типы дат
max_maximum = 500


# находит select, возвращает его как объект класса Select и массив значений для него
def get_select(driver, path, tag):
    try:
        select_element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, path)) )    # находим нужный селект по XPATH
    except:
        return False, [license_mas[0]], [data_mas[0]]
    select = Select(select_element)                                         # получаем к нему доступ
    select_options_ = select_element.find_elements(By.TAG_NAME, 'option')   # находим опции
    select_options = [i.get_attribute(tag) for i in select_options_]        # выбираем из них нужный атрибут
    return select, select_options                                           # вовзращает объект для взаимодействия и список значений


class Parser:
    def __init__(self):
        self.wb = Workbook()  # для экселя
        self.ws = self.wb.active

        self.driver = webdriver.Chrome(service=s)
        self.driver.implicitly_wait(5)
        self.driver.get(url)
        select = Select(WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="package_select"]')) ))
        select.select_by_visible_text('Россия')

        categories_menu = self.driver.find_element(By.ID, 'tabs_menu')  # получаем все панель с категориями
        categories = categories_menu.find_elements(By.TAG_NAME, 'a')    # получаем все категории
        for i in categories:                                            # перебираем все категории
            try:
                i.click()                                               # нажимаем на кнопку категории, ждём загрузки
            except:
                continue
            self.driver.implicitly_wait(3)
            self.get_category_info()                                    # собираем данные

        self.driver.quit()
        self.wb.save("result.xlsx")

    # получает все данные в категории (кнопки "Для Бизнеса", "Для дома"...)
    def get_category_info(self):
        select_license, select_options = get_select(self.driver, '//*[@id="discount_type"]', 'title')   # доступ и данные для выбора лицении
        for i in license_mas:                                                                           # перебираем все нужные нам типы лицензий
            if not i in select_options:                                                                 # если данного типа нет - переходим к следующему
                continue
            if select_license != False:
                select_license.select_by_visible_text(i)                                                # выбираем текущий тип лицензии
            select_time, time_options = get_select(self.driver, '//*[@id="period_license"]', 'value')   # доступ и данные для выбора времени
            for i in data_mas:                                                                          # перебираем все временные отрезки
                if not i in time_options:                                                               # если данного типа нет - переходим к следующему
                    continue
                if select_time != False:
                    select_time.select_by_visible_text(i)
                sleep(1)
                all_items = self.driver.find_elements(By.CLASS_NAME, 'item_table')              # находим все таблицы в элементах
                all_items
                for item_ in all_items:                                                         # перебираем все поля
                    flag = True     # в категории 'подписки для бизнеса' код таблицы меняется - для этого флаг и try
                    rows = item_.find_elements(By.CLASS_NAME, 'additional')                     # строки в таблице при обычном расположении
                    if rows == []:
                        rows = item_.find_elements(By.CLASS_NAME, 'lpad')                       # строки в таблице в некоторых категориях
                        flag = False

                    for row in rows:                                                            # перебираем строки таблицы
                        self.item = row
                        if flag:                                                                # если таблица как в большинстве категорий
                            checkboxes_cells = self.item.find_elements(By.CLASS_NAME, 'cell')   # находим поле с одними чекбоксами
                            self.get_all_info(checkboxes_cells[0])                              # получаем по нему всю информацию
                        else:
                            self.write_count(lambda: None, start='lpad')

    # получение данных о странице
    def get_all_info(self, checkboxes_cell):
        checkboxes = checkboxes_cell.find_elements(By.TAG_NAME, 'label')
        for checkbox in checkboxes:                                                 # отсеиваем ненужный чекбокс - ФСТЭК
            if 'Сертифицированный ФСТЭК' in checkbox.get_attribute('innerHTML'):
                checkboxes.remove(checkbox)
                break
        checkbox_count = len(checkboxes)                                            # находим количество чекбоксов
        checkboxes_check = checkboxes_cell.find_elements(By.TAG_NAME, 'input')      # нахожим кокретно поле чекбокса
        self.write_count(lambda: None)                                              # сбор информации с 0 нажатыми чекбоксами
        if checkbox_count == 1:                                                     # если у нас один чекбокс получаем информацию с нажатым       
            self.write_count(lambda: self.click_one_checkbox(checkboxes_check, 0))
        elif checkbox_count == 2:
            self.write_count(lambda: self.click_one_checkbox(checkboxes_check, 0))      # всё с первым чекбоксом
            self.write_count(lambda: self.click_one_checkbox(checkboxes_check, 1))      # всё со вторым чекбоксом
            self.write_count(lambda: self.click_two_checkboxes(checkboxes_check, 0, 1)) # всё с обоими чекбоксами
        elif checkbox_count == 3:
            self.write_count(lambda: self.click_one_checkbox(checkboxes_check, 0))      # 1-0-0
            self.write_count(lambda: self.click_one_checkbox(checkboxes_check, 1))      # 0-1-0
            self.write_count(lambda: self.click_one_checkbox(checkboxes_check, 2))      # 0-0-1
            self.write_count(lambda: self.click_two_checkboxes(checkboxes_check, 0, 1)) # 1-1-0
            self.write_count(lambda: self.click_two_checkboxes(checkboxes_check, 0, 2)) # 1-0-1
            self.write_count(lambda: self.click_two_checkboxes(checkboxes_check, 1, 2)) # 0-1-1
            self.write_count(lambda: self.click_three_checkboxes(checkboxes_check, 0, 1, 2)) # 1-1-1

    # нажимает на 3 чекбокса сразу
    def click_three_checkboxes(self, checkboxes_check, i, j, k):
        checkboxes_check[i].click()
        checkboxes_check[j].click()
        checkboxes_check[k].click()
        sleep(0.2)

    # нажимает на 2 чекбокса сразу
    def click_two_checkboxes(self, checkboxes_check, i, j):
        checkboxes_check[i].click()
        checkboxes_check[j].click()
        sleep(0.2)

    # нажимает на чекбокс под номером i из массива чекбоксов checkboxes_check
    def click_one_checkbox(self, checkboxes_check, i):
        checkboxes_check[i].click()
        sleep(0.2)

    # выставляем количество либо цифрой, либо из селекта
    def write_count(self, func, start=None):
        flag = True
        if start == 'lpad':     # в категории 'подписки для бизнеса' код таблицы меняется и находим сразу lpad
            lpad = self.item
        else:
            lpad = self.item.find_element(By.CLASS_NAME, 'lpad')
        try:                                                            # пытаемся найти текстовый инпут. если ошибка - то это селект
            input_ = lpad.find_element(By.TAG_NAME, 'input')
        except:
            select_input_ = lpad.find_element(By.TAG_NAME, 'select')
            flag = False
        if flag:
            self.get_info_input(lpad, input_, func)
        else:
            self.get_info_select(select_input_, func)

    # получение всех данных из числового инпута (перебор всех значений и их сохранение)
    def get_info_input(self, lpad, input_, func):
        info = lpad.find_element(By.CLASS_NAME, 'hint')     # текстовое поле с минимумом и максимумом
        minimum = int(info.get_attribute('min'))
        maximum = int(info.get_attribute('max'))
        if maximum == 500:
            maximum = max_maximum
        for i in range(minimum, maximum+1):                 # перебираем все возможные значения
            input_.send_keys(i)
            func()
            self.get_info()
            input_.clear()

    # получение всех данных из селекта (перебор всех значений и их сохранение)
    def get_info_select(self, select_input_, func):
        select_input = Select(select_input_)
        select_options = select_input_.find_elements(By.TAG_NAME, 'option')
        value0 = select_options[0].get_attribute('value')
        func()
        for i in select_options[1:]:
            val = i.get_attribute('value')
            select_input.select_by_value(val)
            self.get_info()
            sleep(0.3)
        select_input.select_by_value(value0)
        
    # получение данных из "чека" и добавление их в excel
    def get_info(self):
        panel = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[4]/div[2]/div[2]/div/div[1]/div/div[1]')) )
        title = panel.find_element(By.CLASS_NAME, 'title').get_attribute('innerHTML').strip()
        grays = panel.find_elements(By.CLASS_NAME, 'gray')
        tag = grays[0].get_attribute('innerHTML').strip()
        price = grays[-1].get_attribute('innerHTML').strip(r' /.-')
        self.ws.append([title, tag, price])

    def write_data_txt(self, title, tag, price):
        with open('output.txt', 'a') as f:
            f.write(f'{title}\n{tag}\n{price}\n____________________________\n')


if __name__ == '__main__':
    p = Parser()
