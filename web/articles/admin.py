from django.contrib import admin

from web.articles.models import Article, Category


class ArticleAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_filter = ('category',)
    list_display = ('short_title', 'article_url', 'featured', 'published_date', 'category')
    fieldsets = (
        ('', {
            'fields': (
                'title', 'slug', 'summary', 'text', 'is_sponsored', 'featured', 'created_date',
                'published_date', 'category', 'image', 'image_caption'
            )
        }),
        ('Social', {
            'classes': ('collapse',),
            'fields': (
                'meta_title', 'meta_desc', 'meta_keywords', 'social_image', 'og_type', 'og_title',
                'og_description', 'fb_app_id', 'twitter_card', 'twitter_author', 'twitter_site', 'meta_tags'
            ),
        }),
    )

    def article_url(self, obj):
        url = obj.get_absolute_url()
        return '<a target="_blank" href="%s">%s</a>' % (url, url)

    article_url.allow_tags = True


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')


admin.site.register(Article, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)
