#coding:utf8
import pandas

df_wz = pandas.read_csv('blog_Article.csv')
df_fl = pandas.read_csv('blog_Category.csv')
df = pandas.merge(df_wz, df_fl, left_on='log_CateID', right_on='cate_ID')
df.to_csv('all.csv',index=False)

#得到了所有文章的数据表,接下去主要把数据导入进django里面就可以了
#先创建分类
#再根据分类导入文章列表
