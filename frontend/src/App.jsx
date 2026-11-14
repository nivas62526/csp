import React, { useState } from 'react';
import FertilizerCalculator from './FertilizerCalculator.jsx';

export default function App() {
  const [lang, setLang] = useState('te'); // default to Telugu, support English

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f1f5f9',
      fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
      color: '#0f172a'
    }}>
      {/* Top Navbar */}
      <header style={{
        backgroundColor: '#15803d',
        color: '#ffffff',
        padding: '14px 20px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.12)',
        position: 'sticky',
        top: 0,
        zIndex: 100
      }}>
        <div style={{
          maxWidth: '1100px',
          margin: '0 auto',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '1.8rem' }}>🌾</span>
            <div>
              <h1 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.3px' }}>
                {lang === 'te' ? 'రైతు ఎరువుల కాలిక్యులేటర్' : 'Smart Farm Fertilizer Calculator'}
              </h1>
              <p style={{ margin: 0, fontSize: '0.78rem', color: '#bbf7d0' }}>
                {lang === 'te' ? 'శాస్త్రీయ పోషకాల నిర్వహణ & మోతాదుల సలహా' : 'Scientific N-P-K Recommendation & Cost Estimator'}
              </p>
            </div>
          </div>

          {/* Language Switcher */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '0.8rem', color: '#dcfce7' }}>Language:</span>
            <button
              type="button"
              onClick={() => setLang('te')}
              style={{
                backgroundColor: lang === 'te' ? '#ffffff' : 'transparent',
                color: lang === 'te' ? '#15803d' : '#ffffff',
                border: '1px solid #ffffff',
                borderRadius: '20px',
                padding: '4px 12px',
                fontSize: '0.82rem',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              తెలుగు
            </button>
            <button
              type="button"
              onClick={() => setLang('en')}
              style={{
                backgroundColor: lang === 'en' ? '#ffffff' : 'transparent',
                color: lang === 'en' ? '#15803d' : '#ffffff',
                border: '1px solid #ffffff',
                borderRadius: '20px',
                padding: '4px 12px',
                fontSize: '0.82rem',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              English
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main style={{ maxWidth: '1100px', margin: '24px auto', padding: '0 16px' }}>
        <FertilizerCalculator lang={lang} />
      </main>

      {/* Footer */}
      <footer style={{
        marginTop: '40px',
        borderTop: '1px solid #e2e8f0',
        backgroundColor: '#ffffff',
        padding: '20px 16px',
        textAlign: 'center',
        fontSize: '0.82rem',
        color: '#64748b'
      }}>
        <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
          <p style={{ margin: '0 0 6px 0', fontWeight: 600 }}>
            {lang === 'te'
              ? 'వ్యవసాయ పరిశోధనా మండలి (ICAR) & ఆచార్య ఎన్.జి. రంగా వ్యవసాయ విశ్వవిద్యాలయ ప్రమాణాల ఆధారంగా రూపొందించబడింది.'
              : 'Formulated per ICAR & State Agricultural University scientific fertilizer benchmarks.'}
          </p>
          <p style={{ margin: 0 }}>
            © 2026 Smart Agriculture & Precision Nutrient Advisory System
          </p>
        </div>
      </footer>
    </div>
  );
}
