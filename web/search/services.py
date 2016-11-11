from web.search.models import StrainReview


def build_strain_rating(strain):
    reviews = StrainReview.objects.filter(strain=strain)
    rating = 0
    for r in reviews:
        rating += r.rating
    return 'Not Rated' if len(reviews) == 0 else "{0:.2f}".format(round(rating / len(reviews), 2))
