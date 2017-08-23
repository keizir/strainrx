from django.conf import settings
from django.db import models
from djangocms_text_ckeditor.fields import HTMLField
from django_resized import ResizedImageField
from django.utils import timezone
from django.utils.text import slugify
from uuid import uuid4
from django.template.defaultfilters import truncatechars


import logging

logger = logging.getLogger(__name__)

def upload_to(instance, filename):
    path = 'articles/{0}_{1}'.format(uuid4(), filename)
    return path

def validate_image(field_file_obj):
    file_size = field_file_obj.file.size
    megabyte_limit = settings.MAX_IMAGE_SIZE
    if file_size > megabyte_limit:
        raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

class Category(models.Model):          
    title = models.CharField(max_length=256, unique=True, blank=False)
    is_active = models.BooleanField(default=False)
    slug = models.SlugField(max_length=1024, default=None, blank=True, null=True, unique=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug})

class Article(models.Model):
    title = models.CharField(max_length=1024, unique=True, blank=False)
    summary = models.CharField(max_length=3072, blank=True)
    meta_desc = models.CharField(max_length=3072, blank=True)
    meta_keywords = models.CharField(max_length=3072, blank=True)
    text = HTMLField(blank=True)
    is_sponsored = models.BooleanField(default=False)
    featured = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True)
    deleted_date = models.DateTimeField(null=True, blank=True)
    category = models.ForeignKey(Category, null=True, blank=True,  verbose_name='Category')
    image = ResizedImageField(max_length=255, blank=True, help_text='Maximum file size allowed is 10Mb', validators=[validate_image], quality=75, size=[1024, 1024], upload_to=upload_to)
    image_caption = models.CharField(max_length=1024, blank=True)
    slug = models.SlugField(max_length=1024, default=None, blank=True, null=True)
    is_page = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
      
        super(Article, self).save(*args, **kwargs)
        
        # try:
        #     ping_google()
        # except Exception as e:
        #     logger.error("Unable to ping google for sitemap update")
        #     # Bare 'except' because we could get a variety of HTTP-related exceptions.
        #     pass        

    def get_absolute_url(self):
        return reverse('article', kwargs={'slug': self.slug})

    @property
    def short_title(self):
        return truncatechars(self.title, 75)

    @property
    def url(self):
        if self.is_page:
            return '/%s' % self.slug
        else:
            return '/%s/%s' % (self.category.slug, self.slug) if self.category is not None else ""

    def __str__(self):
        return self.title


