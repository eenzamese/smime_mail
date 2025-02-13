try:
    import time
    import random
    import requests
    import smtplib
    import string
    import sqlite3
    import urllib2
    import sys
    import logging
    import sys
    import socket
    import shutil
    from os import sep
    from subprocess import Popen
    if plat == 'Linux':
        import syslog
        from Crypto.Cipher import AES
        from Crypto import Random
        from M2Crypto import SMIME
        from M2Crypto import X509
        from M2Crypto import BIO
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from subprocess import PIPE
    from termcolor import colored
    from hashlib import md5
    from multiprocessing import Value
except Exception as ex:
    print ex
    str_out = "%s [CRITICAL]\t\tSystem import error" % ctime()
    logging.critical(str_out+'. '+str(ex))
    print str_out
    try:
        os.system('reboot')
    except Exception as ex:
        str_out = "%s [CRITICAL]\t\tCant reboot. Are you root?" % ctime()
        logging.critical(str_out+'. '+str(ex))
        print str_out
    sys.exit()
    



if plat == 'Linux':
        import syslog
        from Crypto.Cipher import AES
        from Crypto import Random
        from M2Crypto import SMIME
        from M2Crypto import X509
        from M2Crypto import BIO


def sendsmime(from_addr=mail_cfg['mail_login'],
                  to_addrs=[mail_cfg['mbox']],
                  subject=mail_cfg['theme'],
                  msg='Test_content',
                  from_key=default_from_key,
                  from_cert=default_from_cert,
                  to_certs=default_to_certs):
        subject = subject+str(ctime())
        msg_bio = BIO.MemoryBuffer(msg)
        sign = from_key
        encrypt = to_certs
        s = SMIME.SMIME()
        if sign:
            s.load_key(from_key, from_cert)
            p7 = s.sign(msg_bio, flags=SMIME.PKCS7_TEXT)
            msg_bio = BIO.MemoryBuffer(msg)
        if encrypt:
            sk = X509.X509_Stack()
            for x in to_certs:
                sk.push(X509.load_cert(x))
            s.set_x509_stack(sk)
            s.set_cipher(SMIME.Cipher(crypt_settings['cipher_mode']))
            tmp_bio = BIO.MemoryBuffer()
            if sign:
                s.write(tmp_bio, p7)
            else:
                tmp_bio.write(msg)
            p7 = s.encrypt(tmp_bio)
        out = BIO.MemoryBuffer()
        out.write('From: %s\r\n' % from_addr)
        out.write('To: %s\r\n' % string.join(to_addrs, ", "))
        out.write('Subject: %s\r\n' % subject)
        if encrypt:
            s.write(out, p7)
        else:
            if sign:
                s.write(out, p7, msg_bio, SMIME.PKCS7_TEXT)
            else:
                out.write('\r\n')
                out.write(msg)
        out.close()
        smtp = smtplib.SMTP(mail_cfg['smtp_server'], 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(mail_cfg['mail_login'], mail_cfg['mail_password'])
        smtp.sendmail(from_addr, to_addrs, out.read())
        smtp.quit()
