from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(chrome_options)
driver.get('http://www.google.com/')
search_box = driver.find_element(By.NAME, "q")
search_box.send_keys('Chowder')
search_box.submit()
driver.title
driver.quit()
