import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const ScoreRing = ({ value, label, size = 120, color = '#f0c040' }) => {
    const r = 48;
    const circ = 2 * Math.PI * r;
    const offset = circ - (value / 100) * circ;

    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.4rem' }}>
            <svg width={size} height={size} viewBox="0 0 110 110">
                <circle cx="55" cy="55" r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
                <motion.circle
                    cx="55" cy="55" r={r}
                    fill="none"
                    stroke={color}
                    strokeWidth="8"
                    strokeLinecap="round"
                    strokeDasharray={circ}
                    initial={{ strokeDashoffset: circ }}
                    animate={{ strokeDashoffset: offset }}
                    transition={{ duration: 1.4, ease: 'easeOut' }}
                    transform="rotate(-90 55 55)"
                    style={{ filter: `drop-shadow(0 0 8px ${color}60)` }}
                />
                <text x="55" y="52" textAnchor="middle" fill="white" fontSize="18" fontWeight="800">{value}</text>
                <text x="55" y="66" textAnchor="middle" fill="#6b7280" fontSize="9">/100</text>
            </svg>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.8px' }}>{label}</span>
        </div>
    );
};

const FeatureBar = ({ feature, index }) => {
    const catColors = {
        genetics: '#9b5de5', grooming: '#00e5ff', fitness: '#26ff8a', skin: '#f0c040', style: '#ff8c42'
    };
    const color = catColors[feature.category] || '#f0c040';

    return (
        <motion.div
            className="feature-row"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.08 }}
        >
            <div className="feature-header">
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    <span className={`cat-badge cat-${feature.category}`}>{feature.category}</span>
                    <span className="feature-name">{feature.name}</span>
                </div>
                <div className="feature-scores">
                    <span className="score-now">{feature.baseline}</span>
                    <span style={{ color: 'var(--muted)' }}>→</span>
                    <span className="score-pot">{feature.potential}✦</span>
                </div>
            </div>
            <div className="bar-track">
                <div className="bar-potential" style={{ width: `${feature.potential}%`, background: `${color}` }} />
                <motion.div
                    className="bar-fill"
                    style={{ background: `linear-gradient(90deg, ${color}aa, ${color})` }}
                    initial={{ width: 0 }}
                    animate={{ width: `${feature.baseline}%` }}
                    transition={{ duration: 1.2, delay: index * 0.08 + 0.3, ease: 'easeOut' }}
                />
            </div>
            <p style={{ fontSize: '0.76rem', color: 'var(--muted)', marginTop: '0.3rem' }}>{feature.tip}</p>
        </motion.div>
    );
};

const Scorecard = ({ analysis }) => {
    if (!analysis) {
        return (
            <div className="glass" style={{ padding: '2rem', display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ fontSize: '3rem', opacity: 0.3 }}>✦</div>
                <p style={{ color: 'var(--muted)', fontSize: '0.95rem' }}>Awaiting face scan...</p>
            </div>
        );
    }

    return (
        <AnimatePresence>
            <motion.div
                className="glass"
                style={{ padding: '1.8rem' }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                {/* Dual Score Rings */}
                <div style={{ display: 'flex', justifyContent: 'center', gap: '2.5rem', marginBottom: '2rem' }}>
                    <ScoreRing value={analysis.baseline_score} label="Your Baseline" color="#9b5de5" size={110} />
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '0.2rem' }}>
                        <span style={{ fontSize: '1.5rem' }}>→</span>
                        <span style={{ fontSize: '0.7rem', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '1px' }}>With effort</span>
                    </div>
                    <ScoreRing value={analysis.potential_score} label="Your Potential" color="#f0c040" size={110} />
                </div>

                {/* Feature Breakdown */}
                <div className="section-title">
                    <span>⚡</span> Feature Analysis
                </div>
                {analysis.features.map((f, i) => <FeatureBar key={f.name} feature={f} index={i} />)}
            </motion.div>
        </AnimatePresence>
    );
};

export default Scorecard;
