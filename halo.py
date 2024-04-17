import datetime
import re
import sys
import time

from appium import webdriver
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from send_mail import QQMail

# 设置Appium参数
options = AppiumOptions()
options.load_capabilities({
    "appium:automationName": "uiautomator2",
    "platformName": "Android",
    "appPackage": "com.jingyao.easybike",
    "udid": "192.168.1.5:5555",
    "waitForIdleTimeout": 100,  # 要加上这个元素，不然查找元素很慢
    # "appActivity": "com.didi.sdk.app.MainActivity",
    "noReset": True
})

# 创建Appium驱动程序
driver = webdriver.Remote("http://127.0.0.1:4725", options=options)
print('driver has init')

# 获取屏幕尺寸
x = driver.get_window_size()['width']
y = driver.get_window_size()['height']
# 创建ActionChains对象
actions = ActionChains(driver)
wait = WebDriverWait(driver, 5)
# 定义元素ID
itemId = 'com.jingyao.easybike:id/tvMainInfoLayout'
shunId = 'com.jingyao.easybike:id/tvHitchPercent'
priceId = 'com.jingyao.easybike:id/tvAmount'
confirmId = 'com.jingyao.easybike:id/tvButton'
confirmSelector = 'new UiSelector().resourceId("com.jingyao.easybike:id/tvButton").textMatches("确认同行|立即抢单")'
confirmTimeId = 'com.jingyao.easybike:id/tvPickerSure'
otherSelector = 'new UiSelector().text("查看其他订单")'
startDistanceId = 'com.jingyao.easybike:id/tvStartDistanceCross'
startDistanceId2 = 'com.jingyao.easybike:id/tvStartAddress'

# 定义最小顺路度
defineShun = 90
# 定义最小订单金额
definePrice = 80
# 是否能刷新
canRefresh = True

shun = None
price = None

while True:
    for i in range(sys.maxsize):
        try:
            if canRefresh:
                driver.swipe(x / 2, y * 3 / 5, x / 2, y, 0)
                time.sleep(1)

            # 查找元素
            list = driver.find_elements(By.ID, itemId)
            canRefresh = True
            item = list[0]
            shun = item.find_element(By.ID, shunId).text

            shunNum = int(re.findall(r'\d+', shun)[0])
            if shunNum < defineShun:
                print(datetime.datetime.now(), f'顺路度{shunNum}%,低于{defineShun}%,继续第{i + 1}次刷新')
                continue

            price = item.find_element(By.ID, priceId).text
            priceNum = float(re.findall(r'\d+\.\d+', price)[0])

            if priceNum < definePrice:
                print(datetime.datetime.now(),
                      f'顺路度{shunNum},价格{priceNum}元,低于{definePrice}元,继续第{i + 1}次刷新')
                continue

            print(datetime.datetime.now(),
                  f'顺路度{shunNum},价格{priceNum}元,找到达到{defineShun}%顺路,{definePrice}元的订单,开始抢单...')
            break
        except Exception as e:
            # 不在订单列表页面
            print('请回到订单列表页面')
            time.sleep(2)
            canRefresh = False

    item.click()

    try:
        wait.until(EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, confirmSelector))).click()
        wait.until(EC.presence_of_element_located((By.ID, confirmTimeId))).click()
        try:
            # 如果订单已失效，点击查看其他订单
            wait.until(EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, otherSelector))).click()
        except Exception as e:
            break

        break
    except Exception as e:
        print(e)

print("抢单成功")
# QQ邮件通知
mail = QQMail()
mail.sendMail('哈啰抢单成功提示', f'已抢到顺路{shun}、价格{price}的订单')
# 退出驱动程序
print('退出程序')
driver.quit()
