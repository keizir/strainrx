TYPES = {
    'strain': "strain",
    'strain_review': "strain_review"
}

strain_mapping = {
    "properties": {
        "id": {
            "type": "long",
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

strain_suggester_mapping = {
    "properties": {
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
        "name_suggest": {
            "type": "completion",
            "analyzer": "simple",
            "payloads": True
        }
    }
}

strain_review_mapping = {
    "_parent": {
        "type": TYPES.get('strain')
    },
    "properties": {
        "id": {
            "type": "long"
        },
        "rating": {
            "type": "float"
        },
        "review": {
            "type": "string"
        },
        "review_approved": {
            "type": "boolean"
        },
        "created_date": {
            "type": "date"
        },
        "created_by": {
            "type": "long"
        },
        "last_modified_date": {
            "type": "date"
        },
        "last_modified_by": {
            "type": "long"
        }
    }
}
