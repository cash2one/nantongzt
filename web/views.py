# -*- coding: utf-8 -*-
# from __future__ import unicode_literals
from django import template
from django.http import HttpResponse, Http404
from django.template import Context, loader
from django.views.generic import View, TemplateView, ListView, DetailView
from django.db.models import Q
from django.core.cache import caches
from django.core.exceptions import PermissionDenied
from web.models import *
from django.conf import settings
import json
import logging
from django.shortcuts import render_to_response
from django.template import RequestContext
try:
    cache = caches['memcache']
except ImportError as e:
    cache = caches['default']

# logger
logger = logging.getLogger(__name__)


class BaseMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super(BaseMixin, self).get_context_data(**kwargs)
        try:
            # 网站标题等内容
            context['website_title'] = settings.WEBSITE_TITLE
            context['website_welcome'] = settings.WEBSITE_WELCOME
            context['website_desc'] = '沃克理财生活网官网首页登录地址,wk拆分盘项目解析,全面解析沃客理财的全套赚钱思路,以小博大,杠杆借力,实现资金倍增!'
            context['host']= 'http://'+ self.request.get_host()   #网站的主域名
            context['path'] = self.request.path

            #作者相关信息
            context['author'] = u'沃克理财'       #网站作者
            context['iphone'] = u'18659741771'       #电话
            context['email'] = u'353335447@qq.com'       #邮箱
            context['gphone'] = u'0513-85323007'       #固定电话
            context['dizhi'] = u'南通市崇川区南大街88号名都广场'       #地址

            context['website_keywords'] = [u'沃客理财',u'wk理财',u'demwk',u'沃克生活网'] #网站关键词



            # 热门文章
            context['hot_article_list'] = \
                Article.objects.order_by("-view_times")[0:10]

            # 随机文章10篇
            context['romdon_article_list'] = \
                Article.objects.order_by("?")[0:6]

            # 随机文章倒6篇
            context['dromdon_article_list'] = \
                Article.objects.order_by("?")[:10].reverse()[:6]

            #站长推荐
            context['rank_article_list'] = \
                Article.objects.order_by("-rank")[:6]




            #新闻
            context['new_article_list'] = \
                Article.objects.order_by("-pub_time")[:6]




            #获取所有分类
            fenlei = Category.objects.all()
            context['zfenlei'] = fenlei
            #获取当前分类下的子分类



            #获取分类
            context['fenlei'] = Category


            #获取文章
            context['wenzhang'] = Article

            # 导航条
            context['nav_list'] = Nav.objects.filter(status=0)[::-1]

            # 最新评论
            context['latest_comment_list'] = \
                Comment.objects.order_by("-create_time")[0:10]

            # 友情链接
            context['links'] = Link.objects.order_by('create_time').all()
            colors = ['primary', 'success', 'info', 'warning', 'danger']
            for index, link in enumerate(context['links']):
                link.color = colors[index % len(colors)]


            #获取所有的tags (这里没有热门标签,热门标签需要对所有标签先进行计数,可以考虑采用随机获取20个标签
            tags_list = []
            for post in  Article.objects.all():
                tags_list+=post.get_tags()
            context['alltags'] = set(tags_list)

            # 用户未读消息数
            user = self.request.user
            if user.is_authenticated():
                context['notification_count'] = \
                    user.to_user_notification_set.filter(is_read=0).count()
        except Exception as e:
            logger.error(u'[BaseMixin]加载基本信息出错')

        return context


class IndexView(BaseMixin, ListView):
    template_name = 'index.html'
    context_object_name = 'article_list'
    paginate_by = settings.PAGE_NUM  # 分页--每页的数目

    def get_context_data(self, **kwargs):
        # 轮播
        kwargs['carousel_page_list'] = Carousel.objects.all()
        kwargs['home']= True
        return super(IndexView, self).get_context_data(**kwargs)

    def get_queryset(self):
        article_list = Article.objects.filter(status=0)
        return article_list




class ArticleView(BaseMixin, DetailView):
    queryset = Article.objects.filter(Q(status=0) | Q(status=1))
    template_name = 'article.html'
    context_object_name = 'article'


    #可以传递额外的参数给模板,其中kwargs为传给这个视图的参数
    def get_context_data(self, **kwargs):
        # 评论
        # kwargs['comment_list'] = \
        #     self.article.comment_set.all()

        pk = self.kwargs.get('pk')
        try:
            self.article = self.queryset.get(pk=pk)
        except Article.DoesNotExist:
            logger.error(u'[ArticleView]访问不存在的文章:[%s]' % pk)
            raise Http404

        # 上下一篇文章 ---- 这个算法还需要优化一下 -- 感觉上有点低效率
        queryset = Article.objects.filter(Q(status=0) | Q(status=1))
        index = list(queryset).index(self.article)
        if index > 0:
            kwargs['s_article'] = queryset[index-1]

        if index+1 < len(self.queryset):
            kwargs['n_article'] = queryset[index+1]


        #相关文章计算(感觉这个效率有点低)
        # xg = Xiangguan.objects.filter(zhuwzpk=self.article.pk)
        # kwargs['xg_article'] =[ Article.objects.get(pk=int(i.xgwz)) for i in xg]


        #获取同类目录的文章
        gx_article = self.article.category.pk


        kwargs['xg_article'] = Category.objects.get(pk=gx_article).article_set.all()[1:7]


        return super(ArticleView, self).get_context_data(**kwargs)


    def get(self, request, *args, **kwargs):
        # 统计文章的访问访问次数
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        self.cur_user_ip = ip
        pk = self.kwargs.get('pk')

        # 获取15*60s时间内访问过这篇文章的所有ip
        visited_ips = cache.get(pk, [])

        # 如果ip不存在就把文章的浏览次数+1
        if ip not in visited_ips:
            try:
                self.article = self.queryset.get(pk=pk)
            except Article.DoesNotExist:
                logger.error(u'[ArticleView]访问不存在的文章:[%s]' % pk)
                raise Http404
            else:
                self.article.view_times += 1
                self.article.save()
                visited_ips.append(ip)

            # 更新缓存
            cache.set(pk, visited_ips, 15*60)

        return super(ArticleView, self).get(request, *args, **kwargs)




class AllView(BaseMixin, ListView):
    template_name = 'all.html'
    context_object_name = 'article_list'

    def get_context_data(self, **kwargs):
        kwargs['category_list'] = Category.objects.all()
        kwargs['PAGE_NUM'] = settings.PAGE_NUM
        return super(AllView, self).get_context_data(**kwargs)

    def get_queryset(self):
        article_list = Article.objects.filter(
            status=0
        ).order_by("-pub_time")[0:settings.PAGE_NUM]
        return article_list

    def post(self, request, *args, **kwargs):
        val = self.request.POST.get("val", "")
        sort = self.request.POST.get("sort", "time")
        start = self.request.POST.get("start", 0)
        end = self.request.POST.get("end", settings.PAGE_NUM)

        start = int(start)
        end = int(end)

        if sort == "time":
            sort = "-pub_time"
        elif sort == "recommend":
            sort = "-view_times"
        else:
            sort = "-pub_time"

        if val == "all":
            article_list = \
                Article.objects.filter(status=0).order_by(sort)[start:end+1]
        else:
            try:
                article_list = Category.objects.get(
                                   name=val
                               ).article_set.filter(
                                   status=0
                               ).order_by(sort)[start:end+1]
            except Category.DoesNotExist:
                logger.error(u'[AllView]此分类不存在:[%s]' % val)
                raise PermissionDenied

        isend = len(article_list) != (end-start+1)

        article_list = article_list[0:end-start]

        html = ""
        for article in article_list:
            html += template.loader.get_template(
                        'include/all_post.html'
                    ).render(template.Context({'post': article}))

        mydict = {"html": html, "isend": isend}
        return HttpResponse(
            json.dumps(mydict),
            content_type="application/json"
        )


class SearchView(BaseMixin, ListView):
    template_name = 'search.html'
    context_object_name = 'article_list'
    paginate_by = settings.PAGE_NUM

    def get_context_data(self, **kwargs):
        kwargs['s'] = self.request.GET.get('s', '')
        return super(SearchView, self).get_context_data(**kwargs)

    def get_queryset(self):
        # 获取搜索的关键字
        s = self.request.GET.get('s', '')
        # 在文章的标题,summary和tags中搜索关键字
        article_list = Article.objects.only(
            'title', 'summary', 'tags'
        ).filter(
            Q(title__icontains=s) |
            Q(summary__icontains=s) |
            Q(tags__icontains=s),
            status=0
        )
        return article_list


class TagView(BaseMixin, ListView):
    template_name = 'tag.html'
    context_object_name = 'article_list'
    paginate_by = settings.PAGE_NUM

    def get_queryset(self):
        self.tag = self.kwargs.get('tag', '')
        article_list = \
            Article.objects.only('tags').filter(tags__icontains=self.tag, status=0)
        return article_list

    def get_context_data(self, **kwargs):
        kwargs['tag_name'] = self.tag
        return super(TagView, self).get_context_data(**kwargs)


class CategoryView(BaseMixin, ListView):
    '''分类视图'''
    template_name = 'fenlei.html'
    context_object_name = 'article_list'
    paginate_by = settings.PAGE_NUM

    def get_queryset(self):
        category = self.kwargs.get('category', '')
        self.category = category
        try:
            fenleis = Category.objects.get(url=category).category_set.all()  #获取所有的分类
            #如果子分类
            if fenleis:
                #先获取父分类的文章
                article_list = Category.objects.get(url=category).article_set.all()
                #获取所有的子分类文章,并且和父分类合并
                for fenlei in fenleis:
                    article_list = article_list | fenlei.article_set.all()
                article_list = article_list.distinct().order_by('title')

            else:
                article_list = \
                    Category.objects.get(url=category).article_set.all()


        except Category.DoesNotExist:
            logger.error(u'[CategoryView]此分类不存在:[%s]' % category)
            raise Http404

        except IndexError:
            raise Http404

        return article_list

    def get_context_data(self, **kwargs):
        kwargs['category_title'] = Category.objects.get(url=self.category)
        # kwargs['category_title']= self.category_title
        # kwargs['category_desc']= self.category_desc
        return super(CategoryView, self).get_context_data(**kwargs)






class CustomView(BaseMixin, ListView):
    #这个其实只要把标题和内容读取出来就可以了
    template_name = 'custom.html'

    def get_queryset(self):
        url = self.kwargs.get('url', '')
        self.article = Custom.objects.get(url=url)

    def get_context_data(self, **kwargs):
        kwargs['article'] = self.article
        return super(CustomView, self).get_context_data(**kwargs)



class AllView(BaseMixin, ListView):
    template_name = 'all.html'
    context_object_name = 'article_list'


    def get_queryset(self):
        article_list = Article.objects.filter(
            status=0
        ).order_by("-pub_time")[0:500]
        return article_list

    def get_context_data(self, **kwargs):
        kwargs['category_list'] = Category.objects.all()
        kwargs['PAGE_NUM'] = settings.PAGE_NUM
        return super(AllView, self).get_context_data(**kwargs)



    #
    # def post(self, request, *args, **kwargs):
    #     val = self.request.POST.get("val", "")
    #     sort = self.request.POST.get("sort", "time")
    #     start = self.request.POST.get("start", 0)
    #     end = self.request.POST.get("end", settings.PAGE_NUM)
    #
    #     start = int(start)
    #     end = int(end)
    #
    #     if sort == "time":
    #         sort = "-pub_time"
    #     elif sort == "recommend":
    #         sort = "-view_times"
    #     else:
    #         sort = "-pub_time"
    #
    #     if val == "all":
    #         article_list = \
    #             Article.objects.filter(status=0).order_by(sort)[start:end+1]
    #     else:
    #         try:
    #             article_list = Category.objects.get(
    #                                name=val
    #                            ).article_set.filter(
    #                                status=0
    #                            ).order_by(sort)[start:end+1]
    #         except Category.DoesNotExist:
    #             logger.error(u'[AllView]此分类不存在:[%s]' % val)
    #             raise PermissionDenied
    #
    #     isend = len(article_list) != (end-start+1)
    #
    #     article_list = article_list[0:end-start]
    #
    #     html = ""
    #     for article in article_list:
    #         html += template.loader.get_template(
    #                     'blog/include/all_post.html'
    #                 ).render(template.Context({'post': article}))
    #
    #     mydict = {"html": html, "isend": isend}
    #     return HttpResponse(
    #         json.dumps(mydict),
    #         content_type="application/json"
    #     )
