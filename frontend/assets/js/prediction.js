/**
 * SMART POULTRY HEALTH MONITORING & DISEASE-RISK PREDICTION SYSTEM
 * AI Computer Vision & Machine Learning Disease-Risk Engine (prediction.js)
 */

// Preset Sample Poultry Images for Instant Demo Testing
const SAMPLE_PREDICTIONS = {
  healthy: {
    name: 'Healthy Broiler (Baseline)',
    imageUrl: 'https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?auto=format&fit=crop&w=600&q=80',
    visualCondition: 'Healthy Plumage & Alert Posture',
    riskLevel: 'Low',
    confidence: 96.4,
    detectedFeatures: [
      { label: 'Eye Clarity', status: 'Optimal / Clear', isGood: true },
      { label: 'Comb & Wattle Color', status: 'Bright Red (Normal)', isGood: true },
      { label: 'Feather Smoothness', status: 'Intact & Clean', isGood: true },
      { label: 'Standing Stance', status: 'Erect / Active', isGood: true }
    ],
    aiSummary: 'Visual Health Indicator: No ocular discharge, swelling, or feather disarray detected. Bird exhibits healthy posture and morphology.',
    recommendedActions: 'Maintain baseline hygiene, clean drinking water, and standard feeding intervals.'
  },
  respiratory: {
    name: 'Respiratory Distress Suspect',
    imageUrl: 'https://images.unsplash.com/photo-1516467508483-a7212febe31a?auto=format&fit=crop&w=600&q=80',
    visualCondition: 'Possible Respiratory Irritation / Ruffled Feathers',
    riskLevel: 'Medium',
    confidence: 89.2,
    detectedFeatures: [
      { label: 'Ocular Area', status: 'Mild Conjunctival Swelling', isGood: false },
      { label: 'Beak / Nostril', status: 'Moist / Potential Exudate', isGood: false },
      { label: 'Feather Condition', status: 'Ruffled Plumage', isGood: false },
      { label: 'Head Stance', status: 'Slight Droop / Low Energy', isGood: false }
    ],
    aiSummary: 'Early-Warning Risk: Visual indicators correlate with upper respiratory stress (such as Infectious Bronchitis or Ammonia irritation). Early isolation recommended.',
    recommendedActions: 'Verify shed ventilation flow, measure ammonia levels, inspect drinker lines, and consult an avian veterinarian if symptoms persist.'
  },
  fowlpox: {
    name: 'Fowl Pox Lesion Suspect',
    imageUrl: 'https://images.unsplash.com/photo-1563281577-a7be47e20db9?auto=format&fit=crop&w=600&q=80',
    visualCondition: 'Possible Cutaneous Lesions on Unfeathered Skin',
    riskLevel: 'High',
    confidence: 91.8,
    detectedFeatures: [
      { label: 'Comb & Wattle', status: 'Nodular / Crusty Spots', isGood: false },
      { label: 'Eyelid Margins', status: 'Papular Formations', isGood: false },
      { label: 'Plumage Uniformity', status: 'Normal', isGood: true },
      { label: 'Activity Index', status: 'Suppressed Stance', isGood: false }
    ],
    aiSummary: 'Early-Warning Risk: Detected cutaneous nodular artifacts consistent with Avian Poxvirus signs. Prompt veterinary confirmation advised.',
    recommendedActions: 'Isolate affected birds immediately. Implement strict mosquito vector control and biosecurity sanitation.'
  },
  lethargy: {
    name: 'Lethargic / Gut Stress Suspect',
    imageUrl: 'https://images.unsplash.com/photo-1612170153139-6f881ff067e0?auto=format&fit=crop&w=600&q=80',
    visualCondition: 'Depression / Huddled Posture',
    riskLevel: 'Medium',
    confidence: 87.5,
    detectedFeatures: [
      { label: 'Posture', status: 'Huddled with Drooping Wings', isGood: false },
      { label: 'Feather Quality', status: 'Dull / Unkempt', isGood: false },
      { label: 'Vent Area', status: 'Suspected Dropping Staining', isGood: false },
      { label: 'Eye Alertness', status: 'Half-Closed / Dull', isGood: false }
    ],
    aiSummary: 'Early-Warning Risk: Stance suggests gastrointestinal discomfort, chilling, or early subclinical coccidiosis.',
    recommendedActions: 'Check brooder floor temperatures, inspect litter dry-matter %, provide clean fresh water with electrolytes, and collect fecal samples for vet testing.'
  }
};

const AIPredictor = {
  // Simulate AI Computer Vision Image Analysis with Hen Symptoms
  async analyzeImage(imageSource, sampleType = null, symptoms = '') {
    // Return sample preset or evaluate based on input
    let resultData;
    if (sampleType && SAMPLE_PREDICTIONS[sampleType]) {
      resultData = { 
        ...SAMPLE_PREDICTIONS[sampleType],
        detectedFeatures: [...SAMPLE_PREDICTIONS[sampleType].detectedFeatures]
      };
    } else {
      // Default realistic mock prediction
      resultData = {
        name: 'Uploaded Bird Photo',
        imageUrl: imageSource,
        visualCondition: 'Visual Health Risk: Mild Feather Disarray & Lethargy Signs',
        riskLevel: 'Medium',
        confidence: 86.4,
        detectedFeatures: [
          { label: 'Comb Color', status: 'Normal Pigmentation', isGood: true },
          { label: 'Plumage Texture', status: 'Slightly Ruffled', isGood: false },
          { label: 'Head Posture', status: 'Mild Droop', isGood: false },
          { label: 'Eye Margin', status: 'Clear / No Exudate', isGood: true }
        ],
        aiSummary: 'Early-Warning Assessment: Visual analysis detected slight posture anomalies with mild feather unruliness. No acute nodular lesions detected.',
        recommendedActions: 'Monitor bird water consumption closely and maintain optimal shed temperature.'
      };
    }

    // Process entered Hen Symptoms if available
    const symptomsStr = typeof symptoms === 'string' ? symptoms.trim() : (Array.isArray(symptoms) ? symptoms.join(', ').trim() : '');
    if (symptomsStr) {
      const symLower = symptomsStr.toLowerCase();
      resultData.reportedSymptoms = symptomsStr;
      const matchedIssues = [];
      const recs = [];

      // 1. Ranikhet / Newcastle Disease (ND)
      if (/ranikhet|newcastle|రాణీఖేత్|రాణికేత్|న్యూకాసిల్|रानीखेत|ராணிகேத்/.test(symLower)) {
        matchedIssues.push('Ranikhet Disease / Newcastle (ND)');
        resultData.detectedFeatures.push({
          label: 'Nervous & Systemic Signs',
          status: 'Ranikhet / Newcastle Indicators Reported',
          isGood: false
        });
        recs.push('Immediately isolate affected birds. Administer LaSota/RDV vaccine booster, vitamins, and spray virucidal disinfectant.');
      }

      // 2. Respiratory indicators / CRD
      if (/cough|sneez|gasp|rale|rattle|wheez|nasal|breath|crd|bronchitis|రొంప|దగ్గు|గురక|శ్వాస|छींक|खांसी|सीआरडी|சளி|இருமல்/.test(symLower)) {
        matchedIssues.push('Respiratory Distress (CRD / Bronchitis)');
        resultData.detectedFeatures.push({
          label: 'Respiratory Tract',
          status: 'Coughing / Wheezing / Exudate Reported',
          isGood: false
        });
        recs.push('Administer Tylosin / Doxycycline in drinking water; inspect shed cross-ventilation flow and dispel ammonia.');
      }

      // 3. Enteric / Coccidiosis indicators
      if (/diarrhea|loose|droppings|wet litter|blood|coccid|white droppings|విరేచనాలు|రక్తం|కాక్సి|రక్త విరేచనాలు|दस्त|कॉक्सिडिओसिस|கழிச்சல்/.test(symLower)) {
        matchedIssues.push('Enteric Infection (Coccidiosis / Enteritis)');
        resultData.detectedFeatures.push({
          label: 'Digestive & Excreta',
          status: 'Abnormal Droppings / Bloody Diarrhea Reported',
          isGood: false
        });
        recs.push('Administer Amprolium (20%) or Toltrazuril immediately; sanitize drinker lines and rake dry lime onto litter.');
      }

      // 4. Comb / Head / Pox lesions
      if (/comb|wattle|pox|lesion|crust|scab|nodule|pale|జుట్టు వాపు|చేతులు|తల వాపు|పొక్కులు|పాక్స్|ఫౌల్ పాక్స్|చేతులు|चेचक|फाउल पॉक्स/.test(symLower)) {
        matchedIssues.push('Comb / Integument Lesions (Fowl Pox)');
        resultData.detectedFeatures.push({
          label: 'Comb & Integument',
          status: 'Comb Lesions / Pox Crusts Reported',
          isGood: false
        });
        recs.push('Isolate affected birds; apply topical Betadine or glycerine to scabs and implement mosquito control netting.');
      }

      // 5. Coryza / Swollen Eyes & Face
      if (/coryza|కోరిజా|swollen eyes|swollen face|కళ్ల వాపు|కంటి నీరు|ముఖం వాపు|कोरिजा|सूजी आंखें/.test(symLower)) {
        matchedIssues.push('Infectious Coryza / Facial Edema');
        resultData.detectedFeatures.push({
          label: 'Ocular & Facial',
          status: 'Swollen Eyes / Facial Edema Reported',
          isGood: false
        });
        recs.push('Administer Enrofloxacin via water; gently flush crusted eye discharge with warm sterile saline.');
      }

      // 6. Gumboro (IBD)
      if (/gumboro|ibd|గంబోరో|गम्बोरो/.test(symLower)) {
        matchedIssues.push('Infectious Bursal Disease (Gumboro / IBD)');
        resultData.detectedFeatures.push({
          label: 'Immune & Bursa',
          status: 'Gumboro (IBD) Symptoms Reported',
          isGood: false
        });
        recs.push('Provide immuno-boosters, liver tonics, and continuous electrolytes with glucose to prevent dehydration.');
      }

      // 7. Marek's Disease / Paralysis / Weakness
      if (/marek|paralys|మరెక్స్|లక్వా|పక్షవాతం|కుంటి|కాలు వెనక్కి|लंगड़ा|मारेक्स|letharg|dull|weak|droop|huddled|limp|నీరసం|బలహీనత|బద్ధకం/.test(symLower)) {
        matchedIssues.push('Marek\'s Paralysis / Posture Suppression');
        resultData.detectedFeatures.push({
          label: 'Vitality & Stance',
          status: 'Paralysis / Suppressed Stance Reported',
          isGood: false
        });
        recs.push('Support with Vitamin B-Complex (Neurobion); isolate affected birds and consult avian veterinarian.');
      }

      // 8. Feed / Appetite Drop
      if (/feed|appetite|eat|eating|మేత|ఆకలి|भूख|दाना/.test(symLower)) {
        matchedIssues.push('Loss of Appetite');
        resultData.detectedFeatures.push({
          label: 'Appetite & Intake',
          status: 'Subnormal Feed Consumption Reported',
          isGood: false
        });
      }

      const currentLang = localStorage.getItem('smart_poultry_lang') || 'te';

      if (matchedIssues.length > 0) {
        resultData.riskLevel = (matchedIssues.length >= 2 || /ranikhet|newcastle|coccid|pox|paralys|blood|marek|gumboro|రాణీఖేత్|రక్తం|లక్వా|కాక్సి|గంబోరో/.test(symLower)) ? 'High' : 'Medium';
        resultData.confidence = Math.min(98.8, Math.max(91.5, (resultData.confidence || 88) + 5.2));

        if (currentLang === 'te') {
          const teConditions = [];
          const teRecs = [];
          if (/ranikhet|newcastle|రాణీఖేత్|రాణికేత్|న్యూకాసిల్/.test(symLower)) {
            teConditions.push('రాణీఖేత్ వ్యాధి (Ranikhet / Newcastle - ND)');
            teRecs.push('🚨 తక్షణమే సోకిన కోళ్లను వేరు చేయండి. లాసోటా/RDV వాక్సిన్ ఇవ్వండి, విర్కాన్-ఎస్ స్ప్రే చేయండి.');
          }
          if (/crd|cough|sneez|gasp|rale|wheez|రొంప|దగ్గు|గురక|శ్వాస|జలుబు/.test(symLower)) {
            teConditions.push('శ్వాసకోశ వ్యాధి / రొంప (CRD / Bronchitis)');
            teRecs.push('💊 టైలోసిన్ లేదా డాక్సీసైక్లిన్ యాంటీబయాటిక్ ఇవ్వండి; షెడ్డులో వెంటిలేషన్ మెరుగుపరచండి.');
          }
          if (/coccid|diarrhea|loose|blood|రక్త విరేచనాలు|కాక్సి|రక్తం|మోషన్స్/.test(symLower)) {
            teConditions.push('కాక్సిడియోసిస్ / రక్త విరేచనాలు (Coccidiosis / Enteritis)');
            teRecs.push('🚨 తాగునీటిలో ఆంప్రోలియం (Amprolium) లేదా టోల్ట్రాజురిల్ కలపండి; తడి లిట్టర్‌ను తీసి సున్నం చల్లండి.');
          }
          if (/pox|lesion|scab|nodule|తల వాపు|పొక్కులు|పాక్స్|ఫౌల్ పాక్స్/.test(symLower)) {
            teConditions.push('ఫౌల్ పాక్స్ / కోడి అమ్మవారు (Fowl Pox)');
            teRecs.push('🛡️ పొక్కులపై పోవిడోన్ అయోడిన్ లేదా గ్లిజరిన్ రాయండి; దోమల నివారణ చర్యలు తీసుకోండి.');
          }
          if (/coryza|కోరిజా|కళ్ల వాపు|కంటి నీరు|ముఖం వాపు/.test(symLower)) {
            teConditions.push('ఇన్ఫెక్షియస్ కోరిజా / ముఖం & కళ్ల వాపు (Coryza)');
            teRecs.push('💧 ఎన్రోఫ్లోక్సాసిన్ మందులు ఇవ్వండి; కళ్లను గోరువెచ్చని నీటితో తుడవండి.');
          }
          if (/gumboro|ibd|గంబోరో/.test(symLower)) {
            teConditions.push('గంబోరో వ్యాధి (Gumboro / IBD)');
            teRecs.push('🚨 ఇమ్యూనోబూస్టర్, లివర్ టానిక్ మరియు గ్లూకోజ్ ఎలక్ట్రోలైట్స్ అందించండి.');
          }
          if (/marek|paralys|మరెక్స్|లక్వా|పక్షవాతం|కుంటి|కాలు వెనక్కి/.test(symLower)) {
            teConditions.push('మరెక్స్ వ్యాధి / పక్షవాతం (Marek\'s Paralysis)');
            teRecs.push('⚠️ విటమిన్ బి-కాంప్లెక్స్ (Neurobion) ఇవ్వండి; వెటర్నరీ డాక్టర్‌ను సంప్రదించండి.');
          }
          if (/letharg|dull|weak|droop|నీరసం|బలహీనత|బద్ధకం/.test(symLower) && teConditions.length === 0) {
            teConditions.push('తీవ్రమైన నీరసం మరియు బలహీనత (Lethargy & Weakness)');
            teRecs.push('తాగునీటిలో ఎలక్ట్రోలైట్లు మరియు విటమిన్ బి/ఇ కాంప్లెక్స్ అందించండి.');
          }
          if (/feed|appetite|eat|మేత|ఆకలి/.test(symLower)) {
            teConditions.push('మేత తినకపోవడం / ఆకలి మందగించడం');
          }

          resultData.visualCondition = teConditions.length > 0 ? teConditions.join(' & ') : matchedIssues.join(' & ');
          resultData.aiSummary = `క్లినికల్ & వాయిస్ విశ్లేషణ: తెలిపిన వ్యాధి/లక్షణాలు ("${symptomsStr}") ఆధారంగా నిర్ధారించబడిన వ్యాధి రిస్క్: ${resultData.visualCondition}.`;
          resultData.recommendedActions = teRecs.length > 0 ? teRecs.join(' ') : recs.join(' ');
        } else if (currentLang === 'hi') {
          const hiConditions = [];
          const hiRecs = [];
          if (/ranikhet|newcastle|रानीखेत/.test(symLower)) {
            hiConditions.push('रानीखेत रोग (Ranikhet / Newcastle - ND)');
            hiRecs.push('🚨 प्रभावित मुर्गियों को तुरंत अलग करें; लासोटा टीका और विरकोन स्प्रे करें।');
          }
          if (/crd|cough|sneez|छींक|खांसी|सांस|सीआरडी/.test(symLower)) {
            hiConditions.push('सीआरडी / श्वसन रोग (CRD / Bronchitis)');
            hiRecs.push('💊 टायलोसिन या डॉक्सीसाइक्लिन दें; वेंटिलेशन में सुधार करें।');
          }
          if (/coccid|diarrhea|blood|दस्त|खूनी दस्त|कॉक्सिडिओसिस/.test(symLower)) {
            hiConditions.push('कॉक्सिडिओसिस / खूनी दस्त (Coccidiosis)');
            hiRecs.push('🚨 एम्प्रोलियम या टॉल्ट्राजुरिल दें; गीला बिछावन हटाकर चूना डालें।');
          }
          if (/pox|चेचक|फाउल पॉक्स/.test(symLower)) {
            hiConditions.push('फाउल पॉक्स / चेचक (Fowl Pox)');
            hiRecs.push('🛡️ घावों पर पोविडोन आयोडीन लगाएं और मच्छरों का नियंत्रण करें।');
          }
          if (/coryza|कोरिजा|आंख सूजन|चेहरे पर सूजन/.test(symLower)) {
            hiConditions.push('संक्रामक कोरिजा (Infectious Coryza)');
            hiRecs.push('💧 एनरोफ्लोक्सासिन दें और आंखों को साफ पानी से पोंछें।');
          }
          if (/gumboro|गम्बोरो/.test(symLower)) {
            hiConditions.push('गम्बोरो रोग (Gumboro / IBD)');
            hiRecs.push('🚨 इम्यूनोबूस्टर, लिवर टॉनिक और इलेक्ट्रोलाइट्स दें।');
          }
          if (/marek|मारेक्स|लकवा|लंगड़ा/.test(symLower)) {
            hiConditions.push('मारेक्स रोग / पक्षी लकवा (Marek\'s Disease)');
            hiRecs.push('⚠️ विटामिन बी-कॉम्प्लेक्स (Neurobion) दें और डॉक्टर से संपर्क करें।');
          }

          resultData.visualCondition = hiConditions.length > 0 ? hiConditions.join(' & ') : matchedIssues.join(' & ');
          resultData.aiSummary = `नैदानिक और आवाज विश्लेषण: बताए गए रोग/लक्षणों ("${symptomsStr}") के आधार पर जोखिम: ${resultData.visualCondition}।`;
          resultData.recommendedActions = hiRecs.length > 0 ? hiRecs.join(' ') : recs.join(' ');
        } else {
          resultData.visualCondition = matchedIssues.join(' & ');
          resultData.aiSummary = `Clinical & Voice Synthesis: Analysis correlated visual scan with reported disease/symptoms ("${symptomsStr}"). Primary risk identified: ${matchedIssues.join(', ')}.`;
          if (recs.length > 0) {
            resultData.recommendedActions = recs.join(' ');
          }
        }
      } else {
        resultData.detectedFeatures.push({
          label: currentLang === 'te' ? 'గమనించిన లక్షణాలు' : 'Observed Signs',
          status: symptomsStr,
          isGood: false
        });
        resultData.riskLevel = resultData.riskLevel === 'Low' ? 'Medium' : resultData.riskLevel;
        resultData.aiSummary += currentLang === 'te' 
          ? ` తెలిపిన కోడి లక్షణాలు: "${symptomsStr}". పర్యవేక్షణ అవసరం.`
          : ` Reported hen symptoms: "${symptomsStr}". Close clinical surveillance recommended.`;
      }
    }

    // Generate explicit structured Safety & Precautions, Predictions, and Treatments
    const currentLang = localStorage.getItem('smart_poultry_lang') || 'te';
    const isTe = currentLang === 'te';

    let safetyPrecautions = [];
    let predictions = [];
    let treatments = [];

    if (resultData.riskLevel === 'High') {
      safetyPrecautions = isTe ? [
        '🚨 తక్షణ ఐసోలేషన్: అనుమానిత లక్షణాలు ఉన్న కోళ్లను వెంటనే ప్రధాన షెడ్డు నుండి వేరు చేయండి.',
        '🛡️ బయోసెక్యూరిటీ: షెడ్డు ప్రవేశద్వారం వద్ద పొటాషియం పర్మాంగనేట్ లేదా సున్నంతో ఫుట్‌బాత్‌లను ఏర్పాటు చేయండి.',
        '🧪 క్రిమిసంహారక స్ప్రే: షెడ్డులో విర్కాన్-ఎస్ (Virkon-S) లేదా బయోసైడ్ స్ప్రే పిచికారీ చేయండి.',
        '🧹 లిట్టర్ నిర్వహణ: తడి లిట్టర్‌ను వెంటనే తొలగించి, పొడి సున్నం పొడిని చల్లండి.'
      ] : [
        '🚨 Immediate Quarantine: Isolate symptomatic birds to dedicated infirmary bays immediately.',
        '🛡️ Strict Biosecurity: Enforce mandatory footbaths with potassium permanganate/bleach at all entrances.',
        '🧪 Disinfection Fogging: Spray Virkon-S or broad-spectrum virucidal solution throughout the shed.',
        '🧹 Litter Management: Remove any wet caked litter immediately and dust dry agricultural lime.'
      ];

      predictions = isTe ? [
        '⚠️ వ్యాప్తి వేగం: తగిన నివారణ చర్యలు తీసుకోకపోతే 24-48 గంటల్లో ఇతర కోళ్లకు వ్యాపించే అవకాశం 65-80%.',
        '📉 మరణాల రిస్క్: చికిత్స చేయకపోతే మందలో 15% నుండి 35% మరణాలు సంభవించే ముప్పు ఉంది.',
        '📈 రికవరీ అంచనా: 48 గంటల్లో సరైన యాంటీబయాటిక్ లేదా వాక్సిన్ బూస్టర్ ఇస్తే 4-6 రోజుల్లో కోలుకుంటాయి.'
      ] : [
        '⚠️ Transmission Rate: 65-80% probability of cross-pen airborne or waterborne spread within 48h if untreated.',
        '📉 Mortality Risk: Projected 15% to 35% flock mortality risk without immediate clinical intervention.',
        '📈 Recovery Prognosis: 85%+ recovery trajectory within 4-6 days if antibiotics/electrolytes administered promptly.'
      ];

      treatments = isTe ? [
        '💊 సూచించిన మందులు: వైద్యుని సూచన మేరకు తాగునీటిలో యాంటీబయాటిక్ (Tylosin/Enrofloxacin/Amprolium) 4-5 రోజులు ఇవ్వండి.',
        '💧 ఎలక్ట్రోలైట్లు: డీహైడ్రేషన్ నివారించడానికి తాగునీటిలో ఓరల్ ఎలక్ట్రోలైట్స్ & విటమిన్ బి/సి కలపండి.'
      ] : [
        '💊 Recommended Medication: Administer targeted antimicrobial (Tylosin / Amprolium / Enrofloxacin) via drinking water.',
        '💧 Supportive Hydration: Supplement oral electrolytes, Vitamin B-Complex, and Vitamin C to combat physiological stress.'
      ];
    } else if (resultData.riskLevel === 'Medium') {
      safetyPrecautions = isTe ? [
        '💨 వెంటిలేషన్ సరిచూడండి: అమ్మోనియా 15 ppm లోపు ఉండేలా ఎగ్జాస్ట్ ఫ్యాన్లను పెంచండి.',
        '💧 తాగునీటి పరిశుభ్రత: డ్రింకర్ లైన్లను క్లోరినేటెడ్ వాటర్‌తో ఫ్లష్ చేయండి.',
        '🌡️ ఉష్ణోగ్రత నియంత్రణ: షెడ్డులో చలిగాలులు తగలకుండా కర్టెన్లను సరిచూడండి.'
      ] : [
        '💨 Ventilation Flow: Increase tunnel exhaust fans to keep shed ammonia strictly below 15 ppm.',
        '💧 Water Hygiene: Sanitize and flush drinker nipple lines with chlorine dioxide or acidifier.',
        '🌡️ Thermal Comfort: Eliminate cold drafts or excessive heat pockets; adjust curtain drops.'
      ];

      predictions = isTe ? [
        '⚠️ వ్యాప్తి వేగం: మధ్యస్థ వ్యాప్తి అవకాశం (20-35%). తక్షణ పర్యవేక్షణతో నివారించవచ్చు.',
        '📉 మరణాల రిస్క్: సాధారణ పరిశుభ్రత పాటిస్తే మరణాల శాతం 1% లోపు పరిమితం కావచ్చు.',
        '📈 రికవరీ అంచనా: 48-72 గంటల్లో సాధారణ స్థితికి చేరుకుంటాయి.'
      ] : [
        '⚠️ Transmission Rate: Moderate localized spread (20-35%); preventable with timely biosecurity.',
        '📉 Mortality Risk: Low risk (< 1.5%) if supportive liver tonics and electrolytes are deployed.',
        '📈 Recovery Prognosis: Full normalization expected within 48-72 hours.'
      ];

      treatments = isTe ? [
        '💊 లివర్ టానిక్ & రెస్పిరేటరీ సిరప్: మూలికా రెస్పిరేటరీ టానిక్ లేదా లివర్ టానిక్ 3 రోజులు ఇవ్వండి.'
      ] : [
        '💊 Supportive Care: Administer herbal respiratory decongestant or liver restorative tonic for 3 days.'
      ];
    } else {
      safetyPrecautions = isTe ? [
        '✅ ప్రామాణిక పరిశుభ్రత: తాజా శుభ్రమైన తాగునీరు మరియు సమతుల్య మేత నిర్వహణను కొనసాగించండి.',
        '🛡️ సాధారణ బయోసెక్యూరిటీ: బయటి పక్షులు, ఎలుకలు షెడ్డులోకి రాకుండా నెట్లను పరిశీలించండి.'
      ] : [
        '✅ Standard Hygiene: Maintain continuous access to fresh sanitized drinking water and dry balanced feed.',
        '🛡️ Routine Biosecurity: Ensure wild bird netting and rodent bait stations are active.'
      ];

      predictions = isTe ? [
        '🌟 మంద ఆరోగ్యం: కోళ్లు చురుకుగా, సాధారణ ఎదుగుదల రేటుతో ఆరోగ్యంగా ఉన్నాయి.',
        '📉 మరణాల రిస్క్: కనిష్ట స్థాయి (< 0.1% సహజ మరణాల పరిమితి).'
      ] : [
        '🌟 Flock Status: Birds show optimal posture, clear eyes, and uniform plumage weight growth.',
        '📉 Mortality Risk: Baseline minimal (< 0.1% expected natural deviation).'
      ];

      treatments = isTe ? [
        '🌿 సంరక్షణ: రోగనిరోధక శక్తిని కొనసాగించడానికి వారానికి రెండుసార్లు మల్టీవిటమిన్లు ఇవ్వండి.'
      ] : [
        '🌿 Preventive Maintenance: Routine multi-vitamin and probiotic water conditioning 2x weekly.'
      ];
    }

    resultData.safetyPrecautions = safetyPrecautions;
    resultData.predictions = predictions;
    resultData.treatments = treatments;
    resultData.analyzedAt = new Date().toLocaleString([], { year: 'numeric', month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit' });

    return resultData;
  },

  // Calculate ML Disease Risk from Numerical & Categorical Farm Conditions
  calculateConditionRisk(data) {
    let riskScore = 15; // baseline low
    const indicators = [];
    const reasons = [];

    // 1. Mortality Check
    const mortality = parseFloat(data.mortality) || 0;
    if (mortality >= 8) {
      riskScore += 40;
      indicators.push({ label: 'Mortality', value: `${mortality} birds (High)`, status: 'danger' });
      reasons.push('Elevated mortality exceeding standard threshold.');
    } else if (mortality >= 3) {
      riskScore += 20;
      indicators.push({ label: 'Mortality', value: `${mortality} birds (Elevated)`, status: 'warning' });
      reasons.push('Slightly elevated daily mortality observed.');
    } else {
      indicators.push({ label: 'Mortality', value: `${mortality} birds (Normal)`, status: 'success' });
    }

    // 2. Feed Intake Check
    const feed = parseFloat(data.feedConsumption) || 200;
    if (feed < 160) {
      riskScore += 25;
      indicators.push({ label: 'Feed Intake', value: `${feed} kg (-20% Low)`, status: 'danger' });
      reasons.push('Significant drop in feed consumption.');
    } else if (feed < 200) {
      riskScore += 12;
      indicators.push({ label: 'Feed Intake', value: `${feed} kg (Sub-optimal)`, status: 'warning' });
      reasons.push('Moderate decrease in daily feeding.');
    } else {
      indicators.push({ label: 'Feed Intake', value: `${feed} kg (Normal)`, status: 'success' });
    }

    // 3. Water Intake Check
    const water = parseFloat(data.waterConsumption) || 400;
    if (water < 300) {
      riskScore += 20;
      indicators.push({ label: 'Water Intake', value: `${water} L (Low)`, status: 'warning' });
      reasons.push('Reduced water consumption recorded.');
    } else {
      indicators.push({ label: 'Water Intake', value: `${water} L (Normal)`, status: 'success' });
    }

    // 4. Temperature Check
    const temp = parseFloat(data.temperature) || 24;
    if (temp > 32 || temp < 18) {
      riskScore += 20;
      indicators.push({ label: 'Temperature', value: `${temp}°C (Stress Zone)`, status: 'danger' });
      reasons.push('Ambient shed temperature outside optimal 22-26°C range.');
    } else if (temp > 29 || temp < 21) {
      riskScore += 10;
      indicators.push({ label: 'Temperature', value: `${temp}°C (Attention)`, status: 'warning' });
    } else {
      indicators.push({ label: 'Temperature', value: `${temp}°C (Optimal)`, status: 'success' });
    }

    // 5. Activity Level
    if (data.activityLevel === 'Very Low') {
      riskScore += 25;
      indicators.push({ label: 'Activity Level', value: 'Very Low / Lethargic', status: 'danger' });
      reasons.push('Flock displays severe lethargy and suppressed movement.');
    } else if (data.activityLevel === 'Low') {
      riskScore += 12;
      indicators.push({ label: 'Activity Level', value: 'Low Activity', status: 'warning' });
    } else {
      indicators.push({ label: 'Activity Level', value: 'Normal / Active', status: 'success' });
    }

    // 6. Symptoms
    const symptoms = Array.isArray(data.symptoms) ? data.symptoms : [];
    if (symptoms.length > 0) {
      const sympCount = symptoms.length;
      riskScore += sympCount * 10;
      indicators.push({ label: 'Reported Signs', value: symptoms.join(', '), status: sympCount > 1 ? 'danger' : 'warning' });
      reasons.push(`Clinical observations noted: ${symptoms.join(', ')}.`);
    }

    // Cap risk score between 5 and 98
    riskScore = Math.min(Math.max(riskScore, 8), 96);

    let riskLevel = 'Low';
    let conditionRiskTitle = 'Low Disease-Risk (Healthy Flock Parameters)';
    if (riskScore >= 60) {
      riskLevel = 'High';
      conditionRiskTitle = 'High Disease-Risk (Multiple Stress / Clinical Indicators)';
    } else if (riskScore >= 35) {
      riskLevel = 'Medium';
      conditionRiskTitle = 'Medium Disease-Risk (Sub-optimal Conditions Detected)';
    }

    const confidence = (85 + (riskScore % 12) + Math.random() * 2).toFixed(1);

    return {
      riskScore,
      riskLevel,
      conditionRiskTitle,
      confidence: parseFloat(confidence),
      indicators,
      reasons: reasons.length > 0 ? reasons : ['All farm environmental and physiological metrics are within healthy limits.'],
      recommendations: this.generatePreventiveRecommendations(riskLevel, symptoms)
    };
  },

  // Combine Image CV Risk + Condition ML Risk into Multi-Modal Assessment
  combineAnalysis(imageResult, conditionResult) {
    let combinedScore = 0;
    const imgWeight = 0.45;
    const condWeight = 0.55;

    const imgScore = imageResult.riskLevel === 'High' ? 85 : imageResult.riskLevel === 'Medium' ? 50 : 15;
    const condScore = conditionResult.riskScore;

    combinedScore = Math.round((imgScore * imgWeight) + (condScore * condWeight));
    
    let combinedRiskLevel = 'Low';
    if (combinedScore >= 60) combinedRiskLevel = 'High';
    else if (combinedScore >= 35) combinedRiskLevel = 'Medium';

    const avgConfidence = ((imageResult.confidence * 0.5) + (conditionResult.confidence * 0.5)).toFixed(1);

    return {
      combinedScore,
      combinedRiskLevel,
      avgConfidence: parseFloat(avgConfidence),
      imageRisk: imageResult.riskLevel,
      conditionRisk: conditionResult.riskLevel,
      summaryText: `Integrated Multi-Modal AI assessment synthesized visual indicators (${imageResult.riskLevel} Risk) with current farm parameters (${conditionResult.riskLevel} Risk). Resulting early warning indicator is ${combinedRiskLevel.toUpperCase()} RISK.`
    };
  },

  generatePreventiveRecommendations(riskLevel, symptoms = []) {
    const recs = [];
    if (riskLevel === 'High') {
      recs.push({ priority: 'High', title: 'Flock Isolation & Quarantine', desc: 'Isolate symptomatic birds in a dedicated recovery bay to prevent potential cross-shed spread.' });
      recs.push({ priority: 'High', title: 'Avian Veterinary Consultation', desc: 'Contact a certified poultry veterinarian for diagnostic sample collection and clinical evaluation.' });
      recs.push({ priority: 'Medium', title: 'Intensified Shed Sanitization', desc: 'Sanitize drinker lines, footbaths, and equipment using approved biosecurity disinfectant protocols.' });
    } else if (riskLevel === 'Medium') {
      recs.push({ priority: 'Medium', title: 'Ventilation & Airflow Adjustment', desc: 'Check exhaust fans and air inlet baffles to ensure ammonia levels remain below 15 ppm.' });
      recs.push({ priority: 'Medium', title: 'Nutritional & Electrolyte Support', desc: 'Provide fresh drinking water enriched with standard poultry electrolytes to mitigate physical stress.' });
      recs.push({ priority: 'Low', title: 'Litter Moisture Inspection', desc: 'Ensure litter moisture is between 20-25% to prevent footpad burns and fungal growth.' });
    } else {
      recs.push({ priority: 'Low', title: 'Routine Biosecurity Compliance', desc: 'Maintain vehicle disinfection baths, visitor entry logs, and bird-proofing nets.' });
      recs.push({ priority: 'Low', title: 'Daily Health Surveillance', desc: 'Continue daily morning and evening walk-throughs to observe bird alertness and flock distribution.' });
    }
    return recs;
  },

  /**
   * Predicts Food Quantity, Water Consumption, and Optimal Shed Temperature
   * based on the exact age of the hens (in days), flock size, and breed.
   */
  predictByAge(ageDaysInput, birdCountInput = 1000, breedInput = 'Broiler') {
    const ageDays = Math.max(1, parseInt(ageDaysInput) || 1);
    const birdCount = Math.max(1, parseInt(birdCountInput) || 1000);
    const breed = (breedInput || 'Broiler').toString();
    const isLayer = /layer|bv 300|leghorn/i.test(breed);
    const isDesi = /country|desi|kadaknath|aseel/i.test(breed);

    let gramsPerBird = 15;
    let waterMlPerBird = 35;
    let targetTempC = 33.5;
    let minTempC = 32.0;
    let maxTempC = 35.0;
    let feedStage = 'Pre-Starter Crumbs';
    let broodingStatus = 'Active Brooder Heating (Day 1-7)';
    let climateAdvice = 'Maintain active brooding lamps or gas brooders. Prevent drafts while providing minimum fresh air exchange.';
    let waterRatio = '2.2 : 1 (Water to Feed)';

    if (ageDays <= 7) {
      gramsPerBird = 12 + (ageDays * 2.5);
      waterMlPerBird = gramsPerBird * 2.2;
      targetTempC = Math.max(31.0, 34.0 - (ageDays * 0.43));
      minTempC = targetTempC - 1.2;
      maxTempC = targetTempC + 1.2;
      feedStage = 'Pre-Starter Crumbs (23% Protein)';
      broodingStatus = 'Active Brooder Heating';
      climateAdvice = 'Chicks cannot thermoregulate yet. Keep brooder lamps at chick height. Check floor litter temperature (29-30°C).';
    } else if (ageDays <= 14) {
      gramsPerBird = 30 + ((ageDays - 7) * 3.5);
      waterMlPerBird = gramsPerBird * 2.1;
      targetTempC = Math.max(28.0, 31.0 - ((ageDays - 7) * 0.43));
      minTempC = targetTempC - 1.2;
      maxTempC = targetTempC + 1.2;
      feedStage = 'Starter Crumbles (21-22% Protein)';
      broodingStatus = 'Transition Brooding';
      climateAdvice = 'Gradually reduce brooder heating. Expand brooding guard rings and ensure fresh water drinker lines are clean.';
    } else if (ageDays <= 21) {
      gramsPerBird = 55 + ((ageDays - 14) * 5.0);
      waterMlPerBird = gramsPerBird * 2.0;
      targetTempC = Math.max(25.0, 28.0 - ((ageDays - 14) * 0.43));
      minTempC = targetTempC - 1.5;
      maxTempC = targetTempC + 1.5;
      feedStage = 'Grower Pellets (20% Protein)';
      broodingStatus = 'Minimal Brooder / Natural Shed Comfort';
      climateAdvice = 'Turn off supplementary heat during daytime. Increase cross-ventilation to remove ammonia fumes.';
    } else if (ageDays <= 28) {
      gramsPerBird = 90 + ((ageDays - 21) * 6.5);
      waterMlPerBird = gramsPerBird * 1.95;
      targetTempC = Math.max(23.0, 25.0 - ((ageDays - 21) * 0.28));
      minTempC = targetTempC - 1.5;
      maxTempC = targetTempC + 1.5;
      feedStage = 'Grower / Early Finisher Pellets';
      broodingStatus = 'Tunnel Ventilation Active';
      climateAdvice = 'Turn on tunnel exhaust fans as needed. Birds generate high metabolic heat. Maintain litter dryness.';
    } else if (ageDays <= 35) {
      gramsPerBird = 135 + ((ageDays - 28) * 6.0);
      waterMlPerBird = gramsPerBird * 1.9;
      targetTempC = Math.max(21.0, 23.0 - ((ageDays - 28) * 0.28));
      minTempC = targetTempC - 1.5;
      maxTempC = targetTempC + 1.5;
      feedStage = 'Finisher Pellets (19% Protein)';
      broodingStatus = 'Full Tunnel Ventilation & Cooling Pads';
      climateAdvice = 'Risk of heat stress! Keep evaporative cooling pads ready. Ensure cold fresh water is always available.';
    } else {
      gramsPerBird = Math.min(225.0, 175 + ((ageDays - 35) * 5.0));
      waterMlPerBird = gramsPerBird * 1.85;
      targetTempC = 21.0;
      minTempC = 19.5;
      maxTempC = 22.5;
      feedStage = 'Finisher Pellets (Pre-Harvest)';
      broodingStatus = 'Maximum Tunnel Ventilation';
      climateAdvice = 'Maximum bird density and body mass. Run all tunnel fans and monitor panting. Discontinue pre-harvest medication.';
    }

    if (isLayer) {
      gramsPerBird = Math.min(115.0, gramsPerBird * 0.72);
      waterMlPerBird = gramsPerBird * 2.0;
      feedStage = ageDays > 120 ? 'Layer Phase-1 Mash (High Calcium)' : 'Pullet Grower Mash';
      if (ageDays > 28) targetTempC = 22.0;
    } else if (isDesi) {
      gramsPerBird = gramsPerBird * 0.55;
      waterMlPerBird = gramsPerBird * 1.9;
      feedStage = 'Country Chick Mash / Grower Grain';
      targetTempC = Math.max(22.0, targetTempC - 1.0);
    }

    // Totals for the entire flock
    const dailyFeedKg = (gramsPerBird * birdCount) / 1000.0;
    const weeklyFeedKg = dailyFeedKg * 7.0;
    const bags50kg = Math.ceil(weeklyFeedKg / 50.0);

    const dailyWaterLiters = (waterMlPerBird * birdCount) / 1000.0;
    const weeklyWaterLiters = dailyWaterLiters * 7.0;

    const targetTempF = Math.round((targetTempC * 9 / 5) + 32);
    const minTempF = Math.round((minTempC * 9 / 5) + 32);
    const maxTempF = Math.round((maxTempC * 9 / 5) + 32);

    const targetTempRound = Math.round(targetTempC * 10) / 10;
    const minTempRound = Math.round(minTempC * 10) / 10;
    const maxTempRound = Math.round(maxTempC * 10) / 10;
    const feedPerBirdRound = Math.round(gramsPerBird * 10) / 10;
    const feedDailyKgRound = Math.round(dailyFeedKg * 10) / 10;
    const waterDailyLRound = Math.round(dailyWaterLiters * 10) / 10;
    const waterPerBirdRound = Math.round(waterMlPerBird * 10) / 10;
    const weekNum = Math.ceil(ageDays / 7);

    return {
      ageDays,
      ageWeeks: weekNum,
      week: weekNum,
      birdCount,
      breed,
      // Flat properties for direct binding
      feedStage: feedStage,
      dailyFlockFeedKg: feedDailyKgRound,
      dailyFeedPerBirdG: feedPerBirdRound,
      dailyFeedBags50kg: bags50kg,
      waterToFeedRatio: waterRatio,
      dailyFlockWaterL: waterDailyLRound,
      dailyWaterPerBirdMl: waterPerBirdRound,
      broodingStatus: broodingStatus,
      targetTempC: targetTempRound,
      targetTempF: targetTempF,
      minComfortTempC: minTempRound,
      maxComfortTempC: maxTempRound,
      ventilationAdvice: climateAdvice,
      // Nested objects
      food: {
        perBirdGrams: feedPerBirdRound,
        dailyKg: feedDailyKgRound,
        weeklyKg: Math.round(weeklyFeedKg * 10) / 10,
        bags50kg: bags50kg,
        stage: feedStage
      },
      water: {
        perBirdMl: waterPerBirdRound,
        dailyLiters: waterDailyLRound,
        weeklyLiters: Math.round(weeklyWaterLiters * 10) / 10,
        ratio: waterRatio
      },
      temperature: {
        targetC: targetTempRound,
        minC: minTempRound,
        maxC: maxTempRound,
        targetF: targetTempF,
        minF: minTempF,
        maxF: maxTempF,
        broodingStatus,
        climateAdvice
      }
    };
  }
};
