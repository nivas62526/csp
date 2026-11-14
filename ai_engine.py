"""
Smart Poultry Farm - AI/ML Decision Support Engine
Provides risk assessment and mathematical predictions for:
1. Disease Risk Prediction (Respiratory, Heat Stress, Enteritis/Coccidiosis)
2. Mortality Risk Estimator
3. Feed Requirement & FCR Prediction
"""

import math

def predict_disease_risk(age_days, temperature, humidity, ammonia_ppm, feed_drop_pct=0, water_change_pct=0, mortality_rate_pct=0, symptoms=""):
    """
    Evaluates environmental and biological signals to calculate disease risk level and potential issues.
    Risk Levels: LOW, MEDIUM, HIGH, CRITICAL
    """
    score = 0
    factors = []
    possible_conditions = []
    recommendations_en = []
    recommendations_te = []

    symptoms_lower = (symptoms or "").lower()

    # Temperature checks (Broiler comfort zone: ~32C day 1 down to ~20-22C by week 5)
    target_temp = max(21.0, 32.0 - (age_days * 0.3))
    temp_diff = abs(temperature - target_temp)

    if temperature > 33.0:
        score += 30
        factors.append(f"High shed temperature ({temperature}°C vs target {target_temp:.1f}°C)")
        possible_conditions.append("Heat Stress & Panting Exhaustion")
        recommendations_en.append("Turn on evaporative cooling pads and foggers immediately; ensure cold fresh water.")
        recommendations_te.append("వెంటనే కూలింగ్ ప్యాడ్లు, ఫాగర్లు ఆన్ చేయండి; చల్లని మంచి నీరు అందించండి.")
    elif temperature < 18.0 and age_days < 21:
        score += 25
        factors.append(f"Low temperature ({temperature}°C) for young birds")
        possible_conditions.append("Chilling / Hypothermia & Ascites Risk")
        recommendations_en.append("Increase brooder heating; check curtain management to prevent cold drafts.")
        recommendations_te.append("బ్రూడర్ వేడిని పెంచండి; చలి గాలులు తగలకుండా కర్టెన్లను సరిచూడండి.")

    # Humidity checks (Optimal 50% - 70%)
    if humidity > 75.0:
        score += 20
        factors.append(f"High humidity ({humidity}%) in shed")
        possible_conditions.append("Wet Litter & Coccidiosis / Enteritis")
        recommendations_en.append("Increase tunnel exhaust fans to reduce dampness; check drinker lines for leaks.")
        recommendations_te.append("తేమను తగ్గించడానికి ఎగ్జాస్ట్ ఫ్యాన్లను పెంచండి; నీటి పైపుల లీకేజీలను తనిఖీ చేయండి.")
    elif humidity < 40.0:
        score += 10
        factors.append("Low humidity causing excessive dust in shed air")

    # Ammonia / Gas checks (Safe: < 20 ppm; Dangerous: > 25 ppm)
    if ammonia_ppm > 25.0:
        score += 35
        factors.append(f"Hazardous ammonia gas level ({ammonia_ppm} ppm)")
        possible_conditions.append("Severe Respiratory Infection (CRD / Infectious Bronchitis)")
        recommendations_en.append("Urgent: Flush air through maximum ventilation; rake or replace wet litter.")
        recommendations_te.append("అత్యవసరం: వెంటిలేషన్ పెంచండి; తడి చెత్తను తవ్వి ఎండబెట్టండి లేదా మార్చండి.")
    elif ammonia_ppm > 15.0:
        score += 15
        factors.append(f"Elevated ammonia level ({ammonia_ppm} ppm)")
        possible_conditions.append("Mild tracheal irritation")

    # Feed / Water drop detection
    if feed_drop_pct >= 15.0:
        score += 25
        factors.append(f"Sudden feed intake drop of {feed_drop_pct:.1f}%")
        possible_conditions.append("Systemic Infection or Toxic Feed / Mycotoxins")
        recommendations_en.append("Inspect feed quality, smell and texture; add liver tonic or toxin binder in water.")
        recommendations_te.append("మేత నాణ్యతను తనిఖీ చేయండి; తాగునీటిలో లివర్ టానిక్ లేదా టాక్సిన్ బైండర్ కలపండి.")

    if water_change_pct >= 20.0:
        score += 20
        factors.append(f"Abnormal water consumption deviation ({water_change_pct:.1f}%)")

    # Mortality spike
    if mortality_rate_pct >= 0.5:
        score += 40
        factors.append(f"Alarming daily mortality rate ({mortality_rate_pct:.2f}%)")
        recommendations_en.append("Isolate sick birds immediately; contact registered veterinarian for post-mortem.")
        recommendations_te.append("జబ్బుపడిన కోళ్లను వేరు చేయండి; వెంటనే పశువైద్యుడిని సంప్రదించండి.")
    elif mortality_rate_pct >= 0.2:
        score += 20
        factors.append(f"Elevated daily mortality ({mortality_rate_pct:.2f}%)")

    # Symptom NLP keywords
    if any(k in symptoms_lower for k in ["cough", "gasp", "sneez", "rattle", "swollen", "రొంప", "దగ్గు"]):
        score += 35
        possible_conditions.append("Infectious Bronchitis / Ranikhet (Newcastle) / CRD")
        recommendations_en.append("Administer respiratory herbal decongestants; review Newcastle vaccine history.")
        recommendations_te.append("శ్వాసకోశ మందులు అందించండి; రాణీఖేత్ వ్యాక్సిన్ వివరాలు పరిశీలించండి.")

    if any(k in symptoms_lower for k in ["diarrhea", "blood", "white droppings", "loose", "విరేచనాలు", "రక్తం"]):
        score += 35
        possible_conditions.append("Coccidiosis / Bacillary White Diarrhea (Pullorum)")
        recommendations_en.append("Administer anti-coccidial or gut antibiotic under veterinary direction.")
        recommendations_te.append("వైద్యుని సూచన మేరకు కాక్సిడియోసిస్ నివారణ మందులు ఇవ్వండి.")

    if any(k in symptoms_lower for k in ["paralysis", "neck twist", "leg weakness", "కుంటి"]):
        score += 30
        possible_conditions.append("Marek's Disease or Vitamin B/E Nutritional Deficiency")

    # Classification
    if score >= 60:
        risk_level = "CRITICAL"
        risk_level_te = "తీవ్రమైన ప్రమాదం (CRITICAL)"
        badge_color = "red"
    elif score >= 40:
        risk_level = "HIGH"
        risk_level_te = "అధిక ప్రమాదం (HIGH)"
        badge_color = "orange"
    elif score >= 20:
        risk_level = "MEDIUM"
        risk_level_te = "మధ్యస్థ ప్రమాదం (MEDIUM)"
        badge_color = "yellow"
    else:
        risk_level = "LOW"
        risk_level_te = "తక్కువ ప్రమాదం - సాధారణం (LOW)"
        badge_color = "green"
        if not possible_conditions:
            possible_conditions.append("Flock operating under standard health parameters")
        if not recommendations_en:
            recommendations_en.append("Maintain strict bio-security, fresh drinker water sanitation, and balanced feed.")
            recommendations_te.append("పరిశుభ్రత, స్వచ్ఛమైన తాగునీరు, సమతుల్య మేత నిర్వహణను కొనసాగించండి.")

    return {
        "score": min(score, 100),
        "risk_level": risk_level,
        "risk_level_te": risk_level_te,
        "badge_color": badge_color,
        "possible_conditions": list(set(possible_conditions)),
        "risk_factors": factors,
        "recommendations_en": recommendations_en,
        "recommendations_te": recommendations_te
    }

def predict_feed_requirement(breed, age_days, bird_count):
    """
    Standard poultry daily feed intake calculation based on standard broiler (Cobb/Ross) growth curves.
    Returns:
    - daily_feed_per_bird_grams
    - total_daily_feed_kg
    - next_7_days_feed_kg
    """
    if bird_count <= 0:
        return {"per_bird_grams": 0, "daily_kg": 0, "weekly_kg": 0}

    # Standard Broiler daily intake curve (grams/day)
    # Week 1 (1-7): 15-30g
    # Week 2 (8-14): 35-55g
    # Week 3 (15-21): 65-95g
    # Week 4 (22-28): 105-135g
    # Week 5 (29-35): 145-175g
    # Week 6 (36-42): 180-210g
    if age_days <= 7:
        grams_per_bird = 12 + (age_days * 2.5)
    elif age_days <= 14:
        grams_per_bird = 30 + ((age_days - 7) * 3.5)
    elif age_days <= 21:
        grams_per_bird = 55 + ((age_days - 14) * 5.0)
    elif age_days <= 28:
        grams_per_bird = 90 + ((age_days - 21) * 6.5)
    elif age_days <= 35:
        grams_per_bird = 135 + ((age_days - 28) * 6.0)
    else:
        grams_per_bird = min(220.0, 175 + ((age_days - 35) * 5.0))

    if "layer" in breed.lower():
        # Layer birds stabilize around 110-120g during peak lay
        grams_per_bird = min(115.0, grams_per_bird * 0.75)
    elif "country" in breed.lower() or "desi" in breed.lower():
        # Desi breeds consume ~40-60% of commercial broiler intake
        grams_per_bird = grams_per_bird * 0.55

    daily_kg = (grams_per_bird * bird_count) / 1000.0
    weekly_kg = daily_kg * 7.0

    return {
        "per_bird_grams": round(grams_per_bird, 1),
        "daily_kg": round(daily_kg, 2),
        "weekly_kg": round(weekly_kg, 2)
    }

def calculate_fcr(total_feed_consumed_kg, total_live_weight_kg):
    """
    FCR = Total Feed Consumed (kg) / Total Live Weight (kg)
    Industry benchmarks: Broiler: 1.45 - 1.75 is good.
    """
    if total_live_weight_kg <= 0:
        return 0.0
    return round(total_feed_consumed_kg / total_live_weight_kg, 2)

def predict_age_requirements(breed="Broiler (Cobb 500)", age_days=21, bird_count=1000):
    """
    Predicts required daily food quantity, water volume, and optimal shed temperature
    based on hen age in days and flock size.
    Bilingual output (English and Telugu).
    """
    age = max(1, int(age_days))
    count = max(1, int(bird_count))
    breed_lower = (breed or "").lower()

    # Determine growth stage and feed stage
    if age <= 10:
        stage = "Brooding / Starter"
        stage_te = "బ్రూడింగ్ / స్టార్టర్"
        feed_stage = "Pre-Starter Crumbles"
        feed_stage_te = "ప్రీ-స్టార్టర్ రవ్వ"
    elif age <= 24:
        stage = "Grower Stage"
        stage_te = "గ్రోవర్ దశ"
        feed_stage = "Broiler Starter / Grower Pellets"
        feed_stage_te = "స్టార్టర్ / గ్రోవర్ పెల్లెట్స్"
    elif age <= 38:
        stage = "Finisher Stage"
        stage_te = "ఫినిషర్ దశ"
        feed_stage = "Finisher Feed (High Energy)"
        feed_stage_te = "ఫినిషర్ మేత"
    else:
        stage = "Market / Harvest Ready"
        stage_te = "మార్కెట్ / కోతకు సిద్ధం"
        feed_stage = "Market Finisher / Withdrawal Feed"
        feed_stage_te = "మార్కెట్ మేత"

    # Feed intake curve (grams/bird/day)
    if age <= 7:
        feed_per_bird_g = 12.0 + (age * 2.8)
    elif age <= 14:
        feed_per_bird_g = 32.0 + ((age - 7) * 3.8)
    elif age <= 21:
        feed_per_bird_g = 59.0 + ((age - 14) * 5.2)
    elif age <= 28:
        feed_per_bird_g = 95.0 + ((age - 21) * 6.5)
    elif age <= 35:
        feed_per_bird_g = 140.0 + ((age - 28) * 6.2)
    elif age <= 42:
        feed_per_bird_g = 183.0 + ((age - 35) * 4.8)
    else:
        feed_per_bird_g = min(225.0, 215.0 + ((age - 42) * 2.0))

    if "layer" in breed_lower:
        feed_per_bird_g = min(115.0, feed_per_bird_g * 0.72)
        feed_stage = "Layer Phase Mash"
        feed_stage_te = "లేయర్ మేత"
    elif "country" in breed_lower or "desi" in breed_lower:
        feed_per_bird_g = feed_per_bird_g * 0.58

    daily_flock_feed_kg = round((feed_per_bird_g * count) / 1000.0, 1)
    daily_feed_bags = round(daily_flock_feed_kg / 50.0, 1)

    # Water intake calculation (water-to-feed ratio is 1.8x to 2.2x under normal temp)
    if age <= 7:
        water_ratio = 2.2
    elif age <= 21:
        water_ratio = 2.0
    else:
        water_ratio = 1.9

    water_per_bird_ml = round(feed_per_bird_g * water_ratio, 1)
    daily_flock_water_l = round((water_per_bird_ml * count) / 1000.0, 1)

    # Optimal Temperature Curve (Starts at 32-34C for Day 1 chicks down to 20-22C by Day 35)
    if age <= 3:
        target_temp_c = 33.5
        min_temp_c = 32.0
        max_temp_c = 34.5
        brooding_status = "Active Brooding (Chicks)"
        brooding_status_te = "యాక్టివ్ బ్రూడింగ్ (పిల్లలు)"
        ventilation_advice = "Maintain heating hovers; minimize cold drafts while ensuring minimum air exchange."
        ventilation_advice_te = "బ్రూడర్ వేడిని కాపాడండి; చలి గాలులు తగలకుండా కర్టెన్లు మూయండి."
    elif age <= 7:
        target_temp_c = 31.5
        min_temp_c = 30.0
        max_temp_c = 32.5
        brooding_status = "Week 1 Brooding"
        brooding_status_te = "వారం 1 బ్రూడింగ్"
        ventilation_advice = "Gradually reduce brooder heat; monitor chick dispersion under heat lamps."
        ventilation_advice_te = "క్రమంగా బ్రూడర్ వేడిని తగ్గించండి; పిల్లల విస్తరణను గమనించండి."
    elif age <= 14:
        target_temp_c = 28.5
        min_temp_c = 27.0
        max_temp_c = 29.5
        brooding_status = "Transition Brooding"
        brooding_status_te = "పరివర్తన బ్రూడింగ్"
        ventilation_advice = "Begin cross-ventilation; remove brooder guards; maintain clean litter bedding."
        ventilation_advice_te = "క్రాస్-వెంటిలేషన్ ప్రారంభించండి; బెడ్డింగ్ పొడిగా ఉంచండి."
    elif age <= 21:
        target_temp_c = 26.0
        min_temp_c = 24.5
        max_temp_c = 27.5
        brooding_status = "Grower Comfort Zone"
        brooding_status_te = "గ్రోవర్ సౌకర్యవంతమైన ఉష్ణోగ్రత"
        ventilation_advice = "Maintain active tunnel or natural ventilation; ensure cool drinking water."
        ventilation_advice_te = "ఎగ్జాస్ట్ ఫ్యాన్లు నడపండి; తాజా నీటిని నిరంతరం అందించండి."
    elif age <= 28:
        target_temp_c = 23.5
        min_temp_c = 22.0
        max_temp_c = 25.0
        brooding_status = "Finisher Comfort Zone"
        brooding_status_te = "ఫినిషర్ సౌకర్య ఉష్ణోగ్రత"
        ventilation_advice = "Run tunnel fans to prevent heat accumulation; check ammonia levels."
        ventilation_advice_te = "హీట్ స్ట్రెస్ రాకుండా ఫ్యాన్లు వేయండి; అమ్మోనియా వాసన లేకుండా చూడండి."
    else:
        target_temp_c = 21.5
        min_temp_c = 20.0
        max_temp_c = 23.0
        brooding_status = "Market Weight Thermal Zone"
        brooding_status_te = "మార్కెట్ బరువు ఉష్ణోగ్రత"
        ventilation_advice = "Maximum air velocity required; prevent heat stress panting in heavy birds."
        ventilation_advice_te = "గరిష్ట గాలి ప్రసరణ అవసరం; బరువైన కోళ్లకు ఆయాసం రాకుండా చూడండి."

    target_temp_f = round((target_temp_c * 9.0 / 5.0) + 32.0, 1)

    return {
        "age_days": age,
        "week": math.ceil(age / 7.0),
        "bird_count": count,
        "breed": breed,
        "growth_stage": stage,
        "growth_stage_te": stage_te,
        "feed": {
            "per_bird_grams": round(feed_per_bird_g, 1),
            "daily_flock_kg": daily_flock_feed_kg,
            "weekly_flock_kg": round(daily_flock_feed_kg * 7.0, 1),
            "daily_bags_50kg": daily_feed_bags,
            "feed_stage": feed_stage,
            "feed_stage_te": feed_stage_te
        },
        "water": {
            "per_bird_ml": water_per_bird_ml,
            "daily_flock_liters": daily_flock_water_l,
            "weekly_flock_liters": round(daily_flock_water_l * 7.0, 1),
            "ratio_to_feed": water_ratio
        },
        "temperature": {
            "target_c": target_temp_c,
            "target_f": target_temp_f,
            "min_comfort_c": min_temp_c,
            "max_comfort_c": max_temp_c,
            "brooding_status": brooding_status,
            "brooding_status_te": brooding_status_te,
            "ventilation_advice": ventilation_advice,
            "ventilation_advice_te": ventilation_advice_te
        },
        "safety_precautions": [
            f"Ensure drinking water temperature does not exceed 25°C at age {age} days.",
            f"Clean and flush water lines twice daily to eliminate bacterial biofilm.",
            f"Target shed temperature of {target_temp_c}°C ({target_temp_f}°F) must be monitored with digital sensors at bird head height."
        ],
        "safety_precautions_te": [
            f"{age} రోజుల వయస్సులో తాగునీటి ఉష్ణోగ్రత 25°C మించకుండా చూసుకోండి.",
            "రోజుకు రెండుసార్లు నీటి పైపులను ఫ్లష్ చేయండి.",
            f"షెడ్ ఉష్ణోగ్రత {target_temp_c}°C ఉండేలా డిజిటల్ మీటర్లతో నిరంతరం పర్యవేక్షించండి."
        ]
    }
