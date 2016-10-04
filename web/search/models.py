from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from web.users.models import User


class Strain(models.Model):
    TYPE = (
        ('SATIVA', 'Sativa'),
        ('INDICA', 'Indica'),
        ('HYBRID', 'Hybrid')
    )

    CATEGORY = (
        ('FLOWER', 'Flower'),
        ('EDIBLE', 'Edible'),
        ('LIQUID', 'Liquid'),
        ('OIL', 'Oil'),
        ('WAX', 'Wax')
    )

    internal_id = models.IntegerField(_('Internal Identifier'), blank=False, null=False)
    name = models.CharField(_('Name'), blank=False, null=False, max_length=255)
    type = models.CharField(_('Type'), blank=False, null=False, max_length=6, choices=TYPE)
    category = models.CharField(_('Category'), blank=False, null=False, max_length=6, choices=CATEGORY)
    about = models.CharField(_('About'), blank=True, null=True, max_length=1500)
    origins = models.CharField(_('Origins'), blank=True, null=True, max_length=500)
    similar = models.CharField(_('Similar'), blank=True, null=True, max_length=500)

    def __str__(self):
        return self.name


class Effect(models.Model):
    NAMES = (
        ('happy', 'Happy'),
        ('uplifting', 'Uplifted (raised spirits)'),
        ('stimulated', 'Aroused'),
        ('energetic', 'Energetic'),
        ('creative', 'Creative'),
        ('focused', 'Focused (productive)'),
        ('relaxed', 'Relaxed (calm and relaxed)'),
        ('sleepy', 'Sleepy'),
        ('talkative', 'Talkative (social)'),
        ('euphoric', 'Euphoric'),
        ('hungry', 'Hungry'),
        ('tingly', 'Tingly (stimulated)'),
        ('good_humored', 'Giggly (good humor)')
    )

    name = models.CharField(_('Name'), blank=False, null=False, max_length=30, choices=NAMES)


class StrainEffect(models.Model):
    strain = models.ForeignKey(Strain, on_delete=models.SET_NULL)
    effect = models.ForeignKey(Effect, on_delete=models.SET_NULL)
    effect_value = models.IntegerField(_('Effect Strength'), blank=False, null=False)


class Benefit(models.Model):
    NAMES = (
        ('reduce-stress', 'Reduce Stress'),
        ('help-depression', 'Help Depression'),
        ('relieve-pain', 'Help With Pain'),
        ('reduce-fatigue', 'Reduce Fatigue'),
        ('reduce-headaches', 'Help With Headaches'),
        ('help-muscles-spasms', 'Relieve Muscle Spasms'),
        ('lower-eye-pressure', 'Lower Eye Pressure'),
        ('reduce-nausea', 'Help With Nausea'),
        ('reduce-inflammation', 'Reduce Inflammation'),
        ('relieve-cramps', 'Relieve Cramps'),
        ('help-with-seizures', 'Help With Seizures'),
        ('restore-appetite', 'Restore Appetite'),
        ('help-with-insomnia', 'Help With Insomnia')
    )

    name = models.CharField(_('Name'), blank=False, null=False, max_length=30, choices=NAMES)


class StrainBenefit(models.Model):
    strain = models.ForeignKey(Strain, on_delete=models.SET_NULL)
    benefit = models.ForeignKey(Benefit, on_delete=models.SET_NULL)
    benefit_value = models.IntegerField(_('Benefit Strength'), blank=False, null=False)


class NegativeEffect(models.Model):
    NAMES = (
        ('anxiety', 'Anxiety'),
        ('dry-mouth', 'Dry Mouth'),
        ('paranoia', 'Paranoia'),
        ('headache', 'Headache'),
        ('dizziness', 'Dizziness'),
        ('dry-eyes', 'Dry Eyes')
    )

    name = models.CharField(_('Name'), blank=False, null=False, max_length=30, choices=NAMES)


class StrainNegativeEffect(models.Model):
    strain = models.ForeignKey(Strain, on_delete=models.SET_NULL)
    negative_effect = models.ForeignKey(NegativeEffect, on_delete=models.SET_NULL)
    negative_effect_value = models.IntegerField(_('Negative Effect Strength'), blank=False, null=False)


class Flavor(models.Model):
    NAMES = (
        ('ammonia', 'Ammonia'),
        ('apple', 'Apple'),
        ('apricot', 'Apricot'),
        ('berry', 'Berry'),
        ('blue-cheese', 'Blue Cheese'),
        ('blueberry', 'Blueberry'),
        ('buttery', 'Buttery'),
        ('cheese', 'Cheese'),
        ('chemical', 'Chemical'),
        ('chestnut', 'Chestnut'),
        ('citrus', 'Citrus'),
        ('coffee', 'Coffee'),
        ('diesel', 'Diesel'),
        ('earthy', 'Earthy'),
        ('flowery', 'Flowery'),
        ('grape', 'Grape'),
        ('grapefruit', 'Grapefruit'),
        ('herbal', 'Herbal'),
        ('honey', 'Honey'),
        ('lavender', 'Lavender'),
        ('lemon', 'Lemon'),
        ('lime', 'Lime'),
        ('mango', 'Mango'),
        ('menthol', 'Menthol'),
        ('minty', 'Minty'),
        ('nutty', 'Nutty'),
        ('orange', 'Orange'),
        ('peach', 'Peach'),
        ('pear', 'Pear'),
        ('pepper', 'Pepper'),
        ('pine', 'Pine'),
        ('pineapple', 'Pineapple'),
        ('plum', 'Plum'),
        ('pungent', 'Pungent'),
        ('rose', 'Rose'),
        ('sage', 'Sage'),
        ('skunk', 'Skunk'),
        ('spicy-herbal', 'Spicy/Herbal'),
        ('strawberry', 'Strawberry'),
        ('sweet', 'Sweet'),
        ('tar', 'Tar'),
        ('tea', 'Tea'),
        ('tobacco', 'Tobacco'),
        ('tree-fruit', 'Tree Fruit'),
        ('tropical', 'Tropical'),
        ('vanilla', 'Vanilla'),
        ('violet', 'Violet'),
        ('woody', 'Woody')
    )

    name = models.CharField(_('Name'), blank=False, null=False, max_length=30, choices=NAMES)


class StrainFlavor(models.Model):
    strain = models.ForeignKey(Strain, on_delete=models.SET_NULL)
    flavor = models.ForeignKey(Flavor, on_delete=models.SET_NULL)
    flavor_value = models.IntegerField(_('Flavor Strength'), blank=False, null=False)


class StrainReview(models.Model):
    strain = models.ForeignKey(Strain, on_delete=models.SET_NULL)
    rating = models.FloatField(_('Rating'), blank=False, null=False)
    comment = models.CharField(_('Comment'), blank=True, null=True, max_length=500)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(_('Created Date'), blank=False, null=False, default=datetime.now)
