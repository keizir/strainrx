# -*- coding: utf-8 -*-
import csv
import logging
import sys
import time
import uuid

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from web.search.models import Strain, StrainRating
from web.users.models import User

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
            time_start = time.time()

            reader = csv.DictReader(f)

            strain_origins = {}
            strain_models = []

            print('\n1. Parsing ...')

            for row in reader:
                name = row.get('Strain')
                internal_id = row.get('ID')
                variety = self.get_variety(row)
                category = self.get_category(row)
                effects = self.build_effects_json(row)
                benefits = self.build_benefits_json(row)
                side_effects = self.build_side_effects(row)
                flavors = self.build_flavors(row)
                about = row.get('About')

                strain_origins[slugify(name)] = row.get('Origins')

                if Strain.objects.filter(name=name, category=category).exists():
                    strain = Strain.objects.get(name=name, category=category)
                    strain.internal_id = internal_id
                    strain.strain_slug = slugify(name)
                    strain.variety = variety
                    strain.effects = effects
                    strain.benefits = benefits
                    strain.side_effects = side_effects
                    strain.flavor = flavors
                    strain.about = about
                else:
                    strain = Strain(name=name, internal_id=internal_id, variety=variety, category=category,
                                    effects=effects, benefits=benefits, side_effects=side_effects,
                                    flavor=flavors, about=about)

                try:
                    strain.full_clean()
                    strain_models.append(strain)
                except ValidationError as e:
                    raise CommandError('Model did not pass validation.\n Errors: {0}\n Model: [{1}]'
                                       .format(str(e.message_dict), str(strain.__dict__)))

            print('\n2. Persisting ...')

            persisted = []

            for to_persist in strain_models:
                to_persist.save()
                to_persist.origins.clear()
                persisted.append(to_persist)
                print('   --> Strain Persisted: [name="{0}", category="{1}"]'
                      .format(to_persist.name, to_persist.category))

            print('\n3. Persisting origins ...')
            for s in persisted:
                origins = strain_origins[slugify(s.name)]

                if origins is not None and origins != '':
                    origins_split = origins.split(',')
                    for name in origins_split:
                        name_cleared = name.strip()
                        strain_slug = slugify(name_cleared)
                        if Strain.objects.filter(strain_slug=strain_slug).exists():
                            existing = Strain.objects.get(strain_slug=strain_slug)
                            s.origins.add(existing.id)
                        else:
                            print('   ---> !!! Error: Origin [name="{0}"] does not exist. '
                                  'Parent strain [name="{1}", category="{2}"]'
                                  .format(name_cleared, s.name, s.category),
                                  file=sys.stderr)

            print('\n4. Creating rate_bot user and default ratings ...')
            try:
                rate_bot = User.objects.get(email='tech+rate_bot@strainrx.co')
            except User.DoesNotExist:
                rate_bot = User(username='srx_ratebot', email='tech+rate_bot@strainrx.co',
                                is_email_verified=True, is_age_verified=True)
                rate_bot.set_password(str(uuid.uuid4()))
                rate_bot.save()

            for s in persisted:
                if not StrainRating.objects.filter(strain=s, created_by=rate_bot, removed_date=None).exists():
                    r = StrainRating(strain=s, created_by=rate_bot, effects=s.effects, benefits=s.benefits,
                                     side_effects=s.side_effects, status='pending')
                    r.save()
                else:
                    r = StrainRating.objects.get(strain=s, created_by=rate_bot, removed_date=None)
                    r.effects = s.effects
                    r.benefits = s.benefits
                    r.side_effects = s.side_effects
                    r.save()

            time_end = time.time()
            print('\n5. Well Done! Persisted {0} strains in {1}sec!\n'
                  .format(len(persisted), str(time_end - time_start)))

    def get_variety(self, row):
        if row.get('Sativa').upper() == 'X':  # Sativa
            return 'sativa'
        elif row.get('Indica').upper() == 'X':  # Indica
            return 'indica'
        elif row.get('Hybrid').upper() == 'X':  # Hybrid
            return 'hybrid'
        else:
            raise CommandError('Invalid variety: name - {0}, sativa - {1}, indica - {2}, hybrid - {3}'
                               .format(row.get('Strain'), row.get('Sativa'), row.get('Indica'), row.get('Hybrid')))

    def get_category(self, row):
        if row.get('Flower').upper() == 'X':
            return 'flower'
        elif row.get('Edible').upper() == 'X':
            return 'edible'
        elif row.get('Liquid').upper() == 'X':
            return 'liquid'
        elif row.get('Oil').upper() == 'X':
            return 'oil'
        elif row.get('Wax').upper() == 'X':
            return 'wax'
        else:
            raise CommandError('Invalid category: '
                               'name - {0}, flower - {1}, edible - {2}, liquid - {3}, oil - {4}, wax - {5}'
                               .format(row.get('Strain'), row.get('Flower'), row.get('Edible'), row.get('Liquid'),
                                       row.get('Oil'), row.get('Wax')))

    def build_effects_json(self, row):
        return {"happy": self.value_or_zero(row.get('Happy')),
                "uplifted": self.value_or_zero(row.get('Uplifted (raised spirits)')),
                "stimulated": self.value_or_zero(row.get('Aroused')),
                "energetic": self.value_or_zero(row.get('Energetic')),
                "creative": self.value_or_zero(row.get('Creative')),
                "focused": self.value_or_zero(row.get('Focused (productive)')),
                "relaxed": self.value_or_zero(row.get('Relaxed (calm and relaxed)')),
                "sleepy": self.value_or_zero(row.get('Sleepy')),
                "talkative": self.value_or_zero(row.get('Talkative (social)')),
                "euphoric": self.value_or_zero(row.get('Euphoric')),
                "hungry": self.value_or_zero(row.get('Hungry')),
                "tingly": self.value_or_zero(row.get('Tingly (stimulated)')),
                "good_humored": self.value_or_zero(row.get('Giggly (good humor)'))}

    def build_benefits_json(self, row):
        return {"reduce_stress": self.value_or_zero(row.get('Reduce Stress')),
                "help_depression": self.value_or_zero(row.get('Help Depression')),
                "relieve_pain": self.value_or_zero(row.get('Help With Pain')),
                "reduce_fatigue": self.value_or_zero(row.get('Reduce Fatigue')),
                "reduce_headaches": self.value_or_zero(row.get('Help With Headaches')),
                "help_muscles_spasms": self.value_or_zero(row.get('Relieve Muscle Spasms')),
                "lower_eye_pressure": self.value_or_zero(row.get('Lower Eye Pressure')),
                "reduce_nausea": self.value_or_zero(row.get('Help With Nausea')),
                "reduce_inflammation": self.value_or_zero(row.get('Reduce Inflammation')),
                "relieve_cramps": self.value_or_zero(row.get('Relieve Cramps')),
                "help_with_seizures": self.value_or_zero(row.get('Help With Seizures')),
                "restore_appetite": self.value_or_zero(row.get('Restore Appetite')),
                "help_with_insomnia": self.value_or_zero(row.get('Help With Insomnia'))}

    def value_or_zero(self, value):
        if value is not None and value != '':
            return int(value)
        else:
            return 0

    def build_side_effects(self, row):
        return {"anxiety": self.get_side_effect_value(row.get('Anxiety')),
                "dry_mouth": self.get_side_effect_value(row.get('Dry Mouth')),
                "paranoia": self.get_side_effect_value(row.get('Paranoia')),
                "headache": self.get_side_effect_value(row.get('Headache')),
                "dizziness": self.get_side_effect_value(row.get('Dizziness')),
                "dry_eyes": self.get_side_effect_value(row.get('Dry Eyes')), }

    def get_side_effect_value(self, value):
        if value is not None and value != '':
            parsed = float(value)
            if 0.1 <= parsed <= 0.5:
                return 6
            if 0.5 < parsed <= 1.4:
                return 7
            if 1.4 < parsed <= 2.3:
                return 8
            if 2.3 < parsed <= 3.1:
                return 9
            if 3.1 < parsed <= 4:
                return 10
        else:
            return 0

    def build_flavors(self, row):
        return {"ammonia": self.get_flavor_value(row.get('Ammonia')),
                "apple": self.get_flavor_value(row.get('Apple')),
                "apricot": self.get_flavor_value(row.get('Apricot')),
                "berry": self.get_flavor_value(row.get('Berry')),
                "blue-cheese": self.get_flavor_value(row.get('Blue Cheese')),
                "blueberry": self.get_flavor_value(row.get('Blueberry')),
                "buttery": self.get_flavor_value(row.get('Buttery')),
                "cheese": self.get_flavor_value(row.get('Cheese')),
                "chemical": self.get_flavor_value(row.get('Chemical')),
                "chestnut": self.get_flavor_value(row.get('Chestnut')),
                "citrus": self.get_flavor_value(row.get('Citrus')),
                "coffee": self.get_flavor_value(row.get('Coffee')),
                "diesel": self.get_flavor_value(row.get('Diesel')),
                "earthy": self.get_flavor_value(row.get('Earthy')),
                "flowery": self.get_flavor_value(row.get('Flowery')),
                "grape": self.get_flavor_value(row.get('Grape')),
                "grapefruit": self.get_flavor_value(row.get('Grapefruit')),
                "herbal": self.get_flavor_value(row.get('Herbal')),
                "honey": self.get_flavor_value(row.get('Honey')),
                "lavender": self.get_flavor_value(row.get('Lavender')),
                "lemon": self.get_flavor_value(row.get('Lemon')),
                "lime": self.get_flavor_value(row.get('Lime')),
                "mango": self.get_flavor_value(row.get('Mango')),
                "menthol": self.get_flavor_value(row.get('Menthol')),
                "minty": self.get_flavor_value(row.get('Minty')),
                "nutty": self.get_flavor_value(row.get('Nutty')),
                "orange": self.get_flavor_value(row.get('Orange')),
                "peach": self.get_flavor_value(row.get('Peach')),
                "pear": self.get_flavor_value(row.get('Pear')),
                "pepper": self.get_flavor_value(row.get('Pepper')),
                "pine": self.get_flavor_value(row.get('Pine')),
                "pineapple": self.get_flavor_value(row.get('Pineapple')),
                "plum": self.get_flavor_value(row.get('Plum')),
                "pungent": self.get_flavor_value(row.get('Pungent')),
                "rose": self.get_flavor_value(row.get('Rose')),
                "sage": self.get_flavor_value(row.get('Sage')),
                "skunk": self.get_flavor_value(row.get('Skunk')),
                "spicy-herbal": self.get_flavor_value(row.get('Spicy/Herbal')),
                "strawberry": self.get_flavor_value(row.get('Strawberry')),
                "sweet": self.get_flavor_value(row.get('Sweet')),
                "tar": self.get_flavor_value(row.get('Tar')),
                "tea": self.get_flavor_value(row.get('Tea')),
                "tobacco": self.get_flavor_value(row.get('Tobacco')),
                "tree-fruit": self.get_flavor_value(row.get('Tree Fruit')),
                "tropical": self.get_flavor_value(row.get('Tropical')),
                "vanilla": self.get_flavor_value(row.get('Vanilla')),
                "violet": self.get_flavor_value(row.get('Violet')),
                "woody": self.get_flavor_value(row.get('Woody')), }

    def get_flavor_value(self, value):
        if value is not None and value.strip() != '':
            if value == 'X' or value:
                return 2
            else:
                return int(value)
        else:
            return 0
