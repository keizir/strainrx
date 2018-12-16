from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_resized import ResizedImageField


def upload_to(instance, filename):
    return 'articles/{0}_{1}'.format(uuid4(), filename)


def validate_image(instance):
    file_size = instance.file.size
    megabyte_limit = settings.MAX_IMAGE_SIZE
    if file_size > megabyte_limit:
        raise ValidationError("Max file size is %sMB" % str(megabyte_limit))


class MetaDataAbstract(models.Model):
    WEBSITE, ARTICLE = 'website', 'article'

    OBJECT_TYPES = (
        (ARTICLE, _('Article')),
        (WEBSITE, _('Website')),
    )

    TWITTER_TYPES = (
        ('summary', _('Summary Card')),
        ('summary_large_image', _('Summary Card with Large Image')),
        ('product', _('Product')),
        ('photo', _('Photo')),
        ('player', _('Player')),
        ('app', _('App')),
    )

    meta_title = models.CharField(_('Page Title'), default='Strains Web', max_length=3072, blank=True)
    meta_desc = models.CharField(
        _('Meta Description'), max_length=3072, blank=True,
        default=_('StrainRx is the premiere online source for strain intelligence. '
                  'We help cannabis users find the perfect strain that\'s ideally suited for their needs.'))
    meta_keywords = models.CharField(_('Meta Keywords'), max_length=3072, blank=True)
    social_image = ResizedImageField(max_length=255, blank=True,
                                     help_text='Maximum file size allowed is 10Mb', validators=[validate_image],
                                     quality=75, size=[1024, 1024], upload_to=upload_to)

    # Open Graph
    og_type = models.CharField(
        _('Resource type property="og:type"'), max_length=25, choices=OBJECT_TYPES, default=WEBSITE, blank=True,
        help_text=_('Use Article for generic pages.')
    )
    og_title = models.CharField(
        _('Resource title property="og:title"'), max_length=255,
        default=_('Cannabis Intelligence Platform - StrainRx'), blank=True)
    og_description = models.CharField(
        _('Resource description property="og:description"'), max_length=255, blank=True,
        default=_('StrainRx is a tool to identify and locate cannabis strains with optimal effects and benefits, '
                  'based on a user\'s personal preference and need.'))

    # Facebook
    fb_app_id = models.CharField(
        _('Facebook App ID property="fb:app_id"'), max_length=255, default='', blank=True
    )

    # Twitter
    twitter_card = models.CharField(
        _('Resource type name="twitter:card"'), max_length=25, choices=TWITTER_TYPES,
        default=TWITTER_TYPES[1][0], blank=True,
        help_text=_('The card type, which will be one of "summary", "summary_large_image", "app", or "player".')
    )
    twitter_author = models.CharField(
        _('Author Twitter Account name="twitter:author"'), max_length=255, default='@StrainRx', blank=True,
    )
    twitter_site = models.CharField(
        _('Website Twitter Account name="twitter:site"'), max_length=255, default='@StrainRx', blank=True,
    )

    meta_tags = models.TextField(
        _('Meta tags'), blank=True,
        help_text=_('Use this field to insert meta tags in html which you may need.')
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.meta_title
