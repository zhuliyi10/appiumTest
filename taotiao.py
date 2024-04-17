from appium import webdriver
from appium.options.common.base import AppiumOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# 设置Appium参数
options = AppiumOptions()
options.load_capabilities({
    "appium:automationName": "uiautomator2",
    "platformName": "Android",
    "appPackage": "com.ss.android.article.news",
    "appActivity": "com.ss.android.article.news.activity.MainActivity",
    "noReset": True
})

# 创建Appium驱动程序
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
print('driver has init')
x = driver.get_window_size()['width']
y = driver.get_window_size()['height']
wait = WebDriverWait(driver, 5)
for i in range(10):
    print(f'第 {i} 次刷新开始')
    driver.swipe(x / 2, y / 2, x / 2, y * 3 / 4, 0)
    print(f'第 {i} 次刷新结束')
    refreshXpath = '//android.widget.RelativeLayout[@resource-id="com.ss.android.article.news:id/fr5"]'
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, refreshXpath)))
    except Exception as e:
        print('发生异常:', e)
    print('刷新出现')
    try:
        wait.until_not(EC.presence_of_element_located((By.XPATH, refreshXpath)))
    except Exception as e:
        print('发生异常:', e)
    print('刷新消失')

# 退出驱动程序
print('退出程序')
driver.quit()
