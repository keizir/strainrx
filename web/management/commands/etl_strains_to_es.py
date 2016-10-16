# -*- coding: utf-8 -*-
import json
import logging

from django.core.management.base import BaseCommand, CommandError

from web.search.es_mappings import strain_mapping, strain_suggester_mapping
from web.search.es_service import SearchElasticService as ElasticService
from web.search.models import Strain

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

        parser.add_argument('--index_type',
                            action='store',
                            default=None,
                            dest='index_type',
                            help='Name of ES index type to store results in')

        parser.add_argument('--create_or_update_suggester',
                            action='store_true',
                            default=None,
                            dest='update_suggester',
                            help='If arg is included will create/recreate strain suggester index')

    def handle(self, *args, **options):
        if options.get('index'):
            self.INDEX = options.get('index').lower()
        else:
            raise CommandError('Index is required')

        self.DROP_AND_REBUILD = options.get('drop_and_rebuild', False)
        self.UPDATE_SUGGESTER_INDEX = options.get('update_suggester', False)
        self.INDEX_TYPE = options.get('index_type', 'flower').lower()
        self.SUGGESTER_INDEX_TYPE = 'name'

        self.etl_strains()

    def etl_strains(self):
        if self.DROP_AND_REBUILD:
            self.drop_and_rebuild()

        self.load_strains()

    def drop_and_rebuild(self):
        es = ElasticService()

        # create custom analyzer for strain names
        index_settings = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "name_analyzer": {
                            "tokenizer": "standard",
                            "filter": ["lowercase"]
                        }
                    }
                }
            }
        }

        # delete index
        es.delete_index(self.INDEX)

        # set analyzer
        es.set_settings(self.INDEX, index_settings)

        # set mapping
        es.set_mapping(self.INDEX, self.INDEX_TYPE, strain_mapping)

        if self.UPDATE_SUGGESTER_INDEX:
            es.set_mapping(self.INDEX, self.SUGGESTER_INDEX_TYPE, strain_suggester_mapping)

        self.stdout.write('Setup complete for {0} index'.format(self.INDEX))

    def load_strains(self):
        es = ElasticService()
        # fetch all strains
        strains = Strain.objects.all()

        bulk_strain_data = []
        bulk_strain_suggester_data = []

        # build up bulk update
        for s in strains:
            action_data = json.dumps({
                'index': {}
            })

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
                'origins': ''
            }))

            if self.UPDATE_SUGGESTER_INDEX:
                bulk_strain_suggester_data.append(action_data)
                bulk_strain_suggester_data.append(json.dumps({
                    'name': s.name,
                    'name_suggest': {
                        'input': s.name,
                        'output': s.name,
                        'payload': {
                            'id': s.id,
                            'name': s.name,
                            'strain_slug': s.strain_slug,
                            'variety': s.variety,
                            'category': s.category
                        }
                    }
                }))

        if len(bulk_strain_data) == 0:
            self.stdout.write('Nothing to update')
            return

        transformed_bulk_data = '{0}\n'.format('\n'.join(bulk_strain_data))
        results = es.bulk_index(transformed_bulk_data, index=self.INDEX, index_type=self.INDEX_TYPE)

        if results.get('success') is False:
            # keep track of any errors we get
            logger.error(('Error updating {index}/{index_type} in ES. Errors: {errors}'.format(
                index=self.INDEX,
                index_type=self.INDEX_TYPE,
                errors=results.get('errors')
            )))

        if self.UPDATE_SUGGESTER_INDEX:
            transformed_bulk_suggester_data = '{0}\n'.format('\n'.join(bulk_strain_suggester_data))
            results_suggester = es.bulk_index(transformed_bulk_suggester_data, index=self.INDEX,
                                              index_type=self.SUGGESTER_INDEX_TYPE)

            if results_suggester.get('success') is False:
                # keep track of any errors we get
                logger.error(('Error updating {index}/{index_type} in ES. Errors: {errors}'.format(
                    index=self.INDEX,
                    index_type=self.SUGGESTER_INDEX_TYPE,
                    errors=results.get('errors')
                )))

        self.stdout.write(
            'Updated {0} index with {1} strains'.format(self.INDEX, len(strains))
        )
