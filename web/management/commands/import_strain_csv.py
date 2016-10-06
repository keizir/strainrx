# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from web.search.models import Strain

import logging, csv

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = """
            Imports strain data from csv
        """

    def add_arguments(self, parser):
        parser.add_argument('--starting_row',
                            action='store',
                            default=None,
                            dest='starting_row',
                            help='If doing a partial import, row number to start on')

        parser.add_argument('--csv_path',
                            action='store',
                            default=None,
                            dest='csv_path',
                            help='Path to csv relative to current directory')


    def handle(self, *args, **options):
        if options.get('csv_path'):
            self.csv_path = options.get('csv_path')
        else:
            raise CommandError('csv_path is required')

        self.import_csv()

    def import_csv(self):
        with open(self.csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                # TODO logic to skip rows based on starting_row param
                # regular logging (logger.info, etc) should work but this is best practice for simple console output
                self.stdout.write('importing {0}'.format(row.get('Strain')))

                # determine which variety is selected
                if row.get('Sativa').upper() == 'X':
                    variety = 'sativa'
                elif row.get('Indica').upper() == 'X':
                    variety = 'indica'
                elif row.get('Hybrid').upper() == 'X':
                    variety = 'hybrid'
                else:
                    # no valid option found
                    raise CommandError('invalid variety')

                # TODO get category via similar logic as variety

                s = Strain(
                    name=row.get('Strain'),
                    variety=variety,
                    category='flower', # TODO temp hardcoding for testing until logic above is done
                    # effects='', # TODO for each of these we'll need to build up the dicts with all applicable options (JSON encoding should be handled by django on save so you can use native python data structs)
                    # benefits='',
                    # side_effects='',
                    # flavor='',
                    about=row.get('About'),
                )

                # just for debug - print dict representation of the new strain
                print('strain: ', s.__dict__)

                # TODO validate / save strain
                # django model validation: https://docs.djangoproject.com/en/1.10/ref/models/instances/#validating-objects
                # s.save()


