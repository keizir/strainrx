MILE = 0.000621371

ADVANCED_SEARCH_SCORE = """
    def total = 0;
    def varietyArray = params["variety"] ?: [];
    def terpenesArray = params['terpenes'] ?: [];
    def cannabinoidsArray = params['cannabinoids'] ?: [];
    def terpenes = params._source.terpenes;
    def cannabinoids = params._source.cannabinoids;
    def cannabinoid_min = 0;
    def cannabinoid_max = 100;
    def delta = 0;
    def cannabinoid = 0;
    
    for (int i = 0; i < terpenesArray.length; ++i){
        if (params.containsKey(terpenesArray[i])){
            if (params[terpenesArray[i]] && terpenes != null && 
                terpenes.containsKey(terpenesArray[i]) && terpenes[terpenesArray[i]] > 0){
                    total += 20;
            }
        }
    }

    if (cannabinoids != null) {
        for (int i = 0; i < cannabinoidsArray.length; ++i){
            cannabinoid_min = 0;
            cannabinoid_max = 100;
            cannabinoid = cannabinoids[cannabinoidsArray[i]];
             
            if (params.containsKey(cannabinoidsArray[i] + '_from')){
                cannabinoid_min = params[cannabinoidsArray[i] + '_from'];
            }
            if (params.containsKey(cannabinoidsArray[i] + '_to')){
                cannabinoid_max = params[cannabinoidsArray[i] + '_to'];
            }
            if (cannabinoid_min >= 0 || cannabinoid_max <= 100){
                total += 100;
            
                if (cannabinoid > cannabinoid_max){
                    delta = cannabinoid - cannabinoid_max;
                } else {
                    delta = cannabinoid_min - cannabinoid;
                }
                         
                if (delta >= (float) (0.75 * cannabinoid)) {
                    total = (float) (total * 0.25);
                } else {
                    if (delta >= (float) (cannabinoid * 0.55)) {total = (float) (total * 0.50)} else {
                        if (delta >= (float) (cannabinoid * 0.20)) {total = (float) (total * 0.75)}
                    }
                }
            }
        }  
    }

    for (int i = 0; i < varietyArray.length; ++i){
        if (doc['variety'].value == varietyArray[i]) {
            total += 20;
        }
    }

    if (doc['cup_winner'].value && params.containsKey("cup_winner") && params.cup_winner){
        total += 10;
    }
    
    return total;
"""


def advanced_search_nested_location_filter(**kwargs):
    nested_filter = []
    if kwargs.get('is_indoor'):
        nested_filter.append({'term': {'locations.is_indoor': True}})
    if kwargs.get('is_clean'):
        nested_filter.append({'term': {'locations.is_clean': True}})
    return nested_filter


def advanced_search_sort(**kwargs):
    nested_filter = advanced_search_nested_location_filter(**kwargs)
    should_query = [
        {"script": {
            "script": {
                "inline": """
                    def delivery_radius = doc['locations.delivery_radius'].value ?: 0; 
                    return doc['locations.delivery'].value == true && delivery_radius >= 
                        doc['locations.location'].planeDistanceWithDefault(
                          params.lat, params.lon, 0) * {}
                    """.format(MILE),
                "lang": "painless",
                "params": {
                    "lat": kwargs.get('lat'),
                    "lon": kwargs.get('lon'),
                    'proximity': kwargs.get('proximity')
                }
            }
        }},
        {"bool": {
            "must": [
                {
                    "geo_distance": {
                        "distance": "{0}mi".format(kwargs.get('proximity')),
                        "distance_type": "plane",
                        "locations.location": {"lat": kwargs.get('lat'), "lon": kwargs.get('lon')}
                    }
                },
                {"match": {'locations.dispensary': True}}
            ]
        }}
    ]

    query = {
        "nested_path": "locations",
        'order': 'asc',
        "nested_filter": {
            'bool': {
                'must': nested_filter,
                "should": should_query,
                "minimum_should_match": '0<80%'
            }
        }
    }
    query.update(kwargs.get('subquery', {}))
    return query


"""
Groovy script unminified

Workflow:
    - use https://groovyconsole.appspot.com/ to validate script runs
    - minify via http://codebeautify.org/javaviewer (copy only part below comment below that is actual script)
    - paste minified version into script field in query_strain_srx_score

// TEMP for testing syntax

def effectSum = 20;
def benefitSum = 1;

def _source = [
    'effects': [
        'happy': 4.5,
        'relaxed': 4.0,
        'creative': 2.23,
        'talkative': 2.123,
        'energetic': 1.564,
        'sleepy': 3.23
    ],
    'side_effects': [
        'dry_mouth': 7.4
    ],
    'benefits': [
        'relieve_pain': 2.0
    ]
];

def userEffects = [
    'happy': 5,
    'relaxed': 5,
    'creative': 2,
    'talkative': 2,
    'energetic': 2,
    'sleepy': 5
];

def userBenefits = [
    'relieve_pain': 4
];

def userNegEffects = [
    'dry_mouth': 3
];


// actual script below here
//***********************************************************************

// points available
def psa = params.effectSum + params.benefitSum;

// calculate distance
def benefitPoints = 0.0f;
def effectPoints = 0.0f;
def negEffectPoints = 0.0f;

// calc all effect points awarded
for (e in params.userEffects.entrySet()) {
    def strainE = (float) params._source['effects'][e.getKey()];
    def userE = (float) e.getValue();
    def effectBonus = 0.0f;

    def dist = strainE - userE;
    def npe = 0.0f;
    if (dist > 0) {
        npe = -0.01f;
    } else {
        if (dist == 0) {
            npe = 0.0f;
        }

        if (dist < 0 && dist >= -1) {
            npe = -0.14f * userE;
        }

        if (dist < -1 && dist >= -2) {
            npe = -0.33f * userE;
        }

        if (dist < -2 && dist >= -3) {
            npe = -0.51f * userE;
        }

        if (dist < -3 && dist >= -4) {
            npe = -0.8f * userE;
        }

        if (dist < -4 && dist >= -5) {
            npe = -1.0f * userE;
        }
    }

    if (userE == strainE) {
        if (strainE == 3) {
            effectBonus = 0.3f;
        }

        if (strainE == 4) {
            effectBonus = 0.5f;
        }

        if (strainE == 5) {
            effectBonus = 1.0f;
        }
    }

    effectPoints += effectBonus + userE + npe;
}

// calc all benefit points awarded
for (b in params.userBenefits.entrySet()) {
    def strainB = (float) params._source['benefits'][b.getKey()];
    def userB = (float) b.getValue();
    def benefitBonus = 0.0f;

    def dist = strainB - userB;
    def npb = 0.0f;
    if (dist > 0) {
        npb = -0.01f;
    } else {
        if (dist == 0) {
            npb = 0.0f;
        }

        if (dist < 0 && dist >= -1) {
            npb = -0.14f * userB;
        }

        if (dist < -1 && dist >= -2) {
            npb = -0.33f * userB;
        }

        if (dist < -2 && dist >= -3) {
            npb = -0.51f * userB;
        }

        if (dist < -3 && dist >= -4) {
            npb = -0.8f * userB;
        }

        if (dist < -4 && dist >= -5) {
            npb = -1.0f * userB;
        }
    }

    if (userB == strainB) {
        if (strainB == 3) {
            benefitBonus = 0.3f;
        }

        if (strainB == 4) {
            benefitBonus = 0.5f;
        }

        if (strainB == 5) {
            benefitBonus = 1.0f;
        }
    }

    benefitPoints += benefitBonus + userB + npb;
}

for (ne in params.userNegEffects.entrySet()) {
    def strainNE = (float) params._source['side_effects'][ne.getKey()];
    def userNE = (float) ne.getValue();
    def negPoints = 0.0f;

    if (userNE == 0 || strainNE == 0) {
        negPoints = 0.0f;
    } else {
        negPoints = (float) ((Math.pow(userNE - strainNE, 2)) * -1) / (float) psa;
    }

    negEffectPoints += negPoints;
}

def tp = effectPoints + negEffectPoints + benefitPoints;
return ((float) tp / (float) psa) * 100;​
"""

SRX_RECOMMENDATION_SCORE = "def psa=params.effectSum+params.benefitSum;def benefitPoints=0.0f;def effectPoints=0.0f;def negEffectPoints=0.0f;for(e in params.userEffects.entrySet()){def strainE=(float)params._source['effects'][e.getKey()];def userE=(float)e.getValue();def effectBonus=0.0f;def dist=strainE-userE;def npe=0.0f;if(dist>0){npe=-0.01f;}else{if(dist==0){npe=0.0f;}if(dist<0&&dist>=-1){npe=-0.14f*userE;}if(dist<-1&&dist>=-2){npe=-0.33f*userE;}if(dist<-2&&dist>=-3){npe=-0.51f*userE;}if(dist<-3&&dist>=-4){npe=-0.8f*userE;}if(dist<-4&&dist>=-5){npe=-1.0f*userE;}}if(userE==strainE){if(strainE==3){effectBonus=0.3f;}if(strainE==4){effectBonus=0.5f;}if(strainE==5){effectBonus=1.0f;}}effectPoints+=effectBonus+userE+npe;}for(b in params.userBenefits.entrySet()){def strainB=(float)params._source['benefits'][b.getKey()];def userB=(float)b.getValue();def benefitBonus=0.0f;def dist=strainB-userB;def npb=0.0f;if(dist>0){npb=-0.01f;}else{if(dist==0){npb=0.0f;}if(dist<0&&dist>=-1){npb=-0.14f*userB;}if(dist<-1&&dist>=-2){npb=-0.33f*userB;}if(dist<-2&&dist>=-3){npb=-0.51f*userB;}if(dist<-3&&dist>=-4){npb=-0.8f*userB;}if(dist<-4&&dist>=-5){npb=-1.0f*userB;}}if(userB==strainB){if(strainB==3){benefitBonus=0.3f;}if(strainB==4){benefitBonus=0.5f;}if(strainB==5){benefitBonus=1.0f;}}benefitPoints+=benefitBonus+userB+npb;}for(ne in params.userNegEffects.entrySet()){def strainNE=(float)params._source['side_effects'][ne.getKey()];def userNE=(float)ne.getValue();def negPoints=0.0f;if(userNE==0||strainNE==0){negPoints=0.0f;}else{negPoints=(float)((Math.pow(userNE-strainNE,2))*-1)/(float)psa;}negEffectPoints+=negPoints;}def tp=effectPoints+negEffectPoints+benefitPoints;return((float)tp/(float)psa)*100;"

CHECK_DELIVERY_RADIUS = """
    def delivery_radius = doc['delivery_radius'].value ?: 0; 
    return doc['delivery'].value == true && delivery_radius >= 
        doc['location'].planeDistanceWithDefault(
          params.lat, params.lon, 0) * {}
    """.format(MILE)
