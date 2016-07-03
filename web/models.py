# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from DjangoUeditor.models import UEditorField
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class string_with_title(str):
    """ 用来修改admin中显示的app名称,因为admin app 名称是用 str.title()显示的,
    所以修改str类的title方法就可以实现.
    """
    def __new__(cls, value, title):
        instance = str.__new__(cls, value)
        instance._title = title
        return instance

    def title(self):
        return self._title

    __copy__ = lambda self: self
    __deepcopy__ = lambda self, memodict: self

# Create your models here.
STATUS = {
        0: u'正常',
        1: u'草稿',
        2: u'删除',
}





class Nav(models.Model):
    name = models.CharField(max_length=40, verbose_name=u'导航条内容')
    url = models.CharField(max_length=200, blank=True, null=True,
                           verbose_name=u'指向地址')
    info = models.CharField(max_length=40, verbose_name=u'显示的简写名称',blank=True, null=True,)

    status = models.IntegerField(default=0, choices=STATUS.items(),
                                 verbose_name=u'状态')
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = verbose_name = u"导航条"
        ordering = ['-create_time']
        app_label = string_with_title('web', u"博客管理")

    def __unicode__(self):
        return self.name

    __str__ = __unicode__


class Category(models.Model):
    name = models.CharField(max_length=40, verbose_name=u'名称')
    parent = models.ForeignKey('self', default=None, blank=True, null=True,
                               verbose_name=u'上级分类')
    rank = models.IntegerField(default=0, verbose_name=u'排序')
    url = models.CharField(max_length=40,verbose_name=u'网址')
    info = models.CharField(max_length=500,verbose_name=u'简介')
    status = models.IntegerField(default=0, choices=STATUS.items(),
                                verbose_name=u'状态')

    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = verbose_name = u'分类'
        ordering = ['rank', '-create_time']
        app_label = string_with_title('web', u"博客管理")

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('category-detail-view', args=(self.url,))

    def __unicode__(self):
        if self.parent:
            return '%s-->%s' % (self.parent, self.name)
        else:
            return '%s' % (self.name)

    __str__ = __unicode__


class Article(models.Model):
    category = models.ForeignKey(Category, verbose_name=u'分类')
    title = models.CharField(max_length=100, verbose_name=u'标题')

    img = models.CharField(max_length=200,
                           default='/static/img/article/default.jpg')

    tags = models.CharField(max_length=200, null=True, blank=True,
                             verbose_name=u'标签', help_text=u'用逗号分隔')
    summary = UEditorField('摘要', height=300, width=1000,
        default=u'', blank=True, imagePath="uploads/images/",
        toolbars='besttome', filePath='uploads/files/')

    content = UEditorField('内容', height=300, width=1000,
        default=u'', blank=True, imagePath="uploads/images/",
        toolbars='besttome', filePath='uploads/files/')

    view_times = models.IntegerField(default=0)
    zan_times = models.IntegerField(default=0)

    is_top = models.BooleanField(default=False, verbose_name=u'置顶')
    is_tuijian = models.BooleanField(default=False, verbose_name=u'推荐')
    is_tuisong = models.BooleanField(default=False, verbose_name=u'百度推送')
    rank = models.IntegerField(default=0, verbose_name=u'排序')
    status = models.IntegerField(default=0, choices=STATUS.items(),
                                 verbose_name='状态')
    # pub_time = models.DateTimeField(default=False,verbose_name=u'发布时间')
    pub_time = models.DateTimeField(auto_now_add = True,verbose_name=u'发布时间')  #博客日期
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    update_time = models.DateTimeField(u'更新时间', auto_now=True)

    def get_tags(self):
        if self.tags:
            tags_list = self.tags.split(',')
            while '' in tags_list:
                tags_list.remove('')

            return tags_list
        else:
            return

    class Meta:
        verbose_name_plural = verbose_name = u'文章'
        ordering = ['rank', '-is_top', '-pub_time', '-create_time']
        app_label = string_with_title('web', u"博客管理")


    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        # return reverse('article-detail-view', args=(self.pk,))
        return reverse('article-detail-view', args=(self.category.url,self.pk,))



    def __unicode__(self):
            return self.title

    __str__ = __unicode__



#轮播
class Carousel(models.Model):
    title = models.CharField(max_length=100, verbose_name=u'标题')
    summary = models.TextField(blank=True, null=True, verbose_name=u'摘要')
    img = models.CharField(max_length=200, verbose_name=u'轮播图片',
                           default='/static/img/carousel/default.jpg')
    article = models.ForeignKey(Article, verbose_name=u'文章')
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = verbose_name = u'轮播'
        ordering = ['-create_time']
        app_label = string_with_title('web', u"博客管理")




class Changweifenzu(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u'长尾词分组'
    title = models.CharField(max_length=200,verbose_name=u'分组标题')

    def __unicode__(self):
        return self.title


class Changwei(models.Model):
    title = models.CharField(max_length=200,verbose_name=u'关键词')
    url =  models.URLField(max_length=200,verbose_name=u'域名')
    fenzu = models.ForeignKey(Changweifenzu,verbose_name=u'分组',null=True,blank=True,)
    def __unicode__(self):
        return self.title
    class Meta:
        verbose_name_plural = verbose_name = u'长尾词'



#tags链接
class Tag(models.Model):
      title = models.CharField(max_length=20,blank=True)
      url =  models.CharField(max_length=200,verbose_name=u'域名')
      creat_time = models.DateTimeField(auto_now_add=True)
      @models.permalink
      def get_absolute_url(self):
          return('tagDetail', (), {
          'tag':self.title})
      def __unicode__(self):
          return self.title


#储存相关文章的列表
class Xiangguan(models.Model):
    zhuwzpk = models.IntegerField()
    xgwz =  models.IntegerField()


class Custom(models.Model):
    title = models.CharField(max_length=100, verbose_name=u'标题')
    img = models.CharField(max_length=200,
                           default='/static/img/article/default.jpg')
    url = models.CharField(max_length=100, verbose_name=u'自定义路径')
    kewwords = models.CharField(max_length=100, verbose_name=u'关键词',null=True, blank=True)
    desc = models.CharField(max_length=300, verbose_name=u'seo描述',null=True, blank=True)

    content = UEditorField('内容', height=300, width=1000,
        default=u'', blank=True, imagePath="uploads/images/",
        toolbars='besttome', filePath='uploads/files/')

    view_times = models.IntegerField(default=0)
    zan_times = models.IntegerField(default=0)

    rank = models.IntegerField(default=0, verbose_name=u'排序')
    status = models.IntegerField(default=0, choices=STATUS.items(),
                                 verbose_name='状态')
    pub_time = models.DateTimeField(auto_now_add = True,verbose_name=u'发布时间')  #博客日期
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    update_time = models.DateTimeField(u'更新时间', auto_now=True)

    class Meta:
        verbose_name_plural = verbose_name = u'自定义页面'
        ordering = ['-create_time']
        app_label = string_with_title('web', u"博客管理")
