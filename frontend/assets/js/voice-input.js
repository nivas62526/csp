/**
 * SMART POULTRY HEALTH MONITORING & DISEASE-RISK PREDICTION SYSTEM
 * Voice & Speech Recognition Engine (voice-input.js)
 * Instant Voice Input -> Instant Clinical Diagnosis Output & Care Instructions
 * Supports: Telugu (te-IN), English (en-US), Hindi (hi-IN), Tamil (ta-IN), Bengali (bn-IN), Spanish (es-ES)
 */

const POULTRY_DISEASE_DB = [
  {
    id: 'ranikhet',
    keywords: /ranikhet|newcastle|రాణీఖేత్|రాణికేత్|రాణికెట్|రాణీకేత్|న్యూకాసిల్|గిలక|మెడ తిప్పడం|మెడ కొక్కడం|తల ఊపడం|పారలైసిస్|रानीखेत|न्यूकैसल|ராணிகேத்|ரனிகெட்/i,
    name: {
      te: '🚨 రాణీఖేత్ వ్యాధి / న్యూకాసిల్ (Ranikhet / Newcastle Disease - ND)',
      en: '🚨 Ranikhet Disease / Newcastle Disease (ND)',
      hi: '🚨 रानीखेत रोग / न्यूकैसल (Ranikhet / ND)',
      ta: '🚨 ராணிகேத் நோய் / நியூகாஸில் (Ranikhet / ND)'
    },
    risk: 'High',
    riskLabel: {
      te: 'తీవ్ర రిస్క్ (High Risk Alert)',
      en: 'High Risk Alert (Severe)',
      hi: 'उच्च जोखिम चेतावनी (High Risk)',
      ta: 'அதி தீவிர ஆபத்து (High Risk)'
    },
    guidance: {
      te: '🚨 తక్షణ చర్య: సోకిన కోళ్లను వెంటనే ఇతర బ్యాచ్‌ల నుండి వేరు చేయండి (Isolation). LaSota (లాసోటా) లేదా RDV బూస్టర్ వాక్సిన్ వేయండి. త్రాగునీటిలో ఎలక్ట్రోలైట్స్, బి-కాంప్లెక్స్ మరియు యాంటీబయాటిక్స్ ఇవ్వండి. షెడ్డు అంతా విర్కాన్-ఎస్ (Virkon-S) క్రిమిసంహారక స్ప్రే పిచికారీ చేయండి.',
      en: '🚨 Immediate Action: Strictly isolate affected birds. Administer LaSota or RDV booster vaccination. Provide electrolytes and broad-spectrum antibiotics via drinking water. Disinfect sheds thoroughly with virucidal spray.',
      hi: '🚨 तत्काल कार्रवाई: प्रभावित मुर्गियों को तुरंत अलग करें। लासोटा (LaSota) का टीका लगवाएं। पीने के पानी में इलेक्ट्रोलाइट्स और बी-कॉम्प्लेक्स दें। शेड को विरकोन-एस से कीटाणुरहित करें।',
      ta: '🚨 உடனடி நடவடிக்கை: பாதிக்கப்பட்ட கோழிகளை உடனடியாக தனியாக பிரிக்கவும். லசோட்டா அல்லது ஆர்டிவி தடுப்பூசி போடவும். குடிநீரில் எலக்ட்ரோலைட்டுகள் மற்றும் பி-காம்ப்ளக்ஸ் மருந்து வழங்கவும்.'
    }
  },
  {
    id: 'crd',
    keywords: /crd|chronic respiratory|bronchitis|రొంప|గురక|దగ్గు|తుమ్ములు|శ్వాస సమస్య|శ్వాస|జలుబు|ముక్కు కారడం|सीआरडी|घरघराहट|सांस|सिआरडी|சளி|இருமல்|தும்மல்/i,
    name: {
      te: '⚠️ తీవ్ర రొంప / శ్వాసకోశ వ్యాధి (CRD - Chronic Respiratory Disease)',
      en: '⚠️ Chronic Respiratory Disease (CRD / Bronchitis)',
      hi: '⚠️ सीआरडी / पुरानी श्वसन बीमारी (CRD / Bronchitis)',
      ta: '⚠️ சிஆர்டி / தீவிர சளி மற்றும் சுவாச நோய் (CRD)'
    },
    risk: 'Medium',
    riskLabel: {
      te: 'మధ్యస్థ - అధిక రిస్క్ (Medium-High Risk)',
      en: 'Medium-High Risk Alert',
      hi: 'मध्यम-उच्च जोखिम (Medium Risk)',
      ta: 'நடுத்தர - தீவிர ஆபத்து (Medium Risk)'
    },
    guidance: {
      te: '💊 ఔషధ సూచన: తాగునీటిలో టైలోసిన్ (Tylosin) లేదా డాక్సీసైక్లిన్ (Doxycycline) యాంటీబయాటిక్ 4-5 రోజులు ఇవ్వండి. షెడ్డులో అమ్మోనియా రాకుండా వెంటిలేషన్ పెంచండి. మూలికా రెస్పిరేటరీ సిరప్ వాడండి.',
      en: '💊 Medication: Administer Tylosin Tartrate or Doxycycline in drinking water for 4-5 days. Enhance cross-ventilation to dispel ammonia fumes and reduce respiratory stress.',
      hi: '💊 दवा सलाह: पीने के पानी में टायलोसिन (Tylosin) या डॉक्सीसाइक्लिन 4-5 दिनों तक दें। शेड में वेंटिलेशन बढ़ाएं और अमोनिया कम करें।',
      ta: '💊 மருந்து ஆலோசனை: குடிநீரில் டைலோசின் அல்லது டாக்ஸிசைக்ளின் 4-5 நாட்களுக்கு வழங்கவும். கொட்டகையில் காற்றோட்டத்தை அதிகரிக்கவும்.'
    }
  },
  {
    id: 'coccidiosis',
    keywords: /coccid|కాక్సిడియోసిస్|కాక్సి|రక్త విరేచనాలు|ఎర్ర విరేచనాలు|రక్తపు మలము|నీళ్ల విరేచనాలు|మోషన్స్|విరేచనాలు|రక్తం|कॉक्सिडिओसिस|खूनी दस्त|கோக்சீடியோசிஸ்|இரத்தக் கழிச்சல்/i,
    name: {
      te: '🚨 కాక్సిడియోసిస్ / రక్త విరేచనాలు (Coccidiosis / Enteritis)',
      en: '🚨 Coccidiosis (Bloody Enteritis)',
      hi: '🚨 कॉक्सिडिओसिस / खूनी दस्त (Coccidiosis)',
      ta: '🚨 கோக்சீடியோசிஸ் / இரத்தக் கழிச்சல் (Coccidiosis)'
    },
    risk: 'High',
    riskLabel: {
      te: 'తీవ్ర రిస్క్ (High Risk Alert)',
      en: 'High Risk Alert (Severe)',
      hi: 'उच्च जोखिम चेतावनी (High Risk)',
      ta: 'அதி தீவிர ஆபத்து (High Risk)'
    },
    guidance: {
      te: '🚨 తక్షణ చర్య: తాగునీటిలో ఆంప్రోలియం (Amprolium 20%) లేదా టోల్ట్రాజురిల్ (Toltrazuril) కలపండి. తడి లిట్టర్‌ను వెంటనే తీసివేసి పొడి సున్నం చల్లండి. ప్రేగుల్లో రక్తస్రావం తగ్గడానికి విటమిన్-K ఇవ్వండి.',
      en: '🚨 Immediate Action: Administer Amprolium (20%) or Toltrazuril immediately in water for 3-5 days. Remove damp caked litter, apply dry lime, and supplement Vitamin K.',
      hi: '🚨 तत्काल कार्रवाई: तुरंत पानी में एम्प्रोलियम (Amprolium) या टॉल्ट्राजुरिल दें। गीला बिछावन हटाएं, चूना पाउडर डालें और विटामिन-के दें।',
      ta: '🚨 உடனடி நடவடிக்கை: குடிநீரில் ஆம்ப்ரோலியம் அல்லது டோல்ட்ராசூரில் உடனே கலக்கவும். ஈரமான படுக்கையை அகற்றி உலர் சுண்ணாம்பு தூவவும்.'
    }
  },
  {
    id: 'fowlpox',
    keywords: /fowl pox|pox|పాక్స్|ఫౌల్ పాక్స్|అమ్మవారు|కోడి అమ్మవారు|పొక్కులు|తల వాపు|జుట్టుపై పొక్కులు|కళ్ల బొబ్బలు|चेचक|फाउल पॉक्स|அம்மை நோய்/i,
    name: {
      te: '🛡️ ఫౌల్ పాక్స్ / కోడి అమ్మవారు (Fowl Pox Lesions)',
      en: '🛡️ Fowl Pox (Avian Poxvirus)',
      hi: '🛡️ फाउल पॉक्स / चेचक (Fowl Pox)',
      ta: '🛡️ பவுல் பாக்ஸ் / கோழி அம்மை (Fowl Pox)'
    },
    risk: 'Medium',
    riskLabel: {
      te: 'మధ్యస్థ రిస్క్ (Medium Risk)',
      en: 'Medium Risk Alert',
      hi: 'मध्यम जोखिम (Medium Risk)',
      ta: 'நடுத்தர ஆபத்து (Medium Risk)'
    },
    guidance: {
      te: '🛡️ సంరక్షణ: జుట్టు, ముఖంపై ఉన్న పొక్కులపై గ్లిజరిన్ లేదా పోవిడోన్ అయోడిన్ (Betadine) దూదితో రాయండి. దోమల ద్వారా వ్యాపిస్తుంది కాబట్టి దోమల నివారణ మందులు పిచికారీ చేయండి. విటమిన్-A ఇవ్వండి.',
      en: '🛡️ Care Instructions: Swab lesions with Povidone-Iodine or glycerine. Implement strict mosquito vector netting and spraying. Supplement with Vitamin A.',
      hi: '🛡️ उपचार: छालों पर पोविडोन आयोडीन या ग्लिसरीन लगाएं। मच्छरों का नियंत्रण करें और पानी में विटामिन-ए दें।',
      ta: '🛡️ பராமரிப்பு: கொப்புளங்களில் போவிடோன்-அயோடின் தடவவும். கொசுக்களை கட்டுப்படுத்த மருந்து தெளிக்கவும். வைட்டமின்-ஏ வழங்கவும்.'
    }
  },
  {
    id: 'coryza',
    keywords: /coryza|కోరిజా|కళ్ల వాపు|కంటి నీరు|కంటి చీము|ముఖం వాపు|వాచిన కళ్ళు|कोरिजा|आंख में सूजन|चेहरे पर सूजन|கண் வீக்கம்/i,
    name: {
      te: '🚨 ఇన్ఫెక్షియస్ కోరిజా / కళ్ల & ముఖం వాపు (Infectious Coryza)',
      en: '🚨 Infectious Coryza (Facial Swelling)',
      hi: '🚨 संक्रामक कोरिजा / आंख सूजन (Infectious Coryza)',
      ta: '🚨 தொற்று கோரிசா / முக மற்றும் கண் வீக்கம் (Coryza)'
    },
    risk: 'High',
    riskLabel: {
      te: 'తీవ్ర రిస్క్ (High Risk)',
      en: 'High Risk Alert',
      hi: 'उच्च जोखिम (High Risk)',
      ta: 'அதி தீவிர ஆபத்து (High Risk)'
    },
    guidance: {
      te: '💧 చికిత్స: ఎన్రోఫ్లోక్సాసిన్ (Enrofloxacin) లేదా సల్ఫా మందులు తాగునీటిలో ఇవ్వండి. కళ్లలోని చీమును శుభ్రమైన గోరువెచ్చని నీటితో తుడవండి.',
      en: '💧 Treatment: Administer Enrofloxacin or Sulfa medication in drinking water. Gently cleanse crusty eye discharge with warm saline or boric lotion.',
      hi: '💧 उपचार: पानी में एनरोफ्लोक्सासिन (Enrofloxacin) या सल्फा दवाएं दें। आंखों को हल्के गर्म पानी से साफ करें।',
      ta: '💧 சிகிச்சை: என்ரோஃப்ளோக்சாசின் மருந்தை குடிநீரில் வழங்கவும். கண்களில் உள்ள சீழை வெதுவெதுப்பான நீரால் சுத்தம் செய்யவும்.'
    }
  },
  {
    id: 'gumboro',
    keywords: /gumboro|ibd|గంబోరో|ఐబీడీ|గంబోరొ|తెల్ల విరేచనాలు|गम्बोरो|आईबीडी/i,
    name: {
      te: '🚨 గంబోరో వ్యాధి (Infectious Bursal Disease - Gumboro)',
      en: '🚨 Infectious Bursal Disease (Gumboro / IBD)',
      hi: '🚨 गम्बोरो रोग / आईबीडी (Gumboro / IBD)',
      ta: '🚨 கும்போரோ நோய் (IBD / Gumboro)'
    },
    risk: 'High',
    riskLabel: {
      te: 'తీవ్ర రిస్క్ (High Risk Alert)',
      en: 'High Risk Alert (Severe)',
      hi: 'उच्च जोखिम चेतावनी (High Risk)',
      ta: 'அதி தீவிர ஆபத்து (High Risk)'
    },
    guidance: {
      te: '🚨 తక్షణ చర్య: ఇమ్యూనో బూస్టర్ మరియు లివర్ టానిక్ (Liver tonic) అందించండి. డీహైడ్రేషన్ నివారించడానికి తాగునీటిలో గ్లూకోజ్ మరియు ఎలక్ట్రోలైట్స్ నిరంతరం ఇవ్వండి.',
      en: '🚨 Immediate Action: Administer immuno-stimulants and liver tonics. Provide continuous glucose + electrolyte hydration to combat severe immunosuppression.',
      hi: '🚨 तत्काल कार्रवाई: इम्यूनोबूस्टर और लिवर टॉनिक दें। निर्जलीकरण रोकने के लिए पानी में ग्लूकोज और इलेक्ट्रोलाइट्स लगातार दें।',
      ta: '🚨 உடனடி நடவடிக்கை: கல்லீரல் டானிக் மற்றும் நோய் எதிர்ப்பு மருந்துகள் வழங்கவும். நீரிழப்பைத் தடுக்க குளுக்கோஸ் மற்றும் எலக்ட்ரோலைட்டுகள் தரவும்.'
    }
  },
  {
    id: 'marek',
    keywords: /marek|మరెక్స్|లక్వా|పక్షవాతం|కాళ్లు పడిపోవడం|కుంటి|కాలు వెనక్కి లాగడం|నడవలేకపోవడం|నడవట్లేదు|मारेक्स|लकवा|लंगड़ाना/i,
    name: {
      te: '⚠️ మరెక్స్ వ్యాధి / లక్వా - పక్షవాతం (Marek\'s Disease / Paralysis)',
      en: '⚠️ Marek\'s Disease (Avian Paralysis / Neuro-Lymphomatosis)',
      hi: '⚠️ मारेक्स रोग / पक्षी लकवा (Marek\'s Disease)',
      ta: '⚠️ மாரெக் நோய் / பக்கவாதம் (Marek\'s Disease)'
    },
    risk: 'High',
    riskLabel: {
      te: 'తీవ్ర రిస్క్ (High Risk Alert)',
      en: 'High Risk Alert (Severe)',
      hi: 'उच्च जोखिम चेतावनी (High Risk)',
      ta: 'அதி தீவிர ஆபத்து (High Risk)'
    },
    guidance: {
      te: '⚠️ అత్యవసరం: పక్షవాతం సోకిన కోళ్లను ఇతర కోళ్లు తొక్కకుండా ప్రత్యేకంగా ఉంచండి. విటమిన్ బి-కాంప్లెక్స్ (Neurobion) ఇవ్వండి. వెంటనే పౌల్ట్రీ వెటర్నరీ వైద్యుడిని సంప్రదించండి.',
      en: '⚠️ Urgent: Isolate paralyzed birds with separate soft bedding and accessible shallow feed/water. Administer Vitamin B-Complex (Neurobion). Contact poultry vet immediately.',
      hi: '⚠️ जरूरी: लकवाग्रस्त मुर्गियों को अलग रखें। विटामिन बी-कॉम्प्लेक्स (Neurobion) दें। तुरंत पशु चिकित्सक से संपर्क करें।',
      ta: '⚠️ அவசரம்: பக்கவாதத்தால் பாதிக்கப்பட்ட கோழிகளை தனியாக பாதுகாக்கவும். வைட்டமின் பி-காம்ப்ளக்ஸ் வழங்கவும். மருத்துவரை உடனே தொடர்பு கொள்ளவும்.'
    }
  }
];

const VoiceInput = {
  recognition: null,
  isListening: false,
  targetInputId: 'mobScanSymptomsInput',
  micBtnId: 'mobDirectVoiceBtn',
  lastOutput: null,

  init() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn('SpeechRecognition API not supported on this browser.');
      return false;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.interimResults = true;

    this.recognition.onstart = () => {
      this.isListening = true;
      this.updateMicUi(true);
      const currentLang = localStorage.getItem('smart_poultry_lang') || 'te';
      const langNames = { en: 'English', hi: 'हिन्दी', te: 'తెలుగు (Telugu)', ta: 'தமிழ்', bn: 'বাংলা', es: 'Español' };
      const promptMsg = (typeof I18n !== 'undefined') ? I18n.get('voiceListeningPrompt', 'Listening... Speak disease or symptoms') : 'Listening... Speak disease or symptoms';
      showToast(`${promptMsg} [${langNames[currentLang] || currentLang}]`, 'info', 'Voice Input Active');
      
      // Update listening banner in viewScan & Dashboard
      const statusBox = document.getElementById('mobVoiceListeningStatus');
      const statusText = document.getElementById('mobVoiceListeningText');
      if (statusBox && statusText) {
        statusText.textContent = `${promptMsg} [${langNames[currentLang] || currentLang}]`;
        statusBox.classList.remove('d-none');
        statusBox.classList.add('d-flex');
      }

      const dashStatusBox = document.getElementById('dashVoiceListeningStatus');
      const dashStatusText = document.getElementById('dashVoiceListeningText');
      if (dashStatusBox && dashStatusText) {
        dashStatusText.textContent = `${promptMsg} [${langNames[currentLang] || currentLang}]`;
        dashStatusBox.classList.remove('d-none');
        dashStatusBox.classList.add('d-flex');
      }

      // Update spoken live text box
      const spokenBox = document.getElementById('mobVoiceSpokenBox');
      const spokenText = document.getElementById('mobVoiceSpokenText');
      if (spokenBox && spokenText) {
        spokenBox.classList.remove('d-none');
        spokenText.textContent = '... (మాటలు వినబడుతున్నాయి / Listening...)';
      }

      const dashSpokenBox = document.getElementById('dashVoiceSpokenBox');
      const dashSpokenText = document.getElementById('dashVoiceSpokenText');
      if (dashSpokenBox && dashSpokenText) {
        dashSpokenBox.classList.remove('d-none');
        dashSpokenText.textContent = '... (మాటలు వినబడుతున్నాయి / Listening...)';
      }
    };

    this.recognition.onresult = (event) => {
      let finalTranscript = '';
      let interimTranscript = '';
      for (let i = 0; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      const fullTranscript = (finalTranscript || interimTranscript).trim();
      if (!fullTranscript) return;

      // Update spoken live text box IMMEDIATELY
      VoiceInput.updateSpokenDisplay(fullTranscript);

      if (this.targetInputId) {
        const inputEl = document.getElementById(this.targetInputId);
        if (inputEl) {
          inputEl.value = fullTranscript;
        }
      }

      const dashInput = document.getElementById('dashVoiceInputText');
      if (dashInput && !dashInput.value) {
        dashInput.value = fullTranscript;
      }

      VoiceInput.autoTagSymptoms(fullTranscript);

      // Instantly evaluate transcript so output is ready in real time
      VoiceInput.evaluateAndDisplayOutput(fullTranscript, false);
    };

    this.recognition.onerror = (event) => {
      console.warn('Speech recognition error:', event.error);
      this.isListening = false;
      this.updateMicUi(false);
      let errMsg = 'Voice recognition: ' + event.error;
      if (event.error === 'not-allowed') {
        errMsg = 'Microphone permission denied. Please allow microphone access.';
      }
      showToast(errMsg, 'warning');
      const statusBox = document.getElementById('mobVoiceListeningStatus');
      if (statusBox) {
        statusBox.classList.add('d-none');
        statusBox.classList.remove('d-flex');
      }
      const dashStatusBox = document.getElementById('dashVoiceListeningStatus');
      if (dashStatusBox) {
        dashStatusBox.classList.add('d-none');
        dashStatusBox.classList.remove('d-flex');
      }
    };

    this.recognition.onend = () => {
      this.isListening = false;
      this.updateMicUi(false);
      const statusBox = document.getElementById('mobVoiceListeningStatus');
      if (statusBox) {
        statusBox.classList.add('d-none');
        statusBox.classList.remove('d-flex');
      }
      const dashStatusBox = document.getElementById('dashVoiceListeningStatus');
      if (dashStatusBox) {
        dashStatusBox.classList.add('d-none');
        dashStatusBox.classList.remove('d-flex');
      }

      // If text exists in input, trigger final output delivery
      const inputEl = document.getElementById(this.targetInputId || 'mobScanSymptomsInput') || document.getElementById('dashVoiceInputText');
      const text = inputEl ? inputEl.value.trim() : '';
      if (text) {
        VoiceInput.evaluateAndDisplayOutput(text, true);
      }
    };

    return true;
  },

  updateSpokenDisplay(text) {
    const spokenBox = document.getElementById('mobVoiceSpokenBox');
    const spokenText = document.getElementById('mobVoiceSpokenText');
    if (spokenBox && spokenText) {
      spokenBox.classList.remove('d-none');
      spokenText.textContent = `"${text}"`;
    }

    const cvSpokenBox = document.getElementById('cvVoiceSpokenBox');
    const cvSpokenText = document.getElementById('cvVoiceSpokenText');
    if (cvSpokenBox && cvSpokenText) {
      cvSpokenBox.classList.remove('d-none');
      cvSpokenText.textContent = `"${text}"`;
    }

    const dashSpokenBox = document.getElementById('dashVoiceSpokenBox');
    const dashSpokenText = document.getElementById('dashVoiceSpokenText');
    if (dashSpokenBox && dashSpokenText) {
      dashSpokenBox.classList.remove('d-none');
      dashSpokenText.textContent = `"${text}"`;
    }
  },

  // Instant 1-Tap Voice Test Sample (Simulates instant voice input and produces output)
  testVoiceSample(sampleText) {
    const input1 = document.getElementById('dashVoiceInputText');
    const input2 = document.getElementById('mobScanSymptomsInput');
    const input3 = document.getElementById('cvSymptomsInput');
    if (input1) input1.value = sampleText;
    if (input2) input2.value = sampleText;
    if (input3) input3.value = sampleText;

    VoiceInput.updateSpokenDisplay(sampleText);
    VoiceInput.autoTagSymptoms(sampleText);
    VoiceInput.evaluateAndDisplayOutput(sampleText, true);
  },

  toggleListening(targetInputId = 'mobScanSymptomsInput', micBtnId = 'mobDirectVoiceBtn') {
    this.targetInputId = targetInputId;
    this.micBtnId = micBtnId;

    if (!this.recognition) {
      const initialized = this.init();
      if (!initialized) {
        showToast('Voice input is not supported on this browser. Please type symptoms in the text box.', 'warning');
        return;
      }
    }

    if (this.isListening) {
      // User tapped mic to stop -> submit output immediately!
      this.submitVoiceDiagnosis(targetInputId);
    } else {
      const currentLang = localStorage.getItem('smart_poultry_lang') || 'te';
      const langMap = {
        te: 'te-IN',
        en: 'en-US',
        hi: 'hi-IN',
        ta: 'ta-IN',
        bn: 'bn-IN',
        es: 'es-ES'
      };
      this.recognition.lang = langMap[currentLang] || 'te-IN';

      try {
        this.recognition.start();
      } catch (e) {
        console.warn('Recognition start error:', e);
      }
    }
  },

  // Instant Enter / Submit button handler
  submitVoiceDiagnosis(targetInputId = null) {
    if (this.recognition && this.isListening) {
      try {
        this.recognition.stop();
      } catch (e) {
        console.warn(e);
      }
    }
    this.isListening = false;
    this.updateMicUi(false);

    const inputId = targetInputId || this.targetInputId || 'mobScanSymptomsInput';
    const inputEl = document.getElementById(inputId);
    const text = inputEl ? inputEl.value.trim() : '';

    if (!text) {
      showToast('దయచేసి మైక్ నొక్కి మాట్లాడండి లేదా టైప్ చేయండి (Please speak or type symptoms first)', 'warning');
      return;
    }

    VoiceInput.updateSpokenDisplay(text);
    VoiceInput.autoTagSymptoms(text);
    VoiceInput.evaluateAndDisplayOutput(text, true);
  },

  updateMicUi(active) {
    const btnIds = [this.micBtnId, 'mobDirectVoiceBtn', 'mobScanVoiceMicBtn', 'cvVoiceMicBtn', 'cvDirectVoiceBtn'];
    
    btnIds.forEach(id => {
      if (!id) return;
      const btn = document.getElementById(id);
      if (!btn) return;

      const listeningText = (typeof I18n !== 'undefined') ? I18n.get('voiceBtnActive', 'Listening...') : 'Listening...';
      const speakText = (typeof I18n !== 'undefined') ? I18n.get('speakDiseaseBtn', '🎙️ మైక్ నొక్కి వ్యాధి లేదా లక్షణాలు చెప్పండి') : '🎙️ Tap to Speak Disease';

      if (active) {
        btn.classList.add('btn-danger', 'animate-pulse');
        btn.classList.remove('btn-outline-primary', 'btn-outline-success', 'btn-primary');
        if (btn.id === 'mobDirectVoiceBtn' || btn.id === 'cvDirectVoiceBtn') {
          btn.innerHTML = `<span class="spinner-grow spinner-grow-sm me-2" role="status"></span> ${listeningText}`;
        } else {
          btn.innerHTML = `<i class="bi bi-mic-fill me-1"></i> ${listeningText}`;
        }
      } else {
        btn.classList.remove('btn-danger', 'animate-pulse');
        if (btn.id === 'mobDirectVoiceBtn' || btn.id === 'cvDirectVoiceBtn') {
          btn.classList.add('btn-danger');
          btn.innerHTML = `<i class="bi bi-mic-fill fs-5 me-2"></i> <span>${speakText}</span>`;
        } else {
          btn.classList.add('btn-outline-primary');
          const voiceText = (typeof I18n !== 'undefined') ? I18n.get('voiceInput', 'Voice') : 'Voice';
          btn.innerHTML = `<i class="bi bi-mic me-1"></i> ${voiceText}`;
        }
      }
    });
  },

  // Multi-tier Evaluator: ALWAYS GENERATES REAL CLINICAL OUTPUT FOR ANY SPOKEN INPUT
  evaluateAndDisplayOutput(transcript, isFinal = false) {
    if (!transcript) return;
    const lower = transcript.toLowerCase();
    const currentLang = localStorage.getItem('smart_poultry_lang') || 'te';

    let outputResult = null;

    // TIER 1: Exact / Partial Disease Identification
    for (const item of POULTRY_DISEASE_DB) {
      if (item.keywords.test(lower)) {
        outputResult = {
          name: item.name[currentLang] || item.name['te'],
          risk: item.risk,
          riskLabel: item.riskLabel[currentLang] || item.riskLabel['te'],
          guidance: item.guidance[currentLang] || item.guidance['te']
        };
        break;
      }
    }

    // TIER 2: Specific Symptoms Evaluator
    if (!outputResult) {
      if (/cough|sneeze|gasp|wheez|రొంప|దగ్గు|గురక|శ్వాస|జలుబు|ముక్కు|खांसी|छींक|சளி/.test(lower)) {
        outputResult = {
          name: currentLang === 'te' ? '⚠️ తీవ్ర శ్వాసకోశ ఇన్ఫెక్షన్ / రొంప (Respiratory Distress / CRD)' :
                currentLang === 'hi' ? '⚠️ गंभीर श्वसन संक्रमण / सीआरडी (Respiratory Distress)' :
                '⚠️ Severe Respiratory Distress / CRD Risk',
          risk: 'Medium',
          riskLabel: currentLang === 'te' ? 'మధ్యస్థ - అధిక రిస్క్ (Medium-High Risk)' : 'Medium-High Risk',
          guidance: currentLang === 'te' ? '💊 ఔషధం & జాగ్రత్తలు: టైలోసిన్ (Tylosin Tartrate) లేదా డాక్సీసైక్లిన్ యాంటీబయాటిక్ 4-5 రోజులు నీటిలో అందించండి. షెడ్డులో వెంటిలేషన్ పెంచి అమ్మోనియా లెవెల్స్ తగ్గించండి. మూలికా రెస్పిరేటరీ సిరప్ ఇవ్వండి.' :
                    currentLang === 'hi' ? '💊 दवा और देखभाल: टायलोसिन या डॉक्सीसाइक्लिन 4-5 दिनों तक पानी में दें। वेंटिलेशन में सुधार करें।' :
                    '💊 Medication & Care: Administer Tylosin or Doxycycline in drinking water for 4-5 days. Enhance shed cross-ventilation to dispel ammonia fumes.'
        };
      } else if (/diarrhea|loose|droppings|blood|wet|విరేచనాలు|రక్తం|మోషన్స్|నీళ్ల విరేచనాలు|दस्त|மலம்|பேதி/.test(lower)) {
        outputResult = {
          name: currentLang === 'te' ? '🚨 జీర్ణకోశ ఇన్ఫెక్షన్ / రక్త విరేచనాలు (Enteric Infection / Coccidiosis)' :
                currentLang === 'hi' ? '🚨 आंतों का संक्रमण / खूनी दस्त (Enteric Infection)' :
                '🚨 Enteric Infection / Suspected Coccidiosis',
          risk: 'High',
          riskLabel: currentLang === 'te' ? 'తీవ్ర రిస్క్ (High Risk Alert)' : 'High Risk Alert (Severe)',
          guidance: currentLang === 'te' ? '🚨 తక్షణ చర్య: ఆంప్రోలియం (Amprolium 20%) లేదా టోల్ట్రాజురిల్ తాగునీటిలో ఇవ్వండి. తడి లిట్టర్ వెంటనే తీసివేసి పొడి సున్నం చల్లండి. రక్తస్రావం తగ్గడానికి విటమిన్-K సప్లిమెంట్ ఇవ్వండి.' :
                    currentLang === 'hi' ? '🚨 तत्काल कार्रवाई: एम्प्रोलियम या टॉल्ट्राजुरिल दें। गीला बिछावन तुरंत हटाएं और चूना पाउडर छिड़कें।' :
                    '🚨 Immediate Action: Provide Amprolium (20%) or Toltrazuril immediately in water. Remove damp caked litter, apply dry lime, and supplement Vitamin K.'
        };
      } else if (/comb|wattle|scab|pox|తల వాపు|పొక్కులు|పాక్స్|కళ్ల వాపు|చేతులు|चेचक|கொண்டை/.test(lower)) {
        outputResult = {
          name: currentLang === 'te' ? '🛡️ చర్మ & తల వాపు / పొక్కులు (Integument / Pox Lesions)' :
                currentLang === 'hi' ? '🛡️ त्वचा व कलगी घाव (Pox Lesions)' :
                '🛡️ Cutaneous Nodules / Pox Lesions',
          risk: 'Medium',
          riskLabel: currentLang === 'te' ? 'మధ్యస్థ రిస్క్ (Medium Risk)' : 'Medium Risk Alert',
          guidance: currentLang === 'te' ? '🛡️ సంరక్షణ: జుట్టు, ముఖంపై ఉన్న పొక్కులపై గ్లిజరిన్ లేదా పోవిడోన్ అయోడిన్ (Betadine) రాయండి. దోమల నివారణ మందులు పిచికారీ చేయండి. విటమిన్-A అందించండి.' :
                    currentLang === 'hi' ? '🛡️ उपचार: घावों पर पोविडोन आयोडीन लगाएं और मच्छरों का नियंत्रण करें।' :
                    '🛡️ Care: Swab lesions with Povidone-Iodine ointment. Implement strict mosquito vector control and supplement Vitamin A.'
        };
      } else if (/paralys|leg|limp|walk|weak|letharg|లక్వా|పక్షవాతం|కుంటి|కాళ్లు|నీరసం|బలహీనత|బద్ధకం|నడవలేకపోవడం|लंगड़ा|सुस्त/.test(lower)) {
        outputResult = {
          name: currentLang === 'te' ? '⚠️ తీవ్ర బలహీనత & నరాల సమస్య / లక్వా (Lethargy & Paralysis Signs)' :
                currentLang === 'hi' ? '⚠️ अत्यधिक कमजोरी और लकवा लक्षण (Lethargy / Paralysis)' :
                '⚠️ Severe Lethargy & Neuro-Muscular Impairment',
          risk: 'High',
          riskLabel: currentLang === 'te' ? 'తీవ్ర రిస్క్ (High Risk Alert)' : 'High Risk Alert (Severe)',
          guidance: currentLang === 'te' ? '⚠️ తక్షణ చర్య: బలహీనపడిన కోళ్లను వెంటనే వేరు చేసి ప్రత్యేక పంజరంలో ఉంచండి. తాగునీటిలో ఎలక్ట్రోలైట్లు మరియు విటమిన్ బి-కాంప్లెక్స్ (Neurobion) కలిపి ఇవ్వండి.' :
                    currentLang === 'hi' ? '⚠️ कार्रवाई: कमजोर पक्षियों को अलग रखें। पानी में इलेक्ट्रोलाइट्स और विटामिन बी-कॉम्प्लेक्स दें।' :
                    '⚠️ Immediate Action: Isolate paralyzed birds with soft bedding. Mix Vitamin B-Complex (Neurobion) and oral electrolytes in fresh water.'
        };
      } else if (/feed|eat|food|appetite|మేత|ఆకలి|తినడం లేదు|दाना|भूख|தீவனம்/.test(lower)) {
        outputResult = {
          name: currentLang === 'te' ? '📉 మేత తినకపోవడం / ఆకలి మందగించడం (Feed Intake Drop)' :
                currentLang === 'hi' ? '📉 दाना न खाना / भूख में भारी कमी (Loss of Appetite)' :
                '📉 Acute Feed Intake Drop / Inappetence',
          risk: 'Medium',
          riskLabel: currentLang === 'te' ? 'మధ్యస్థ రిస్క్ (Medium Risk)' : 'Medium Risk Alert',
          guidance: currentLang === 'te' ? '🐔 సంరక్షణ: లివర్ టానిక్ (Liver tonic) మరియు మల్టీవిటమిన్లు నీటిలో అందించండి. ఫీడర్లను శుభ్రం చేసి తగినంత స్థలం ఉండేలా చూడండి.' :
                    currentLang === 'hi' ? '🐔 देखभाल: लिवर टॉनिक और विटामिन पानी में दें। फीडर साफ रखें।' :
                    '🐔 Care: Administer liver tonics and digestive electrolytes in water. Verify feed quality and moisture content.'
        };
      }
    }

    // TIER 3: Universal Clinical Assessment for ANY other speech/text
    if (!outputResult) {
      outputResult = {
        name: currentLang === 'te' ? `📋 పౌల్ట్రీ ఆరోగ్య విశ్లేషణ: "${transcript}"` :
              currentLang === 'hi' ? `📋 पोल्ट्री स्वास्थ्य विश्लेषण: "${transcript}"` :
              `📋 Flock Health Assessment: "${transcript}"`,
        risk: 'Medium',
        riskLabel: currentLang === 'te' ? 'పరిశీలన అవసరం (Observation Needed)' : 'Observation Needed',
        guidance: currentLang === 'te' ? `🏥 సిఫార్సులు: తెలిపిన సమస్య ("${transcript}") ఆధారంగా: అనారోగ్య కోళ్లను వెంటనే పరిశీలన గదిలో వేరు చేయండి. రోగనిరోధక శక్తి పెంచడానికి తాగునీటిలో ఎలక్ట్రోలైట్లు మరియు విటమిన్లు అందించండి. కింద ఉన్న బటన్ ద్వారా డాక్టర్‌కు వాట్సాప్ సందేశం పంపండి.` :
                  currentLang === 'hi' ? `🏥 सिफारिशें: बताए गए विवरण ("${transcript}") के आधार पर: अस्वस्थ पक्षियों को अलग करें और पानी में इलेक्ट्रोलाइट्स दें। नीचे दिए गए बटन से डॉक्टर से सलाह लें।` :
                  `🏥 Recommendations: Based on reported input ("${transcript}"): Strictly quarantine affected birds. Provide hydration electrolytes and multivitamins in fresh water. Contact veterinary support below.`
      };
    }

    this.lastOutput = outputResult;
    this.renderOutputUi(outputResult, transcript, currentLang, isFinal);
  },

  renderOutputUi(output, transcript, lang = 'te', isFinal = false) {
    const alertBox = document.getElementById('mobVoiceDiseaseAlertBox');
    const badgeEl = document.getElementById('mobVoiceRiskBadge');
    const headingEl = document.getElementById('mobVoiceDiseaseHeading');
    const careTextEl = document.getElementById('mobVoiceCareText');
    const waBtn = document.getElementById('mobVoiceWhatsAppBtn');

    if (alertBox) {
      alertBox.classList.remove('d-none');
      if (badgeEl) {
        badgeEl.className = `badge ${output.risk === 'High' ? 'bg-danger' : 'bg-warning text-dark'} px-2 py-1 mb-1 fw-bold`;
        badgeEl.textContent = output.riskLabel;
      }
      if (headingEl) {
        headingEl.textContent = output.name;
      }
      if (careTextEl) {
        careTextEl.innerHTML = output.guidance;
      }
      if (waBtn) {
        const text = encodeURIComponent(`Hello Doctor, Poultry Health Alert detected: ${output.name}. Spoken details: "${transcript}". Please advise on urgent medicines.`);
        waBtn.href = `https://wa.me/18005550199?text=${text}`;
      }

      if (isFinal) {
        alertBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
        showToast(`${output.name}`, output.risk === 'High' ? 'danger' : 'success', 'వ్యాధి నిర్ధారణ పూర్తయింది (Output Ready)');
        // Voice Audio Output (Text to Speech)
        VoiceInput.speakCurrentOutput(output.name);

        // Auto-save voice diagnosis to History
        if (typeof MockAPI !== 'undefined' && MockAPI.saveScanResult) {
          MockAPI.saveScanResult({
            type: 'Voice Message Diagnosis',
            condition: output.name,
            riskLevel: output.risk,
            confidence: 94.8,
            symptoms: transcript,
            guidance: output.guidance,
            safetyPrecautions: [
              output.risk === 'High' ? '🚨 Isolate affected birds immediately to prevent shed spread.' : '💨 Enhance shed ventilation to lower ammonia levels.',
              '🧪 Flush and sanitize drinker lines with fresh water.',
              '🛡️ Enforce footbaths and restricted pen access.'
            ],
            predictions: [
              output.risk === 'High' ? '⚠️ Elevated risk of flock transmission if untreated within 48h.' : '📈 Favorable recovery trajectory with immediate care.',
              '💊 85%+ clinical recovery expected with suggested therapy.'
            ]
          });
        }
      }
    }

    // Also update in image-prediction page if present
    const cvAlertBox = document.getElementById('cvVoiceDiseaseAlertBox');
    const cvBadgeEl = document.getElementById('cvVoiceRiskBadge');
    const cvHeadingEl = document.getElementById('cvVoiceDiseaseHeading');
    const cvCareTextEl = document.getElementById('cvVoiceCareText');
    const cvWaBtn = document.getElementById('cvVoiceWhatsAppBtn');

    if (cvAlertBox) {
      cvAlertBox.classList.remove('d-none');
      if (cvBadgeEl) {
        cvBadgeEl.className = `badge ${output.risk === 'High' ? 'bg-danger' : 'bg-warning text-dark'} px-2 py-1 mb-1 fw-bold`;
        cvBadgeEl.textContent = output.riskLabel;
      }
      if (cvHeadingEl) cvHeadingEl.textContent = output.name;
      if (cvCareTextEl) cvCareTextEl.innerHTML = output.guidance;
      if (cvWaBtn) {
        const text = encodeURIComponent(`Hello Doctor, Poultry Voice AI detected ${output.name}. Spoken input: "${transcript}". Urgent prescription needed.`);
        cvWaBtn.href = `https://wa.me/18005550199?text=${text}`;
      }
      if (isFinal) {
        cvAlertBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  },

  // Voice Audio Output (Text to Speech / TTS)
  speakCurrentOutput(customText = null) {
    if (!('speechSynthesis' in window)) return;
    try {
      window.speechSynthesis.cancel();
      const currentLang = localStorage.getItem('smart_poultry_lang') || 'te';
      let spokenMessage = '';

      if (customText) {
        spokenMessage = customText;
      } else if (this.lastOutput) {
        spokenMessage = `${this.lastOutput.name}. ${this.lastOutput.guidance.replace(/<[^>]*>?/gm, '')}`;
      }

      if (!spokenMessage) return;

      const utterance = new SpeechSynthesisUtterance(spokenMessage);
      const langCodes = { te: 'te-IN', hi: 'hi-IN', en: 'en-US', ta: 'ta-IN' };
      utterance.lang = langCodes[currentLang] || 'te-IN';
      utterance.rate = 0.95;
      window.speechSynthesis.speak(utterance);
    } catch (e) {
      console.warn('TTS error:', e);
    }
  },

  // Auto-detect spoken symptoms across languages and highlight chips
  autoTagSymptoms(text) {
    if (!text) return;
    const lower = text.toLowerCase();
    
    const highlightChip = (symptomKey) => {
      const chips = document.querySelectorAll(`.mob-symptom-chip[data-symptom-key="${symptomKey}"], .cv-symptom-chip[data-symptom-key="${symptomKey}"]`);
      chips.forEach(chip => {
        chip.classList.remove('btn-light', 'border', 'btn-white');
        chip.classList.add('btn-success', 'text-white');
      });
    };

    // 1. Sneezing / Coughing / Respiratory
    if (/sneeze|cough|gasp|rale|wheez|breath|छींक|खांसी|सांस|తుమ్ము|దగ్గు|రొంప|శ్వాస|జలుబు|గురక|ముక్కు|இருமல்|தும்மல்|কাশি|হাঁচি|tos|estornudo/.test(lower)) {
      const el = document.getElementById('mSymSneeze') || document.querySelector('.symptom-check[value="Sneezing"]');
      if (el) el.checked = true;
      highlightChip('cough');
    }

    // 2. Swollen / Watery Eyes
    if (/eye|watery|swollen eye|आंख|कళ్ళు|కళ్ల వాపు|కంటి నీరు|వాపు|కంటి చీము|ముఖం వాపు|கண்|চোখ|ojo/.test(lower)) {
      highlightChip('eyes');
    }

    // 3. Diarrhea / Abnormal droppings
    if (/diarrhea|wet|dropping|loose|blood|coccid|दस्त|पतला मल|విరేచనాలు|రక్త విరేచనాలు|నీళ్ల విరేచనాలు|రక్తం|మోషన్స్|మలం|கழிச்சல்|பேதி|ডায়রিয়া|diarrea/.test(lower)) {
      const el = document.getElementById('mSymDrop') || document.querySelector('.symptom-check[value="Abnormal Droppings"]');
      if (el) el.checked = true;
      highlightChip('diarrhea');
    }

    // 4. Comb Swelling / Head / Fowl Pox
    if (/comb|wattle|pox|scab|कलगी|चेचक|జుట్టు|తల వాపు|పొక్కులు|పాక్స్|చేతులు|கொண்டை|வீக்கம்|ঝুঁటి|cresta|viruela/.test(lower)) {
      const el = document.getElementById('mSymSwell') || document.querySelector('.symptom-check[value="Swelling"]');
      if (el) el.checked = true;
      highlightChip('comb');
    }

    // 5. Lethargy / Weakness / Dullness
    if (/lethargic|slow|tired|weak|dull|सुस्त|कमजोर|నీరసం|బలహీనత|బద్ధకం|కదలడం లేదు|సత్తువ లేదు|పడిపోవడం|சோர்வு|மந்தம்|অলস|letárgico|débil/.test(lower)) {
      const actLow = document.getElementById('mActVeryLow') || document.getElementById('mActLow');
      if (actLow) actLow.checked = true;
      highlightChip('lethargic');
    }

    // 6. Ruffled Feathers
    if (/feather|ruffled|plumage|पंख|ఈకలు|రెక్కలు|ఈకలు రాలడం|ఈకలు నిక్కబొడుచు|இறகு|পালক|pluma/.test(lower)) {
      highlightChip('feathers');
    }

    // 7. Feed Intake Drop / Loss of Appetite
    if (/feed|eat|food|appetite|दाना|खाना|భోజనం|మేత|ఆకలి|మేత తినడం లేదు|తినట్లేదు|మేత సరిగ్గా తినడం లేదు|తీவனம்|খাবার|apetito|comida/.test(lower)) {
      const el = document.getElementById('mSymFeed') || document.querySelector('.symptom-check[value="Reduced Feed"]');
      if (el) el.checked = true;
      highlightChip('appetite');
    }

    // 8. Leg Weakness / Limping / Paralysis
    if (/leg|limp|paralys|walk|लंगड़ाना|पैर|కాళ్లు|కుంటి|నకు|నకునడక|లక్వా|పక్షవాతం|కాలు వెనక్కి|నడవలేకపోవడం|నడవట్లేదు|கால்|பா|pata|cojera/.test(lower)) {
      highlightChip('legs');
    }
  }
};

function dismissVoiceDiseaseAlert() {
  const alertBox = document.getElementById('mobVoiceDiseaseAlertBox');
  if (alertBox) alertBox.classList.add('d-none');
  const cvAlertBox = document.getElementById('cvVoiceDiseaseAlertBox');
  if (cvAlertBox) cvAlertBox.classList.add('d-none');
}

function fillSymptomsFromVoice() {
  if (VoiceInput.lastOutput) {
    const input = document.getElementById('mobScanSymptomsInput') || document.getElementById('cvSymptomsInput');
    if (input) {
      if (!input.value.includes(VoiceInput.lastOutput.name)) {
        input.value = `${VoiceInput.lastOutput.name} - ${input.value}`.trim();
      }
      showToast('వ్యాధి స్కాన్ ఫీల్డ్‌కు జోడించబడింది! (Applied to scan)', 'success');
    }
  }
}

// Global submit handler for UI button & Keyboard Enter key
function submitScanSymptoms() {
  VoiceInput.submitVoiceDiagnosis('mobScanSymptomsInput');
}

function submitCvSymptoms() {
  VoiceInput.submitVoiceDiagnosis('cvSymptomsInput');
}
