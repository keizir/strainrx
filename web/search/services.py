from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models import Avg, Prefetch


from web.search.models import Strain, StrainImage, StrainReview


def build_strain_rating(strain):
    rating = StrainReview.objects.filter(strain=strain).aggregate(avg_rating=Avg('rating'))
    rating = rating.get('avg_rating')
    return 'Not Rated' if rating is None else "{0:.2f}".format(round(rating, 2))


def get_strains_and_images_for_location(location):
    urls = []
    strains = Strain.objects.filter(menu_items__business_location=location)
    strains = strains.prefetch_related(Prefetch('images', queryset=StrainImage.objects.filter(is_approved=True)))

    for strain in strains:
        images = list(strain.images.all())
        if images:
            for image in images:
                if image.is_primary:
                    url = image.url
                    break
            else:
                url = images[0].url
        else:
            url = static('images/weed_small.jpg')

        urls.append(url)

    return list(zip(strains, urls))
