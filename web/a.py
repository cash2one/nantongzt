#coding:utf8
import jieba.analyse
import random
import re
from web.models import *
import requests

#提取tags标签
def tags(html):
    tags = jieba.analyse.extract_tags(html,random.randint(1,4))
    return ",".join(tags)


#更新长尾词记录单
def changwei(content,changweis):
    for changwei in changweis:
        kw = changwei.title
        url = changwei.url
        if  kw in content:
            allkw = re.findall('<a href.+?>(.+?)</a>',content)    #找出所有链接
            if kw not in allkw:       #如果发现关键词在这篇文章中没有添加链接
                kw1 = '<a href="{url}" title="{kw}">{kw}</a>'.format(kw=kw,url = url)
                content = content.replace(kw,kw1,1)
    return content

#更新tags链接
def uppdatetags():
    tags_list = []
    for post in  Article.objects.all():
        if post.tags:
            tags_list+=post.get_tags()
    #先删除掉所有的tags
    for tag in set(tags_list):  #获取了所有的标签
        try:
            Tag.objects.get(title=tag)
        except Tag.DoesNotExist:
            Tag.objects.create(title=tag,url='/tag/%s' % tag)    #对所有的长尾进行删除
