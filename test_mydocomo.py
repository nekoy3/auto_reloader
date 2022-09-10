#https://reffect.co.jp/python/selenium

from selenium import webdriver
from selenium.webdriver.common.by import By

timeout = 5 #タイムアウトまでの秒数

chrome = webdriver.Chrome(executable_path='./driver/chromedriver.exe')
chrome.implicitly_wait(timeout) #タイムアウト時間or処理完了（ページ読み込み完了）待機して次の処理に進む
chrome.get("https://www.nttdocomo.co.jp/mydocomo/")
#chrome.find_element_by_partial_link_text('ログインする').click()
#find_element_by_partial_link_textメソッドがSelenium4.3.0で削除されたためfind_elementメソッドを使用する必要がある
'''
Byのimport
https://qiita.com/mochio/items/dc9935ee607895420186

Byが持つメソッド
https://www.selenium.dev/selenium/docs/api/javascript/module/selenium-webdriver/index_exports_By.html

旧メソッドの代替
https://stackoverflow.com/questions/71097378/selenium-common-exceptions-invalidargumentexception-message-invalid-argument
If username is the value of class attribute:

login = driver.find_element(By.CLASS_NAME, "username")
If username is the value of id attribute:

login = driver.find_element(By.ID, "username")
If username is the value of name attribute:

login = driver.find_element(By.NAME, "username")
If username is the value of linktext attribute:

login = driver.find_element(By.LINK_TEXT, "username")
'''
#chrome.find_element(By.LINK_TEXT, 'ログインする').click() #ログインするﾘﾝｸﾃｷｽﾄタグの要素をクリック
chrome.find_element(By.CLASS_NAME, 'home-opan-all-area-btn-login').click() #クラス名でもいい、要素にテキストがない時はこれ
chrome.find_element(By.ID, 'Di_Uid').send_keys("johndoe@docomo.ne.jp")
chrome.find_element(By.CLASS_NAME, 'nextaction').click() #次へ進むクラスのタグをクリック

#IDが誤っています、とログインしようとするところまで自動で実行する。docomoは二段階認証があるから、こういった場合は対応できない