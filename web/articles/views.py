from django.shortcuts import render
from web.articles.models import Article

def view_article(request, category_slug, article_slug):
    article = Article.objects.get(category__slug=category_slug, slug=article_slug)
    #article = Article.objects.get(category__slug=category_slug, slug=article_slug, is_approved=True, deleted_date__isnull=True)

    return render(request, 'pages/articles/article.html', {
        "article": article,
        })
