# -*- coding: utf-8 -*-
import urllib
import urllib2
import cookielib
from bs4 import BeautifulSoup
import random
import time
from StringIO import StringIO
import gzip
day = 0
while True:
    day = day +1
    print "This is "+str(day)+" days"
    print "Start at "+time.ctime()
    cookie = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    opener.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36'),
                         ('Connection','keep-alive'),
                         ('Host','t66y.com'),
                         ('Origin','http://t66y.com'),
                         ('Referer','http://t66y.com/index.php'),
                         ('Accept-Encoding','gzip')]
    url = 'http://t66y.com/index.php'
    index = opener.open(url)
    login_data = {}
    login_data['pwuser'] = ''
    login_data['pwpwd'] = ''
    login_data['jumpurl'] = 'index.php'
    login_data['step'] = '2'
    login_data['cktime'] = '31536000'
    post_data = urllib.urlencode(login_data)
    try:
        login_success = opener.open('http://t66y.com/login.php',post_data) #登陆
    except:
        day = day - 1
        continue
    file = open('zong.txt','r')
    all_lines = file.readlines()
    file.close()
    file = open('zong.txt','r')
    i = 0
    for line in file:
        line = line.strip('\n')
        del all_lines[0]
        page_url = 'http://t66y.com/'+line
        try:
            page_open = opener.open(page_url)
        except:
            print 'open t66y error'
            continue
        if page_open.info().get('Content-Encoding') == 'gzip':
            page_content = gzip.GzipFile(fileobj=StringIO(page_open.read())).read()
        else:
            page_content = page_open.read()
        soup = BeautifulSoup(page_content,'html.parser',from_encoding='gb18030')
        p_node1 = soup.find_all('input',type = "hidden")
        p_node2 = soup.find_all('input',type = "checkbox")
        p_node3 = soup.find_all(class_='input')
        temp = p_node3[0].get('value')
        try:
            temp = temp.encode('gb18030')
        except:
            print 'encode error'
            continue
        '''
        m = {'par':temp.decode('utf-8').encode('gb2312')}
        s = urllib.urlencode(m)
        print s
        '''
        reply = {}
        reply['atc_content'] = '1024'
        for nodes in p_node1:
            reply[nodes['name']] = nodes['value']
        for nodes in p_node2:
            reply[nodes['name']] = nodes['value']
        reply['atc_title'] = temp
        reply_data = urllib.urlencode(reply)
        #print reply_data
        try:
            result = opener.open('http://t66y.com/post.php',reply_data)
        except:
            print 'reply error'
            continue
        if result.info().get('Content-Encoding')=='gzip':
            result_content = gzip.GzipFile(fileobj=StringIO(result.read())).read()
        else:
            result_content = result.read()
        resultfile = open('result.html','w')
        resultfile.write(result_content)
        resultfile.close()
        i = i + 1
        print "success "+str(i)+' on '+line
        if i==10:
            break
        else:
            time.sleep(1024+random.sample(range(120,320),1)[0])
    file.close()
    file = open('zong.txt','w')
    file.writelines(all_lines)
    file.close()
    wait_hour = 24-int(time.localtime()[3])+random.sample(range(0,18),1)[0]
    wait_second = random.sample(range(100,2400),1)[0]
    print "End at "+time.ctime()+"\n"+"Next start at "+time.asctime(time.localtime(time.time()+3600*wait_hour+wait_second))
    time.sleep(wait_hour*3600+wait_second)
