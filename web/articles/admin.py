from django.contrib import admin
from web.articles.models import Article, Category

class ArticleAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_filter = ('featured', 'is_sponsored', 'published_date', 'category')
    list_display = ['short_title', 'article_url', 'featured', 'published_date', 'deleted_date', 'category',]

    def has_delete_permission(self, request, obj=None):
        return False

    def article_url(self, obj):
        return '<a target="_blank" href="%s">%s</a>' % (obj.url, obj.url)

    article_url.allow_tags = True

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')

    def get_actions(self, request):
        #Disable delete
        actions = super(CategoryAdmin, self).get_actions(request)
        # del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        #Disable delete
        return False

admin.site.register(Article, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.disable_action('delete_selected')
