# coding: utf-8
#cfg.txtにログイン画面のリンク->「A」にid入力->「B」にパスワード入力
''' cfg.txtのフォーマット
タイムアウト秒数(デフォルト5)
ログインURL
ログインid(項目名):id(入力値)
パスワード:pass
ログインのためにクリックするボタンの名前
更にクリックするボタンのxpath (要素を右クリック->copy->xpathをコピー)
リロードするXPath　存在するときリロードを繰り返す.
画像ファイルを持つタグのalt
inputするclass名

画像
<img id="card_img_200000******" src="******" class="lazy meishiparts" alt="メールアドレス">
value
<input type="text" name="email_account[200000******]" id="email_account200000******" value="" class="size20big">
domainなら右辺、accountなら左辺
'''
#XPath
#https://qiita.com/NagaokaKenichi/items/7a111467dcae3354048d
import re
import os
import shutil
import glob
import PySimpleGUI as sg
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome import service as fs
import time

class ConfigClass():
    def __init__(self):
        with open('cfg.txt', 'r', encoding='utf-8') as f:
            self.timeout = int(f.readline().rstrip())
            self.login_url = f.readline().rstrip()
            self.user_id_text_name, self.user_id = f.readline().rstrip().split(':')
            self.password_class_name, self.password = f.readline().rstrip().split(':')
            self.button_text_name = f.readline().rstrip()
            self.button_xpath = f.readline().rstrip()
            self.reload_xpath = f.readline().rstrip()
            self.img_alt = f.readline().rstrip()
            self.input_class_name = f.readline().rstrip()

class MainDisplay():
    def __init__(self, options):
        self.options = options
        sg.theme('Reddit')
        self.first_layout = [[sg.Text('ログイン中です。')]]
        self.waiting_layout = [  [sg.Text('仕事待機中です。')],
                                 [sg.Button('ログアウト')] ]

    def stopping(self):
        self.window.close()
        shutil.rmtree('./tmp/') if os.path.exists("./tmp") else None
        exit()

    def make_driver_process(self):
        options = webdriver.ChromeOptions()
        for option in self.options:
            options.add_argument(option)
        chrome_service = fs.Service(executable_path='./driver/chromedriver.exe')
        self.chrome = webdriver.Chrome(service=chrome_service, options=options)
    
    def login_url_and_makewindow(self, cfg):
        self.chrome.implicitly_wait(cfg.timeout)
        self.chrome.get(cfg.login_url)

        self.window = sg.Window('ログイン中', self.first_layout, alpha_channel=0.95, no_titlebar=True)
        
        self.window.read(timeout=100) #readはイベントが返されるまでCPUリソースを持ち続けるがtimeoutを設けると持ち続けなくなる
        self.chrome.find_element(By.ID, cfg.user_id_text_name).send_keys(cfg.user_id)
        self.chrome.find_element(By.ID, cfg.password_class_name).send_keys(cfg.password)
        self.chrome.find_element(By.LINK_TEXT, cfg.button_text_name).click()
        self.chrome.find_element(By.XPATH, cfg.button_xpath).click()

        self.window.close()
    
    def save_img_in_elements(self, elements):
        os.mkdir("./tmp") if not os.path.exists("./tmp") else None
        for index, element in enumerate(elements):
            imgurl = element.get_attribute('src')
            print(" downloading from " + imgurl + " ...")
            with open(f'./tmp/img_{index}.jpg', 'wb') as f:
                f.write(element.screenshot_as_png)
    
    def get_input_id(self, element):
        name = element.get_attribute('name')
        return re.sub(r"\D", "", name)

    def get_input_group(self, elements):
        input_list = [[elements[0]]]
        for i in range(1, len(elements)):
            if input_list[i-1] == 0:
                input_list.append([elements[i]])
            elif self.get_input_id(input_list[i-1][0]) == self.get_input_id(elements[i]):
                input_list[i-1] = [elements[i-1], elements[i]]
                input_list.append(0)
            else:
                input_list.append([elements[i]])
        input_list = [i for i in input_list if i != 0]
        return input_list
    
    def get_page_data(self, img_alt, input_class_name):
        img_elements = self.chrome.find_elements(By.TAG_NAME, 'img')
        img_elements = [img for img in img_elements if img.get_attribute('alt') == img_alt]
        self.save_img_in_elements(img_elements)
        self.work_img_names = glob.glob("./tmp/*")
        
        input_elements = self.chrome.find_elements(By.CLASS_NAME, input_class_name)
        self.input_list = self.get_input_group(input_elements)
    
    def make_working_layout_and_window(self):
        #work_img_names, input_list
        progress_text = str(now_work_num) + "/" + str(self.work_img_names)
        working_layout = [  [sg.Text('現在の仕事 '), sg.Text(progress_text)],
                            [sg.InputText()],
                            [sg.Button('OK'), sg.Button('キャンセル')] ]
        self.window = sg.Window('ワーキングウィンドウ', working_layout, alpha_channel=0.95, no_titlebar=True, grab_anywhere=True, return_keyboard_events=True)
    
    def working(self):
        self.make_working_layout_and_window()
        while True:
            event, value = self.window.read()

            if event == "ログアウト" or event == sg.WIN_CLOSED:
                sg.Popup("終了します。")
                self.stopping()
    
    def main(self):
        cfg = ConfigClass()
        self.make_driver_process()
        self.login_url_and_makewindow(cfg)

        self.window = sg.Window('待機中', self.waiting_layout, alpha_channel=0.95, grab_anywhere=True, return_keyboard_events=True)
        self.work_img_names = None

        count = 0
        while True:
            event, value = self.window.read(timeout=1)

            time.sleep(0.1)
            count += 1
            #2秒に一度、所持データが存在しないときデータ収集を検証する
            if count % 10 == 0 and (self.work_img_names == None):
                try: #存在すればエラーページと判断しelseへ
                    self.chrome.find_element(By.XPATH, cfg.reload_xpath)
                except: #情報が取得できる状況である場合
                    self.get_page_data(cfg.img_alt, cfg.input_class_name)
                    self.window.close()
                    #仕事中、終わればwork_img_names=Noneに設定、関数内でexitを実行する場合有り
                    self.working() 
                else: #項目が存在する(エラーページ）時の処理
                    self.window = sg.Window('待機中', self.waiting_layout, alpha_channel=0.95, no_titlebar=True, grab_anywhere=True, return_keyboard_events=True)
                    self.chrome.refresh()
        
            if event == "ログアウト" or event == sg.WIN_CLOSED:
                sg.Popup("終了します。")
                self.stopping()

def main():
    options = []
    disp = MainDisplay(options)
    disp.main()

if __name__ == "__main__":
    main()