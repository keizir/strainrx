from django.db.models import Avg

from web.search.models import StrainReview


def build_strain_rating(strain):
    rating = StrainReview.objects.filter(strain=strain).aggregate(avg_rating=Avg('rating'))
    rating = rating.get('avg_rating')
    return 'Not Rated' if rating is None else "{0:.2f}".format(round(rating, 2))
