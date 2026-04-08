import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

export default function Leaderboard() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const { token, user: currentUser } = useAuth();
  
  useEffect(() => {
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    fetch(`${API_URL}/api/leaderboard`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    .then(r => {
      if (!r.ok) throw new Error('Failed to fetch leaderboard');
      return r.json();
    })
    .then(data => {
      setUsers(data);
      setLoading(false);
    })
    .catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, [token]);

  if (loading) return <div className="glass" style={{ padding: '2rem', textAlign: 'center' }}>Loading Leaderboard...</div>;

  return (
    <div className="glass" style={{ padding: '2rem', borderRadius: 16 }}>
      <h2 style={{ color: '#f0c040', marginBottom: '1.5rem', textAlign: 'center' }}>🏆 AuraScore Leaderboard</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {users.length === 0 && <p style={{ textAlign: 'center', color: 'var(--muted)' }}>No scores yet.</p>}
        {users.map((u, i) => {
          const isTop3 = i < 3;
          const medals = ['🥇', '🥈', '🥉'];
          const isMe = currentUser?.id === u.id;
          return (
            <div key={u.id} style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              padding: '1rem 1.5rem', background: isMe ? 'rgba(38,255,138,0.1)' : 'var(--bg-card)',
              border: isMe ? '1px solid rgba(38,255,138,0.3)' : '1px solid rgba(255,255,255,0.05)',
              borderRadius: 12,
              fontWeight: isTop3 ? 'bold' : 'normal',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <span style={{ fontSize: '1.25rem', width: 30, textAlign: 'center' }}>{isTop3 ? medals[i] : `#${i + 1}`}</span>
                <span>{u.name} {isMe && <span style={{ color: '#26ff8a', fontSize: '0.85em', marginLeft: '0.5rem' }}>(You)</span>}</span>
              </div>
              <div style={{ fontSize: '1.25rem', color: isTop3 ? '#f0c040' : 'var(--text-light)' }}>
                {u.aura_score}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
