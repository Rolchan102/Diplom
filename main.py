from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from openpyxl import Workbook
from time import sleep

# geckodriver_path = r'C:/Users/ktoto/Documents/geckodriver.exe' #
chromedriver_path = r''
url = 'https://pa.drweb.com/static/web_price/web/'    


class Parser:
    def __init__(self):
        self.wb = Workbook()  # для экселя
        self.ws = self.wb.active
        
        # self.driver = webdriver.Firefox(executable_path=geckodriver_path)
        self.driver = webdriver.Chrome(executable_path=chromedriver_path)
        self.driver.implicitly_wait(5)
        self.driver.get(url)
        sleep(5)
        select = Select(self.driver.find_element(By.XPATH, '//*[@id="package_select"]'))
        select.select_by_visible_text('Россия')
        select = Select(self.driver.find_element(By.XPATH, '//*[@id="discount_type"]'))
        select.select_by_visible_text('Новая лицензия')
        for i in ['12', '24', '36']:
            select = Select(self.driver.find_element(By.XPATH, '//*[@id="period_license"]'))
            select.select_by_visible_text(i)
            sleep(1)
            all_items = self.driver.find_elements(By.CLASS_NAME, 'additional')
            for item in all_items:
                checkboxes_cells = item.find_elements(By.CLASS_NAME, 'cell')
                self.get_all_info(item, checkboxes_cells[0])
        self.driver.quit()
        self.wb.save("result.xlsx")

    def get_all_info(self, item, checkboxes_cell):
        checkboxes = checkboxes_cell.find_elements(By.TAG_NAME, 'label')
        for checkbox in checkboxes:
            if 'Сертифицированный ФСТЭК' in checkbox.get_attribute('innerHTML'):
                checkboxes.remove(checkbox)
                break
        checkbox_count = len(checkboxes)
        checkboxes_check = checkboxes_cell.find_elements(By.TAG_NAME, 'input')
        flag, input_, value_0, value_1 = self.write_count(item)
        sleep(0.5)
        self.get_info()
        sleep(0.5)
        if checkbox_count == 1:
            self.click_one_checkbox(checkboxes_check, 0)
        elif checkbox_count == 2:
            self.click_two_checkboxes(checkboxes_check, 0, 1)
        elif checkbox_count == 3:
            self.click_two_checkboxes(checkboxes_check, 0, 1)
            self.click_one_checkbox(checkboxes_check, 1)
            sleep(0.5)
            self.click_one_checkbox(checkboxes_check, 2)
            sleep(0.5)
            self.get_info()
            self.click_two_checkboxes(checkboxes_check, 0, 1)
        self.clear_count(flag, input_, value_0, value_1)

    def click_two_checkboxes(self, checkboxes_check, i, j):
        self.click_one_checkbox(checkboxes_check, i)  # + -
        self.click_one_checkbox(checkboxes_check, j)  # + +
        checkboxes_check[i].click()              # - +
        sleep(0.5)
        self.get_info()
        sleep(0.5)
    
    def click_one_checkbox(self, checkboxes_check, i):
        checkboxes_check[i].click()
        sleep(0.5)
        self.get_info()
        sleep(0.5)

    def write_count(self, item):
        flag = False
        lpad = item.find_element(By.CLASS_NAME, 'lpad')
        try:
            input_ = lpad.find_element(By.TAG_NAME, 'input')
        except:
            select_input_ = lpad.find_element(By.TAG_NAME, 'select')
            flag = True
        if flag:
            select_input = Select(select_input_)
            select_options = select_input_.find_elements(By.TAG_NAME, 'option')
            value_0 = select_options[0].get_attribute('value')
            value_1 = select_options[1].get_attribute('value')
            select_input.select_by_value(value_1)
            input_ = select_input
        else:
            value_0, value_1 = None, None
            minimum_ = lpad.find_element(By.CLASS_NAME, 'hint')
            minimum = int(minimum_.get_attribute('min'))
            input_.send_keys(minimum)
        return flag, input_, value_0, value_1

    def get_info(self):
            panel = self.driver.find_element(By.XPATH, '/html/body/div[3]/div[4]/div[2]/div[2]/div/div[1]/div/div[1]')
            title = panel.find_element(By.CLASS_NAME, 'title').get_attribute('innerHTML').strip()
            grays = panel.find_elements(By.CLASS_NAME, 'gray')
            tag = grays[0].get_attribute('innerHTML').strip()
            price = grays[-1].get_attribute('innerHTML').strip(r' /.-')
            self.ws.append([title, tag, price])

    def clear_count(self, flag, input_, value_0, value_1):
        if flag:
            input_.select_by_value(value_0)
        else:
            input_.clear()

    def write_data_txt(self, title, tag, price):
        with open('output.txt', 'a') as f:
            f.write(f'{title}\n{tag}\n{price}\n____________________________\n')


if __name__ == '__main__':
    p = Parser()
