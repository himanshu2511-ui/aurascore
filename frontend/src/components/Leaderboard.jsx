import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';

const TIER_CONFIG = {
  Legendary: { color: '#ff8c42', glow: 'rgba(255,140,66,0.35)', bg: 'rgba(255,140,66,0.08)' },
  Elite:     { color: '#f0c040', glow: 'rgba(240,192,64,0.3)',  bg: 'rgba(240,192,64,0.07)' },
  High:      { color: '#9b5de5', glow: 'rgba(155,93,229,0.25)', bg: 'rgba(155,93,229,0.07)' },
  Good:      { color: '#26ff8a', glow: 'rgba(38,255,138,0.2)',  bg: 'rgba(38,255,138,0.06)' },
  Average:   { color: '#60a5fa', glow: 'rgba(96,165,250,0.2)',  bg: 'rgba(96,165,250,0.06)' },
  Developing:{ color: '#9ca3af', glow: 'rgba(156,163,175,0.1)', bg: 'rgba(156,163,175,0.05)' },
};

const RANK_MEDALS = {
  1: { symbol: '🥇', color: '#f0c040', size: '1.5rem' },
  2: { symbol: '🥈', color: '#9ca3af', size: '1.35rem' },
  3: { symbol: '🥉', color: '#cd7f32', size: '1.35rem' },
};

function getInitials(name = '') {
  return name.trim().split(/\s+/).map(w => w[0]).join('').slice(0, 2).toUpperCase();
}

function ScoreRing({ score, color, size = 52 }) {
  const r = (size - 8) / 2;
  const circ = 2 * Math.PI * r;
  const fill = circ * (score / 100);
  return (
    <svg width={size} height={size} style={{ flexShrink: 0 }}>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth={4} />
      <circle
        cx={size/2} cy={size/2} r={r}
        fill="none" stroke={color} strokeWidth={4}
        strokeDasharray={`${fill} ${circ}`}
        strokeLinecap="round"
        transform={`rotate(-90 ${size/2} ${size/2})`}
        style={{ transition: 'stroke-dasharray 0.8s ease' }}
      />
      <text x={size/2} y={size/2 + 5} textAnchor="middle"
        style={{ fontSize: '12px', fontWeight: 800, fill: color, fontFamily: 'inherit' }}>
        {score}
      </text>
    </svg>
  );
}

function LeaderRow({ entry, isMe, animDelay }) {
  const tier  = TIER_CONFIG[entry.score_label] || TIER_CONFIG.Developing;
  const medal = RANK_MEDALS[entry.rank];
  const gender = entry.gender === 'female' ? '♀' : '♂';
  const genderColor = entry.gender === 'female' ? '#ff6b9d' : '#60a5fa';

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        padding: '0.9rem 1.25rem',
        borderRadius: 14,
        background: isMe ? 'rgba(38,255,138,0.07)' : tier.bg,
        border: `1px solid ${isMe ? 'rgba(38,255,138,0.35)' : 'rgba(255,255,255,0.05)'}`,
        boxShadow: isMe ? '0 0 18px rgba(38,255,138,0.12)' : 'none',
        transition: 'transform 0.2s, box-shadow 0.2s',
        animation: `fadeSlideIn 0.35s ease ${animDelay}s both`,
        cursor: 'default',
      }}
      onMouseEnter={e => { e.currentTarget.style.transform = 'translateX(4px)'; e.currentTarget.style.boxShadow = `0 0 20px ${tier.glow}`; }}
      onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = isMe ? '0 0 18px rgba(38,255,138,0.12)' : 'none'; }}
    >
      {/* Rank */}
      <div style={{ width: 36, textAlign: 'center', flexShrink: 0 }}>
        {medal
          ? <span style={{ fontSize: medal.size }}>{medal.symbol}</span>
          : <span style={{ fontSize: '0.85rem', color: '#4b5563', fontWeight: 700 }}>#{entry.rank}</span>
        }
      </div>

      {/* Avatar */}
      <div style={{
        width: 40, height: 40, borderRadius: '50%', flexShrink: 0,
        background: `linear-gradient(135deg, ${tier.color}40, ${tier.color}20)`,
        border: `2px solid ${tier.color}60`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '0.85rem', fontWeight: 800, color: tier.color,
        boxShadow: `0 0 10px ${tier.glow}`,
      }}>
        {getInitials(entry.name)}
      </div>

      {/* Name + tier */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flexWrap: 'wrap' }}>
          <span style={{
            fontWeight: 700, fontSize: '0.95rem', color: '#f0f0f5',
            whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
          }}>
            {entry.name}
          </span>
          <span style={{ fontSize: '0.8rem', color: genderColor }}>{gender}</span>
          {isMe && <span style={{ fontSize: '0.7rem', padding: '1px 7px', borderRadius: 20, background: 'rgba(38,255,138,0.15)', color: '#26ff8a', fontWeight: 700 }}>YOU</span>}
        </div>
        <div style={{
          fontSize: '0.72rem', color: tier.color, fontWeight: 600,
          marginTop: '1px', letterSpacing: '0.5px',
        }}>
          {entry.score_label}
        </div>
      </div>

      {/* Score ring */}
      <ScoreRing score={entry.aura_score} color={tier.color} />
    </div>
  );
}

export default function Leaderboard() {
  const [users, setUsers]     = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState('');
  const [filter, setFilter]   = useState('all'); // 'all' | 'male' | 'female'
  const { token, user: currentUser } = useAuth();

  const load = useCallback(() => {
    setLoading(true);
    setError('');
    let API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    if (API.endsWith('/')) API = API.slice(0, -1);
    if (!API.startsWith('http')) API = `https://${API}`;

    fetch(`${API}/api/leaderboard`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    .then(r => {
      if (!r.ok) throw new Error('Failed to fetch leaderboard');
      return r.json();
    })
    .then(data => { setUsers(data); setLoading(false); })
    .catch(err => { setError(err.message); setLoading(false); });
  }, [token]);

  useEffect(() => { load(); }, [load]);

  const filtered = filter === 'all' ? users : users.filter(u => u.gender === filter);

  const stats = {
    total:    users.length,
    males:    users.filter(u => u.gender === 'male').length,
    females:  users.filter(u => u.gender === 'female').length,
    topScore: users[0]?.aura_score ?? 0,
  };

  return (
    <div style={{ maxWidth: 680, margin: '0 auto' }}>
      <style>{`
        @keyframes fadeSlideIn {
          from { opacity: 0; transform: translateY(12px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse-glow {
          0%, 100% { box-shadow: 0 0 20px rgba(240,192,64,0.2); }
          50%       { box-shadow: 0 0 36px rgba(240,192,64,0.45); }
        }
      `}</style>

      {/* Header */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(155,93,229,0.15), rgba(240,192,64,0.1))',
        border: '1px solid rgba(240,192,64,0.2)',
        borderRadius: 20, padding: '1.5rem 2rem', marginBottom: '1.5rem',
        animation: 'pulse-glow 3s ease infinite',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 900, color: '#f0c040' }}>
              🏆 AuraScore Leaderboard
            </h2>
            <p style={{ margin: '4px 0 0', color: '#6b7280', fontSize: '0.82rem' }}>
              Global rankings · Updated in real-time
            </p>
          </div>
          <div style={{ display: 'flex', gap: '1.5rem' }}>
            {[
              { label: 'Total', value: stats.total, color: '#f0c040' },
              { label: '♂ Male', value: stats.males, color: '#60a5fa' },
              { label: '♀ Female', value: stats.females, color: '#ff6b9d' },
            ].map(s => (
              <div key={s.label} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '1.4rem', fontWeight: 900, color: s.color }}>{s.value}</div>
                <div style={{ fontSize: '0.7rem', color: '#4b5563', fontWeight: 600 }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Filter pills */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        {[
          { key: 'all',    label: 'All' },
          { key: 'male',   label: '♂ Male' },
          { key: 'female', label: '♀ Female' },
        ].map(f => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            style={{
              padding: '0.4rem 1rem', borderRadius: 20, border: 'none', cursor: 'pointer',
              fontFamily: 'inherit', fontWeight: 700, fontSize: '0.8rem',
              background: filter === f.key ? 'linear-gradient(135deg,#9b5de5,#f0c040)' : 'rgba(255,255,255,0.07)',
              color: filter === f.key ? '#111' : '#9ca3af',
              transition: 'all 0.2s',
            }}
          >
            {f.label}
          </button>
        ))}

        {/* Refresh */}
        <button
          onClick={load}
          style={{
            marginLeft: 'auto', padding: '0.4rem 1rem', borderRadius: 20,
            border: '1px solid rgba(255,255,255,0.1)', background: 'transparent',
            color: '#6b7280', cursor: 'pointer', fontFamily: 'inherit', fontSize: '0.78rem',
          }}
        >
          ↻ Refresh
        </button>
      </div>

      {/* Content */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#4b5563' }}>
          <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>⏳</div>
          Loading leaderboard...
        </div>
      )}
      {error && (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#ff4d6d',
          background: 'rgba(255,77,109,0.07)', borderRadius: 12, border: '1px solid rgba(255,77,109,0.2)' }}>
          ⚠️ {error}
          <br /><button onClick={load} style={{ marginTop: '0.75rem', padding: '0.4rem 1rem',
            background: 'rgba(255,77,109,0.15)', border: '1px solid rgba(255,77,109,0.3)',
            borderRadius: 8, color: '#ff4d6d', cursor: 'pointer', fontFamily: 'inherit' }}>
            Retry
          </button>
        </div>
      )}
      {!loading && !error && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
          {filtered.length === 0 && (
            <div style={{ textAlign: 'center', padding: '3rem', color: '#4b5563' }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🌟</div>
              No scores yet — be the first!
            </div>
          )}
          {filtered.map((u, i) => (
            <LeaderRow
              key={u.id}
              entry={u}
              isMe={currentUser?.id === u.id}
              animDelay={i * 0.04}
            />
          ))}
        </div>
      )}

      {!loading && filtered.length > 0 && (
        <p style={{ textAlign: 'center', color: '#374151', fontSize: '0.72rem', marginTop: '1.5rem' }}>
          Showing top {filtered.length} verified users sorted by AuraScore
        </p>
      )}
    </div>
  );
}
