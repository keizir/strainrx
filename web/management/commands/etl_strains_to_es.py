# -*- coding: utf-8 -*-
import json
import logging
import time

from django.core.management.base import BaseCommand, CommandError

from web.search import es_mappings
from web.search.es_mappings import strain_mapping, strain_review_mapping
from web.search.es_service import SearchElasticService as ElasticService
from web.search.models import Strain, StrainReview
from web.search.strain_es_service import StrainESService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
            ETL strain data from psql to ES
        """

    def add_arguments(self, parser):
        parser.add_argument('--drop_and_rebuild',
                            action='store_true',
                            dest='drop_and_rebuild',
                            help='If arg is included will drop given index, set mappings, analyzers')

        parser.add_argument('--index',
                            action='store',
                            default=None,
                            dest='index',
                            help='Name of ES index to store results in')

    def handle(self, *args, **options):
        if options.get('index'):
            self.INDEX = options.get('index').lower()
        else:
            raise CommandError('Index is required')

        self.DROP_AND_REBUILD = options.get('drop_and_rebuild', False)
        self.etl_strains()

    def etl_strains(self):
        if self.DROP_AND_REBUILD:
            self.drop_and_rebuild()

        self.load_strains()
        time.sleep(2)
        self.load_strain_reviews()

    def drop_and_rebuild(self):
        es = ElasticService()

        # create custom analyzer for strain names
        index_settings = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "name_analyzer": {
                            "type": "custom",
                            "tokenizer": "whitespace",
                            "filter": ["lowercase"]
                        }
                    }
                }
            },
            "mappings": {
                es_mappings.TYPES.get('strain'): strain_mapping,
                es_mappings.TYPES.get('strain_review'): strain_review_mapping
            }
        }

        # delete index
        es.delete_index(self.INDEX)

        # set analyzer
        es.set_settings(self.INDEX, index_settings)

        self.stdout.write('1. Setup complete for [{0}] index'.format(self.INDEX))

    def load_strains(self):
        es = ElasticService()
        # fetch all strains
        strains = Strain.objects.all()

        bulk_strain_data = []

        # build up bulk update
        for s in strains:
            action_data = json.dumps({
                'index': {}
            })

            input_variants = [s.name]
            name_words = s.name.split(' ')
            for i, name_word in enumerate(name_words):
                if i < len(name_words) - 1:
                    input_variants.append('{0} {1}'.format(name_word, name_words[i + 1]))
                else:
                    input_variants.append(name_word)

            bulk_strain_data.append(action_data)
            bulk_strain_data.append(json.dumps({
                'id': s.id,
                'name': s.name,
                'strain_slug': s.strain_slug,
                'variety': s.variety,
                'category': s.category,
                'effects': s.effects,
                'benefits': s.benefits,
                'side_effects': s.side_effects,
                'flavor': s.flavor,
                'about': s.about,
                'origins': '',
                'removed_date': s.removed_date.isoformat() if s.removed_date else None,
                'removed_by_id': s.removed_by,
                'name_suggest': {
                    'input': input_variants
                }
            }))

        if len(bulk_strain_data) == 0:
            self.stdout.write('   ---> Nothing to update')
            return

        transformed_bulk_data = '{0}\n'.format('\n'.join(bulk_strain_data))
        results = es.bulk_index(transformed_bulk_data, index=self.INDEX, index_type=es_mappings.TYPES.get('strain'))

        if results.get('success') is False:
            # keep track of any errors we get
            logger.error(('Error updating {index}/{index_type} in ES. Errors: {errors}'.format(
                index=self.INDEX,
                index_type=es_mappings.TYPES.get('strain'),
                errors=results.get('errors')
            )))

        self.stdout.write(
            '2. Updated [{0}] index with {1} strains'.format(self.INDEX, len(strains))
        )

    def load_strain_reviews(self):
        self.stdout.write('3. Updating a strain reviews')

        es = ElasticService()
        reviews = StrainReview.objects.all()
        bulk_reviews_data = []
        strains_cache_map = {}

        for r in reviews:
            strain_id = r.strain.id
            strain = strains_cache_map.get(strain_id)

            if strain is None or len(strain) == 0:
                es_strain = StrainESService().get_strain_by_db_id(strain_id)
                strain = es_strain.get('hits', {}).get('hits', [])
                strains_cache_map[strain_id] = strain

            if strain is None or len(strain) == 0:
                raise CommandError('   !!!---> No strain found in ES for id [{0}].'.format(strain_id))

            action_data = json.dumps({
                'index': {
                    '_parent': strain[0].get('_id')
                }
            })

            bulk_reviews_data.append(action_data)
            bulk_reviews_data.append(json.dumps({
                'id': r.id,
                'rating': r.rating,
                'review': r.review,
                'review_approved': r.review_approved,
                'created_date': r.created_date.isoformat(),
                'created_by': r.created_by.id,
                'last_modified_date': r.last_modified_date.isoformat() if r.last_modified_date else None,
                'last_modified_by': r.last_modified_by.id if r.last_modified_by else None
            }))

        if len(bulk_reviews_data) == 0:
            self.stdout.write('   ---> No reviews to update')
            return

        transformed_bulk_data = '{0}\n'.format('\n'.join(bulk_reviews_data))
        results = es.bulk_index(transformed_bulk_data, index=self.INDEX,
                                index_type=es_mappings.TYPES.get('strain_review'))

        if results.get('success') is False:
            # keep track of any errors we get
            logger.error(('Error updating {index}/{index_type} in ES. Errors: {errors}'.format(
                index=self.INDEX,
                index_type=es_mappings.TYPES.get('strain_review'),
                errors=results.get('errors')
            )))

        self.stdout.write(
            'Updated [{0}] index with {1} strain reviews'.format(self.INDEX, len(reviews))
        )
