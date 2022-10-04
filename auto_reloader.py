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
import io
from PIL import Image

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
    
    #work_img_namesに画像ファイルを保持、input_listに[[account, domain], [account...], ...]の形式で保持
    def get_page_data(self, img_alt, input_class_name):
        img_elements = self.chrome.find_elements(By.TAG_NAME, 'img')
        img_elements = [img for img in img_elements if img.get_attribute('alt') == img_alt] # and img.get_attribute('id').find('gray') != -1
        self.save_img_in_elements(img_elements)
        self.work_img_names = glob.glob("./tmp/*")
        
        input_elements = self.chrome.find_elements(By.CLASS_NAME, input_class_name)
        self.input_list = self.get_input_group(input_elements)
    
    #仕事ウィンドウのaccount@domain入力ボックスを表示非表示、既存データがあればそれを取得する
    def work_input_update(self):
        name = self.input_list[self.now_index][0].get_attribute('name')
        if name.find("domain") != -1:
            have_attribute = 2 #1 accのみ 2 domainのみ 3両方持ち
            already_domain = self.input_list[self.now_index][0].get_attribute('value')
        else:
            if len(self.input_list[self.now_index]) == 1:
                have_attribute = 1
                already_account = self.input_list[self.now_index][0].get_attribute('value')
            else: #要素が2個存在する時
                have_attribute = 3
                already_account = self.input_list[self.now_index][0].get_attribute('value')
                already_domain = self.input_list[self.now_index][1].get_attribute('value')
        
        match have_attribute:
            case 1:
                self.w_window['-IN1-'].update(value=already_account, visible=True)
                self.w_window['-IN2-'].update(visible=False)
            case 2:
                self.w_window['-IN1-'].update(visible=False)
                self.w_window['-IN2-'].update(value=already_domain, visible=True)
            case 3:
                self.w_window['-IN1-'].update(value=already_account, visible=True)
                self.w_window['-IN2-'].update(value=already_domain, visible=True)
    
    def make_working_layout_and_window(self):
        shortcut_descript_text = """
            ショートカットキーとかは
            まだ未実装
        """
        working_layout = [  [sg.Text('現在の仕事 '), sg.Text(f'1 / {len(self.work_img_names)}', key='-work-process-')],
                            [sg.Text('進捗 '), sg.ProgressBar(len(self.work_img_names), orientation='h', size=(20, 20), key='progressbar')],
                            [sg.Text('前回入力したデータ： '), sg.Text('', key='-OLD-')],
                            [sg.Image(filename=f'./tmp/img_0.jpg', key='-IMAGE-'), sg.Text(shortcut_descript_text)],
                            [sg.Input(visible=True, tooltip="account", key='-IN1-', size=25), sg.Text(' @ '), 
                                sg.Input(visible=True, tooltip="domain", key='-IN2-', size=25)],
                            [sg.Button('次へ'), sg.Button('戻る', key='-back-', visible=False)] ]
        self.w_window = sg.Window('ワーキングウィンドウ', working_layout, alpha_channel=0.95, no_titlebar=True, grab_anywhere=True)
        self.progress_bar = self.w_window['progressbar']

    def working_window_update(self):
        self.progress_bar.UpdateBar(self.now_index)
        self.w_window['-work-process-'].update(f'{self.now_index} / {len(self.work_img_names)}')
        img_path = f'./tmp/img_{self.now_index}.jpg'
        self.w_window['-IMAGE-'].update(filename=img_path)
    
    def working_data_save(self, value):
        if value['-IN1-']:
            self.input_list[self.now_index][0].send_keys(value['-IN1-'])
        
        if value['-IN2-']:
            self.input_list[self.now_index][1].send_keys(value['-IN2-'])

    def working(self):
        self.now_index = 0
        self.make_working_layout_and_window()
        
        while True:
            event, value = self.w_window.read()
            self.work_input_update()

            if event == '-back-':
                self.working_data_save(value)
                self.now_index -= 1
                
                if self.now_index == 0:
                    self.w_window['-back-'].Update(visible=False)
                
                self.working_window_update()

            if event == '次へ':
                self.working_data_save(value)
                self.w_window['-back-'].Update(visible=True)

                self.now_index += 1

                if self.now_index == len(self.work_img_names):
                    sg.popup_quick_message("仕事を送信しました。")
                    self.work_img_names = None
                    break #mainに返す

                self.working_window_update()

            if event == "ログアウト" or event == sg.WIN_CLOSED:
                sg.Popup("終了します。")
                self.stopping()
    
    def main(self):
        cfg = ConfigClass()
        self.make_driver_process()
        self.login_url_and_makewindow(cfg)

        window = sg.Window('待機中', self.waiting_layout, alpha_channel=0.95, grab_anywhere=True)
        self.work_img_names = None

        count = 0
        while True:
            event, value = window.read(timeout=1)

            time.sleep(0.1)
            count += 1
            #2秒に一度、所持データが存在しないときデータ収集を検証する
            if count % 10 == 0 and (self.work_img_names == None):
                try: #存在すればエラーページと判断しelseへ
                    self.chrome.find_element(By.XPATH, cfg.reload_xpath)
                except: #情報が取得できる状況である場合
                    window.close()
                    self.get_page_data(cfg.img_alt, cfg.input_class_name)
                    #仕事中、終わればwork_img_names=Noneに設定、関数内でexitを実行する場合有り
                    self.working() 
                else: #項目が存在する(エラーページ）時の処理
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