#coding:utf8
import os
from jinja2 import Template
import sys
reload(sys)
sys.setdefaultencoding('utf8')

domain = 'cms.zhangte.org'


conf = open('site.conf').read()     #打开配置文件模板
template = Template(conf)           #传入模板对象


#渲染模板文件
path1 = os.getcwd()
path2 = path1.split('/')[:-1]
conf = template.render(path = '/'.join(path2),domain=domain)

siteconf = path2[-2]+'.conf'
print (siteconf)
#添加配置文件
path = '/etc/apache2/sites-available/' + siteconf
fl = open(path,'w')             #打开配置文件
fl.write(conf)                  #写入配置文件
fl.close()

output = os.popen('sudo a2ensite %s' % siteconf)
#output1 = os.popen("sudo service apache2 restart")
print output.read()
#print output1.read()
