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
    
            if (cannabinoid_min > 0 || cannabinoid_max < 100){
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
        if (params._source.variety == varietyArray[i]) {
            total += 20;
        }
    }

    if (params._source.containsKey("is_clean") && params._source.is_clean && params.containsKey("is_clean")){
        total += 40;
    }
    if (params._source.containsKey("is_indoor") && params._source.is_indoor && params.containsKey("is_indoor")){
        total += 15;
    }

    if (params._source.containsKey("cup_winner") && params._source.cup_winner && params.containsKey("cup_winner")){
        total += 10;
    }
    
    return total;
"""
