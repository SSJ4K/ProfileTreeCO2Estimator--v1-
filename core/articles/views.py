from django.shortcuts import render, get_object_or_404, redirect
from .models import Article, Comment

# def all_articles(request):
#     articles = Article.objects.filter(published=True)
#     return render(request, 'articles/articles_list.html', {'articles': articles})
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def all_articles(request):
    articles = Article.objects.filter(published=True).order_by('-created_at')

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(articles, 5) 
    try:
        articles_page = paginator.page(page)
    except PageNotAnInteger:
        articles_page = paginator.page(1)
    except EmptyPage:
        articles_page = paginator.page(paginator.num_pages)

    # Create a range of page numbers for numeric pagination
    page_range = range(max(1, articles_page.number - 2), min(articles_page.number + 3, paginator.num_pages + 1))

    return render(request, 'articles/articles_list.html', {'articles': articles_page, 'page_range': page_range})

def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id, published=True)
    comments = article.comments.all()

    if request.method == 'POST':
        comment_text = request.POST.get('comment_text')
        if comment_text:
            Comment.objects.create(content=comment_text, article=article, author=request.user)
            return redirect('article_detail', article_id=article.id)

    return render(request, 'articles/article_detail.html', {'article': article, 'comments': comments})