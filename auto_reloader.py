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
画像ファイルのclass名

画像
<img id="card_img_200000******" src="******" class="lazy meishiparts" alt="メールアドレス">
value
<input type="text" name="email_account[200000******]" id="email_account200000******" value="" class="size20big">
domainなら右辺、accountなら左辺
'''
#XPath
#https://qiita.com/NagaokaKenichi/items/7a111467dcae3354048d
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
            self.img_class_name = f.readline().rstrip()
            self.input_class_name = f.readline().rstrip()

class MainDisplay():
    def __init__(self, options):
        self.options = options
        sg.theme('Reddit')
        self.first_layout = [  [sg.Text('ログイン中です。')]]
        self.waiting_layout = [  [sg.Text('仕事待機中です。')],
                                 [sg.Button('ログアウト')] ]

    def make_driver_process(self):
        options = webdriver.ChromeOptions()
        for option in self.options:
            options.add_argument(option)
        chrome_service = fs.Service(executable_path='./driver/chromedriver.exe')
        chrome = webdriver.Chrome(service=chrome_service, options=options)
        return chrome
    
    def get_page_data(self, chrome, img_class_name, input_class_name):
        pictures = chrome.find_elements(By.CLASS_NAME, img_class_name)
        for picture in pictures:
            # imgタグ要素を取得
            img = picture.find_element(By.TAG_NAME, 'img')
            # urlを取得
            src = img.get_attribute('src')
            id = img.get_attribute('id')
            if src:
                # ファイルの保存
                os.mkdir("./tmp") if not os.path.exists("./tmp") else None
                with open(f'./tmp/out_{id}.png', 'wb') as f:
                    f.write(img.screenshot_as_png)
        files = glob.glob("./tmp/*")
        
        text_boxes = chrome.find_elements(By.CLASS_NAME, input_class_name)
        return files, text_boxes
    
    def working(self):
        self.working_layout = [  [sg.Text('何か入力してください')],
                                 [sg.InputText()],
                                 [sg.Button('OK'), sg.Button('キャンセル')] ]
        self.window = sg.Window('ワーキングウィンドウ', self.second_layout, alpha_channel=0.95, no_titlebar=True, grab_anywhere=True, return_keyboard_events=True)
    
    def main(self):
        cfg = ConfigClass()
        self.window = sg.Window('ワーキングウィンドウ', self.first_layout, alpha_channel=0.95, no_titlebar=True, grab_anywhere=True, return_keyboard_events=True)
        chrome = self.make_driver_process()

        chrome.implicitly_wait(cfg.timeout)
        chrome.get(cfg.login_url)

        chrome.find_element(By.ID, cfg.user_id_text_name).send_keys(cfg.user_id)
        chrome.find_element(By.ID, cfg.password_class_name).send_keys(cfg.password)
        chrome.find_element(By.LINK_TEXT, cfg.button_text_name).click()
        chrome.find_element(By.XPATH, cfg.button_xpath).click()

        self.window.close()
        try: #リロードのトリガーになる項目のxpath
            chrome.find_element(By.XPATH, cfg.reload_xpath)
        except: #項目が存在しないとき待機ウィンドウを開く
            self.window = sg.Window('待機中', self.waiting_layout, alpha_channel=0.95, no_titlebar=True, grab_anywhere=True, return_keyboard_events=True)
            files = None
            text_boxes = None
        else: #項目が存在する時データを収集してワーキングウィンドウを開く
            files, text_boxes = self.get_page_data(chrome, cfg.img_class_name, cfg.input_class_name) #画像保存もココ

        count = 0
        while True:
            event, value = self.window.read()

            time.sleep(0.1)
            count += 1
            if count % 20 == 0 and (files == None or text_boxes == None):
                try: #リロードのトリガーになる項目のxpath
                    chrome.find_element(By.XPATH, cfg.reload_xpath)
                except: #項目が存在しないときの処理
                    files, text_boxes = self.get_page_data(chrome, cfg.img_class_name, cfg.input_class_name)
                else: #項目が存在する時の処理
                    chrome.refresh()
            
            
        
            if event == "ログアウト":
                sg.Popup("終了します。")
                break
        
        self.window.close()
        shutil.rmtree('./tmp/') if os.path.exists("./tmp") else None

def main():
    options = ["--start-maximized"]
    disp = MainDisplay(options)
    disp.main()

if __name__ == "__main__":
    main()