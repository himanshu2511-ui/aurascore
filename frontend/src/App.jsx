import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import AuthPage from './pages/AuthPage';
import Scanner from './components/Scanner';
import Scorecard from './components/Scorecard';
import Roadmap from './components/Roadmap';
import StyleGuide from './components/StyleGuide';
import Leaderboard from './components/Leaderboard';
import { generateAuraPDF } from './utils/pdfReport';
import './index.css';

const TABS = [
  { id: 'scan', label: '✦ Scan' },
  { id: 'score', label: '⚡ Scorecard' },
  { id: 'road', label: '🗺️ Roadmap' },
  { id: 'style', label: '💇 Style' },
  { id: 'leader', label: '🏆 Leader' },
];

function MainApp() {
  const { user, logout, token } = useAuth();
  const [tab, setTab] = useState('scan');
  const [analysis, setAnalysis] = useState(null);
  const [scanStatus, setScanStatus] = useState('idle');
  const [generating, setGenerating] = useState(false);
  const [reportReady, setReportReady] = useState(false);

  const handleResult = (data) => setAnalysis(data);

  const handleSessionComplete = async (snapshots) => {
    if (!snapshots?.length) return;
    setGenerating(true);
    setReportReady(false);
    await new Promise(r => setTimeout(r, 400));
    try {
      const date = new Date().toLocaleString('en-IN', { dateStyle: 'full', timeStyle: 'short' });
      const final = snapshots[snapshots.length - 1];
      generateAuraPDF(snapshots, final, date);
      setReportReady(true);
    } catch (e) { console.error('PDF error:', e); }
    setGenerating(false);
  };

  return (
    <div className="app-shell">
      {/* Header */}
      <header className="header">
        <h1>✦ AuraScore</h1>
        <p>AI Personal Glow-Up Coach — analyze, improve, transform.</p>
      </header>

      {/* User bar */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', marginBottom: '1rem', gap: '0.75rem' }}>
        <div style={{ background: 'rgba(240,192,64,0.1)', border: '1px solid rgba(240,192,64,0.25)', borderRadius: 8, padding: '0.35rem 0.9rem', fontSize: '0.82rem', color: '#f0c040' }}>
          👤 {user?.name}
        </div>
        <button
          id="logout-btn"
          onClick={logout}
          style={{ background: 'rgba(255,77,109,0.1)', border: '1px solid rgba(255,77,109,0.3)', borderRadius: 8, padding: '0.35rem 0.9rem', fontSize: '0.82rem', color: '#ff4d6d', cursor: 'pointer', fontFamily: 'inherit' }}
        >
          Log Out
        </button>
      </div>

      {/* PDF banners */}
      {generating && (
        <div style={{ background: 'linear-gradient(90deg,rgba(155,93,229,0.2),rgba(240,192,64,0.2))', border: '1px solid rgba(240,192,64,0.5)', borderRadius: 12, padding: '0.9rem 1.5rem', marginBottom: '1.5rem', textAlign: 'center', fontWeight: 700 }}>
          ⚙️ Generating your full AI report PDF...
        </div>
      )}
      {reportReady && !generating && (
        <div style={{ background: 'rgba(38,255,138,0.07)', border: '1px solid rgba(38,255,138,0.4)', borderRadius: 12, padding: '0.9rem 1.5rem', marginBottom: '1.5rem', textAlign: 'center', fontWeight: 700, color: '#26ff8a' }}>
          ✅ PDF Report downloaded! Check your Downloads folder.
        </div>
      )}

      {/* Tabs */}
      <nav className="tabs" role="tablist">
        {TABS.map(t => (
          <button key={t.id} className={`tab-btn ${tab === t.id ? 'active' : ''}`} onClick={() => setTab(t.id)} role="tab" id={`tab-${t.id}`}>
            {t.label}
          </button>
        ))}
      </nav>

      {/* Always-mounted scanner keeps polling */}
      <div style={{ display: tab === 'scan' ? 'block' : 'none' }}>
        <div className="two-col" style={{ alignItems: 'start' }}>
          <Scanner
            onResult={handleResult}
            onStatusChange={setScanStatus}
            onSessionComplete={handleSessionComplete}
            token={token}
          />
          <Scorecard analysis={analysis} />
        </div>
      </div>

      {tab === 'score' && (analysis
        ? <Scorecard analysis={analysis} />
        : <div className="glass" style={{ padding: '2rem', textAlign: 'center', color: 'var(--muted)' }}>Go to <strong>Scan</strong> and click <strong>Start 40-Second Analysis</strong> first.</div>
      )}
      {tab === 'road' && <Roadmap analysis={analysis} />}
      {tab === 'style' && <StyleGuide analysis={analysis} />}
      {tab === 'leader' && <Leaderboard />}

      {analysis && <div className="disclaimer">{analysis.disclaimer}</div>}
    </div>
  );
}

function AppGate() {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ color: '#f0c040', fontSize: '1.2rem' }}>✦ Loading AuraScore...</div>
      </div>
    );
  }
  return user ? <MainApp /> : <AuthPage />;
}

export default function App() {
  return (
    <AuthProvider>
      <AppGate />
    </AuthProvider>
  );
}
