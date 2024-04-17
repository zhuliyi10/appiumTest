import datetime
import re
import sys
import time

from appium import webdriver
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from send_mail import QQMail

# 设置Appium参数
options = AppiumOptions()
options.load_capabilities({
    "appium:automationName": "uiautomator2",
    "platformName": "Android",
    "appPackage": "com.sdu.didi.psnger",
    "appActivity": "com.didi.sdk.app.MainActivity",
    "udid": "127.0.0.1:58526",  # 指定连接的设备
    "waitForIdleTimeout": 100,  # 要加上这个元素，不然查找元素很慢
    "noReset": True  # 不重置应用
})

# 创建Appium驱动程序
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
print('driver has init')

# 获取屏幕尺寸1
x = driver.get_window_size()['width']
y = driver.get_window_size()['height']

# 定义元素ID
itemId = 'com.sdu.didi.psnger:id/sfc_wait_list_item_layout'
shunId = 'com.sdu.didi.psnger:id/sfc_new_order_card_degree_title'
priceId = 'com.sdu.didi.psnger:id/sfc_order_price_content'
inviteId = 'com.sdu.didi.psnger:id/sfc_wait_list_send_invit_button'
timeConfirmId = 'com.sdu.didi.psnger:id/time_result_btn'
confirmSelector = 'new UiSelector().resourceId("com.sdu.didi.psnger:id/btn_main_title").text("确认")'
# 定义最小顺路度
defineShun = 95
# 定义最小订单金额
definePrice = 80
# 是否能刷新
canRefresh = True

item = None
shun = None
price = None

while True:

    for i in range(sys.maxsize):
        try:
            if canRefresh:
                # 滑动屏幕
                driver.swipe(x / 2, y / 2, x / 2, y, 0)

            # 查找元素
            list = driver.find_elements(By.ID, itemId)
            canRefresh = True
            if len(list) == 0:
                time.sleep(2)
                continue
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
    # 点击邀请按钮
    item.find_element(By.ID, inviteId).click()

    # 等待确认时间元素出现
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, confirmSelector))).click()
    break

print("抢单成功")
# QQ邮件通知
mail = QQMail()
mail.sendMail('滴滴抢单成功提示', f'已抢到顺路{shun}、价格{price}的订单')
# 退出驱动程序
print('退出程序')
driver.quit()
