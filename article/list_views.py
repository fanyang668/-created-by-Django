# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from article.forms import CommentForm
from .models import ArticleColumn, ArticlePost
# 建立redis数据库连接
import redis
from django.conf import settings

r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


@login_required(login_url='/account/login/')
@require_POST
@csrf_exempt
def like_article(request):
    article_id = request.POST.get('id')
    action = request.POST.get('action')
    if article_id and action:
        try:
            article = ArticlePost.objects.get(id=article_id)
            if action == 'like':
                article.users_like.add(request.user)
                return HttpResponse("1")
            else:
                article.users_like.remove(request.user)
                return HttpResponse("0")
        except:
            return HttpResponse("no")


def article_detail(request, ac_id, slug):
    article = get_object_or_404(ArticlePost, id=ac_id, slug=slug)
    # 存储文章的浏览次数
    # redis中对于键的命名并没有强制的要求，比较好的做法是用＇对象类型：对象ID：对象属性＇来命名一个键
    # 比如下句中使用键article:15:views来存储ID为15的文章的浏览次数
    total_views = r.incr('aticle:{}:views'.format(article.id))
    # zincrby(name, value, amount)是根据amount所设定的步长值增加有序集合name中的value数值
    # 下句实现了article_ranking中的article.id以步长１自增，即文章被访问一次的，article_ranking
    # 就将该文章的id值增加１
    r.zincrby('article_ranking', article.id, 1)
    # 得到article_ranking中排名前10的对象
    article_ranking = r.zrange('article_ranking', 0, -1, desc=True)[:10]
    # 得到最热文章对象的id组成的列表
    article_ranking_ids = [int(id) for id in article_ranking]
    # 注意id__in中间是双下划线，这是django里面的一种相当于条件查询的语句，其功能是查询出
    # id在article_ranking_ids中的所有文章对象，并以文章对象为元素生成列表
    most_viewed = list(ArticlePost.objects.filter(id_＿in=article_ranking_ids))
    # 将most_viewed中的文章按照他们的id在article_ranking_ids列表中的索引顺序排序
    most_viewed.sort(key=lambda x: article_ranking_ids.index(x.id))

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.article = article
            new_comment.save()
    else:
        comment_form = CommentForm()

    # 以列表的形式返回查询到的所有文章标签的id，若不设置flat=True，返回的列表是由元组组成的
    article_tags_ids = article.article_tag.values_list("id", flat=True)
    # 查询并返回所有除本文以外的相同标签的文章
    similar_articles = ArticlePost.objects.filter(article_tag__in=article_tags_ids).exclude(id=article.id)
    similar_articles = similar_articles.annotate(same_tags=Count("article_tag")).order_by("-same_tags", "-created")[:4]
    return render(request, 'article/list/article_detail.html', {'article': article,
                                                                'total_views': total_views,
                                                                'most_viewed': most_viewed,
                                                                'comment_form': comment_form,
                                                                'similar_articles': similar_articles})


def article_titles(request, username=None):
    if username:
        user = User.objects.get(username=username)
        articles_title = ArticlePost.objects.filter(author=user)
        try:
            userinfo = user.userinfo
        except:
            userinfo = None
    else:
        articles_title = ArticlePost.objects.all()

    paginator = Paginator(articles_title, 2)
    page = request.GET.get('page')
    try:
        current_page = paginator.page(page)
        articles = current_page.object_list
    except PageNotAnInteger:
        current_page = paginator.page(1)
        articles = current_page.object_list
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
        articles = current_page.object_list

    if username:
        return render(request, 'article/list/author_articles.html', {"articles": articles, "page": current_page,
                                                                     "user": user, "userinfo": userinfo})

    return render(request, 'article/list/article_titles.html', {"articles": articles, "page": current_page})

