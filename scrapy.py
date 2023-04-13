import json
import time
from typing import Union

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

from config import *
from database import Database, Shop

driver = webdriver.Chrome()
config = Config()

cookies_path = pathlib.Path('cookies.json')

BASE_URL = 'https://www.dianping.com/'
LOGIN_URL = 'https://account.dianping.com/pclogin'

SearchChannel = {'不限': '0', '美食': '10', '电影演出赛事': '25', '休闲娱乐': '30', '酒店': '60', '丽人': '50',
                 'K歌': '15',
                 '运动健身': '45', '景点/周边游': '35', '亲子': '70', '结婚': '55', '购物': '20', '宠物': '95',
                 '生活服务': '80', '学习培训': '75', '养车/用车': '65', '医疗健康': '85', '家居': '90',
                 '交通设施': '34259',
                 '地名地址信息': '50124', '其他分类': '5016'}
FoodCategory = {'不限': '', '面包/饮品': 'g117', '自助餐': 'g111', '火锅': 'g110', '湖北菜': 'g246', '咖啡厅': 'g132',
                '西餐': 'g116', '烧烤烤串': 'g508', '川菜': 'g102', '酒吧': 'g133', '小吃快餐': 'g112',
                '水果生鲜': 'g2714', '特色菜': 'g34284', '小吃面食': 'g217', '饮品店': 'g34236', '面馆': 'g215',
                '食品滋补': 'g33759', '家常菜': 'g1783', '农家菜': 'g25474', '私房菜': 'g1338', '小龙虾': 'g219',
                '鱼鲜': 'g251', '烤肉': 'g34303', '茶馆': 'g134', '北京菜': 'g311', '日本菜': 'g113',
                '韩国料理': 'g114', '湘菜': 'g104', '粤菜': 'g103', '东北菜': 'g106', '本帮江浙菜': 'g101',
                '新疆菜': 'g3243', '螺蛳粉': 'g32725', '东南亚菜': 'g115', '创意菜': 'g250', '素食': 'g109',
                '更多地方菜': 'g34351', '其他美食': 'g118'}


def login_with_qrcode(**kwargs) -> None:
    # check the page url is changed
    while driver.current_url != BASE_URL:
        time.sleep(1)
    return


def login_with_password(**kwargs) -> None:
    phone_number = kwargs.get('phone_number', config.account.get('phone', None))
    password = kwargs.get('password', config.account.get('password', None))

    # check the phone number and password
    assert phone_number is not None, 'Phone number is required'
    assert password is not None, 'Password is required'

    driver.implicitly_wait(5)

    # goto password login page
    driver.find_element(By.CLASS_NAME, 'bottom-password-login').click()
    driver.find_element(By.CLASS_NAME, 'segment-label-grey').click()

    # input username and password
    driver.find_element(By.ID, 'mobile-number-textbox').send_keys(phone_number)
    driver.find_element(By.ID, 'password-textbox').send_keys(password)

    # read the terms and login
    driver.find_element(By.ID, 'pc-check').click()
    driver.find_element(By.CLASS_NAME, 'button-pc').click()

    check_login_danger()
    check_login_auth()

    pass


def login_with_phone(**kwargs) -> None:
    phone_number = kwargs.get('phone_number', config.account.get('phone', None))

    # check the phone number
    assert phone_number is not None, 'Phone number is required'

    driver.implicitly_wait(5)

    # goto phone login page
    driver.find_element(By.CLASS_NAME, 'bottom-password-login').click()

    # read the terms
    driver.find_element(By.ID, 'pc-check').click()

    # input phone number
    driver.find_element(By.ID, 'mobile-number-textbox').send_keys(phone_number)
    driver.find_element(By.ID, 'send-vcode-button').click()

    check_login_danger()

    # wait to log in
    while driver.current_url == LOGIN_URL:
        time.sleep(1)

    pass


def login_with_cookies(**kwargs) -> None:
    with open(cookies_path, 'r') as f:
        cookies = json.loads(f.read())

    if cookies:
        for cookie in cookies:
            driver.add_cookie(cookie)


def check_cookies() -> bool:
    if cookies_path.exists() and cookies_path.is_file():
        return True
    return False


def save_cookies() -> None:
    with open(cookies_path, 'w') as f:
        f.write(json.dumps(driver.get_cookies()))


def check_login_danger() -> None:
    driver.implicitly_wait(5)

    if driver.find_element(By.CLASS_NAME, 'warning'):
        raise Exception('Login danger')


def check_login_auth() -> None:
    driver.implicitly_wait(5)

    while driver.current_url == LOGIN_URL:
        time.sleep(1)


def check_login() -> bool:
    driver.get(LOGIN_URL)

    time.sleep(1)
    driver.implicitly_wait(5)

    if driver.current_url == LOGIN_URL:
        return False
    else:
        return True


def login(types: Union[str, None] = None, **kwargs) -> None:
    """
    :param types: The type of login, can be 'qrcode', 'password', 'phone', 'cookies' or None (default)
    :return: None
    """
    driver.get(LOGIN_URL)

    if types is None:
        types = 'qrcode'

    if types == 'cookies' or check_cookies():
        login_with_cookies(**kwargs)

        if check_login():
            save_cookies()
            return

    if types == 'qrcode':
        login_with_qrcode(**kwargs)
    elif types == 'password':
        login_with_password(**kwargs)
    elif types == 'phone':
        login_with_phone(**kwargs)
    else:
        raise Exception('Unknown login type')

    assert check_login(), 'Login failed'

    save_cookies()


def get_search_page(url: str) -> int:
    driver.get(url)

    driver.implicitly_wait(5)

    # scroll to the bottom of the page
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

    page_cursor = driver.find_elements(By.CLASS_NAME, 'PageLink')

    # if page is empty, return 0
    if not page_cursor:
        return 0
    page_num = max(*[int(i.text) for i in page_cursor])
    return page_num


def get_page_detail(url: str, page_num: int) -> None:
    curr_url = f'{url}/p{page_num}'
    driver.get(curr_url)

    driver.implicitly_wait(5)

    # scroll to the bottom of the page
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

    # get the shop list
    shop_html = driver.find_element(By.CLASS_NAME, 'shop-list').get_attribute('innerHTML')
    soup = BeautifulSoup(shop_html, 'html.parser')
    shop_list = soup.find_all('li')
    obj_list = []
    for shop in shop_list:
        try:
            shop_name = shop.find('h4').text
            shop_url = shop.find('a').get('href')
            shop_star = int(shop.find('span', class_='star').attrs.get('class', ['', ''])[1][5:]) / 10
            shop_comment = shop.find('a', class_='review-num').find('b').text if shop.find('a',
                                                                                           class_='review-num') else 0
            shop_price = shop.find('a', class_='mean-price').find('b').text[1:] if shop.find('a',
                                                                                             class_='mean-price').find(
                'b') else -1
            shop_pic_url = shop.find('img').get('data-src')
            shop_category, shop_region = [i.text for i in
                                          shop.find('div', class_='tag-addr').find_all('span', class_='tag')]
            shop_recommend = shop.find('div', class_='recommend').text.strip()[5:].replace('\n', '，')
            promotion = shop.find('div', class_='svr-info') if shop.find('div', class_='svr-info') else False
            shop_promotion = 0 if not promotion else len(promotion.find_all('a')) - 1
            shop_promotion_info = '' if not promotion else '\n'.join(
                [i.text.strip() for i in promotion.find_all('a')][1:])

            s = Shop(name=shop_name, url=shop_url, category=shop_category, region=shop_region, star=shop_star,
                     comment=shop_comment, price=shop_price, pic_url=shop_pic_url, recommend=shop_recommend,
                     promotion=shop_promotion, promotion_info=shop_promotion_info)
            obj_list.append(s)
        except Exception as error:
            print(error)
    db.insert_shop(obj_list)
    pass


def search_keyword(keyword: str, types: str, **kwargs) -> None:
    channel = SearchChannel.get(types, '0')

    base_url = 'https://www.dianping.com/search/keyword/180'
    url = f'{base_url}/{channel}_{keyword}'

    start_page = kwargs.get('start_page', 1)
    end_page = kwargs.get('end_page', get_search_page(url))

    for i in range(start_page, end_page + 1):
        get_page_detail(url, i)
        time.sleep(5)
        pass

    pass


if __name__ == '__main__':
    db = Database('mysql+pymysql://root:20131114@localhost:3306/dianping?charset=utf8mb4')
    db.init()
    login()
    search_keyword('襄阳', '美食', start_page=5)
    pass
