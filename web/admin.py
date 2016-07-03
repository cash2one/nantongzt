# -*- coding: utf-8 -*-
from django.contrib import admin
from web.models import *
import a
import time
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_filter = ('status', 'create_time')
    list_display = ('id','name', 'parent', 'rank', 'status')
    fields = ('name', 'url','info','parent', 'rank', 'status') #在管理界面显示出来的东西


class ArticleAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        obj.save()   #先把文章保存一下
        obj_original = self.model.objects.get(pk=obj.pk)    #调取这篇文章的数据
        changweis = Changwei.objects.order_by('-title')   #获取长尾词的搜索结果结合
        obj.tags = a.tags(obj_original.title)     #修改tags


        obj.content = a.changwei(obj_original.content,changweis)   #对长尾词记录单的词进行维护
        obj.save()
        #changweis2 = Tag.objects.order_by('-title')
        # obj.content = a.changwei(obj.content,changweis2)

        #这个是外部调用的数据
        import os
        #os.system('nohup python -c "import os;import blog.a;blog.a.uppdatetags()" &')
        #还不成熟,因为tags标签是变动的,所以最好是进行全部删除以后,再重新添加


    search_fields = ('title', 'summary')
    list_filter = ('status', 'category', 'is_top',
                   'create_time', 'update_time', 'is_top')
    list_display = ('title', 'category',
                    'status', 'is_top', 'update_time','is_tuijian','is_tuisong','id')
    fieldsets = (
        (u'基本信息', {
            'fields': ('title','img',
                       'category', 'tags',
                       'is_top','is_tuijian' ,'is_tuisong','rank', 'status')
            }),
        (u'内容', {
            'fields': ('content',)
            }),
        (u'摘要', {
            'fields': ('summary',)
            }),
        # (u'时间', {
        #     'fields': ('pub_time',)
        #     }),
    )



class NavAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'url', 'status', 'create_time')
    list_filter = ('status', 'create_time')
    fields = ('name', 'url', 'status','info')




class CarouselAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display = ('title', 'article', 'img', 'create_time')
    list_filter = ('create_time',)
    fields = ('title', 'article', 'img', 'summary')


class ChangweiAdmin(admin.ModelAdmin):
    search_fields = ('title','url',)
    list_display = ('title', 'url', 'fenzu')



class TagAdmin(admin.ModelAdmin):
    search_fields = ('title','url',)
    list_display = ('title', 'url')


class CustomAdmin(admin.ModelAdmin):
    search_fields = ('title','url',)
    list_display = ('title', 'url')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Nav, NavAdmin)
admin.site.register(Carousel, CarouselAdmin)
admin.site.register(Changwei,ChangweiAdmin)
admin.site.register(Changweifenzu)
admin.site.register(Tag,TagAdmin)
admin.site.register(Custom,CustomAdmin)
