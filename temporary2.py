import datetime
import re
import time

from appium import webdriver
from appium.options.common.base import AppiumOptions
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from send_mail import QQMail

# 查看appPackage和appActivity
# adb -s 192.168.0.100:5555 shell dumpsys activity recents | find "intent={"
options = AppiumOptions()
options.load_capabilities({
    "platformName": "Android",
    "platformVersion": "11",
    "deviceName": "realme RMX1991",
    "udid": "NFQSDYCQROT8SGQ8",
    # "udid": "192.168.1.5:5555",
    "appPackage": "com.jingyao.easybike",
    "appActivity": "com.hellobike.atlas.business.portal.PortalActivity",
    "noReset": True,
    "newCommandTimeout": 6000,
    "automationName": "uiautomator2",
    'skipServerInstallation': True,
    'skipDeviceInitialization': True
})

# 连接Appium Server，初始化自动化环境
driver = webdriver.Remote('http://127.0.0.1:4725', options=options)

# 获取屏幕尺寸1
screen_width = driver.get_window_size()['width']
screen_height = driver.get_window_size()['height']

# 定义最小顺路度(%)
define_shun = 90
# 定义最小订单金额(元)
define_price = 70
# 定义最大起点距离(km)
define_start_distance = 90

while True:
    item = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.ID, 'com.jingyao.easybike:id/tvMainInfoLayout')))

    # 检查顺路度
    shun_element = item.find_element(By.ID, 'com.jingyao.easybike:id/tvHitchPercent')
    shun_num = int(shun_element.text.split('%')[0])
    if shun_num < define_shun:
        print(datetime.datetime.now(), f'顺路{shun_num}%,顺路未达到要求，继续刷新')
        driver.swipe(start_x=screen_width // 2, start_y=screen_height // 2, end_x=screen_width // 2,
                     end_y=screen_height * 0.8, duration=200)
        # time.sleep(random.uniform(0, 0.5))
        continue

    # 检查订单价格
    price_element = item.find_element(By.ID, 'com.jingyao.easybike:id/tvAmount')
    price_num = float(price_element.text)
    if price_num < define_price:
        print(datetime.datetime.now(), f'顺路{shun_num}%,{price_num}元,价格未达到要求，继续刷新')
        driver.swipe(start_x=screen_width // 2, start_y=screen_height // 2, end_x=screen_width // 2,
                     end_y=screen_height, duration=200)
        continue

    # # 检查起点距离
    # try:
    #     start_distance_element = item.find_element(By.ID, 'com.jingyao.easybike:id/tvStartAddress')
    #     print(start_distance_element.text)
    # except NoSuchElementException:
    #     start_distance_element = item.find_element(By.ID, 'com.jingyao.easybike:id/tvStartDistanceCross')
    # start_distance_num = float(re.search(r"\d+(\.\d+)?", start_distance_element.text).group())
    # if start_distance_num > define_start_distance:
    #     print(datetime.datetime.now(),
    #           f'顺路{shun_num}%,{price_num}元,起点{start_distance_num}km,起点距离未达要求,继续刷新')
    #     driver.swipe(start_x=screen_width // 2, start_y=screen_height // 2, end_x=screen_width // 2,
    #                  end_y=screen_height, duration=200)
    #     continue

    # 找到设定的订单,开始抢单
    shun_element.click()
    print(datetime.datetime.now(), f'顺路{shun_num}%,价格{price_num}元,开始抢单')
    try:
        # 确认同行或立即抢单,是同一个ID吗?     立即抢单ID:com.jingyao.easybike:id/tvButton  确认同行ID:com.jingyao.easybike:id/tvButton
        # driver.find_element(By.ID,'com.jingyao.easybike:id/tvButton').click()
        # 舒适拼订单,立即抢单怎么总是点不了?
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, 'com.jingyao.easybike:id/tvButton'))).click()
    except TimeoutException:
        print('订单已失效,该订单已被接走,去看看其他订单吧,查看其他订单1')
        driver.find_element(By.XPATH, '//android.widget.Button[@text="查看其他订单"]').click()
        driver.swipe(start_x=screen_width // 2, start_y=screen_height // 2, end_x=screen_width // 2,
                     end_y=screen_height, duration=200)
        continue

    # 提示确认接单类型,选择接独享
    try:
        WebDriverWait(driver, 0.2).until(EC.presence_of_element_located(
            (By.XPATH, '(//android.widget.CheckBox[@resource-id="com.jingyao.easybike:id/checkBox"])[2]'))).click()
        print('提示确认接单类型,选择接独享')
        driver.find_element(By.ID, 'com.jingyao.easybike:id/tvPickerSure').click()
    except TimeoutException:
        print('没有提示确认接单类型')
        pass

    # 提醒不出高速费或使用油车
    try:
        WebDriverWait(driver, 0.2).until(
            EC.presence_of_element_located((By.ID, 'com.jingyao.easybike:id/tvButton'))).click()
        print('提示乘客不出高速费或指定油车')
    except TimeoutException:
        print('没有谈及高速费或指定油车')
        pass

    # 提醒临近出发时间,不沟通时间,直接确认同行
    try:
        WebDriverWait(driver, 0.2).until(
            EC.presence_of_element_located((By.ID, 'com.jingyao.easybike:id/tvRightButton'))).click()
        print('若无法保证,请与乘客沟通其他时间:确认同行1')
    except TimeoutException:
        print('没有提示需要沟通时间1')
        pass

    try:
        # 选择到达乘客起点的时间,选了最早出发时间
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.ID, 'com.jingyao.easybike:id/tvPickerSure'))).click()
    except TimeoutException:
        # 订单已失效, 该订单已被接走, 去看看其他订单吧, 查看其他订单
        WebDriverWait(driver, 4).until(
            EC.presence_of_element_located((By.XPATH, '//android.widget.Button[@text="查看其他订单"]'))).click()
        print(datetime.datetime.now(), '订单已失效,该订单已被接走,去看看其他订单吧,查看其他订单2')
        driver.swipe(start_x=screen_width // 2, start_y=screen_height // 2, end_x=screen_width // 2,
                     end_y=screen_height, duration=200)
        continue

    # 提醒临近出发时间,不沟通时间,直接确认同行
    try:
        WebDriverWait(driver, 0.2).until(
            EC.presence_of_element_located((By.ID, 'com.jingyao.easybike:id/tvRightButton'))).click()
        print('若无法保证,请与乘客沟通其他时间:确认同行2')
    except TimeoutException:
        print('没有提示需要沟通时间2')
        pass

    # 根据抢单结果判断是否抢单成功

    try:
        # 为了让页面稳定,这个加时间不能影响到抢单环节
        time.sleep(2)
        # 加入失败,该订单已在确认接单中,返回继续刷新
        # WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.ID, 'com.jingyao.easybike:id/tvButton')))
        # input('回车键1')
        # 如果左上角有ID:com.jingyao.easybike:id/ivOrderBack,说明加入失败,该订单已在确认接单中,返回继续刷新
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, 'com.jingyao.easybike:id/ivOrderBack'))).click()
        print('加入失败,该订单已在确认接单中,返回继续刷新')
        driver.swipe(start_x=screen_width // 2, start_y=screen_height // 2, end_x=screen_width // 2,
                     end_y=screen_height, duration=200)
        continue
    except TimeoutException:
        pass

    try:
        # input('回车键2')
        # 订单已失效, 该订单已被接走, 去看看其他订单吧, 查看其他订单
        WebDriverWait(driver, 4).until(
            EC.presence_of_element_located((By.XPATH, '//android.widget.Button[@text="查看其他订单"]'))).click()
        # 订单已失效的XPath的元素不同?                                                         //android.widget.Button[@text="查看其他订单"]
        # WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, '//android.widget.TextView[@text="返回查看其他订单"]'))).click()
        print(datetime.datetime.now(), '订单已失效,该订单已被接走,去看看其他订单吧,查看其他订单3')
        driver.swipe(start_x=screen_width // 2, start_y=screen_height // 2, end_x=screen_width // 2,
                     end_y=screen_height, duration=200)
        continue
    except TimeoutException:
        pass

    # 进行抢单PK
    print('正在PK中,最多30秒,请耐心等待')
    try:
        # 有这个元素代表抢单成功,ID:恭喜你，抢单成功
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, '//android.widget.TextView[@text="恭喜你，抢单成功"]')))
        print('PK抢单成功')
        mail = QQMail()
        mail.sendMail("哈啰抢单成功提醒",
                      f' 抢到顺路{shun_num}%,价格{price_num}元的订单,请及时查看')
        break
    except TimeoutException:
        try:
            # 有这个元素代表抢单成功,ID:安全中心
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.ID, 'com.jingyao.easybike:id/tvOperationOne')))
            print('常规抢单成功')
            mail = QQMail()
            mail.sendMail("哈啰抢单成功提醒",
                          f' 抢到顺路{shun_num}%,价格{price_num}元的订单,请及时查看')
            break
        except TimeoutException:
            WebDriverWait(driver, 2).until(EC.presence_of_element_located(
                (By.XPATH, '//android.widget.TextView[@text="返回查看其他订单"]'))).click()
            print(datetime.datetime.now(), '很遗憾,抢单失败,返回查看其他订单')
            driver.swipe(start_x=screen_width // 2, start_y=screen_height // 2, end_x=screen_width // 2,
                         end_y=screen_height, duration=200)

# 退出驱动程序
print('退出程序')
driver.quit()
