#coding:utf8
from django import template
import re
from web.models import *

register = template.Library()
@register.filter
def getfenlei(key):
    '''
    传入父分类,获得子分类
    '''
    if key.category_set.all():
        return key.category_set.all()


@register.filter
def cutimg(key):
    '''
    去除图片链接 一般用于摘要中
    '''
    P = re.compile(r'<img src=.+?/>')
    return P.sub('',key)


@register.filter
def geturlfenlei(key):
    '''
    获取分类
    '''
    # return Category.objects.get(url=key).article_set.all()[:10]
    return Category.objects.get(url=key)




#传入分类的id 获取这个分类下的所有文章
@register.filter
def get_fenlei_wenzhang(pk):
    return Category.objects.get(pk=pk).article_set.all()[:10]


#传入分类id直接获取这个分类
@register.filter
def get_fenlei_url(pk):
    return Category.objects.get(pk=pk).get_absolute_url()



#------------------------自定义变量----------------------
class SetVarNode(template.Node):

    def __init__(self, var_name, var_value):
        self.var_name = var_name
        self.var_value = var_value

    def render(self, context):
        try:
            value = template.Variable(self.var_value).resolve(context)
        except template.VariableDoesNotExist:
            value = ""
        context[self.var_name] = value
        return u""

def set_var(parser, token):
    """
        {% set <var_name>  = <var_value> %}
    """
    parts = token.split_contents()
    if len(parts) < 4:
        raise template.TemplateSyntaxError("'set' tag must be of the form:  {% set <var_name>  = <var_value> %}")
    return SetVarNode(parts[1], parts[3])

register.tag('set', set_var)
#------------------------自定义变量结束----------------------