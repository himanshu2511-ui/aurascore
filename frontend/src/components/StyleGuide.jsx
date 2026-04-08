import React from 'react';
import { motion } from 'framer-motion';

const SHAPE_ICONS = {
    Oval: '⬭', Round: '⬤', Square: '■', Heart: '♥', Diamond: '◆', Oblong: '▭',
};

const StyleGuide = ({ analysis }) => {
    if (!analysis) {
        return (
            <div className="glass" style={{ padding: '2rem', minHeight: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ fontSize: '2.5rem', opacity: 0.25 }}>💇</div>
                <p style={{ color: 'var(--muted)' }}>Scan your face to unlock your Style Guide</p>
            </div>
        );
    }

    const { grooming } = analysis;

    return (
        <div>
            <div className="glass" style={{ padding: '1.8rem', marginBottom: '1.5rem' }}>
                <div className="section-title" style={{ marginBottom: '1rem' }}>
                    <span>💇</span> Your Personal Style Guide
                </div>

                <div className="face-shape-badge">
                    <span>{SHAPE_ICONS[grooming.face_shape] || '●'}</span>
                    {grooming.face_shape} Face Shape
                </div>

                <div className="style-section">
                    <h4>✂️ Recommended Hairstyles</h4>
                    <div className="style-chips">
                        {grooming.hairstyles.map(h => <span key={h} className="style-chip">{h}</span>)}
                    </div>
                </div>

                <div className="style-section">
                    <h4>🧔 Beard Style Suggestions</h4>
                    <div className="style-chips">
                        {grooming.beard_styles.map(b => <span key={b} className="style-chip">{b}</span>)}
                    </div>
                </div>

                <div className="style-section">
                    <h4>👓 Best Glasses Frames</h4>
                    <div className="style-chips">
                        {grooming.glasses_frames.map(g => <span key={g} className="style-chip">{g}</span>)}
                    </div>
                </div>
            </div>

            <div className="glass" style={{ padding: '1.8rem' }}>
                <div className="section-title" style={{ marginBottom: '1rem' }}>
                    <span>💡</span> Pro Styling Tips
                </div>
                <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.7rem' }}>
                    {grooming.style_tips.map((tip, i) => (
                        <motion.li
                            key={i}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.15 }}
                            style={{ fontSize: '0.9rem', color: 'var(--muted)', display: 'flex', gap: '0.6rem', lineHeight: 1.6 }}
                        >
                            <span style={{ color: 'var(--cyan)', flexShrink: 0 }}>→</span> {tip}
                        </motion.li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default StyleGuide;
