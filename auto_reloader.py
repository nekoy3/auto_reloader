# coding: utf-8
#cfg.txtにログイン画面のリンク->「A」にid入力->「B」にパスワード入力
''' cfg.txtのフォーマット
タイムアウト秒数(デフォルト5)
ログインURL
ログインid(項目名):id(入力値)
パスワード:pass
ログインのためにクリックするボタンの名前
更にクリックするボタンのxpath (要素を右クリック->copy->xpathをコピー)
リロードするXPath　存在するときリロードを繰り返す
'''
#XPath
#https://qiita.com/NagaokaKenichi/items/7a111467dcae3354048d
from selenium import common
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

cfg = []
timeout = 5
login_url = None
user_id_text_name = None
user_id = None
password_class_name = None
password = None
button_text_name = None
button_xpath = None
reload_xpath = None

with open('cfg.txt', 'r', encoding='utf-8') as f:
    timeout = int(f.readline().rstrip())
    login_url = f.readline().rstrip()
    user_id_text_name, user_id = f.readline().rstrip().split(':')
    password_class_name, password = f.readline().rstrip().split(':')
    button_text_name = f.readline().rstrip()
    button_xpath = f.readline().rstrip()
    reload_xpath = f.readline().rstrip()

chrome = webdriver.Chrome(executable_path='./driver/chromedriver.exe')
chrome.implicitly_wait(timeout)
chrome.get(login_url)

chrome.find_element(By.ID, user_id_text_name).send_keys(user_id)
chrome.find_element(By.ID, password_class_name).send_keys(password)
chrome.find_element(By.LINK_TEXT, button_text_name).click()
chrome.find_element(By.XPATH, button_xpath).click()

while True:
    try:
        chrome.find_element(By.XPATH, reload_xpath)
    except KeyboardInterrupt:
        chrome.close()
        print("Process closed.")
    except:
        pass
    else:
        chrome.refresh()
    time.sleep(2)
