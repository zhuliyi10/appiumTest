# -*- coding: UTF-8 -*-

import smtplib
from email.header import Header
from email.mime.text import MIMEText

# 第三方 SMTP 服务
mail_host = "smtp.qq.com"  # 设置服务器
mail_user = "2280835569@qq.com"  # 用户名
mail_pass = "pbxzmlefeoqaecae"  # 口令


class QQMail(object):

    def sendMail(self, title='标题', content='内容'):

        sender = '2280835569@qq.com'
        receiver = '2280835569@qq.com'  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

        # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = sender  # 发送者
        message['To'] = receiver  # 接收者

        subject = title
        message['Subject'] = Header(subject, 'utf-8')

        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
            smtpObj.login(mail_user, mail_pass)
            smtpObj.sendmail(sender, receiver, message.as_string())
            print("邮件发送成功")
        except smtplib.SMTPException as e:
            print("Error: 无法发送邮件", e)


if __name__ == "__main__":
    mail = QQMail()
    mail.sendMail()
