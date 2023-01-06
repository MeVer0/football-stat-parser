from selenium import webdriver

chromedriver_options = webdriver.ChromeOptions()
chromedriver_options.headless = True

driver = webdriver.Chrome(
    r'C:\Users\Mever\OneDrive\Рабочий стол\programs\nerostat\Parsers\Parser_player\chromedriver.exe')