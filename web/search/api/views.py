import json
import logging
from datetime import datetime
from operator import itemgetter

from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from web.common.text import obfuscate
from web.search.api.serializers import SearchCriteriaSerializer, StrainReviewFormSerializer, StrainImageSerializer, \
    StrainSearchSerializer
from web.search.api.services import StrainDetailsService
from web.search.es_service import SearchElasticService
from web.search.models import Strain, StrainImage, Effect, StrainReview, StrainRating, UserFavoriteStrain, \
    UserSearch, Flavor
from web.search.strain_es_service import StrainESService
from web.search.strain_user_rating_es_service import StrainUserRatingESService
from web.system.models import SystemProperty

logger = logging.getLogger(__name__)


def bad_request(error_message):
    return Response({
        'error': error_message
    }, status=status.HTTP_400_BAD_REQUEST)


class StrainSearchWizardView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        criteria = SearchCriteriaSerializer(data=request.data.get('search_criteria'))
        criteria.is_valid()

        step_1_data = criteria.validated_data.get('step1')
        step_2_data = criteria.validated_data.get('step2')
        step_3_data = criteria.validated_data.get('step3')
        step_4_data = criteria.validated_data.get('step4')

        types = 'skipped' if step_1_data.get('skipped') else step_1_data
        effects = 'skipped' if step_2_data.get('skipped') else step_2_data.get('effects')
        benefits = 'skipped' if step_3_data.get('skipped') else step_3_data.get('effects')
        side_effects = 'skipped' if step_4_data.get('skipped') else step_4_data.get('effects')

        request.session['search_criteria'] = {
            'strain_types': types,
            'effects': effects,
            'benefits': benefits,
            'side_effects': side_effects
        }

        return Response({}, status=status.HTTP_200_OK)


class StrainSearchResultsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        result_filter = request.GET.get('filter')
        page = request.GET.get('page', 1)
        size = request.GET.get('size', 25)
        start_from = (int(page) - 1) * int(size)

        search_criteria = request.session.get('search_criteria')

        if not search_criteria:
            return Response({
                "error": "Cannot determine a search criteria."
            }, status=status.HTTP_400_BAD_REQUEST)

        data = SearchElasticService().query_strain_srx_score(search_criteria, size, start_from,
                                                             current_user=request.user,
                                                             result_filter=result_filter)
        result_list = data.get('list')

        if request.user.is_authenticated() and request.user.is_email_verified:
            user_strain_ratings = StrainRating.objects.filter(created_by=request.user, removed_date=None)
            if len(user_strain_ratings) > 0:
                result_list = self.change_strain_scores(result_list, user_strain_ratings, request.user, page)
        else:
            result_list = [dict(x, name=obfuscate(x['name']), strain_slug=obfuscate(x['strain_slug']))
                           for x in result_list]

        return Response({
            'search_results': result_list,
            'search_results_total': data.get('total')
        }, status=status.HTTP_200_OK)

    @staticmethod
    def change_strain_scores(result_list, user_strain_reviews, current_user, page):
        if len(result_list) == 0:
            return []

        latest_user_search = UserSearch.objects.user_criteria(current_user)

        user_review_scores = {}
        user_review_strain_ids = []
        for r in user_strain_reviews:
            new_score = SearchElasticService().query_user_review_srx_score(latest_user_search.to_search_criteria(),
                                                                           strain_id=r.strain.id,
                                                                           user_id=current_user.id)
            user_review_strain_ids.append(r.strain.id)
            user_review_scores[r.strain.id] = new_score

        current_scores = []
        for s in result_list:
            current_scores.append(s.get('match_percentage'))

        min_score = min(current_scores)
        max_score = max(current_scores)

        to_remove = []
        for s in result_list:
            if s.get('id') in user_review_strain_ids:
                current_score = s.get('match_percentage')
                review_score = user_review_scores.get(s.get('id'))
                if review_score != current_score:
                    to_remove.append(s)

        if len(to_remove) > 0:
            for rem in to_remove:
                result_list.remove(rem)

        to_remove = []
        for k, v in user_review_scores.items():
            if v == 'n/a' or (max_score < v and int(page) != 1):
                to_remove.append(k)

        if len(to_remove) > 0:
            for key in to_remove:
                del user_review_scores[key]

        for k, v in user_review_scores.items():
            if v != 'n/a' and ((max_score <= v and int(page) == 1) or max_score >= v > min_score or v == min_score):
                strain = Strain.objects.get(id=k)
                data = SearchElasticService().query_strain_srx_score(strain.to_search_criteria(),
                                                                     strain_ids=[strain.id], current_user=current_user)
                if len(data.get('list')) > 0:
                    users_strain = data.get('list')[0]
                    users_strain['match_percentage'] = user_review_scores.get(k)
                    result_list.append(users_strain)

        result_list = sorted(result_list, key=itemgetter('match_percentage'), reverse=True)
        return result_list


class StrainFavoriteView(LoginRequiredMixin, APIView):
    def post(self, request, strain_id):
        add_to_favorites = request.data.get('like')
        favorite_strain = UserFavoriteStrain.objects.filter(strain__id=strain_id, created_by=request.user)

        if add_to_favorites and len(favorite_strain) == 0:
            favorite_strain = UserFavoriteStrain(
                strain=Strain.objects.get(id=strain_id),
                created_by=request.user
            )
            favorite_strain.save()
        elif len(favorite_strain) > 0:
            favorite_strain[0].delete()

        return Response({}, status=status.HTTP_200_OK)


class StrainSRXScoreView(LoginRequiredMixin, APIView):
    def get(self, request, strain_id):
        strain = Strain.objects.get(pk=strain_id)
        score = StrainDetailsService().calculate_srx_score(strain, request.user)
        return Response({'srx_score': score}, status=status.HTTP_200_OK)


class StrainAlsoLikeView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, strain_id):
        strain = Strain.objects.get(pk=strain_id)
        user = request.user
        also_like_strains = StrainDetailsService().get_also_like_strains(strain,
                                                                         user if user.is_authenticated() else None)
        return Response({'also_like_strains': also_like_strains}, status=status.HTTP_200_OK)


class StrainLookupView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        query = request.GET.get('q')
        result = SearchElasticService().lookup_strain(query)
        return Response({
            'total': result.get('total'),
            'payloads': result.get('payloads')
        }, status=status.HTTP_200_OK)


class StrainImagesView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, strain_id):
        images = StrainImage.objects.filter(is_approved=True, strain=strain_id).order_by('-is_primary')
        serializer = StrainImageSerializer(images, many=True)
        return Response({'images': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, strain_id):
        if not request.user.is_authenticated():
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)

        file = request.FILES.get('file')
        strain = Strain.objects.get(pk=strain_id)
        image = StrainImage(image=file, strain=strain, created_by=request.user)
        image.save()
        return Response({}, status=status.HTTP_200_OK)


class StrainRateView(LoginRequiredMixin, APIView):
    def post(self, request, strain_id):
        strain = Strain.objects.get(pk=strain_id)
        serializer = StrainReviewFormSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review_text = serializer.validated_data.get('review')
        is_approved = False if review_text and len(review_text) > 0 else True
        review = StrainReview(strain=strain, created_by=request.user,
                              rating=serializer.validated_data.get('rating'),
                              review=review_text, review_approved=is_approved)
        review.save()
        return Response({}, status=status.HTTP_200_OK)


class StrainDetailsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, strain_id):
        user = request.user
        details = StrainDetailsService().build_strain_details(strain_id, user if user.is_authenticated() else None)
        return Response(details, status=status.HTTP_200_OK)


class StrainDeliveriesView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, strain_id):
        d = request.GET
        result_filter = d.get('filter')
        order_field = d.get('order_field')
        order_dir = d.get('order_dir')
        location_type = d.get('location_type')
        user = request.user if request.user.is_authenticated() else None

        l = StrainDetailsService().build_strain_locations(strain_id, user, result_filter, order_field,
                                                          order_dir, location_type)
        return Response(l, status=status.HTTP_200_OK)


class StrainReviewsView(LoginRequiredMixin, APIView):
    def get(self, request, strain_id):
        reviews = StrainDetailsService().get_all_approved_strain_reviews(strain_id)
        return Response({'reviews': reviews}, status=status.HTTP_200_OK)


class StrainRatingsView(LoginRequiredMixin, APIView):
    def post(self, request, strain_id):
        data = request.data
        effect_type = data.get('type')
        effects = data.get('effects')
        strain = Strain.objects.get(id=strain_id)
        sender_ip = get_client_ip(request)

        if StrainRating.objects.filter(strain=strain, created_by=request.user, removed_date=None).exists():
            r = StrainRating.objects.get(strain=strain, created_by=request.user, removed_date=None)
        else:
            r = StrainRating(strain=strain, effects=strain.effects, benefits=strain.benefits,
                             side_effects=strain.side_effects, created_by=request.user,
                             created_by_ip=sender_ip)

        if 'effects' == effect_type:
            r.effects = self.build_effects_object(effects, strain.effects)
            r.effects_changed = True
            r.last_modified_by = request.user
            r.last_modified_by_ip = sender_ip
            r.save()
            self.recalculate_global_effects(request, strain)

        if 'benefits' == effect_type:
            r.benefits = self.build_effects_object(effects, strain.benefits)
            r.benefits_changed = True
            r.last_modified_by = request.user
            r.last_modified_by_ip = sender_ip
            r.save()
            self.recalculate_global_effects(request, strain)

        if 'side_effects' == effect_type:
            r.side_effects = self.build_effects_object(effects, strain.side_effects)
            r.side_effects_changed = True
            r.last_modified_by = request.user
            r.last_modified_by_ip = sender_ip
            r.save()
            self.recalculate_global_effects(request, strain)

        StrainUserRatingESService().save_strain_review(r, strain.id, request.user.id)

        return Response({}, status=status.HTTP_200_OK)

    def build_effects_object(self, effects, strain_default_effects):
        for default_e in strain_default_effects:
            strain_default_effects[default_e] = 0

        effects_to_persist = strain_default_effects
        for e in effects:
            effects_to_persist[e.get('name')] = e.get('value')
        return effects_to_persist

    def recalculate_global_effects(self, request, strain, immediate=False):
        try:
            recalculate_size = int(SystemProperty.objects.get(name='rating_recalculation_size').value)
        except SystemProperty.DoesNotExist:
            recalculate_size = 10

        ratings = StrainRating.objects.filter(strain=strain, status='pending', removed_date=None)

        # First check if there are "recalculate_size" new ratings
        if (len(ratings) >= recalculate_size) or immediate:
            sender_ip = get_client_ip(request)

            for r in ratings:
                r.status = 'processed'
                r.last_modified_ip = sender_ip
                r.last_modified_by = request.user
                r.save()

            # Recalculate Global scores for each review in the system that wasn't removed
            ratings = StrainRating.objects.filter(strain=strain, removed_date=None)

            strain.effects = self.calculate_new_global_values(ratings, 'effects')
            strain.benefits = self.calculate_new_global_values(ratings, 'benefits')
            strain.side_effects = self.calculate_new_global_values(ratings, 'side_effects')
            strain.save()

            StrainESService().save_strain(strain)

    def calculate_new_global_values(self, reviews, effect_type):
        total_strain_effects = {}

        if effect_type == 'effects':
            for r in reviews:
                for effect_name in r.effects:
                    if total_strain_effects.get(effect_name):
                        total_strain_effects[effect_name] += r.effects[effect_name]
                    else:
                        total_strain_effects[effect_name] = r.effects[effect_name]

        if effect_type == 'benefits':
            for r in reviews:
                for effect_name in r.benefits:
                    if total_strain_effects.get(effect_name):
                        total_strain_effects[effect_name] += r.benefits[effect_name]
                    else:
                        total_strain_effects[effect_name] = r.benefits[effect_name]

        if effect_type == 'side_effects':
            for r in reviews:
                for effect_name in r.side_effects:
                    if total_strain_effects.get(effect_name):
                        total_strain_effects[effect_name] += r.side_effects[effect_name]
                    else:
                        total_strain_effects[effect_name] = r.side_effects[effect_name]

        for effect_name in total_strain_effects:
            total_strain_effects[effect_name] /= len(reviews)

        return total_strain_effects

    def delete(self, request, strain_id):
        effect_type = request.data.get('effect_type')
        sender_ip = get_client_ip(request)
        strain = Strain.objects.get(id=strain_id)
        rating = StrainRating.objects.get(strain=strain, created_by=request.user, removed_date=None)

        if effect_type == 'effects':
            rating.effects = strain.effects
            rating.effects_changed = False

        if effect_type == 'benefits':
            rating.benefits = strain.benefits
            rating.benefits_changed = False

        if effect_type == 'side_effects':
            rating.side_effects = strain.side_effects
            rating.side_effects_changed = False

        if not rating.effects_changed and not rating.benefits_changed and not rating.side_effects_changed:
            rating.removed_date = datetime.now()

        rating.last_modified_ip = sender_ip
        rating.last_modified_by = request.user
        rating.save()

        StrainUserRatingESService().save_strain_review(rating, strain.id, request.user.id)

        if rating.status == 'processed':
            self.recalculate_global_effects(request, strain, immediate=True)

        return Response({}, status=status.HTTP_200_OK)


def get_client_ip(request):
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        return request.META.get('HTTP_X_FORWARDED_FOR').split(',')[-1].strip()
    elif request.META.get('HTTP_X_REAL_IP'):
        return request.META.get('HTTP_X_REAL_IP')
    else:
        return request.META.get('REMOTE_ADDR')


class StrainEffectView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, effect_type):
        effects_raw = Effect.objects.filter(effect_type=effect_type)
        effects = []

        for e in effects_raw:
            effects.append({
                'data_name': e.data_name,
                'display_name': e.display_name
            })

        return Response(effects, status=status.HTTP_200_OK)


class StrainFlavorView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        flavors_raw = Flavor.objects.all()
        flavors = []

        for e in flavors_raw:
            flavors.append({
                'data_name': e.data_name,
                'display_name': e.display_name,
                'image': e.image.url if e.image else None
            })

        return Response(flavors, status=status.HTTP_200_OK)


class StrainsListByVarietyView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, strain_variety):
        limit = request.GET.get('limit')
        strains = []
        if limit:
            strains_raw = Strain.objects.filter(variety=strain_variety).order_by('id')[:int(limit)]
        else:
            strains_raw = Strain.objects.filter(variety=strain_variety).order_by('id')

        for e in strains_raw:
            images = StrainImage.objects.filter(strain=e)
            strains.append({
                'image': images[0].image.url if len(images) > 0 and images[0].image else None,
                'name': e.name,
                'variety': e.variety,
                'slug': e.strain_slug
            })

        return Response(strains, status=status.HTTP_200_OK)


class BusinessLocationLookupView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, bus_type):
        query = request.GET.get('q')
        location = json.loads(request.GET.get('loc')) if request.GET.get('loc') else None
        tz = request.GET.get('tz')
        result = SearchElasticService().lookup_business_location(query, bus_type=[bus_type],
                                                                 location=location, timezone=tz)

        return Response({
            'total': result.get('total'),
            'payloads': result.get('payloads')
        }, status=status.HTTP_200_OK)


class StrainSearchAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = StrainSearchSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.GET)
        serializer.is_valid(raise_exception=True)
        query = serializer.data
        q = query.get('q')
        if q:
            result = SearchElasticService().lookup_strain_by_name(q, size=query['size'],
                                                                  start_from=query.get('start_from', 0))
        else:
            current_user = request.user if request.user.is_authenticated() else None
            result = SearchElasticService().advanced_search(
                query, current_user, size=query['size'], start_from=query.get('start_from', 0))
        return Response({
            'total': result.get('total'),
            'payloads': result.get('list', result.get('payloads'))
        }, status=status.HTTP_200_OK)
