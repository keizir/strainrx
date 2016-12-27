'use strict';

W.ns('W.common');

W.common.Constants = {

    html: {
        loader: '<i class="fa fa-spinner fa-pulse" aria-hidden="true"></i>'
    },

    regex: {
        email: /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/,
        phone: /^[0-9]{3}-[0-9]{3}-[0-9]{4}$/,
        specialChar: /[~`!@#$%\^&*+=\-\[\]\\';,/{}|\\":<>\?]/,
        onlyNumeric: /^\d+$/,
        onlyAlpha: /^[a-zA-Z\s]+$/
    },

    masks: {
        phone: {
            mask: '000-000-0000',
            placeholder: '___-___-____'
        },
        time: {
            mask: '00:00',
            placeholder: 'hh:mm'
        }
    },

    days: [
        {name: 'Monday', value: 'mon'},
        {name: 'Tuesday', value: 'tue'},
        {name: 'Wednesday', value: 'wed'},
        {name: 'Thursday', value: 'thu'},
        {name: 'Friday', value: 'fri'},
        {name: 'Saturday', value: 'sat'},
        {name: 'Sunday', value: 'sun'}
    ],

    effectNames: {
        'happy': 'Happy',
        'uplifted': 'Uplifted',
        'stimulated': 'Stimulated',
        'energetic': 'Energetic',
        'creative': 'Creative',
        'focused': 'Focused',
        'relaxed': 'Relaxed',
        'sleepy': 'Sleepy',
        'talkative': 'Talkative',
        'euphoric': 'Euphoric',
        'hungry': 'Hungry',
        'tingly': 'Tingly',
        'good_humored': 'Good Humored'
    },

    benefitNames: {
        'reduce_stress': 'Reduce Stress',
        'help_depression': 'Help Depression',
        'relieve_pain': 'Relieve Pain',
        'reduce_fatigue': 'Reduce Fatigue',
        'reduce_headaches': 'Reduce Headaches',
        'help_muscles_spasms': 'Help Muscles Spasms',
        'lower_eye_pressure': 'Lower Eye Pressure',
        'reduce_nausea': 'Reduce Nausea',
        'reduce_inflammation': 'Reduce Inflammation',
        'relieve_cramps': 'Relieve Cramps',
        'help_with_seizures': 'Help With Seizures',
        'restore_appetite': 'Restore Appetite',
        'help_with_insomnia': 'Help With Insomnia'
    },

    sideEffectNames: {
        'anxiety': 'Anxiety',
        'dry_mouth': 'Dry Mouth',
        'paranoia': 'Paranoia',
        'headache': 'Headache',
        'dizziness': 'Dizziness',
        'dry_eyes': 'Dry Eyes'
    },

    flavors: {
        'ammonia': {
            name: 'Ammonia',
            image: 'images/flavors/lime2-512.png'
        },
        'apple': {
            name: 'Apple',
            image: 'images/flavors/apple-512.png'
        },
        'apricot': {
            name: 'Apricot',
            image: 'images/flavors/lime2-512.png'
        },
        'berry': {
            name: 'Berry',
            image: 'images/flavors/apple-512.png'
        },
        'blue_cheese': {
            name: 'Blue Cheese',
            image: 'images/flavors/lime2-512.png'
        },
        'blueberry': {
            name: 'Blueberry',
            image: 'images/flavors/apple-512.png'
        },
        'buttery': {
            name: 'Buttery',
            image: 'images/flavors/lime2-512.png'
        },
        'cheese': {
            name: 'Cheese',
            image: 'images/flavors/apple-512.png'
        },
        'chemical': {
            name: 'Chemical',
            image: 'images/flavors/lime2-512.png'
        },
        'chestnut': {
            name: 'Chestnut',
            image: 'images/flavors/apple-512.png'
        },
        'citrus': {
            name: 'Citrus',
            image: 'images/flavors/lime2-512.png'
        },
        'coffee': {
            name: 'Coffee',
            image: 'images/flavors/apple-512.png'
        },
        'diesel': {
            name: 'Diesel',
            image: 'images/flavors/lime2-512.png'
        },
        'earthy': {
            name: 'Earthy',
            image: 'images/flavors/apple-512.png'
        },
        'flowery': {
            name: 'Flowery',
            image: 'images/flavors/lime2-512.png'
        },
        'grape': {
            name: 'Grape',
            image: 'images/flavors/apple-512.png'
        },
        'grapefruit': {
            name: 'Grapefruit',
            image: 'images/flavors/lime2-512.png'
        },
        'herbal': {
            name: 'Herbal',
            image: 'images/flavors/apple-512.png'
        },
        'honey': {
            name: 'Honey',
            image: 'images/flavors/lime2-512.png'
        },
        'lavender': {
            name: 'Lavender',
            image: 'images/flavors/apple-512.png'
        },
        'lemon': {
            name: 'Lemon',
            image: 'images/flavors/lime2-512.png'
        },
        'lime': {
            name: 'Lime',
            image: 'images/flavors/apple-512.png'
        },
        'mango': {
            name: 'Mango',
            image: 'images/flavors/lime2-512.png'
        },
        'menthol': {
            name: 'Menthol',
            image: 'images/flavors/apple-512.png'
        },
        'minty': {
            name: 'Minty',
            image: 'images/flavors/lime2-512.png'
        },
        'nutty': {
            name: 'Nutty',
            image: 'images/flavors/apple-512.png'
        },
        'orange': {
            name: 'Orange',
            image: 'images/flavors/lime2-512.png'
        },
        'peach': {
            name: 'Peach',
            image: 'images/flavors/apple-512.png'
        },
        'pear': {
            name: 'Pear',
            image: 'images/flavors/lime2-512.png'
        },
        'pepper': {
            name: 'Pepper',
            image: 'images/flavors/apple-512.png'
        },
        'pine': {
            name: 'Pine',
            image: 'images/flavors/lime2-512.png'
        },
        'pineapple': {
            name: 'Pineapple',
            image: 'images/flavors/apple-512.png'
        },
        'plum': {
            name: 'Plum',
            image: 'images/flavors/lime2-512.png'
        },
        'pungent': {
            name: 'Pungent',
            image: 'images/flavors/apple-512.png'
        },
        'rose': {
            name: 'Rose',
            image: 'images/flavors/lime2-512.png'
        },
        'sage': {
            name: 'Sage',
            image: 'images/flavors/apple-512.png'
        },
        'skunk': {
            name: 'Skunk',
            image: 'images/flavors/lime2-512.png'
        },
        'spicy_herbal': {
            name: 'Spicy Herbal',
            image: 'images/flavors/apple-512.png'
        },
        'strawberry': {
            name: 'Strawberry',
            image: 'images/flavors/lime2-512.png'
        },
        'sweet': {
            name: 'Sweet',
            image: 'images/flavors/apple-512.png'
        },
        'tar': {
            name: 'Tar',
            image: 'images/flavors/lime2-512.png'
        },
        'tea': {
            name: 'Tea',
            image: 'images/flavors/apple-512.png'
        },
        'tobacco': {
            name: 'Tobacco',
            image: 'images/flavors/lime2-512.png'
        },
        'tree_fruit': {
            name: 'Tree Fruit',
            image: 'images/flavors/apple-512.png'
        },
        'tropical': {
            name: 'Tropical',
            image: 'images/flavors/lime2-512.png'
        },
        'vanilla': {
            name: 'Vanilla',
            image: 'images/flavors/apple-512.png'
        },
        'violet': {
            name: 'Violet',
            image: 'images/flavors/lime2-512.png'
        },
        'woody': {
            name: 'Woody',
            image: 'images/flavors/apple-512.png'
        }
    }

};
