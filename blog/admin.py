# -*- coding: utf-8 -*-
from django.contrib import admin
from blog.models import BlogArticles

# Register your models here.


class BlogArticlesAdmin(admin.ModelAdmin):
    # 以列表的形式展现字段，字段是列
    list_display = ('title', 'author', 'publish')
    # 过滤器，即筛选条件
    list_filter = ('publish', 'author')
    # 搜索框可以搜索的条件
    search_fields = ('title', 'body')
    # 只适用于外键，使用时会显示外键信息
    raw_id_fields = ('author',)
    # 设置显示详细日期的模块
    date_hierarchy = "publish"
    # 设置可以排序的字段
    ordering = ["publish", "author"]


admin.site.register(BlogArticles, BlogArticlesAdmin)