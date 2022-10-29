import re
import os
import time
from lxml import etree
import smtplib
from email.mime.text import MIMEText

# Writable path to last known Public IP record cached. Best to place in tmpfs.
CACHED_IP_FILE = '/home/cachePublicIP/temp_IPv4.txt' #临时存放IP地址路径
CACHED_IP_DIR = "/".join(CACHED_IP_FILE.split('/')[0:-1])
CACHED_IP = None
CHECK_URL = 'http://www.ip111.cn' #获取IP地址URL
CACHEFILE_EXIST = False

# 第三方 SMTP 服务
mail_host = "**************"  # SMTP服务器地址
mail_user = "****************"  # 用户名[发件邮箱全名]
mail_pass = "**************"  # 授权密码，并不是邮箱密码

sender = '*****************'  # 发件人邮箱
receivers = ['**************']  # 接收邮件

title = ''  # 邮件主题
content = ''  # 邮件内容


# 发送邮件
def sendemail():
    message = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
    message['From'] = "{}".format(sender)
    message['To'] = ",".join(receivers)
    message['Subject'] = title

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
        smtpObj.login(mail_user, mail_pass)  # 登录验证
        smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
        print("mail has been send successfully.")
    except smtplib.SMTPException as e:
        print(e)


if __name__ == '__main__':
    localtime = time.localtime(time.time())  # 打印本地时间
    print("\n" + time.asctime(localtime))

    # 检查路径下文件夹，若不存在就创建一个
    if not os.path.exists(CACHED_IP_DIR):
        os.mkdir(CACHED_IP_DIR)
        CACHEFILE_EXIST = False
    else:
        # 检查路径下的文件，若不存在就创建文件
        if not os.path.isfile(CACHED_IP_FILE):
            os.mknod(CACHED_IP_FILE)
            CACHEFILE_EXIST = False
        else:
            with open(CACHED_IP_FILE, mode="r", encoding="utf-8") as f:
                CACHED_IP = f.read()
            CACHEFILE_EXIST = True

    # Get Host Public IP, When network is disconnected, program won't go wrong
    try:
        html = etree.parse(CHECK_URL, etree.HTMLParser())
        PUBLIC_IP = html.xpath('normalize-space(//div[@class="container"]/div[1]/div[1]/div[2]/p[1]/text())')[0:-3]

    except Exception as e:
        print(e.args)
        print(str(e))
        print(repr(e))
    else:
        regex = r"^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$"
        if re.search(regex, PUBLIC_IP):
            print("Public IP: {}".format(PUBLIC_IP))
        else:
            print("Fail! Public IP: {}".format(PUBLIC_IP))
            exit(1)

        print("Cached IP: {}".format(CACHED_IP))

        # Check if the IP needs to be updated
        if CACHEFILE_EXIST:
            if CACHED_IP != PUBLIC_IP:
                with open(CACHED_IP_FILE, mode="w", encoding="utf-8") as f:
                    f.write(PUBLIC_IP)
                content = time.asctime(localtime) + "\nOld ip address is : " + CACHED_IP + '\n' + "New ip address is : " + PUBLIC_IP
                sendemail()
            else:
                print("Current 'Public IP' matches 'Cached IP' recorded. No update required!\n")

        else:
            with open(CACHED_IP_FILE, mode="w", encoding="utf-8") as f:
                f.write(PUBLIC_IP)
            content = time.asctime(localtime) + "\nNew ip address is : " + PUBLIC_IP
            sendemail()
