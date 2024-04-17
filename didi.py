import datetime
import re
import time

from appium import webdriver
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common import TimeoutException
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
inviteSelector = 'new UiSelector().textMatches("立即同行|邀请同行")'
timeConfirmId = 'com.sdu.didi.psnger:id/time_result_btn'
confirmSelector = 'new UiSelector().resourceId("com.sdu.didi.psnger:id/btn_main_title").text("确认")'
# 定义最小顺路度
defineShun = 95
# 定义最小订单金额
definePrice = 65
# 是否能刷新
canRefresh = True

item = None
shun = None
price = None
i = 0


# 刷新
def refresh():
    # 滑动屏幕
    driver.swipe(x / 2, y / 2, x / 2, y, 200)


# 发送邮箱
def sendMail(title, content):
    # QQ邮件通知
    mail = QQMail()
    mail.sendMail(title, content)


while True:
    i += 1
    try:
        # 查找元素
        item = driver.find_element(By.ID, itemId)
        shun = item.find_element(By.ID, shunId).text
        shunNum = int(re.findall(r'\d+', shun)[0])
        # 顺路不符合目标
        if shunNum < defineShun:
            print(datetime.datetime.now(), f'顺路度{shunNum}%,低于{defineShun}%,继续第{i}次刷新')
            refresh()
            continue

        price = item.find_element(By.ID, priceId).text
        priceNum = float(re.findall(r'\d+\.\d+', price)[0])

        # 价格不符合目标
        if priceNum < definePrice:
            print(datetime.datetime.now(),
                  f'顺路度{shunNum},价格{priceNum}元,低于{definePrice}元,继续第{i}次刷新')
            refresh()
            continue

        print(datetime.datetime.now(),
              f'顺路度{shunNum},价格{priceNum}元,找到达到{defineShun}%顺路,{definePrice}元的订单,开始抢单...')
        # 点击邀请按钮
        item.find_element(AppiumBy.ANDROID_UIAUTOMATOR, inviteSelector).click()

    except Exception as e:
        print(datetime.datetime.now(), f'元素查找异常,继续第{i}次刷新')
        time.sleep(2)
        refresh()
        continue

    # 等待确认时间元素出现
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, confirmSelector))).click()
    except TimeoutException:
        # 订单已经被抢走
        print(datetime.datetime.now(), f'订单已经被抢走,继续第{i}次刷新')
        refresh()
        continue

    # 默认抢单成功
    print("抢单成功")
    sendMail('滴滴抢单成功提示', f'已抢到顺路{shun}、价格{price}的订单')
    break
# 退出驱动程序
print('退出程序')
driver.quit()
