from selenium import webdriver
import time
import re
import pymysql
import xlrd


# 搜索需要的商品
def taobao_login():
    driver.find_element_by_xpath('.//div[@class="login-password"]')
    driver.find_element_by_xpath('//*[@id="login-form"]/div[5]/a[1]').click()
    driver.find_element_by_xpath('//*[@id="pl_login_logged"]/div/div[2]/div/input').send_keys(username)
    driver.find_element_by_xpath('//*[@id="pl_login_logged"]/div/div[3]/div/input').send_keys(password)
    driver.find_element_by_xpath('//*[@id="pl_login_logged"]/div/div[7]/div[1]').click()
    time.sleep(5)


# 因为有时由于网速等原因，下面的商品信息没有加载出来导致获取不到需要的信息，所以在定义一个下拉函数，让所有商品都展示出来
def drop_down():
    for x in range(1, 11, 2):
        time.sleep(0.5)
        j = x / 10
        js = 'document.documentElement.scrollTop = document.documentElement.scrollHeight * %f' % j
        driver.execute_script(js)


# 获取商品信息
def get_product():
    # 检查分析商品页面发现所有的商品信息的class标签并不一样 所以用xpath的组合选择将两种标签属性都选上
    driver.implicitly_wait(5)
    divs = driver.find_elements_by_xpath(
        '//div[@class="items"]/div[@class="item J_MouserOnverReq  "]|//div[@class="items"]/div[@class="item J_MouserOnverReq item-ad  "]')

    for div in divs:  # 遍历得到需要的每个信息
        info = div.find_element_by_xpath('.//div[@class="row row-2 title"]').text
        price = div.find_element_by_xpath('.//div[@class="price g_price g_price-highlight"]').text
        deal = div.find_element_by_xpath('.//div[@class="deal-cnt"]').text
        shop = div.find_element_by_xpath('.//div[@class="shop"]').text
        location = div.find_element_by_xpath('.//div[@class="location"]').text
        image = div.find_element_by_xpath('.//div[@class="pic"]/a/img').get_attribute('src')
        product = {'info': info, 'price': price, 'deal': deal, 'shop': shop, 'location': location, 'image': image}
        # print(product)
        save_to_mysql(product)


# 将数据存储到数据库
def save_to_mysql(product):
    try:
        conn = pymysql.connect(host='数据库ip', user='用户名', passwd='密码', port=端口, db='数据库名称',
                               charset='utf8')  # 链接数据库
        cur = conn.cursor()  # 创建游标
        sql = """insert into test3 (info,price,deal,shop,location,image)values(%s,%s,%s,%s,%s,%s)"""  # 插入数据
        cur.execute(sql, (
            product['info'], product['price'], product['deal'], product['shop'], product['location'], product['image']))
        # print('---数据存入成功---')
        cur.close()
        conn.commit()
        conn.close()
    except pymysql.Error as e:
        print(e)


# 翻页函数
def next_page():
    taobao_login()
    # 从EXCEL文件中读取关键字
    data = xlrd.open_workbook('EXCEL文件')  ##读取句柄打开指定的文件
    table = data.sheet_by_index(0)  ##获取Excel工作簿的指定工作表
    sheet = data.sheet_by_index(0)  # sheet索引从0开始
    cols = sheet.col_values(0)  # 获取第2列的内容
    for i in cols:
        num = 0
        kw = i
        time.sleep(5)
        driver.get('https://s.taobao.com/search?q={}'.format(kw))
        print("当前关键词：", kw)
        token = driver.find_element_by_xpath('//*[@id="mainsrp-pager"]/div/div/div/div[1]').text  # 定位到页码框得到页码数
        token = int(re.compile('(\d+)').search(token).group(1))  # 使用正则表达式提取总页码数
        print("共", token, "页")
        while num != token:  # 当当前页不为总页码时进行下面的循环
            driver.get('https://s.taobao.com/search?q={}&s={}'.format(kw, 44 * num))
            # driver.implicitly_wait(5)# 等待时间
            num += 1
            print('第', num, '页')
            drop_down()
            get_product()


if __name__ == '__main__':
    start = time.clock()
    # 链接数据库
    # conn = pymysql.connect(host='数据库ip地址', user='用户名', passwd='密码', port=端口, db='数据库名', charset='utf8')
    # cur = conn.cursor()
    # 创建数据库表来存放数据
    # sqlcreate = """CREATE TABLE test3 (
    #         id INT primary key NOT NULL AUTO_INCREMENT,
    #         info VARCHAR(500),
    #         price VARCHAR(500),
    #         deal VARCHAR(500),
    #         shop VARCHAR(500),
    #         location VARCHAR(500),
    #         image VARCHAR(1000))"""
    # cur.execute(sqlcreate)  # 执行sql创建语句
    username = '淘宝绑定微博的账号'
    password = '淘宝绑定微博的密码'
    # kw = input("说吧，干谁：")
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 关闭自动控制提示
    options.add_experimental_option('useAutomationExtension', False)  # 设置为开发者模式
    options.add_argument('blink-setting=imagesEnabled=false')  # 不加载图片
    options.add_argument('--headless')  # 设置为无界面
    driver = webdriver.Chrome(chrome_options=options)
    driver.get('https://login.taobao.com/member/login.jhtml')  # 获取URL
    next_page()
    end = time.clock()
    print("总计用时", end - start)
