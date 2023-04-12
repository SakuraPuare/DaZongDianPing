import time
from typing import Union

from selenium import webdriver

from config import *

driver = webdriver.Chrome()
config = Config()


def login_with_qrcode(**kwargs) -> None:
    # check the page url is changed
    while driver.current_url != 'https://www.dianping.com/':
        time.sleep(1)

    return


def login_with_password(**kwargs) -> None:
    pass


def login_with_phone(**kwargs) -> None:


    pass


def login_with_cookies(**kwargs) -> None:
    pass


def check_login() -> bool:
    driver.get('https://account.dianping.com/pclogin')

    driver.implicitly_wait(5)

    if driver.current_url == 'https://account.dianping.com/pclogin':
        return False
    else:
        return True


def login(types: Union[str, None] = None, **kwargs) -> None:
    """
    :param types: The type of login, can be 'qrcode', 'password', 'phone', 'cookies' or None (default)
    :return: None
    """
    driver.get('https://account.dianping.com/pclogin')

    if types is None:
        types = 'qrcode'

    if types == 'qrcode':
        login_with_qrcode(**kwargs)
    elif types == 'password':
        login_with_password(**kwargs)
    elif types == 'phone':
        login_with_phone(**kwargs)
    elif types == 'cookies':
        login_with_cookies(**kwargs)
    else:
        raise Exception('Unknown login type')

    assert check_login()


def search(keyword: str, types: str, **kwargs) -> None:
    base_url = 'https://www.dianping.com/search/keyword/'

    pass


if __name__ == '__main__':
    login()
    pass
