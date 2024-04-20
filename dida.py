import time
from datetime import datetime

from appium import webdriver
from appium.options.common.base import AppiumOptions
from lxml import etree
from selenium.webdriver.common.by import By

from send_mail import QQMail

# 设置Appium参数
options = AppiumOptions()
options.load_capabilities({
    "appium:automationName": "uiautomator2",
    "platformName": "Android",
    # "appPackage": "com.sdu.didi.psnger",
    # "appActivity": "com.didi.sdk.app.MainActivity",
    "udid": "192.168.1.5:5555",
    "waitForIdleTimeout": 100,  # 要加上这个元素，不然查找元素很慢
    "noReset": True  # 不重置应用
})

# 创建Appium驱动程序
driver = webdriver.Remote("http://127.0.0.1:4725", options=options)
print('driver has init')
time.sleep(2)
source=driver.page_source
print(source)

# 退出驱动程序
print('退出程序')
driver.quit()
