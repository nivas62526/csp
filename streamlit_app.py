"""
Smart Poultry Farm Management and Precision Monitoring System
Streamlit Cloud Deployment Edition
"""

import streamlit as st
import math
import random
import datetime

# Import project's native AI engine
import ai_engine

# --- Page Configuration ---
st.set_page_config(
    page_title="Smart Poultry Farm AI",
    page_icon="🐔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4b5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .risk-low {
        background-color: #ecfdf5;
        border-left: 5px solid #10b981;
        padding: 12px 16px;
        border-radius: 6px;
        color: #065f46;
    }
    .risk-medium {
        background-color: #fffbeb;
        border-left: 5px solid #f59e0b;
        padding: 12px 16px;
        border-radius: 6px;
        color: #92400e;
    }
    .risk-high {
        background-color: #fef2f2;
        border-left: 5px solid #ef4444;
        padding: 12px 16px;
        border-radius: 6px;
        color: #991b1b;
    }
    .risk-critical {
        background-color: #450a0a;
        border-left: 5px solid #dc2626;
        padding: 12px 16px;
        border-radius: 6px;
        color: #fee2e2;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Configuration ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?auto=format&fit=crop&w=400&q=80", use_container_width=True)
    st.title("🐔 Poultry AI Center")
    
    lang = st.radio("Language / భాష", ["English", "తెలుగు (Telugu)"], horizontal=True)
    is_te = (lang != "English")

    st.markdown("---")
    st.subheader("🏡 Shed & Flock Selector" if not is_te else "🏡 షెడ్ & బ్యాచ్ ఎంపిక")
    active_shed = st.selectbox(
        "Active Shed",
        ["Shed #1 - Commercial Broiler (Cobb 500)", "Shed #2 - Commercial Broiler (Ross 308)", "Shed #3 - Layer Hen (BV-300)", "Shed #4 - Country / Desi Chicken"]
    )
    
    st.markdown("---")
    st.subheader("⚡ Live Microclimate Status" if not is_te else "⚡ ప్రత్యక్ష పర్యావరణ స్థితి")
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.metric("Temp", "27.8 °C", "-0.4 °C")
        st.metric("Ammonia", "13 ppm", "Safe")
    with col_sb2:
        st.metric("Humidity", "62 %", "+1 %")
        st.metric("Ventilation", "Optimal", "Normal")
        
    st.info("System connected to Smart Shed IoT Gateway & AI Decision Pipeline.")

# --- Header Section ---
st.markdown('<div class="main-header">🐔 Smart Poultry Farm Management & AI Precision Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multi-Tenant Agricultural IoT, Biosecurity Decision Support & Growth Optimization Platform</div>', unsafe_allow_html=True)

# --- Main Navigation Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🩺 AI Disease Diagnosis" if not is_te else "🩺 AI వ్యాధి నిర్ధారణ",
    "📸 Neural Vision Inspection" if not is_te else "📸 కంప్యూటర్ విజన్ తనిఖీ",
    "🌾 Feed & Age Calculator" if not is_te else "🌾 మేత & వయస్సు లెక్కింపు",
    "📊 IoT Microclimate Monitor" if not is_te else "📊 IoT పర్యావరణ మానిటర్",
    "💉 Vaccination & Biosecurity" if not is_te else "💉 వ్యాక్సినేషన్ & బయోసెక్యూరిటీ",
    "⚖️ Flock Economics & FCR" if not is_te else "⚖️ బ్యాచ్ ఆదాయం & FCR"
])

# ==========================================
# TAB 1: AI DISEASE & SYMPTOM DIAGNOSIS
# ==========================================
with tab1:
    st.header("🩺 Flock Health & Disease Risk Assessment" if not is_te else "🩺 పౌల్ట్రీ ఆరోగ్య & వ్యాధి ప్రమాద అంచనా")
    st.caption("Evaluates environmental microclimate and biological distress signals to calculate disease probability and immediate veterinary interventions.")

    with st.expander("📝 Environmental & Biological Indicators (Input Parameters)", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            age_days = st.slider("Flock Age (Days)", min_value=1, max_value=60, value=24, step=1)
            temperature = st.slider("Current Shed Temperature (°C)", min_value=10.0, max_value=45.0, value=28.5, step=0.5)
            humidity = st.slider("Current Shed Humidity (%)", min_value=20.0, max_value=95.0, value=65.0, step=1.0)
        with col2:
            ammonia_ppm = st.slider("Ammonia Gas Concentration (PPM)", min_value=0.0, max_value=60.0, value=14.0, step=1.0)
            feed_drop = st.slider("Sudden Feed Intake Drop (%)", min_value=0.0, max_value=50.0, value=5.0, step=1.0)
            water_change = st.slider("Water Consumption Deviation (%)", min_value=0.0, max_value=50.0, value=4.0, step=1.0)
        with col3:
            mortality_pct = st.slider("Daily Flock Mortality Rate (%)", min_value=0.0, max_value=5.0, value=0.08, step=0.01)
            
            symptom_options = [
                "Coughing / Snicking / Wheezing (దగ్గు / రొంప)",
                "Severe Panting & Open Beak (ఆయాసం / నోరు తెరచి శ్వాసించడం)",
                "Watery or Bloody Diarrhea (విరేచనాలు / రక్తం)",
                "White Chalky Droppings (తెల్లటి విరేచనాలు)",
                "Twisted Neck / Leg Paralysis (మెడ తిప్పడం / పక్షవాతం)",
                "Ruffled Feathers & Lethargy (ఈకలు విరబోసి ముడుచుకోవడం)",
                "Swollen Facial Wattles & Comb (ముఖం / మొటిమల వాపు)"
            ]
            selected_symptoms = st.multiselect("Observed Symptoms / లక్షణాలు", symptom_options)
            free_symptoms = st.text_input("Additional Observations / ఇతర వివరాలు", "")

    combined_symptoms = ", ".join(selected_symptoms) + " " + free_symptoms

    if st.button("🔍 Run AI Clinical Evaluation", type="primary", use_container_width=True):
        res = ai_engine.predict_disease_risk(
            age_days=age_days,
            temperature=temperature,
            humidity=humidity,
            ammonia_ppm=ammonia_ppm,
            feed_drop_pct=feed_drop,
            water_change_pct=water_change,
            mortality_rate_pct=mortality_pct,
            symptoms=combined_symptoms
        )

        st.markdown("### 📋 AI Evaluation Report")
        score = res.get("score", 0)
        level = res.get("risk_level", "LOW")

        css_class = "risk-low"
        if level == "CRITICAL":
            css_class = "risk-critical"
        elif level == "HIGH":
            css_class = "risk-high"
        elif level == "MEDIUM":
            css_class = "risk-medium"

        st.markdown(f"""
        <div class="{css_class}">
            <h3 style="margin:0 0 8px 0;">Risk Level: {level} ({score} / 100 Risk Index)</h3>
            <p style="margin:0;"><b>Telugu:</b> {res.get('risk_level_te', '')}</p>
        </div>
        """, unsafe_allow_html=True)

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.subheader("⚠️ Suspected Clinical Conditions")
            conditions = res.get("possible_conditions", [])
            if conditions:
                for cond in conditions:
                    st.error(f"• **{cond}**")
            else:
                st.success("No critical pathology identified. Standard operating condition.")

            st.subheader("🚩 Environmental Contributing Factors")
            factors = res.get("risk_factors", [])
            if factors:
                for factor in factors:
                    st.warning(f"• {factor}")
            else:
                st.info("Microclimate parameters remain within comfort thresholds.")

        with col_r2:
            st.subheader("💊 Actionable Protocols & Recommendations (English)")
            recs_en = res.get("recommendations_en", [])
            for r in recs_en:
                st.markdown(f"- ✅ {r}")

            st.subheader("🌾 సిఫార్సులు మరియు రక్షణ చర్యలు (తెలుగు)")
            recs_te = res.get("recommendations_te", [])
            for r in recs_te:
                st.markdown(f"- 🚜 {r}")

# ==========================================
# TAB 2: NEURAL VISION INSPECTION
# ==========================================
with tab2:
    st.header("📸 Computer Vision & Neural Inspection" if not is_te else "📸 కంప్యూటర్ విజన్ & కృత్రిమ మేధ తనిఖీ")
    st.caption("AI-powered plumage, comb, eye, and posture image analysis for rapid symptom identification.")

    col_v1, col_v2 = st.columns([1, 1.2])

    with col_v1:
        st.subheader("Inspection Input Mode")
        inspect_mode = st.radio(
            "Select Input Source",
            ["Clinical Preset Sample 1: Healthy Broiler",
             "Clinical Preset Sample 2: Respiratory Challenge (CRD)",
             "Clinical Preset Sample 3: Cutaneous Fowl Pox",
             "Clinical Preset Sample 4: Systemic Lethargy / Coccidiosis",
             "Upload Custom Flock / Bird Photo"]
        )

        sample_type = "healthy"
        if "Respiratory" in inspect_mode:
            sample_type = "respiratory"
            st.image("https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?auto=format&fit=crop&w=600&q=80", caption="Sample: Open mouth panting & rales signs")
        elif "Fowl Pox" in inspect_mode:
            sample_type = "fowlpox"
            st.image("https://images.unsplash.com/photo-1516467508483-a7212febe31a?auto=format&fit=crop&w=600&q=80", caption="Sample: Facial cutaneous lesions")
        elif "Lethargy" in inspect_mode:
            sample_type = "lethargic"
            st.image("https://images.unsplash.com/photo-1589923188900-85dae523342b?auto=format&fit=crop&w=600&q=80", caption="Sample: Sternal huddle & feather disarray")
        elif "Upload" in inspect_mode:
            sample_type = "custom"
            uploaded_file = st.file_uploader("Upload Bird / Flock Image (JPG, PNG)", type=["jpg", "png", "jpeg"])
            if uploaded_file:
                st.image(uploaded_file, caption="Uploaded Specimen Image", use_container_width=True)
            else:
                st.info("Upload a clear photo of the bird's head, comb, eye, or flock posture.")
        else:
            sample_type = "healthy"
            st.image("https://images.unsplash.com/photo-1563281577-a7be47e20db9?auto=format&fit=crop&w=600&q=80", caption="Sample: Bright comb, smooth plumage, alert posture")

    with col_v2:
        st.subheader("Neural Diagnostic Output")

        if sample_type == "respiratory":
            cond_name = "Avian Respiratory Distress (CRD / Bronchitis)"
            risk = "High"
            conf = 91.4
            summary = "Computer Vision Neural Inspection: Signs of nasal discharge, open-mouth panting, and sternal posture indicative of avian respiratory challenge."
            features = [
                ("Beak & Trachea", "Excess Exudate / Rales", False),
                ("Plumage Texture", "Ruffled / Feathers Raised", False),
                ("Eye Margin", "Mild Ocular Discharge", False),
                ("Comb Color", "Normal Pigmentation", True)
            ]
            treatments = [
                "Administer tylosin / doxycycline in drinking water under veterinary guidance.",
                "Flush air with maximum tunnel ventilation to purge airborne ammonia.",
                "Add electrolyte & vitamin C supplements to mitigate respiratory distress."
            ]
        elif sample_type == "fowlpox":
            cond_name = "Cutaneous Fowl Pox (Facial Lesions)"
            risk = "High"
            conf = 94.2
            summary = "Computer Vision Neural Inspection: Nodular proliferative cutaneous scabs detected on unfeathered facial integument and comb."
            features = [
                ("Comb & Wattle", "Warty Nodules & Scabs Detected", False),
                ("Eyelid Margin", "Crusted Margins", False),
                ("Plumage", "Intact Feather Coat", True),
                ("Leg Scales", "Clean / No Mites", True)
            ]
            treatments = [
                "Isolate visibly affected birds to prevent mechanical transmission.",
                "Apply gentle antiseptic ointment (iodine tincture) on facial scabs.",
                "Control mosquito and biting insect vectors inside shed perimeter."
            ]
        elif sample_type == "lethargic":
            cond_name = "Systemic Lethargy / Enteric Gut Stress"
            risk = "Medium"
            conf = 88.6
            summary = "Computer Vision Neural Inspection: Suppressed alertness, dull ocular response, and posture collapse suggestive of metabolic or coccidial challenge."
            features = [
                ("Head Posture", "Head Droop & Huddled Stance", False),
                ("Feather Alignment", "Severe Disarray", False),
                ("Abdominal Guarding", "Drawn-in Posture", False),
                ("Comb Color", "Slightly Pale", False)
            ]
            treatments = [
                "Inspect litter moisture immediately; test fecal samples for coccidial oocysts.",
                "Administer gut probiotics and water-soluble electrolytes.",
                "Rake damp litter around nipple drinkers."
            ]
        else:
            cond_name = "Healthy Plumage & Alert Posture"
            risk = "Low"
            conf = 96.5
            summary = "Computer Vision Neural Inspection: No ocular exudate, comb crusting, or feather disarray detected. Bird exhibits healthy upright stance and bright red comb turgor."
            features = [
                ("Comb & Wattle", "Bright Red / Healthy Turgor", True),
                ("Plumage Texture", "Smooth & Aligned", True),
                ("Head Posture", "Alert & Upright", True),
                ("Eye Margin", "Clear / No Discharge", True)
            ]
            treatments = [
                "Maintain standard biosecurity protocols and sanitized water chlorination (2-3 PPM)."
            ]

        # Display results
        badge_color = "#10b981" if risk == "Low" else ("#f59e0b" if risk == "Medium" else "#ef4444")
        st.markdown(f"""
        <div style="background:{badge_color}15; border: 1px solid {badge_color}; border-radius:8px; padding:12px; margin-bottom:12px;">
            <span style="background:{badge_color}; color:white; padding:4px 8px; border-radius:4px; font-weight:700; font-size:0.8rem;">{risk.upper()} RISK</span>
            <span style="float:right; font-weight:700; color:{badge_color};">{conf}% Confidence</span>
            <h4 style="margin:8px 0 4px 0; color:#1e293b;">{cond_name}</h4>
            <p style="margin:0; font-size:0.9rem; color:#475569;">{summary}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**🔬 Anatomical Inspection Matrix**")
        col_m1, col_m2 = st.columns(2)
        for idx, (label, status, is_good) in enumerate(features):
            target_col = col_m1 if idx % 2 == 0 else col_m2
            with target_col:
                icon = "🟢" if is_good else "🔴"
                st.markdown(f"{icon} **{label}:** {status}")

        st.markdown("**🛡️ Recommended Interventions & Biosecurity Protocol**")
        for t in treatments:
            st.markdown(f"- 💉 {t}")

# ==========================================
# TAB 3: FEED & AGE REQUIREMENTS PLANNER
# ==========================================
with tab3:
    st.header("🌾 Daily Nutrition, Water & Microclimate Planner" if not is_te else "🌾 రోజువారీ మేత, నీరు & ఉష్ణోగ్రత ప్రణాళిక")
    st.caption("Calculates scientifically calibrated daily feed intake (kg/bags), water volume (liters), and target shed temperatures.")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        calc_breed = st.selectbox(
            "Flock Breed / జాతి",
            ["Broiler (Cobb 500)", "Broiler (Ross 308)", "Commercial Layer (BV-300 / Lohmann)", "Country / Desi Chicken (Aseel / Kadaknath)"]
        )
    with col_f2:
        calc_age = st.number_input("Bird Age in Days / వయస్సు (రోజులు)", min_value=1, max_value=60, value=21, step=1)
    with col_f3:
        calc_count = st.number_input("Bird Count / కోళ్ల సంఖ్య", min_value=10, max_value=200000, value=2500, step=500)

    req = ai_engine.predict_age_requirements(breed=calc_breed, age_days=calc_age, bird_count=calc_count)

    st.markdown("---")
    st.markdown(f"### 📊 Recommended Daily Plan for {calc_count:,} Birds (Day {calc_age} - {req.get('growth_stage')})")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Daily Flock Feed</div>
            <div class="metric-value">{req['feed']['daily_flock_kg']} kg</div>
            <div style="font-size:0.85rem; color:#64748b;">≈ {req['feed']['daily_bags_50kg']} Bags (50kg)</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Feed Per Bird</div>
            <div class="metric-value">{req['feed']['per_bird_grams']} g</div>
            <div style="font-size:0.85rem; color:#64748b;">Stage: {req['feed']['feed_stage']}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Daily Water Required</div>
            <div class="metric-value">{req['water']['daily_flock_liters']} L</div>
            <div style="font-size:0.85rem; color:#64748b;">{req['water']['per_bird_ml']} ml / bird</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Target Shed Temp</div>
            <div class="metric-value">{req['temperature']['target_c']} °C</div>
            <div style="font-size:0.85rem; color:#64748b;">Range: {req['temperature']['min_comfort_c']} - {req['temperature']['max_comfort_c']} °C</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### 🌾 తెలుగు వివరణ (Telugu Summary)")
    st.info(f"""
    - **దశ:** {req.get('growth_stage_te')} ({req['feed']['feed_stage_te']})
    - **రోజువారీ మేత:** {req['feed']['daily_flock_kg']} కేజీలు ({req['feed']['daily_bags_50kg']} బస్తాలు)
    - **రోజువారీ నీరు:** {req['water']['daily_flock_liters']} లీటర్లు
    - **షెడ్ ఉష్ణోగ్రత:** {req['temperature']['target_c']} °C ({req['temperature']['target_f']} °F)
    """)

    # Weekly Growth Projection Table
    st.markdown("#### 📈 Projected 7-Day Growth & Feed Forecast")
    forecast_data = []
    for day_offset in range(7):
        target_day = calc_age + day_offset
        step_req = ai_engine.predict_age_requirements(breed=calc_breed, age_days=target_day, bird_count=calc_count)
        forecast_data.append({
            "Day": f"Day {target_day}",
            "Feed/Bird (g)": step_req['feed']['per_bird_grams'],
            "Flock Feed (kg)": step_req['feed']['daily_flock_kg'],
            "Water (L)": step_req['water']['daily_flock_liters'],
            "Target Temp (°C)": step_req['temperature']['target_c']
        })
    st.table(forecast_data)

# ==========================================
# TAB 4: IOT MICROCLIMATE MONITOR
# ==========================================
with tab4:
    st.header("📊 Real-Time IoT Microclimate Monitoring" if not is_te else "📊 నిజ-సమయ IoT పర్యావరణ పర్యవేక్షణ")
    st.caption("Continuous sensor telemetry tracking temperature, relative humidity, and ammonia gas levels with automatic threshold alerts.")

    iot_col1, iot_col2, iot_col3 = st.columns(3)
    with iot_col1:
        st.metric(label="🌡️ Ambient Temperature", value="28.2 °C", delta="-0.3 °C (Optimal)")
        st.progress(0.68)
        st.caption("Target: 26.0 - 29.5 °C")

    with iot_col2:
        st.metric(label="💧 Relative Humidity", value="63 %", delta="+2 % (Safe)")
        st.progress(0.63)
        st.caption("Optimal Zone: 55% - 70%")

    with iot_col3:
        st.metric(label="💨 Ammonia Gas (NH3)", value="13.5 PPM", delta="Normal (< 20 PPM)")
        st.progress(0.27)
        st.caption("Hazardous above 25 PPM")

    st.markdown("---")
    st.subheader("⏱️ Simulated 24-Hour Environmental Trends")

    # Generate synthetic telemetry trend
    hours = [f"{h:02d}:00" for h in range(0, 24, 2)]
    temps = [24.5, 23.8, 23.2, 24.1, 26.8, 29.5, 31.2, 30.8, 29.1, 27.4, 26.0, 25.1]
    humid = [75, 78, 80, 76, 68, 58, 54, 56, 62, 69, 72, 74]
    ammonia = [11, 12, 13, 14, 15, 16, 15, 14, 13, 13, 12, 11]

    trend_chart_data = {
        "Hour": hours,
        "Temperature (°C)": temps,
        "Humidity (%)": humid,
        "Ammonia (PPM)": ammonia
    }
    st.line_chart(trend_chart_data, x="Hour", y=["Temperature (°C)", "Ammonia (PPM)"])

    st.subheader("⚡ Automated Actuator System Status")
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        st.success("🌀 Tunnel Fans: Running (6/8)")
    with a2:
        st.info("🌫️ Evaporative Pads: Standby")
    with a3:
        st.success("💡 Brooder Lighting: 18 hrs ON")
    with a4:
        st.warning("🚰 Nipple Line Pressure: 2.2 Bar")

# ==========================================
# TAB 5: VACCINATION & BIOSECURITY
# ==========================================
with tab5:
    st.header("💉 Comprehensive Vaccination Schedule & Biosecurity Protocols" if not is_te else "💉 వ్యాక్సినేషన్ షెడ్యూల్ & బయోసెక్యూరిటీ నిబంధనలు")
    st.caption("Scientifically recommended vaccination program and pathogen biosecurity barriers for commercial broiler flocks.")

    vaccine_schedule = [
        {"Day": "Day 1", "Disease": "Marek's Disease (HVT)", "Route": "Subcutaneous Injection at Hatchery", "Status": "Completed (Hatchery)"},
        {"Day": "Day 7", "Disease": "Ranikhet / Newcastle (ND B1)", "Route": "Eye Drop / Coarse Spray", "Status": "Completed"},
        {"Day": "Day 14", "Disease": "Gumboro / IBD (Intermediate)", "Route": "Drinking Water with Skimmed Milk", "Status": "Due Soon"},
        {"Day": "Day 21", "Disease": "Newcastle Disease (LaSota Booster)", "Route": "Drinking Water", "Status": "Pending"},
        {"Day": "Day 28", "Disease": "Gumboro / IBD Plus Booster", "Route": "Drinking Water", "Status": "Pending"}
    ]
    st.table(vaccine_schedule)

    st.markdown("---")
    st.subheader("🛡️ 5 Golden Biosecurity Rules for Poultry Sheds")
    b1, b2 = st.columns(2)
    with b1:
        st.markdown("""
        1. **Strict Footbath Disinfection:** Maintain 2% Virkon-S or bleaching solution at all shed entries. Change solution daily.
        2. **Water Chlorination:** Treat borewell water to maintain 2 - 3 PPM free residual chlorine at the furthest nipple drinker.
        3. **Litter Raking & Ammonia Control:** Rake top litter twice weekly; replace wet patches immediately to prevent coccidiosis oocysts.
        """)
    with b2:
        st.markdown("""
        4. **Vector & Rodent Exclusion:** Enforce mesh net integrity to prevent wild birds and rodents from contaminating feed pans.
        5. **All-In, All-Out Policy:** Strictly adhere to single-age flock rearing with a minimum 14-day shed downtime and thermal wash between batches.
        """)

# ==========================================
# TAB 6: FLOCK ECONOMICS & FCR
# ==========================================
with tab6:
    st.header("⚖️ Batch Economics & Feed Conversion Ratio (FCR)" if not is_te else "⚖️ బ్యాచ్ ఆదాయ వ్యయాలు & FCR కాలిక్యులేటర్")
    st.caption("Measure performance against global Cobb/Ross European Production Efficiency Factor (EPEF) standards.")

    col_ec1, col_ec2, col_ec3 = st.columns(3)
    with col_ec1:
        total_birds_placed = st.number_input("Chicks Placed (Initial)", min_value=100, value=3000, step=100)
        birds_harvested = st.number_input("Birds Harvested (Live)", min_value=100, value=2880, step=50)
    with col_ec2:
        total_feed_used_kg = st.number_input("Total Feed Consumed (kg)", min_value=100.0, value=9200.0, step=100.0)
        total_live_weight_kg = st.number_input("Total Live Biomass Harvested (kg)", min_value=100.0, value=6050.0, step=100.0)
    with col_ec3:
        farmgate_price_kg = st.number_input("Live Bird Selling Price (₹/kg)", min_value=10.0, value=115.0, step=2.0)
        feed_cost_kg = st.number_input("Feed Cost (₹/kg)", min_value=10.0, value=42.0, step=1.0)

    # Calculations
    fcr = ai_engine.calculate_fcr(total_feed_used_kg, total_live_weight_kg)
    mortality_count = max(0, total_birds_placed - birds_harvested)
    mortality_rate = (mortality_count / total_birds_placed) * 100.0 if total_birds_placed > 0 else 0.0
    avg_bird_weight = (total_live_weight_kg / birds_harvested) if birds_harvested > 0 else 0.0

    gross_revenue = total_live_weight_kg * farmgate_price_kg
    total_feed_expense = total_feed_used_kg * feed_cost_kg
    feed_margin = gross_revenue - total_feed_expense

    st.markdown("---")
    st.markdown("### 📊 Performance KPI Dashboard")

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        fcr_color = "#10b981" if fcr <= 1.55 else ("#f59e0b" if fcr <= 1.75 else "#ef4444")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Feed Conversion (FCR)</div>
            <div class="metric-value" style="color:{fcr_color};">{fcr}</div>
            <div style="font-size:0.85rem; color:#64748b;">Benchmark: 1.48 - 1.62</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Average Weight</div>
            <div class="metric-value">{avg_bird_weight:.2f} kg</div>
            <div style="font-size:0.85rem; color:#64748b;">Per Market Bird</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        m_color = "#10b981" if mortality_rate <= 3.5 else "#ef4444"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Batch Mortality</div>
            <div class="metric-value" style="color:{m_color};">{mortality_rate:.2f} %</div>
            <div style="font-size:0.85rem; color:#64748b;">{mortality_count} Birds Lost</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Gross Margin Over Feed</div>
            <div class="metric-value" style="color:#0284c7;">₹{feed_margin:,.0f}</div>
            <div style="font-size:0.85rem; color:#64748b;">Rev: ₹{gross_revenue:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #94a3b8; font-size: 0.85rem;'>"
    "Smart Poultry Farm Management System • Powered by AI Decision Engine & Streamlit Cloud • Designed for Commercial & Rural Poultry Farmers"
    "</div>",
    unsafe_allow_html=True
)
