#coding:utf8
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    # Examples:
    url(r'', include('web.urls')),

]

