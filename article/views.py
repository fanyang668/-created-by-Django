import json

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import ArticleColumnForm, ArticlePostForm, ArticleTagForm
from .models import ArticleColumn, ArticlePost, ArticleTag


# Create your views here.
@login_required(login_url='/account/new_login')
@require_POST
@csrf_exempt
def del_article_tag(request):
    tag_id = request.POST['tag_id']
    try:
        tag = ArticleTag.objects.get(id=tag_id)
        tag.delete()
        return HttpResponse('1')
    except:
        return HttpResponse('2')


@login_required(login_url='/account/new_login')
@csrf_exempt
def article_tag(request):
    if request.method == 'GET':
        article_tags = ArticleTag.objects.filter(author=request.user)
        article_tag_form = ArticleTagForm()
        return render(request, 'article/tag/tag_list.html', {'article_tags': article_tags,
                                                                  'article_tag_form': article_tag_form})
    if request.method == 'POST':
        article_tag_form = ArticleTagForm(request.POST)
        if article_tag_form.is_valid():
            try:
                new_tag = article_tag_form.save(commit=False)
                new_tag.author = request.user
                new_tag.save()
                return HttpResponse('1')
            except:
                return HttpResponse('The data cannot be saved.')
        else:
            return HttpResponse('sorry, the form is invalid.')


@login_required(login_url='/account/new_login')
@csrf_exempt
def redit_article(request, article_id):
    if request.method == 'GET':
        article_columns = request.user.article_column.all()
        article = ArticlePost.objects.get(id=article_id)
        this_article_form = ArticlePostForm(initial={'title': article.title})
        this_article_column = article.column
        return render(request, 'article/column/redit_article.html', {'article_columns': article_columns,
                                                                     'article': article,
                                                                     'this_article_form': this_article_form,
                                                                     'this_article_column': this_article_column})
    else:
        redit_article = ArticlePost.objects.get(id=article_id)
        try:
            redit_article.column = request.user.article_column.get(id=request.POST['column_id'])
            redit_article.title = request.POST['title']
            redit_article.body = request.POST['body']
            redit_article.save()
            return HttpResponse('1')
        except:
            return HttpResponse('2')


@login_required(login_url='/account/new_login')
@require_POST
@csrf_exempt
def del_article(request):
    article_id = request.POST['article_id']
    try:
        article = ArticlePost.objects.get(id=article_id)
        article.delete()
        return HttpResponse("1")
    except:
        return HttpResponse("2")


@login_required(login_url='/account/new_login')
def article_detail(request, ac_id, slug):
    article = get_object_or_404(ArticlePost, id=ac_id, slug=slug)
    return render(request, 'article/column/article_detail.html', {'article': article})


@login_required(login_url='/account/new_login')
def article_list(request):
    article_lists = ArticlePost.objects.filter(author=request.user)
    # 根据查询到的文章对象article_list创建分页的实例对象，并且规定每页最多显示２个对象
    # Paginator(object_list, per_page, orphans=0, allow_empty_first_page=True)
    paginator = Paginator(article_lists, 2)
    # 获得浏览器发送的GET请求中的page的值
    page = request.GET.get('page')
    try:
        # page()是Paginagor对象的一个方法，得到指定页面的内容，参数必须是不小于１的整数
        current_page = paginator.page(page)
        # object_list是Page对象的属性，得捣该页所有的对象列表
        articles = current_page.object_list
    except PageNotAnInteger:
        current_page = paginator.page(1)
        articles = current_page.object_list
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
        articles = current_page.object_list
    return render(request, 'article/column/article_list.html', {"articles": articles, 'page': current_page})


@login_required(login_url='/account/login')
@csrf_exempt
def article_post(request):
    if request.method == 'POST':
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            cd = article_post_form.cleaned_data
            try:
                new_article = article_post_form.save(commit=False)
                new_article.author = request.user
                new_article.column = request.user.article_column.get(id=request.POST['column_id'])
                new_article.save()
                tags = request.POST['tags']
                if tags:
                    for atag in json.loads(tags):
                        tag = request.user.tag.get(tag=atag)
                        new_article.article_tag.add(tag)
                return HttpResponse("1")
            except:
                return HttpResponse("2")
        else:
            return HttpResponse("3")
    else:
        article_post_form = ArticlePostForm()
        article_columns = request.user.article_column.all()
        article_tags = request.user.tag.all()
        return render(request, 'article/column/article_post.html', {'article_post_form': article_post_form,
                                                                    'article_columns': article_columns,
                                                                    'article_tags': article_tags})


@login_required(login_url='/account/new_login/')
@require_POST
@csrf_exempt
def del_article_column(request):
    column_id = request.POST['column_id']
    try:
        line = ArticleColumn.objects.get(id=column_id)
        line.delete()
        return HttpResponse('1')
    except:
        return HttpResponse('2')


@login_required(login_url='/account/new_login/')
@require_POST
@csrf_exempt
def rename_article_column(request):
    column_name = request.POST['column_name']
    column_id =request.POST['column_id']
    try:
        line = ArticleColumn.objects.get(id=column_id)
        line.column = column_name
        line.save()
        return HttpResponse('1')
    except:
        return HttpResponse('0')


@login_required(login_url='/account/new_login/')
@csrf_exempt
def article_column(request):
    if request.method == 'GET':
        columns = ArticleColumn.objects.filter(user=request.user)
        column_form = ArticleColumnForm()
        return render(request, 'article/column/article_column.html', {'columns': columns, 'column_form': column_form})
    if request.method == 'POST':
        column_name = request.POST['column']
        # 根据用户ｉｄ和栏目名称来查询匹配的结果
        columns = ArticleColumn.objects.filter(user_id=request.user.id, column=column_name)
        if columns:
            # 若以存在
            return HttpResponse('2')
        else:
            # 若不存在，则新创建
            ArticleColumn.objects.create(user=request.user, column=column_name)
            return HttpResponse('1')