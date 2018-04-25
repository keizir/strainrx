from __future__ import unicode_literals

from django.conf.urls import url

from web.articles.views import ArticleDetailView, view_page

urlpatterns = [
    url(r'^(?P<category_slug>[/\w-]+)/(?P<article_slug>[\w-]+)/$',
        view=ArticleDetailView.as_view(),
        name='view_article'
        ),
    url(r'^(?P<page_slug>[\w-]+)/$',
        view=view_page,
        name='view_page'
        )
]
