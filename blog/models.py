# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.


class BlogArticles(models.Model):
    title = models.CharField(max_length=300)
    author = models.ForeignKey(User, related_name="blog_posts")
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        # 设置标题排序顺序依据ｐｕｂｌｉｓｈ的降序来
        ordering = ("-publish",)

    def __str__(self):
        return self.title
