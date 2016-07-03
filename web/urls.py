from django.conf.urls import url
from web.views import *
from django.views.generic import TemplateView, DetailView
from web.models import *
from django.conf.urls import include, url
from DjangoUeditor import urls as DjangoUeditor_urls
from django.conf import settings

urlpatterns = [
        url(r'^$', IndexView.as_view(), name='index-view'),



        url(r'^custom/(?P<url>\w+)/$',CustomView.as_view(),name="custom"),



         url(r'^all/$', AllView.as_view(), name='all-view'),




        url(r'^(?P<url>\w+)/(?P<pk>\w+).html$',
            ArticleView.as_view(), name='article-detail-view'),
        url(r'^ueditor/', include(DjangoUeditor_urls)),

        url(r'^all/$', AllView.as_view(), name='all-view'),
        url(r'^search/$', SearchView.as_view()),
        url(r'^tag/(?P<tag>\w+)/$', TagView.as_view(), name='tag-detail-view'),
        url(r'^(?P<category>\w+)/$',
            CategoryView.as_view(), name='category-detail-view'),

]


from django.conf.urls.static import static
urlpatterns += static(
    		settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
