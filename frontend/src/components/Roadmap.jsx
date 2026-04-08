import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const WeekCard = ({ week, index }) => {
    const [open, setOpen] = useState(index === 0);

    return (
        <motion.div
            className={`week-card ${open ? 'open' : ''}`}
            onClick={() => setOpen(!open)}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
        >
            <div className="week-header">
                <span className="week-icon">{week.icon}</span>
                <div>
                    <div className="week-label">{week.week}</div>
                    <div className="week-focus">{week.focus}</div>
                </div>
                <span style={{ marginLeft: 'auto', color: 'var(--muted)', fontSize: '1.1rem' }}>{open ? '▲' : '▼'}</span>
            </div>

            <AnimatePresence>
                {open && (
                    <motion.div
                        className="week-goals"
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.25 }}
                    >
                        {week.goals.map((g, i) => (
                            <div key={i} className="week-goal-item">{g}</div>
                        ))}
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};

const Roadmap = ({ analysis }) => {
    if (!analysis) {
        return (
            <div className="glass" style={{ padding: '2rem', minHeight: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ fontSize: '2.5rem', opacity: 0.25 }}>🗺️</div>
                <p style={{ color: 'var(--muted)' }}>Scan your face to generate your Glow-Up Roadmap</p>
            </div>
        );
    }

    return (
        <div>
            <div className="glass" style={{ padding: '1.8rem', marginBottom: '1.5rem' }}>
                <div className="section-title" style={{ marginBottom: '0.6rem' }}>
                    <span>🎯</span> Your 8-Week AI Glow-Up Roadmap
                </div>
                <p style={{ fontSize: '0.85rem', color: 'var(--muted)', marginBottom: '1.5rem', lineHeight: 1.6 }}>
                    Personalized for your <strong style={{ color: 'var(--gold)' }}>{analysis.face_shape} face shape</strong> and skin profile. Tap any week to expand its action plan.
                </p>
                <div className="roadmap-weeks">
                    {analysis.roadmap.map((week, i) => (
                        <WeekCard key={week.week} week={week} index={i} />
                    ))}
                </div>
            </div>

            {/* Skin Analysis Card */}
            <div className="glass" style={{ padding: '1.8rem' }}>
                <div className="section-title" style={{ marginBottom: '1rem' }}>
                    <span>🔬</span> Skin Intelligence Report
                </div>
                <div className="skin-grid">
                    <div className="skin-stat">
                        <div className="skin-stat-label">Skin Tone</div>
                        <div className="skin-stat-value" style={{ color: 'var(--gold)' }}>{analysis.skin.skin_tone}</div>
                    </div>
                    <div className="skin-stat">
                        <div className="skin-stat-label">Texture Score</div>
                        <div className="skin-stat-value" style={{ color: analysis.skin.texture_score >= 75 ? 'var(--green)' : 'var(--gold2)' }}>
                            {analysis.skin.texture_score}/100
                        </div>
                    </div>
                    <div className="skin-stat">
                        <div className="skin-stat-label">Dark Circles</div>
                        <div className="skin-stat-value" style={{ color: analysis.skin.dark_circle_severity === 'None' ? 'var(--green)' : 'var(--gold2)' }}>
                            {analysis.skin.dark_circle_severity}
                        </div>
                    </div>
                    <div className="skin-stat">
                        <div className="skin-stat-label">Skin Tier</div>
                        <div className="skin-stat-value" style={{ color: analysis.skin.skin_tier === 'Clean' ? 'var(--green)' : 'var(--red)' }}>
                            {analysis.skin.skin_tier}
                        </div>
                    </div>
                </div>

                <div className="section-title" style={{ marginBottom: '0.8rem' }}>
                    <span>💊</span> Skincare Recommendations
                </div>
                <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {analysis.skin.skincare_tips.map((tip, i) => (
                        <motion.li
                            key={i}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.12 }}
                            style={{ fontSize: '0.86rem', color: 'var(--muted)', display: 'flex', gap: '0.5rem', lineHeight: 1.55 }}
                        >
                            <span style={{ color: 'var(--gold)', flexShrink: 0 }}>✓</span> {tip}
                        </motion.li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default Roadmap;
