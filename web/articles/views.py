import html

from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView

from web.articles.models import Article


class ArticleDetailView(DetailView):
    template_name = 'pages/articles/article.html'
    context_object_name = 'article'

    def get_object(self, queryset=None):
        return get_object_or_404(Article, slug=self.kwargs['article_slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = html.unescape(self.object.text)
        return context


def view_page(request, page_slug):
    article = get_object_or_404(Article, slug=page_slug)

    return render(request, 'pages/articles/article.html', {
        "article": article,
        "text": html.unescape(article.text)
        })
