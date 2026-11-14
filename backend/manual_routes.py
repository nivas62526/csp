"""
Smart Farm Fertilizer & Nutrient Management Engine
File: backend/manual_routes.py

Provides scientific N-P-K recommendation curves, commercial fertilizer calculation,
soil fertility calibration, split dose scheduling, and cost estimation.
Standards: ICAR, CRIDA, and State Agricultural University recommendations.
"""

from flask import Blueprint, request, jsonify
import math

manual_bp = Blueprint('manual_routes', __name__, url_prefix='/api/fertilizer')

# Standard Crop Nutrient Recommendations (kg per acre baseline)
# Format: { 'name_en': ..., 'name_te': ..., 'duration_days': ..., 'npk_per_acre': (N, P2O5, K2O) }
CROP_DATABASE = {
    'paddy': {
        'id': 'paddy',
        'name_en': 'Paddy / Rice',
        'name_te': 'వరి (Paddy)',
        'category': 'Cereals',
        'duration_days': 120,
        'n': 48.0,      # kg/acre
        'p': 24.0,      # kg/acre
        'k': 20.0,      # kg/acre
        'fym_tons_per_acre': 4.0,
        'splits': [
            {'stage_en': 'Basal (At Sowing / Transplanting)', 'stage_te': 'విత్తే / నాటు వేసే సమయంలో (బాసల్)', 'n_pct': 33, 'p_pct': 100, 'k_pct': 50},
            {'stage_en': 'Tillering Stage (20-25 DAT)', 'stage_te': 'పిలకల దశ (20-25 రోజులప్పుడు)', 'n_pct': 33, 'p_pct': 0, 'k_pct': 0},
            {'stage_en': 'Panicle Initiation (40-45 DAT)', 'stage_te': 'చిరుపొట్ట / పూత దశ (40-45 రోజులప్పుడు)', 'n_pct': 34, 'p_pct': 0, 'k_pct': 50}
        ]
    },
    'cotton': {
        'id': 'cotton',
        'name_en': 'Cotton',
        'name_te': 'పత్తి (Cotton)',
        'category': 'Cash Crops',
        'duration_days': 160,
        'n': 60.0,
        'p': 24.0,
        'k': 24.0,
        'fym_tons_per_acre': 5.0,
        'splits': [
            {'stage_en': 'Basal (Sowing)', 'stage_te': 'విత్తే సమయంలో (బాసల్)', 'n_pct': 20, 'p_pct': 100, 'k_pct': 50},
            {'stage_en': 'Vegetative Stage (30-35 DAS)', 'stage_te': 'ఎదుగుదల దశ (30-35 రోజులప్పుడు)', 'n_pct': 40, 'p_pct': 0, 'k_pct': 0},
            {'stage_en': 'Squaring & Flowering (60-70 DAS)', 'stage_te': 'పూత & కాత దశ (60-70 రోజులప్పుడు)', 'n_pct': 40, 'p_pct': 0, 'k_pct': 50}
        ]
    },
    'maize': {
        'id': 'maize',
        'name_en': 'Maize / Corn',
        'name_te': 'మొక్కజొన్న (Maize)',
        'category': 'Cereals',
        'duration_days': 110,
        'n': 48.0,
        'p': 24.0,
        'k': 16.0,
        'fym_tons_per_acre': 4.0,
        'splits': [
            {'stage_en': 'Basal (At Sowing)', 'stage_te': 'విత్తే సమయంలో (బాసల్)', 'n_pct': 25, 'p_pct': 100, 'k_pct': 50},
            {'stage_en': 'Knee-High Stage (25-30 DAS)', 'stage_te': 'మోకాలి ఎత్తు దశ (25-30 రోజులప్పుడు)', 'n_pct': 50, 'p_pct': 0, 'k_pct': 0},
            {'stage_en': 'Tasseling / Silking (50-55 DAS)', 'stage_te': 'కంకి / పూత దశ (50-55 రోజులప్పుడు)', 'n_pct': 25, 'p_pct': 0, 'k_pct': 50}
        ]
    },
    'chillies': {
        'id': 'chillies',
        'name_en': 'Chillies',
        'name_te': 'మిర్చి (Chillies)',
        'category': 'Spices / Vegetables',
        'duration_days': 150,
        'n': 60.0,
        'p': 24.0,
        'k': 24.0,
        'fym_tons_per_acre': 6.0,
        'splits': [
            {'stage_en': 'Basal (Transplanting)', 'stage_te': 'నాటు వేసే సమయంలో', 'n_pct': 25, 'p_pct': 100, 'k_pct': 33},
            {'stage_en': 'Branching (30-35 DAT)', 'stage_te': 'కొమ్మల దశ (30-35 రోజులు)', 'n_pct': 25, 'p_pct': 0, 'k_pct': 33},
            {'stage_en': 'Flowering (60 DAT)', 'stage_te': 'పూత దశ (60 రోజులు)', 'n_pct': 25, 'p_pct': 0, 'k_pct': 34},
            {'stage_en': 'Fruit Development (80-90 DAT)', 'stage_te': 'కాయ ఎదుగుదల దశ (80-90 రోజులు)', 'n_pct': 25, 'p_pct': 0, 'k_pct': 0}
        ]
    },
    'groundnut': {
        'id': 'groundnut',
        'name_en': 'Groundnut / Peanut',
        'name_te': 'వేరుశనగ (Groundnut)',
        'category': 'Oilseeds',
        'duration_days': 105,
        'n': 12.0,      # Legume: fixes own nitrogen
        'p': 20.0,
        'k': 16.0,
        'fym_tons_per_acre': 3.0,
        'splits': [
            {'stage_en': 'Basal (At Sowing)', 'stage_te': 'విత్తే సమయంలో (బాసల్)', 'n_pct': 100, 'p_pct': 100, 'k_pct': 100}
        ]
    },
    'sugarcane': {
        'id': 'sugarcane',
        'name_en': 'Sugarcane',
        'name_te': 'చెరకు (Sugarcane)',
        'category': 'Cash Crops',
        'duration_days': 330,
        'n': 100.0,
        'p': 40.0,
        'k': 48.0,
        'fym_tons_per_acre': 10.0,
        'splits': [
            {'stage_en': 'Basal (At Planting)', 'stage_te': 'నాటు వేసే సమయంలో', 'n_pct': 15, 'p_pct': 100, 'k_pct': 30},
            {'stage_en': 'Tillering (45 DAP)', 'stage_te': 'పిలకల దశ (45 రోజులు)', 'n_pct': 35, 'p_pct': 0, 'k_pct': 35},
            {'stage_en': 'Grand Growth (90 DAP)', 'stage_te': 'వృద్ధి దశ (90 రోజులు)', 'n_pct': 35, 'p_pct': 0, 'k_pct': 35},
            {'stage_en': 'Final Dressing (120 DAP)', 'stage_te': 'చివరి మోతాదు (120 రోజులు)', 'n_pct': 15, 'p_pct': 0, 'k_pct': 0}
        ]
    },
    'tomato': {
        'id': 'tomato',
        'name_en': 'Tomato',
        'name_te': 'టమాటా (Tomato)',
        'category': 'Vegetables',
        'duration_days': 100,
        'n': 48.0,
        'p': 32.0,
        'k': 32.0,
        'fym_tons_per_acre': 6.0,
        'splits': [
            {'stage_en': 'Basal (Transplanting)', 'stage_te': 'నాటు వేసే సమయంలో', 'n_pct': 33, 'p_pct': 100, 'k_pct': 33},
            {'stage_en': 'Vegetative (25 DAT)', 'stage_te': 'ఎదుగుదల దశ (25 రోజులు)', 'n_pct': 33, 'p_pct': 0, 'k_pct': 33},
            {'stage_en': 'Fruit Set (45 DAT)', 'stage_te': 'కాయ కట్టే దశ (45 రోజులు)', 'n_pct': 34, 'p_pct': 0, 'k_pct': 34}
        ]
    },
    'wheat': {
        'id': 'wheat',
        'name_en': 'Wheat',
        'name_te': 'గోధుమ (Wheat)',
        'category': 'Cereals',
        'duration_days': 120,
        'n': 48.0,
        'p': 24.0,
        'k': 16.0,
        'fym_tons_per_acre': 4.0,
        'splits': [
            {'stage_en': 'Basal (At Sowing)', 'stage_te': 'విత్తే సమయంలో (బాసల్)', 'n_pct': 50, 'p_pct': 100, 'k_pct': 100},
            {'stage_en': 'Crown Root Initiation (21 DAS)', 'stage_te': 'మొదటి నీటి తడి (21 రోజులప్పుడు)', 'n_pct': 50, 'p_pct': 0, 'k_pct': 0}
        ]
    }
}

# Commercial Fertilizer Compositions (% Nutrient) & Approx Indian Market Prices (per 50kg bag)
FERTILIZERS = {
    'urea': {'name_en': 'Urea', 'name_te': 'యూరియా', 'n': 46.0, 'p': 0.0, 'k': 0.0, 'bag_kg': 50, 'price_per_bag': 266.0},
    'dap': {'name_en': 'DAP (Diammonium Phosphate)', 'name_te': 'డి.ఎ.పి (DAP)', 'n': 18.0, 'p': 46.0, 'k': 0.0, 'bag_kg': 50, 'price_per_bag': 1350.0},
    'mop': {'name_en': 'MOP (Potash)', 'name_te': 'పొటాష్ (MOP)', 'n': 0.0, 'p': 0.0, 'k': 60.0, 'bag_kg': 50, 'price_per_bag': 1650.0},
    'ssp': {'name_en': 'SSP (Single Super Phosphate)', 'name_te': 'సింగిల్ సూపర్ ఫాస్ఫేట్ (SSP)', 'n': 0.0, 'p': 16.0, 'k': 0.0, 'bag_kg': 50, 'price_per_bag': 450.0},
    'complex_10_26_26': {'name_en': 'NPK 10-26-26 (Gromor)', 'name_te': '10-26-26 కాంప్లెక్స్ ఎరువు', 'n': 10.0, 'p': 26.0, 'k': 26.0, 'bag_kg': 50, 'price_per_bag': 1450.0},
    'complex_20_20_0_13': {'name_en': 'NPK 20-20-0-13 (Ammonium Phosphate Sulphate)', 'name_te': '20-20-0-13 కాంప్లెక్స్ ఎరువు', 'n': 20.0, 'p': 20.0, 'k': 0.0, 'bag_kg': 50, 'price_per_bag': 1300.0}
}


@manual_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Fertilizer Recommendation API',
        'supported_crops': len(CROP_DATABASE)
    }), 200


@manual_bp.route('/crops', methods=['GET'])
def get_supported_crops():
    """Returns all supported crops with localized labels and metadata."""
    crops_list = [
        {
            'id': c['id'],
            'name_en': c['name_en'],
            'name_te': c['name_te'],
            'category': c['category'],
            'duration_days': c['duration_days'],
            'recommended_npk': f"{c['n']}-{c['p']}-{c['k']} kg/acre"
        }
        for c in CROP_DATABASE.values()
    ]
    return jsonify({'status': 'success', 'crops': crops_list}), 200


@manual_bp.route('/fertilizers', methods=['GET'])
def get_fertilizers_list():
    """Returns commercial fertilizer nutrient percentages and market benchmarks."""
    return jsonify({'status': 'success', 'fertilizers': FERTILIZERS}), 200


@manual_bp.route('/calculate', methods=['POST'])
def calculate_fertilizer():
    """
    Core fertilizer calculation endpoint.
    Payload:
    {
        "crop": "paddy",
        "area": 2.5,
        "unit": "acres",            // "acres" or "hectares" or "guntas"
        "soil_n": "medium",         // "low", "medium", "high"
        "soil_p": "medium",
        "soil_k": "medium",
        "fertilizer_plan": "dap"    // "dap" (Urea+DAP+MOP) or "ssp" (Urea+SSP+MOP) or "complex" (10-26-26)
    }
    """
    data = request.get_json() or {}

    crop_key = data.get('crop', 'paddy').lower().strip()
    if crop_key not in CROP_DATABASE:
        return jsonify({
            'status': 'error',
            'message': f"Unsupported crop '{crop_key}'. Supported crops: {list(CROP_DATABASE.keys())}"
        }), 400

    crop = CROP_DATABASE[crop_key]

    # Convert Area to Acres
    raw_area = float(data.get('area', 1.0) or 1.0)
    unit = data.get('unit', 'acres').lower()

    if unit in ['ha', 'hectare', 'hectares']:
        acres = raw_area * 2.47105
    elif unit in ['gunta', 'guntas']:
        acres = raw_area / 40.0
    else:
        acres = raw_area

    if acres <= 0:
        return jsonify({'status': 'error', 'message': 'Land area must be greater than zero'}), 400

    # Soil Fertility Adjustment Multipliers
    # Low: +25% requirement, Medium: 100% baseline, High: -25% requirement
    def get_soil_factor(level):
        lvl = str(level).lower().strip()
        if lvl == 'low':
            return 1.25
        elif lvl == 'high':
            return 0.75
        return 1.0

    factor_n = get_soil_factor(data.get('soil_n', 'medium'))
    factor_p = get_soil_factor(data.get('soil_p', 'medium'))
    factor_k = get_soil_factor(data.get('soil_k', 'medium'))

    # Calculate Total Field Nutrient Requirements (in kg)
    total_req_n = round(crop['n'] * acres * factor_n, 1)
    total_req_p = round(crop['p'] * acres * factor_p, 1)
    total_req_k = round(crop['k'] * acres * factor_k, 1)

    fertilizer_plan = data.get('fertilizer_plan', 'dap').lower()
    commercial_bags = []
    total_estimated_cost = 0.0

    # --- PLAN A: Standard Urea + DAP + MOP ---
    if fertilizer_plan == 'dap' or fertilizer_plan not in ['ssp', 'complex']:
        # 1. P fulfilled by DAP (46% P2O5, 18% N)
        dap_kg_needed = (total_req_p / 0.46) if total_req_p > 0 else 0
        dap_bags = round(dap_kg_needed / 50.0, 1)
        dap_n_provided = dap_kg_needed * 0.18
        dap_cost = round(dap_bags * FERTILIZERS['dap']['price_per_bag'], 2)
        total_estimated_cost += dap_cost

        commercial_bags.append({
            'fertilizer_id': 'dap',
            'name_en': 'DAP (Diammonium Phosphate)',
            'name_te': 'డి.ఎ.పి (DAP)',
            'purpose_en': 'Supplies full Phosphorus + partial Nitrogen',
            'purpose_te': 'భాస్వరం మరియు కొంత మోతాదు నత్రజని అందిస్తుంది',
            'quantity_kg': round(dap_kg_needed, 1),
            'bags_50kg': dap_bags,
            'approx_cost_inr': dap_cost,
            'n_provided_kg': round(dap_n_provided, 1),
            'p_provided_kg': total_req_p,
            'k_provided_kg': 0.0
        })

        # 2. Remaining N fulfilled by Urea (46% N)
        remaining_n = max(0.0, total_req_n - dap_n_provided)
        urea_kg_needed = (remaining_n / 0.46) if remaining_n > 0 else 0
        urea_bags = round(urea_kg_needed / 50.0, 1)
        urea_cost = round(urea_bags * FERTILIZERS['urea']['price_per_bag'], 2)
        total_estimated_cost += urea_cost

        commercial_bags.append({
            'fertilizer_id': 'urea',
            'name_en': 'Urea',
            'name_te': 'యూరియా (Urea)',
            'purpose_en': 'Supplies remaining Nitrogen for leaf & vegetative growth',
            'purpose_te': 'పచ్చదనం, ఆకుల ఎదుగుదలకు అవసరమైన మిగిలిన నత్రజని',
            'quantity_kg': round(urea_kg_needed, 1),
            'bags_50kg': urea_bags,
            'approx_cost_inr': urea_cost,
            'n_provided_kg': round(remaining_n, 1),
            'p_provided_kg': 0.0,
            'k_provided_kg': 0.0
        })

        # 3. K fulfilled by MOP (60% K2O)
        mop_kg_needed = (total_req_k / 0.60) if total_req_k > 0 else 0
        mop_bags = round(mop_kg_needed / 50.0, 1)
        mop_cost = round(mop_bags * FERTILIZERS['mop']['price_per_bag'], 2)
        total_estimated_cost += mop_cost

        commercial_bags.append({
            'fertilizer_id': 'mop',
            'name_en': 'MOP (Muriate of Potash)',
            'name_te': 'పొటాష్ (MOP)',
            'purpose_en': 'Supplies Potassium for disease resistance & grain filling',
            'purpose_te': 'రోగనిరోధక శక్తి, గింజ నాణ్యత, దిగుబడి కోసం పొటాష్',
            'quantity_kg': round(mop_kg_needed, 1),
            'bags_50kg': mop_bags,
            'approx_cost_inr': mop_cost,
            'n_provided_kg': 0.0,
            'p_provided_kg': 0.0,
            'k_provided_kg': total_req_k
        })

    # --- PLAN B: Urea + SSP (Single Super Phosphate) + MOP ---
    elif fertilizer_plan == 'ssp':
        # SSP provides 16% P2O5 and 11-12% Sulphur (great for oilseeds / groundnut / pulses)
        ssp_kg_needed = (total_req_p / 0.16) if total_req_p > 0 else 0
        ssp_bags = round(ssp_kg_needed / 50.0, 1)
        ssp_cost = round(ssp_bags * FERTILIZERS['ssp']['price_per_bag'], 2)
        total_estimated_cost += ssp_cost

        commercial_bags.append({
            'fertilizer_id': 'ssp',
            'name_en': 'SSP (Single Super Phosphate)',
            'name_te': 'సింగిల్ సూపర్ ఫాస్ఫేట్ (SSP)',
            'purpose_en': 'Supplies Phosphorus + essential Sulphur (11%)',
            'purpose_te': 'భాస్వరం మరియు 11% సల్ఫర్ (గంధకం) అందిస్తుంది',
            'quantity_kg': round(ssp_kg_needed, 1),
            'bags_50kg': ssp_bags,
            'approx_cost_inr': ssp_cost,
            'n_provided_kg': 0.0,
            'p_provided_kg': total_req_p,
            'k_provided_kg': 0.0
        })

        # All N from Urea
        urea_kg_needed = (total_req_n / 0.46) if total_req_n > 0 else 0
        urea_bags = round(urea_kg_needed / 50.0, 1)
        urea_cost = round(urea_bags * FERTILIZERS['urea']['price_per_bag'], 2)
        total_estimated_cost += urea_cost

        commercial_bags.append({
            'fertilizer_id': 'urea',
            'name_en': 'Urea',
            'name_te': 'యూరియా (Urea)',
            'purpose_en': 'Supplies full Nitrogen requirement',
            'purpose_te': 'మొత్తం నత్రజని అవసరాన్ని తీరుస్తుంది',
            'quantity_kg': round(urea_kg_needed, 1),
            'bags_50kg': urea_bags,
            'approx_cost_inr': urea_cost,
            'n_provided_kg': total_req_n,
            'p_provided_kg': 0.0,
            'k_provided_kg': 0.0
        })

        # MOP for K
        mop_kg_needed = (total_req_k / 0.60) if total_req_k > 0 else 0
        mop_bags = round(mop_kg_needed / 50.0, 1)
        mop_cost = round(mop_bags * FERTILIZERS['mop']['price_per_bag'], 2)
        total_estimated_cost += mop_cost

        commercial_bags.append({
            'fertilizer_id': 'mop',
            'name_en': 'MOP (Muriate of Potash)',
            'name_te': 'పొటాష్ (MOP)',
            'purpose_en': 'Supplies Potassium',
            'purpose_te': 'పొటాష్ పోషకాన్ని అందిస్తుంది',
            'quantity_kg': round(mop_kg_needed, 1),
            'bags_50kg': mop_bags,
            'approx_cost_inr': mop_cost,
            'n_provided_kg': 0.0,
            'p_provided_kg': 0.0,
            'k_provided_kg': total_req_k
        })

    # --- PLAN C: Complex 10-26-26 + Urea ---
    elif fertilizer_plan == 'complex':
        # 10-26-26 covers P & K in 1:1 ratio
        c_kg = (total_req_p / 0.26) if total_req_p > 0 else 0
        c_bags = round(c_kg / 50.0, 1)
        c_n_prov = c_kg * 0.10
        c_k_prov = c_kg * 0.26
        c_cost = round(c_bags * FERTILIZERS['complex_10_26_26']['price_per_bag'], 2)
        total_estimated_cost += c_cost

        commercial_bags.append({
            'fertilizer_id': 'complex_10_26_26',
            'name_en': 'NPK 10-26-26 (Gromor Complex)',
            'name_te': '10-26-26 కాంప్లెక్స్ ఎరువు',
            'purpose_en': 'Balanced Phosphorus and Potash combination',
            'purpose_te': 'భాస్వరం మరియు పొటాష్ సమతుల్యంగా అందిస్తుంది',
            'quantity_kg': round(c_kg, 1),
            'bags_50kg': c_bags,
            'approx_cost_inr': c_cost,
            'n_provided_kg': round(c_n_prov, 1),
            'p_provided_kg': total_req_p,
            'k_provided_kg': round(c_k_prov, 1)
        })

        rem_n = max(0.0, total_req_n - c_n_prov)
        u_kg = (rem_n / 0.46) if rem_n > 0 else 0
        u_bags = round(u_kg / 50.0, 1)
        u_cost = round(u_bags * FERTILIZERS['urea']['price_per_bag'], 2)
        total_estimated_cost += u_cost

        commercial_bags.append({
            'fertilizer_id': 'urea',
            'name_en': 'Urea',
            'name_te': 'యూరియా (Urea)',
            'purpose_en': 'Top dressing Nitrogen supplement',
            'purpose_te': 'పైపాటు నత్రజని ఎరువు',
            'quantity_kg': round(u_kg, 1),
            'bags_50kg': u_bags,
            'approx_cost_inr': u_cost,
            'n_provided_kg': round(rem_n, 1),
            'p_provided_kg': 0.0,
            'k_provided_kg': 0.0
        })

    # Generate Split Application Schedule
    schedule = []
    for split in crop['splits']:
        stage_n_kg = round(total_req_n * (split['n_pct'] / 100.0), 1)
        stage_p_kg = round(total_req_p * (split['p_pct'] / 100.0), 1)
        stage_k_kg = round(total_req_k * (split['k_pct'] / 100.0), 1)

        schedule.append({
            'stage_en': split['stage_en'],
            'stage_te': split['stage_te'],
            'n_pct': split['n_pct'],
            'p_pct': split['p_pct'],
            'k_pct': split['k_pct'],
            'n_kg': stage_n_kg,
            'p_kg': stage_p_kg,
            'k_kg': stage_k_kg,
            'advice_en': f"Apply {split['n_pct']}% of Nitrogen, {split['p_pct']}% Phosphorus, {split['k_pct']}% Potash at this stage.",
            'advice_te': f"ఈ దశలో {split['n_pct']}% నత్రజని, {split['p_pct']}% భాస్వరం, {split['k_pct']}% పొటాష్ అందించండి."
        })

    # Organic Manure & Biofertilizer Recommendations
    fym_total_tons = round(crop['fym_tons_per_acre'] * acres, 1)

    return jsonify({
        'status': 'success',
        'data': {
            'crop': {
                'id': crop['id'],
                'name_en': crop['name_en'],
                'name_te': crop['name_te'],
                'category': crop['category'],
                'duration_days': crop['duration_days']
            },
            'land_area': {
                'raw_input': raw_area,
                'unit': unit,
                'acres': round(acres, 2),
                'hectares': round(acres / 2.47105, 2)
            },
            'soil_test': {
                'nitrogen_status': data.get('soil_n', 'medium'),
                'phosphorus_status': data.get('soil_p', 'medium'),
                'potassium_status': data.get('soil_k', 'medium')
            },
            'total_nutrient_requirement': {
                'nitrogen_n_kg': total_req_n,
                'phosphorus_p2o5_kg': total_req_p,
                'potassium_k2o_kg': total_req_k,
                'ratio': f"{round(crop['n'], 0)}:{round(crop['p'], 0)}:{round(crop['k'], 0)}"
            },
            'commercial_fertilizers': commercial_bags,
            'split_application_schedule': schedule,
            'total_estimated_cost_inr': round(total_estimated_cost, 2),
            'organic_recommendations': {
                'fym_tons': fym_total_tons,
                'neem_cake_kg': round(100 * acres, 0),
                'biofertilizers_en': 'Apply Azospirillum / PSB (Phosphorus Solubilizing Bacteria) @ 2 kg/acre mixed with FYM.',
                'biofertilizers_te': 'ఎకరానికి 2 కేజీల అజోస్పైరిల్లమ్ మరియు పి.ఎస్.బి బయో-ఫెర్టిలైజర్లను పశువుల ఎరువుతో కలిపి చల్లండి.'
            },
            'precautions_en': [
                'Never apply Urea on wet leaves; apply during cool evening hours with soil moisture present.',
                'Do not mix chemical fertilizers directly with microbial bio-fertilizers or Trichoderma.',
                'Ensure balanced Potash application to reduce pest vulnerability and prevent lodging.'
            ],
            'precautions_te': [
                'ఆకులపై తేమ ఉన్నప్పుడు యూరియా చల్లరాదు; నేలలో తగినంత పదును ఉన్నప్పుడు సాయంత్రం వేళల్లో వేయాలి.',
                'రసాయన ఎరువులను జీవన ఎరువులు (బయో-ఫెర్టిలైజర్స్) తో నేరుగా కలపకూడదు.',
                'పైరు పడిపోకుండా మరియు చీడపీడల తట్టుకోవడానికి సరైన మోతాదులో పొటాష్ తప్పనిసరిగా వేయాలి.'
            ]
        }
    }), 200
