from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, WebDriverException, \
    StaleElementReferenceException
from time import sleep
import json
import os, shutil


def create_driver():
    # 创建谷歌浏览器驱动
    chrome_options = Options()

    prefs = {'profile.default_content_settings.popups': 0,
             'download.default_directory': 'D:\GraduationTask\Helper\data',
             'plugins.always_open_pdf_externally': True}
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('blink-settings=imagesEnabled=false')
    driver = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)
    driver.implicitly_wait(15)
    return driver


def seek_url(driver: webdriver.Chrome):
    fp = open('arxiv_bio.txt', 'w', encoding='utf8')
    url_list = []
    url = 'https://arxiv.org/search/advanced?advanced=&terms-0-operator=AND' \
          '&terms-0-term=biological&terms-0-field=abstract&terms-1-operator=OR' \
          '&terms-1-term=medicine&terms-1-field=abstract&classification-physics_archives=all' \
          '&classification-q_biology=y&classification-include_cross_list=include' \
          '&date-year=&date-filter_by=date_range&date-from_date=2019-01-01' \
          '&date-to_date=2021-03-03&date-date_type=submitted_date&abstracts=hide' \
          '&size=200&order=-announced_date_first'
    driver.get(url)
    for _ in range(0, 23):
        urls = driver.find_elements_by_xpath('//*[@id="main-container"]/div[2]/ol//li/div/p/a')
        for url in urls:
            url_list.append({'url': url.get_attribute('href')})
        try:
            driver.find_element_by_xpath('//*[@id="main-container"]/div[2]/nav[2]/a[2]').click()
        except ElementNotInteractableException:
            break
        sleep(5)
    json_file = json.dumps(url_list, ensure_ascii=False, indent=1)
    fp.write(json_file)
    fp.close()


def download_bibliography(driver: webdriver.Chrome, skip: int):
    fp = open('url/arxiv_bio.txt', 'r', encoding='utf8')
    urls = json.load(fp)
    cnt = 0
    alls = 0
    for url in urls:
        alls += 1
        if alls <= skip:
            continue
        link = url['url']
        # 有时候会报connection aborted, 刷新
        for _ in range(0, 5):
            try:
                driver.get(link)
            except (WebDriverException, StaleElementReferenceException):
                continue
            break
        # 如果没有'NASA AD'则重试，至多5次
        for _ in range(0, 5):
            try:
                driver.find_element_by_link_text('NASA ADS').click()
            except (NoSuchElementException, StaleElementReferenceException):
                driver.refresh()
                sleep(10)
                continue
            break
        # 404表示还没有写入NASA AD，跳过
        if '404' in driver.page_source:
            sleep(5)
            print(f'404:{alls}')
            continue
        cnt += 1
        # 如果没有'Export Citation'，多半是没加载出来，刷新，至多5次
        for _ in range(0, 5):
            try:
                driver.find_element_by_link_text('Export Citation').click()
            except (NoSuchElementException, StaleElementReferenceException):
                driver.refresh()
                continue
            break
        # 下载，最多重试5次
        for _ in range(0, 5):
            try:
                sleep(10)
                driver.find_element_by_xpath('//*[@id="ex-dropdown"]/option[4]').click()
                sleep(10)
                driver.find_element_by_xpath(
                    '//*[@id="current-subview"]/div[8]/div/div/div/div[2]/div/div[1]/div/button[1]').click()
                # 下载完毕后就迁移进break文件夹
                for _ in range(0, 5):
                    if os.path.exists('data/export-endnote.enw'):
                        shutil.move('data/export-endnote.enw', f'data/q_bio/{alls}.enw')
                        break
                    sleep(2)
            except (NoSuchElementException, StaleElementReferenceException):
                driver.refresh()
                continue
            break
        # 输出
        print(f'now:{cnt}, all:{alls}')


def download_pdf(driver: webdriver.Chrome, skip: int):
    fp = open('arxiv_bio.txt', 'r', encoding='utf8')
    urls = json.load(fp)
    cnt = 0
    alls = 0
    move_cnt = 0
    for url in urls:
        alls += 1
        if alls <= skip:
            continue
        link = url['url']
        for attempt in range(0, 5):
            try:
                driver.get(link)
            except (WebDriverException, StaleElementReferenceException):
                print(f'exception in visit. {link}, attempt:{attempt}')
                continue
            break
        for attempt in range(0, 5):
            try:
                driver.find_element_by_xpath('//*[@id="abs-outer"]/div[2]/div[1]/ul/li[1]/a').click()
            except (NoSuchElementException, StaleElementReferenceException):
                print(f'exception in click. {link}, attempt:{attempt}')
                driver.refresh()
                sleep(5)
                continue
            cnt += 1
            print(f'download:{link}; now: {cnt}; all: {alls}')
            break
        sleep(30)
        for file_name in os.listdir('data'):
            if file_name.endswith('.pdf'):
                move_cnt += 1
                shutil.move(f'data/{file_name}', f'data/pdf/{file_name}')
                print(f'move {move_cnt}:{file_name}')


if __name__ == '__main__':
    skip = 897
    driver = create_driver()
    download_pdf(driver, skip=skip)
