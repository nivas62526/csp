import React, { useState } from 'react';

// Static Crop Metadata for instant UI selection
const CROPS = [
  { id: 'paddy', name_en: 'Paddy / Rice', name_te: 'వరి (Paddy)', icon: '🌾', duration: '120d', n: 48, p: 24, k: 20 },
  { id: 'cotton', name_en: 'Cotton', name_te: 'పత్తి (Cotton)', icon: '☁️', duration: '160d', n: 60, p: 24, k: 24 },
  { id: 'maize', name_en: 'Maize / Corn', name_te: 'మొక్కజొన్న (Maize)', icon: '🌽', duration: '110d', n: 48, p: 24, k: 16 },
  { id: 'chillies', name_en: 'Chillies', name_te: 'మిర్చి (Chillies)', icon: '🌶️', duration: '150d', n: 60, p: 24, k: 24 },
  { id: 'groundnut', name_en: 'Groundnut', name_te: 'వేరుశనగ (Groundnut)', icon: '🥜', duration: '105d', n: 12, p: 20, k: 16 },
  { id: 'sugarcane', name_en: 'Sugarcane', name_te: 'చెరకు (Sugarcane)', icon: '🎋', duration: '330d', n: 100, p: 40, k: 48 },
  { id: 'tomato', name_en: 'Tomato', name_te: 'టమాటా (Tomato)', icon: '🍅', duration: '100d', n: 48, p: 32, k: 32 },
  { id: 'wheat', name_en: 'Wheat', name_te: 'గోధుమ (Wheat)', icon: '🌱', duration: '120d', n: 48, p: 24, k: 16 }
];

// Offline calculation fallback in case backend is disconnected
function calculateClientSide(cropId, area, unit, soilN, soilP, soilK, plan) {
  const crop = CROPS.find(c => c.id === cropId) || CROPS[0];
  let acres = parseFloat(area) || 1.0;
  if (unit === 'hectares') acres = acres * 2.47105;
  if (unit === 'guntas') acres = acres / 40.0;

  const factor = (level) => level === 'low' ? 1.25 : level === 'high' ? 0.75 : 1.0;
  const totalN = Math.round(crop.n * acres * factor(soilN) * 10) / 10;
  const totalP = Math.round(crop.p * acres * factor(soilP) * 10) / 10;
  const totalK = Math.round(crop.k * acres * factor(soilK) * 10) / 10;

  let commercial = [];
  let totalCost = 0;

  if (plan === 'ssp') {
    const sspKg = Math.round((totalP / 0.16) * 10) / 10;
    const sspBags = Math.round((sspKg / 50) * 10) / 10;
    const sspCost = sspBags * 450;
    commercial.push({ name_en: 'SSP (Single Super Phosphate)', name_te: 'సింగిల్ సూపర్ ఫాస్ఫేట్ (SSP)', bags_50kg: sspBags, quantity_kg: sspKg, approx_cost_inr: sspCost, purpose_en: 'Supplies P + 11% Sulphur', purpose_te: 'భాస్వరం మరియు సల్ఫర్' });

    const ureaKg = Math.round((totalN / 0.46) * 10) / 10;
    const ureaBags = Math.round((ureaKg / 50) * 10) / 10;
    const ureaCost = ureaBags * 266;
    commercial.push({ name_en: 'Urea', name_te: 'యూరియా (Urea)', bags_50kg: ureaBags, quantity_kg: ureaKg, approx_cost_inr: ureaCost, purpose_en: 'Supplies Nitrogen', purpose_te: 'నత్రజని' });

    const mopKg = Math.round((totalK / 0.60) * 10) / 10;
    const mopBags = Math.round((mopKg / 50) * 10) / 10;
    const mopCost = mopBags * 1650;
    commercial.push({ name_en: 'MOP (Potash)', name_te: 'పొటాష్ (MOP)', bags_50kg: mopBags, quantity_kg: mopKg, approx_cost_inr: mopCost, purpose_en: 'Supplies Potash', purpose_te: 'పొటాష్' });
    totalCost = sspCost + ureaCost + mopCost;
  } else if (plan === 'complex') {
    const cKg = Math.round((totalP / 0.26) * 10) / 10;
    const cBags = Math.round((cKg / 50) * 10) / 10;
    const cCost = cBags * 1450;
    commercial.push({ name_en: 'NPK 10-26-26 (Complex)', name_te: '10-26-26 కాంప్లెక్స్ ఎరువు', bags_50kg: cBags, quantity_kg: cKg, approx_cost_inr: cCost, purpose_en: 'Supplies P & K', purpose_te: 'భాస్వరం మరియు పొటాష్' });

    const remN = Math.max(0, totalN - (cKg * 0.10));
    const uKg = Math.round((remN / 0.46) * 10) / 10;
    const uBags = Math.round((uKg / 50) * 10) / 10;
    const uCost = uBags * 266;
    commercial.push({ name_en: 'Urea', name_te: 'యూరియా (Urea)', bags_50kg: uBags, quantity_kg: uKg, approx_cost_inr: uCost, purpose_en: 'Top dressing N', purpose_te: 'పైపాటు నత్రజని' });
    totalCost = cCost + uCost;
  } else {
    // DAP plan (default)
    const dapKg = Math.round((totalP / 0.46) * 10) / 10;
    const dapBags = Math.round((dapKg / 50) * 10) / 10;
    const dapN = dapKg * 0.18;
    const dapCost = dapBags * 1350;
    commercial.push({ name_en: 'DAP (Diammonium Phosphate)', name_te: 'డి.ఎ.పి (DAP)', bags_50kg: dapBags, quantity_kg: dapKg, approx_cost_inr: dapCost, purpose_en: 'Supplies full P + partial N', purpose_te: 'భాస్వరం మరియు కొంత నత్రజని' });

    const remN = Math.max(0, totalN - dapN);
    const ureaKg = Math.round((remN / 0.46) * 10) / 10;
    const ureaBags = Math.round((ureaKg / 50) * 10) / 10;
    const ureaCost = ureaBags * 266;
    commercial.push({ name_en: 'Urea', name_te: 'యూరియా (Urea)', bags_50kg: ureaBags, quantity_kg: ureaKg, approx_cost_inr: ureaCost, purpose_en: 'Supplies remaining Nitrogen', purpose_te: 'మిగిలిన నత్రజని' });

    const mopKg = Math.round((totalK / 0.60) * 10) / 10;
    const mopBags = Math.round((mopKg / 50) * 10) / 10;
    const mopCost = mopBags * 1650;
    commercial.push({ name_en: 'MOP (Potash)', name_te: 'పొటాష్ (MOP)', bags_50kg: mopBags, quantity_kg: mopKg, approx_cost_inr: mopCost, purpose_en: 'Supplies Potassium', purpose_te: 'పొటాష్' });
    totalCost = dapCost + ureaCost + mopCost;
  }

  return {
    crop: { id: crop.id, name_en: crop.name_en, name_te: crop.name_te },
    land_area: { acres: Math.round(acres * 100) / 100, unit, raw_input: area },
    total_nutrient_requirement: { nitrogen_n_kg: totalN, phosphorus_p2o5_kg: totalP, potassium_k2o_kg: totalK },
    commercial_fertilizers: commercial,
    total_estimated_cost_inr: Math.round(totalCost),
    split_application_schedule: [
      { stage_en: 'Basal (At Sowing / Planting)', stage_te: 'విత్తే సమయంలో (బాసల్ మోతాదు)', n_pct: 33, p_pct: 100, k_pct: 50, advice_en: 'Apply all DAP/SSP, half Potash, 1/3rd Urea at root depth.', advice_te: 'మొత్తం DAP/SSP, సగం పొటాష్, 1/3 యూరియా ఆఖరి దుక్కిలో వేయాలి.' },
      { stage_en: 'Vegetative Growth Stage', stage_te: 'శాకీయ ఎదుగుదల దశ (25-30 రోజులు)', n_pct: 33, p_pct: 0, k_pct: 0, advice_en: 'Top dress 1/3rd Urea when soil has optimum moisture.', advice_te: 'నేలలో పదును ఉన్నప్పుడు 1/3 వంతు యూరియా పైపాటుగా చల్లాలి.' },
      { stage_en: 'Flowering / Panicle Initiation', stage_te: 'పూత / గింజ కట్టే దశ (45-55 రోజులు)', n_pct: 34, p_pct: 0, k_pct: 50, advice_en: 'Apply remaining Urea and Potash for grain weight and quality.', advice_te: 'మిగిలిన యూరియా మరియు పొటాష్ గింజ నాణ్యత, బరువు కోసం వేయాలి.' }
    ],
    organic_recommendations: {
      fym_tons: Math.round(4.0 * acres * 10) / 10,
      neem_cake_kg: Math.round(100 * acres),
      biofertilizers_en: 'Apply Azospirillum & PSB bio-fertilizers @ 2 kg/acre mixed with 200 kg FYM.',
      biofertilizers_te: 'ఎకరానికి 2 కేజీల అజోస్పైరిల్లమ్ మరియు పి.ఎస్.బి బయో-ఫెర్టిలైజర్లను పశువుల ఎరువుతో కలిపి చల్లండి.'
    },
    precautions_en: [
      'Apply fertilizers only when soil has adequate moisture.',
      'Split Nitrogen doses to minimize leaching loss in heavy rains.',
      'Incorporate Phosphorus and Potash at root zone depth during land preparation.'
    ],
    precautions_te: [
      'నేలలో తగినంత పదును ఉన్నప్పుడే రసాయన ఎరువులు వేయాలి.',
      'యూరియాను ఒకేసారి వేయకుండా 2-3 దఫాలుగా విభజించి వేస్తే పోషక నష్టం తగ్గుతుంది.',
      'భాస్వరం మరియు పొటాష్ ఎరువులను ఆఖరి దుక్కిలో దున్ని వేర్లకు అందేలా చేయాలి.'
    ]
  };
}

export default function FertilizerCalculator({ lang = 'te' }) {
  const [crop, setCrop] = useState('paddy');
  const [area, setArea] = useState(2.0);
  const [unit, setUnit] = useState('acres');
  const [soilN, setSoilN] = useState('medium');
  const [soilP, setSoilP] = useState('medium');
  const [soilK, setSoilK] = useState('medium');
  const [fertilizerPlan, setFertilizerPlan] = useState('dap');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [notice, setNotice] = useState('');

  const t = {
    title: lang === 'te' ? 'పంట & విస్తీర్ణం వివరాలు' : 'Crop & Farm Area Details',
    selectCrop: lang === 'te' ? 'పంటను ఎంచుకోండి:' : 'Select Crop:',
    farmArea: lang === 'te' ? 'పొలం విస్తీర్ణం:' : 'Land Area:',
    acres: lang === 'te' ? 'ఎకరాలు (Acres)' : 'Acres',
    hectares: lang === 'te' ? 'హెక్టార్లు (Hectares)' : 'Hectares',
    guntas: lang === 'te' ? 'గుంటలు (Guntas)' : 'Guntas',
    soilTest: lang === 'te' ? 'నేల పరీక్ష ఆధారిత సంతృప్తత (Soil Fertility):' : 'Soil Fertility Status (from Soil Test Card):',
    nitrogen: lang === 'te' ? 'నత్రజని (N)' : 'Nitrogen (N)',
    phosphorus: lang === 'te' ? 'భాస్వరం (P)' : 'Phosphorus (P)',
    potassium: lang === 'te' ? 'పొటాష్ (K)' : 'Potassium (K)',
    low: lang === 'te' ? 'తక్కువ (Low)' : 'Low (+25%)',
    medium: lang === 'te' ? 'మధ్యస్థం (Medium)' : 'Medium (Normal)',
    high: lang === 'te' ? 'ఎక్కువ (High)' : 'High (-25%)',
    fertPlan: lang === 'te' ? 'ఎరువుల ఎంపిక విధానం (Fertilizer Combination):' : 'Fertilizer Combination Scheme:',
    planDap: lang === 'te' ? 'యూరియా + డి.ఎ.పి (DAP) + పొటాష్ (MOP) [సాధారణం]' : 'Urea + DAP + MOP [Most Popular]',
    planSsp: lang === 'te' ? 'యూరియా + సింగిల్ సూపర్ ఫాస్ఫేట్ (SSP) + పొటాష్ (MOP)' : 'Urea + SSP + MOP [Ideal for Sulphur Needs]',
    planComplex: lang === 'te' ? '10-26-26 కాంప్లెక్స్ ఎరువు + యూరియా' : 'NPK 10-26-26 Complex + Urea',
    calcBtn: lang === 'te' ? 'ఎరువుల మోతాదును లెక్కించండి ➔' : 'Calculate Fertilizer Quantity ➔',
    calculating: lang === 'te' ? 'శాస్త్రీయంగా లెక్కిస్తోంది...' : 'Calculating scientific recommendation...',
    resultsHeader: lang === 'te' ? 'సిఫార్సు చేయబడిన ఎరువుల నివేదిక' : 'Recommended Fertilizer & Nutrient Plan',
    totalNutrients: lang === 'te' ? 'మొత్తం అవసరమైన శుద్ధ పోషకాలు' : 'Pure Nutrient Requirement',
    commercialBags: lang === 'te' ? 'కొనుగోలు చేయవలసిన ఎరువుల బస్తాల వివరాలు' : 'Commercial Fertilizer Bags Needed (50kg Bags)',
    schedule: lang === 'te' ? 'ఎరువులు వేసే సమయాలు (దఫాల వారీగా)' : 'Split Application Schedule',
    estCost: lang === 'te' ? 'అంచనా వ్యయం:' : 'Estimated Cost:',
    organic: lang === 'te' ? 'సేంద్రీయ & జీవన ఎరువుల సిఫార్సు' : 'Organic Manure & Bio-Fertilizers',
    precautions: lang === 'te' ? 'రైతు సోదరులకు ముఖ్యమైన జాగ్రత్తలు' : 'Application Precautions & Guidelines',
    listen: lang === 'te' ? '🔊 నివేదిక వినండి' : '🔊 Listen Advice',
    print: lang === 'te' ? '🖨️ ప్రింట్ / సేవ్' : '🖨️ Print / Save'
  };

  const handleCalculate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setNotice('');

    try {
      const payload = {
        crop,
        area: parseFloat(area),
        unit,
        soil_n: soilN,
        soil_p: soilP,
        soil_k: soilK,
        fertilizer_plan: fertilizerPlan
      };

      // Call Flask Backend
      const response = await fetch('http://127.0.0.1:5000/api/fertilizer/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error('Backend offline');
      }

      const resData = await response.json();
      if (resData.status === 'success') {
        setResult(resData.data);
      } else {
        throw new Error(resData.message || 'Calculation error');
      }
    } catch (err) {
      // Intelligent fallback to client-side scientific calculation
      const fallbackResult = calculateClientSide(crop, area, unit, soilN, soilP, soilK, fertilizerPlan);
      setResult(fallbackResult);
      setNotice(lang === 'te' ? 'ఆఫ్‌లైన్ శాస్త్రీయ కాలిక్యులేటర్ ద్వారా ఫలితాలు అందించబడ్డాయి.' : 'Results computed via built-in agronomic calculation engine.');
    } finally {
      setLoading(false);
    }
  };

  const speakAdvice = () => {
    if (!result || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();

    const cropName = lang === 'te' ? result.crop.name_te : result.crop.name_en;
    let text = lang === 'te'
      ? `${cropName} పంటకు ${result.land_area.acres} ఎకరాలకు గాను ఎరువుల నివేదిక. `
      : `Fertilizer recommendation for ${cropName} on ${result.land_area.acres} acres. `;

    result.commercial_fertilizers.forEach(f => {
      text += lang === 'te'
        ? `${f.name_te} ${f.bags_50kg} బస్తాలు. `
        : `${f.bags_50kg} bags of ${f.name_en}. `;
    });

    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = lang === 'te' ? 'te-IN' : 'en-US';
    window.speechSynthesis.speak(utter);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Input Card */}
      <div style={{
        backgroundColor: '#ffffff',
        borderRadius: '16px',
        padding: '24px',
        boxShadow: '0 4px 16px rgba(0,0,0,0.06)',
        border: '1px solid #e2e8f0'
      }}>
        <h2 style={{ margin: '0 0 18px 0', fontSize: '1.25rem', color: '#166534', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>📋</span> {t.title}
        </h2>

        <form onSubmit={handleCalculate}>
          {/* Crop Selection Grid */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontSize: '0.88rem', fontWeight: 700, marginBottom: '8px' }}>
              {t.selectCrop}
            </label>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(115px, 1fr))',
              gap: '8px'
            }}>
              {CROPS.map(c => (
                <button
                  key={c.id}
                  type="button"
                  onClick={() => setCrop(c.id)}
                  style={{
                    backgroundColor: crop === c.id ? '#dcfce7' : '#f8fafc',
                    border: crop === c.id ? '2px solid #16a34a' : '1px solid #cbd5e1',
                    borderRadius: '12px',
                    padding: '10px 6px',
                    textAlign: 'center',
                    cursor: 'pointer',
                    transition: 'all 0.15s'
                  }}
                >
                  <div style={{ fontSize: '1.6rem', marginBottom: '2px' }}>{c.icon}</div>
                  <div style={{ fontSize: '0.78rem', fontWeight: 700, color: crop === c.id ? '#15803d' : '#334155' }}>
                    {lang === 'te' ? c.name_te : c.name_en}
                  </div>
                  <div style={{ fontSize: '0.68rem', color: '#64748b' }}>{c.duration}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Area & Unit Row */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '20px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, marginBottom: '6px' }}>
                {t.farmArea}
              </label>
              <input
                type="number"
                step="0.1"
                min="0.1"
                max="500"
                value={area}
                onChange={e => setArea(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: '10px',
                  border: '1px solid #cbd5e1',
                  fontSize: '1rem',
                  fontWeight: 600,
                  boxSizing: 'border-box'
                }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, marginBottom: '6px' }}>
                యూనిట్ (Unit):
              </label>
              <select
                value={unit}
                onChange={e => setUnit(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: '10px',
                  border: '1px solid #cbd5e1',
                  fontSize: '0.95rem',
                  fontWeight: 600,
                  backgroundColor: '#ffffff',
                  boxSizing: 'border-box'
                }}
              >
                <option value="acres">{t.acres}</option>
                <option value="hectares">{t.hectares}</option>
                <option value="guntas">{t.guntas}</option>
              </select>
            </div>
          </div>

          {/* Soil Test Nutrients Calibration */}
          <div style={{ marginBottom: '20px', backgroundColor: '#f8fafc', padding: '14px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#334155', marginBottom: '10px' }}>
              🧪 {t.soilTest}
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px' }}>
              {[
                { label: t.nitrogen, val: soilN, set: setSoilN },
                { label: t.phosphorus, val: soilP, set: setSoilP },
                { label: t.potassium, val: soilK, set: setSoilK }
              ].map((s, idx) => (
                <div key={idx}>
                  <div style={{ fontSize: '0.78rem', fontWeight: 700, marginBottom: '4px', color: '#475569' }}>{s.label}</div>
                  <select
                    value={s.val}
                    onChange={e => s.set(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '8px',
                      borderRadius: '8px',
                      border: '1px solid #cbd5e1',
                      fontSize: '0.82rem',
                      fontWeight: 600,
                      backgroundColor: '#ffffff'
                    }}
                  >
                    <option value="low">{t.low}</option>
                    <option value="medium">{t.medium}</option>
                    <option value="high">{t.high}</option>
                  </select>
                </div>
              ))}
            </div>
          </div>

          {/* Fertilizer Combination Plan Selector */}
          <div style={{ marginBottom: '22px' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, marginBottom: '6px' }}>
              ⚖️ {t.fertPlan}
            </label>
            <select
              value={fertilizerPlan}
              onChange={e => setFertilizerPlan(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 14px',
                borderRadius: '10px',
                border: '1px solid #cbd5e1',
                fontSize: '0.92rem',
                fontWeight: 600,
                backgroundColor: '#ffffff',
                boxSizing: 'border-box'
              }}
            >
              <option value="dap">{t.planDap}</option>
              <option value="ssp">{t.planSsp}</option>
              <option value="complex">{t.planComplex}</option>
            </select>
          </div>

          {/* Calculate Submit Button */}
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              backgroundColor: '#16a34a',
              color: '#ffffff',
              border: 'none',
              borderRadius: '12px',
              padding: '14px',
              fontSize: '1.05rem',
              fontWeight: 800,
              cursor: loading ? 'not-allowed' : 'pointer',
              boxShadow: '0 4px 12px rgba(22, 163, 74, 0.28)',
              transition: 'background-color 0.2s'
            }}
          >
            {loading ? t.calculating : t.calcBtn}
          </button>
        </form>
      </div>

      {notice && (
        <div style={{ padding: '10px 16px', backgroundColor: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '10px', fontSize: '0.82rem', color: '#1e40af' }}>
          ℹ️ {notice}
        </div>
      )}

      {/* Results Dashboard */}
      {result && (
        <div style={{
          backgroundColor: '#ffffff',
          borderRadius: '16px',
          padding: '24px',
          boxShadow: '0 4px 16px rgba(0,0,0,0.06)',
          border: '1px solid #e2e8f0'
        }}>
          {/* Top Bar with actions */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', marginBottom: '18px', paddingBottom: '14px', borderBottom: '1px solid #f1f5f9' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.3rem', fontWeight: 800, color: '#14532d' }}>
                ✅ {t.resultsHeader}
              </h3>
              <p style={{ margin: '2px 0 0 0', fontSize: '0.85rem', color: '#64748b' }}>
                {lang === 'te' ? result.crop.name_te : result.crop.name_en} &bull; {result.land_area.acres} {t.acres}
              </p>
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                type="button"
                onClick={speakAdvice}
                style={{
                  backgroundColor: '#f0fdf4',
                  color: '#166534',
                  border: '1px solid #bbf7d0',
                  borderRadius: '20px',
                  padding: '6px 14px',
                  fontSize: '0.82rem',
                  fontWeight: 700,
                  cursor: 'pointer'
                }}
              >
                {t.listen}
              </button>
              <button
                type="button"
                onClick={() => window.print()}
                style={{
                  backgroundColor: '#f8fafc',
                  color: '#334155',
                  border: '1px solid #cbd5e1',
                  borderRadius: '20px',
                  padding: '6px 14px',
                  fontSize: '0.82rem',
                  fontWeight: 700,
                  cursor: 'pointer'
                }}
              >
                {t.print}
              </button>
            </div>
          </div>

          {/* 3 Nutrient Metric Cards */}
          <h4 style={{ margin: '0 0 10px 0', fontSize: '0.9rem', color: '#475569', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            {t.totalNutrients}
          </h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '24px' }}>
            <div style={{ backgroundColor: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '12px', padding: '14px', textAlign: 'center' }}>
              <div style={{ fontSize: '0.78rem', color: '#1e40af', fontWeight: 700 }}>నత్రజని (Nitrogen - N)</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#1e3a8a', margin: '4px 0' }}>
                {result.total_nutrient_requirement.nitrogen_n_kg} <span style={{ fontSize: '0.8rem' }}>kg</span>
              </div>
              <div style={{ fontSize: '0.72rem', color: '#60a5fa' }}>ఆకుల పచ్చదనం & పిలకలు</div>
            </div>

            <div style={{ backgroundColor: '#fefce8', border: '1px solid #fef08a', borderRadius: '12px', padding: '14px', textAlign: 'center' }}>
              <div style={{ fontSize: '0.78rem', color: '#854d0e', fontWeight: 700 }}>భాస్వరం (Phosphorus - P)</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#713f12', margin: '4px 0' }}>
                {result.total_nutrient_requirement.phosphorus_p2o5_kg} <span style={{ fontSize: '0.8rem' }}>kg</span>
              </div>
              <div style={{ fontSize: '0.72rem', color: '#eab308' }}>వేరు వ్యవస్థ & పిలకలు</div>
            </div>

            <div style={{ backgroundColor: '#fdf2f8', border: '1px solid #fbcfe8', borderRadius: '12px', padding: '14px', textAlign: 'center' }}>
              <div style={{ fontSize: '0.78rem', color: '#9d174d', fontWeight: 700 }}>పొటాష్ (Potassium - K)</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#831843', margin: '4px 0' }}>
                {result.total_nutrient_requirement.potassium_k2o_kg} <span style={{ fontSize: '0.8rem' }}>kg</span>
              </div>
              <div style={{ fontSize: '0.72rem', color: '#ec4899' }}>రోగాన్ని తట్టుకొనుట & గింజ బరువు</div>
            </div>
          </div>

          {/* Commercial Fertilizer Bags Needed */}
          <h4 style={{ margin: '0 0 10px 0', fontSize: '0.9rem', color: '#475569', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            🛒 {t.commercialBags}
          </h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px', marginBottom: '24px' }}>
            {result.commercial_fertilizers.map((item, i) => (
              <div key={i} style={{
                backgroundColor: '#f8fafc',
                border: '1px solid #cbd5e1',
                borderRadius: '12px',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between'
              }}>
                <div>
                  <div style={{ fontSize: '0.98rem', fontWeight: 800, color: '#0f172a', marginBottom: '4px' }}>
                    {lang === 'te' ? item.name_te : item.name_en}
                  </div>
                  <div style={{ fontSize: '0.78rem', color: '#64748b', marginBottom: '10px' }}>
                    {lang === 'te' ? item.purpose_te : item.purpose_en}
                  </div>
                </div>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', borderTop: '1px solid #e2e8f0', paddingTop: '8px' }}>
                    <span style={{ fontSize: '1.4rem', fontWeight: 900, color: '#16a34a' }}>
                      {item.bags_50kg} <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#475569' }}>బస్తాలు (Bags)</span>
                    </span>
                    <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 600 }}>({item.quantity_kg} kg)</span>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#0369a1', fontWeight: 700, marginTop: '4px' }}>
                    సుమారు ఖరీదు: ₹{item.approx_cost_inr.toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Total Estimated Cost Banner */}
          <div style={{
            backgroundColor: '#f0fdf4',
            border: '2px solid #86efac',
            borderRadius: '12px',
            padding: '14px 20px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '24px'
          }}>
            <span style={{ fontSize: '1rem', fontWeight: 800, color: '#166534' }}>
              💰 {t.estCost}
            </span>
            <span style={{ fontSize: '1.5rem', fontWeight: 900, color: '#15803d' }}>
              ₹ {result.total_estimated_cost_inr.toLocaleString()}
            </span>
          </div>

          {/* Split Schedule Timeline */}
          <h4 style={{ margin: '0 0 10px 0', fontSize: '0.9rem', color: '#475569', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            📅 {t.schedule}
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '24px' }}>
            {result.split_application_schedule.map((stg, i) => (
              <div key={i} style={{
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
                borderLeft: '4px solid #16a34a',
                borderRadius: '8px',
                padding: '12px 16px'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <strong style={{ fontSize: '0.92rem', color: '#15803d' }}>
                    {i + 1}. {lang === 'te' ? stg.stage_te : stg.stage_en}
                  </strong>
                  <span style={{ fontSize: '0.78rem', backgroundColor: '#f1f5f9', padding: '2px 8px', borderRadius: '12px', color: '#475569', fontWeight: 700 }}>
                    N: {stg.n_pct}% | P: {stg.p_pct}% | K: {stg.k_pct}%
                  </span>
                </div>
                <p style={{ margin: 0, fontSize: '0.82rem', color: '#475569' }}>
                  {lang === 'te' ? stg.advice_te : stg.advice_en}
                </p>
              </div>
            ))}
          </div>

          {/* Organic & Bio-fertilizer card */}
          <div style={{
            backgroundColor: '#fffbeb',
            border: '1px solid #fde68a',
            borderRadius: '12px',
            padding: '16px',
            marginBottom: '20px'
          }}>
            <h5 style={{ margin: '0 0 6px 0', fontSize: '0.92rem', color: '#92400e', fontWeight: 800 }}>
              🌿 {t.organic}
            </h5>
            <p style={{ margin: '0 0 6px 0', fontSize: '0.85rem', color: '#78350f' }}>
              &bull; <strong>పశువుల ఎరువు (FYM):</strong> {result.organic_recommendations.fym_tons} టన్నులు వేయాలి.
            </p>
            <p style={{ margin: '0 0 6px 0', fontSize: '0.85rem', color: '#78350f' }}>
              &bull; <strong>వేపపిండి (Neem Cake):</strong> {result.organic_recommendations.neem_cake_kg} kg ఆఖరి దుక్కిలో వేస్తే భూమిలోని పురుగులు నశిస్తాయి.
            </p>
            <p style={{ margin: 0, fontSize: '0.85rem', color: '#78350f' }}>
              &bull; <strong>బయో-ఫెర్టిలైజర్స్:</strong> {lang === 'te' ? result.organic_recommendations.biofertilizers_te : result.organic_recommendations.biofertilizers_en}
            </p>
          </div>

          {/* Precautions Alert */}
          <div style={{
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '12px',
            padding: '16px'
          }}>
            <h5 style={{ margin: '0 0 8px 0', fontSize: '0.92rem', color: '#991b1b', fontWeight: 800 }}>
              ⚠️ {t.precautions}
            </h5>
            <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.82rem', color: '#7f1d1d' }}>
              {(lang === 'te' ? result.precautions_te : result.precautions_en).map((p, i) => (
                <li key={i} style={{ marginBottom: '4px' }}>{p}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
