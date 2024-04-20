import re
import time
from datetime import datetime

from appium import webdriver
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from lxml import etree
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from uiautomator2.xpath import TimeoutException

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

# 定义元素Xpath
itemsXpath = '//android.view.ViewGroup[@resource-id="com.sdu.didi.psnger:id/sfc_wait_list_item_layout"]'
shunXpath = '//android.widget.TextView[@resource-id="com.sdu.didi.psnger:id/sfc_new_order_card_degree_title"]'
priceXpath = '//android.widget.TextView[@resource-id="com.sdu.didi.psnger:id/sfc_order_price_content"]'
orderTimeXpath = '//android.widget.TextView[@resource-id="com.sdu.didi.psnger:id/sfc_new_order_card_time_title"]'
fromAddressXPath = '//android.widget.TextView[@resource-id="com.sdu.didi.psnger:id/from_tv"]'
fromDistanceXpath = '//android.widget.TextView[@resource-id="com.sdu.didi.psnger:id/from_tv_tag"]'
toAddressXPath = '//android.widget.TextView[@resource-id="com.sdu.didi.psnger:id/to_tv"]'
toDistanceXpath = '//android.widget.TextView[@resource-id="com.sdu.didi.psnger:id/to_tv_tag"]'
orderContentXpath = '//android.widget.TextView[@resource-id="com.sdu.didi.psnger:id/sfc_order_card_tips_content"]'

itemId = 'com.sdu.didi.psnger:id/sfc_wait_list_item_layout'
inviteSelector = 'new UiSelector().textMatches("立即同行|邀请同行")'
confirmSelector = 'new UiSelector().resourceId("com.sdu.didi.psnger:id/btn_main_title").text("确认")'

# 定义最小顺路度
defineShun = 95
# 定义最小订单金额
definePrice = 80

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
        source = driver.page_source
        root = etree.fromstring(source.encode('utf-8'))
        item = root.xpath(itemsXpath)[0]
        shun = item.xpath(shunXpath)[0].get('text')
        price = item.xpath(priceXpath)[0].get('text')
        fromAddress = item.xpath(fromAddressXPath)[0].get('text')
        fromDistance = item.xpath(fromDistanceXpath)[0].get('text')
        toAddress = item.xpath(toAddressXPath)[0].get('text')
        toDistance = item.xpath(toDistanceXpath)[0].get('text')
        orderContent = item.xpath(orderContentXpath)[0].get('text')
        shunNum = int(re.findall(r'\d+', shun)[0])
        # 顺路不符合目标
        if shunNum < defineShun:
            print(datetime.now(), f'顺路度{shunNum}%,低于{defineShun}%,继续第{i}次刷新')
            refresh()
            continue
        priceNum = float(re.findall(r'\d+\.\d+', price)[0])
        # 价格不符合目标
        if priceNum < definePrice:
            print(datetime.now(),
                  f'顺路度{shunNum},价格{priceNum}元,低于{definePrice}元,继续第{i}次刷新')
            refresh()
            continue

        print(datetime.now(),
              f'顺路度:{shun} 价格:{price} 起点位置:{fromAddress} 起点距离:{fromDistance} 终点位置:{toAddress} 终点距离:{toDistance} 拼单详情:{orderContent}')
        driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, inviteSelector).click()
    except Exception as e:
        print(datetime.now(), f'元素查找异常,继续第{i}次刷新')
        print(e)
        time.sleep(2)
        refresh()
        continue
    # 等待确认时间元素出现
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, confirmSelector))).click()
    except TimeoutException:
        # 订单已经被抢走
        print(datetime.now(), f'订单已经被抢走,继续第{i}次刷新')
        refresh()
        continue

    # 默认抢单成功
    print("抢单成功")
    sendMail('滴滴抢单成功提示', f'已抢到顺路{shun}、价格{price}的订单')
    break

# 退出驱动程序
print(datetime.now(),'退出程序')
driver.quit()
