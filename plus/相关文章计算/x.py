#coding:utf8
import jieba.analyse
import random
import re
import sys
sys.path.append("../..")
from mysite.wsgi import *
from web.models import *
import requests
import pandas
import numpy


#先清空里面的数据
Xiangguan.objects.all().delete()


#去除掉所有的html标签
def cuthtml(content):
    p2 = re.compile(r'</?\w+[^>]*>|</?(a|p style|blockquote)[^>]*>|(http.+?html)|&.*?;')
    content = p2.sub('',content) #去除所有的html代码
    return content

titles = []
contents = []
pk = []

wenzhangs = Article.objects.all()
for wenzhang in wenzhangs:
    title = wenzhang.title
    content = cuthtml(wenzhang.content.strip())  #先去掉空格 然后再去除所有html标签
    segs = jieba.cut(title)   #分词
    for seg in segs:
        if len(seg.strip())>1:
            contents.append(seg)     #去除掉标点符号
            titles.append(title)     #去除掉标点符号
            pk.append(wenzhang.pk)     #去除掉标点符号

segmentDF = pandas.DataFrame({'pk':pk,'title':titles,'content':contents})
#去除停用词
stopwords = pandas.read_csv(
    "StopwordsCN.txt",
    encoding='utf8',
    index_col=False,
    quoting=3,
    sep="\t"
)
segmentDF = segmentDF[~segmentDF.content.isin(stopwords.stopword)]

#按文章进行词频统计
segStat = segmentDF.groupby(
            by=["pk", "content"]
        )["content"].agg({
            "计数":numpy.size
        }).reset_index().sort(
            columns=["计数"],
            ascending=False
        );


#进行文本向量计算
textVector = segStat.pivot_table(
    index=u'content',
    columns='pk',
    values='计数',
    fill_value=0
)

#
def cosineDist(col1, col2):
    return numpy.sum(col1 * col2)/(
        numpy.sqrt(numpy.sum(numpy.power(col1, 2))) *
        numpy.sqrt(numpy.sum(numpy.power(col2, 2)))
    )

distance_df = textVector.apply(
    lambda col1: textVector.apply(
        lambda col2: cosineDist(col1, col2)
    )
)


x = 1
for i in range(wenzhangs.count()):
    tagis = distance_df.iloc[:,i].order(ascending=False)[1:6].index   #去除相似的前5篇文章(自己的不算)

    # print "与 " , distance_df.index[i] , " 相似的文章："    #主文章  整形
    for tag in tagis:
        print (int(tag))
        xiangguan = Xiangguan.objects.get_or_create(
                zhuwzpk = distance_df.index[i],
                xgwz = int(tag),
            )[0]

    print("\n")