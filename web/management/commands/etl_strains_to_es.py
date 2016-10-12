# -*- coding: utf-8 -*-
import logging
import json

from django.core.management.base import BaseCommand, CommandError

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

    def handle(self, *args, **options):
        if options.get('index'):
            self.INDEX = options.get('index').lower()
        else:
            raise CommandError('Index is required')

        self.DROP_AND_REBUILD = options.get('drop_and_rebuild', False)
        self.INDEX_TYPE = options.get('index_type', 'Flower').lower()

        self.etl_strains()

    def etl_strains(self):
        if self.DROP_AND_REBUILD:
            self.drop_and_rebuild()

        self.load_strains()

    def drop_and_rebuild(self):
        es = ElasticService()

        mapping = {
            "properties": {
                "id": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "name": {
                    "type": "string",
                    "index": "analyzed",
                    "analyzer": "name_analyzer",
                    "norms": {
                        "enabled": False
                    },
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        },
                        "stemmed": {
                            "type": "string",
                            "analyzer": "snowball"
                        }
                    }
                },
                "strain_slug": {
                    "type": "string",
                    "index": "no"
                },
                "variety": {
                    "type": "string"
                },
                "category": {
                    "type": "string"
                },
                "effects": {
                    "properties": {
                        "happy": {
                            "type": "short"
                        },
                        "uplifted": {
                            "type": "short"
                        },
                        "stimulated": {
                            "type": "short"
                        },
                        "energetic": {
                            "type": "short"
                        },
                        "creative": {
                            "type": "short"
                        },
                        "focused": {
                            "type": "short"
                        },
                        "relaxed": {
                            "type": "short"
                        },
                        "sleepy": {
                            "type": "short"
                        },
                        "talkative": {
                            "type": "short"
                        },
                        "euphoric": {
                            "type": "short"
                        },
                        "hungry": {
                            "type": "short"
                        },
                        "tingly": {
                            "type": "short"
                        },
                        "good_humored": {
                            "type": "short"
                        }
                    }
                },
                "benefits": {
                    "properties": {
                        "reduce_stress": {
                            "type": "short"
                        },
                        "help_depression": {
                            "type": "short"
                        },
                        "relieve_pain": {
                            "type": "short"
                        },
                        "reduce_fatigue": {
                            "type": "short"
                        },
                        "reduce_headaches": {
                            "type": "short"
                        },
                        "help_muscles_spasms": {
                            "type": "short"
                        },
                        "lower_eye_pressure": {
                            "type": "short"
                        },
                        "reduce_nausea": {
                            "type": "short"
                        },
                        "reduce_inflammation": {
                            "type": "short"
                        },
                        "relieve_cramps": {
                            "type": "short"
                        },
                        "help_with_seizures": {
                            "type": "short"
                        },
                        "restore_appetite": {
                            "type": "short"
                        },
                        "help_with_insomnia": {
                            "type": "short"
                        }
                    }
                },
                "side_effects": {
                    "properties": {
                        "anxiety": {
                            "type": "short"
                        },
                        "dry_mouth": {
                            "type": "short"
                        },
                        "paranoia": {
                            "type": "short"
                        },
                        "headache": {
                            "type": "short"
                        },
                        "dizziness": {
                            "type": "short"
                        },
                        "dry_eyes": {
                            "type": "short"
                        }
                    }
                },
                "flavor": {
                    "properties": {
                        "ammonia": {
                            "type": "short"
                        },
                        "apple": {
                            "type": "short"
                        },
                        "apricot": {
                            "type": "short"
                        },
                        "berry": {
                            "type": "short"
                        },
                        "blue_cheese": {
                            "type": "short"
                        },
                        "blueberry": {
                            "type": "short"
                        },
                        "buttery": {
                            "type": "short"
                        },
                        "cheese": {
                            "type": "short"
                        },
                        "chemical": {
                            "type": "short"
                        },
                        "chestnut": {
                            "type": "short"
                        },
                        "citrus": {
                            "type": "short"
                        },
                        "coffee": {
                            "type": "short"
                        },
                        "diesel": {
                            "type": "short"
                        },
                        "earthy": {
                            "type": "short"
                        },
                        "flowery": {
                            "type": "short"
                        },
                        "grape": {
                            "type": "short"
                        },
                        "grapefruit": {
                            "type": "short"
                        },
                        "herbal": {
                            "type": "short"
                        },
                        "honey": {
                            "type": "short"
                        },
                        "lavender": {
                            "type": "short"
                        },
                        "lemon": {
                            "type": "short"
                        },
                        "lime": {
                            "type": "short"
                        },
                        "mango": {
                            "type": "short"
                        },
                        "menthol": {
                            "type": "short"
                        },
                        "minty": {
                            "type": "short"
                        },
                        "nutty": {
                            "type": "short"
                        },
                        "orange": {
                            "type": "short"
                        },
                        "peach": {
                            "type": "short"
                        },
                        "pear": {
                            "type": "short"
                        },
                        "pepper": {
                            "type": "short"
                        },
                        "pine": {
                            "type": "short"
                        },
                        "pineapple": {
                            "type": "short"
                        },
                        "plum": {
                            "type": "short"
                        },
                        "pungent": {
                            "type": "short"
                        },
                        "rose": {
                            "type": "short"
                        },
                        "sage": {
                            "type": "short"
                        },
                        "skunk": {
                            "type": "short"
                        },
                        "spicy_herbal": {
                            "type": "short"
                        },
                        "strawberry": {
                            "type": "short"
                        },
                        "sweet": {
                            "type": "short"
                        },
                        "tar": {
                            "type": "short"
                        },
                        "tea": {
                            "type": "short"
                        },
                        "tobacco": {
                            "type": "short"
                        },
                        "tree_fruit": {
                            "type": "short"
                        },
                        "tropical": {
                            "type": "short"
                        },
                        "vanilla": {
                            "type": "short"
                        },
                        "violet": {
                            "type": "short"
                        },
                        "woody": {
                            "type": "short"
                        }
                    }
                },
                "about": {
                    "type": "string"
                },
                "origins": {
                    "type": "string"
                }
            }
        }

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
        es.set_mapping(self.INDEX, self.INDEX_TYPE, mapping)

        self.stdout.write('Setup complete for {0} index'.format(self.INDEX))

    def load_strains(self):
        es = ElasticService()
        # fetch all strains
        strains = Strain.objects.all()

        bulk_data = []

        # build up bulk update
        for s in strains:
            action_data = json.dumps({
                'index': {}
            })

            doc = json.dumps({
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
            })

            bulk_data.append(action_data)
            bulk_data.append(doc)

        if len(bulk_data) == 0:
            self.stdout.write('Nothing to update')
            return

        transformed_bulk_data = '{0}\n'.format('\n'.join(bulk_data))
        results = es.bulk_index(transformed_bulk_data, index=self.INDEX, index_type=self.INDEX_TYPE)

        if results.get('success') is False:
            # keep track of any errors we get
            logger.error(('Error updating {index_type} in ES. Errors: {errors}'.format(
                index_type=self.INDEX,
                errors=results.get('errors')
            )))

        self.stdout.write(
            'Updated {0} index with {1} strains'.format(self.INDEX, len(strains))
        )
