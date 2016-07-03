#coding:utf8
from mysite.wsgi import *
from web.models import *
from zhangte import jiqixuexi
from random import choice
import re

#批量更新摘要 --- 随机提取2-3段化作为描述
for post in Article.objects.all():
    a = jiqixuexi.NLP()    #实例化一个类
    content = str(a.cuthtml(post.content,P=1))   #去掉所有的html代码
    list1 = re.split('[</?p>\s]\s*',content)
    while '' in list1:
        list1.remove('')

    #去掉所有
    list1 =  [i for i in list1 if 110 < len(i) < 1200]
    try:
        Article.objects.filter(pk=post.pk).update(summary= choice(list1))
    except:
        Article.objects.filter(pk=post.pk).update(summary= "")





# #先导入一些东西
# df_all = pd.read_csv(os.getcwd()+'/数据库文件/all.csv')
# df_wz = pd.read_csv(os.getcwd()+'/数据库文件/blog_Article.csv')
# df_fl = pd.read_csv(os.getcwd()+'/数据库文件/blog_Category.csv')
#
#
#
#
# #批量创建一些分类
# for i in range(df_fl.shape[0]):
#     Category.objects.get_or_create(name=df_fl['cate_Name'][i], url=df_fl['cate_URL'][i],pk=df_fl['cate_ID'][i],
#                                    info = '南通专业私家侦探,为你提供专业的{}'.format(df_fl['cate_Name'][i]))[0]
#     print '成功创建分类!!',df_fl['cate_Name'][i]




# #批量添加文章
# for i in range(df_all.shape[0]):
#
#     title = df_all['log_Title'][i]
#
#     fenlei = df_all['cate_Name'][i]
#     fenlei = Category.objects.filter(name=fenlei)[0]
#
#
#     pk = df_all['log_ID'][i]
#     content = df_all['log_Content'][i]
#     summary =  df_all['log_Intro'][i]
#
#     article = Article.objects.get_or_create(
#                     pk = pk,
#                     title = title,
#                     content = content,
#                     category = fenlei,
#                     summary = summary,
#                 )[0]
#     print '成功导入文章',title



#更新文章:


