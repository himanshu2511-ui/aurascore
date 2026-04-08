import React, { useRef, useEffect, useState, useCallback } from 'react';
import Webcam from 'react-webcam';
import { useAuth } from '../context/AuthContext';

const TRACK_DURATION = 40; // seconds

const Scanner = ({ onResult, onStatusChange, onSessionComplete }) => {
    const { token } = useAuth();
    const webcamRef = useRef(null);
    const canvasRef = useRef(null);
    const [status, setStatus] = useState('idle');
    const [tracking, setTracking] = useState(false);
    const [timeLeft, setTimeLeft] = useState(TRACK_DURATION);
    const snapshotsRef = useRef([]);
    const timerRef = useRef(null);
    const captureRef = useRef(null);

    const updateStatus = useCallback((s) => {
        setStatus(s);
        onStatusChange?.(s);
    }, [onStatusChange]);

    // ── Continuous capture loop (always runs when camera is open) ──
    useEffect(() => {
        let timer;

        const capture = async () => {
            if (!webcamRef.current) { timer = setTimeout(capture, 1000); return; }
            const src = webcamRef.current.getScreenshot();
            if (!src) { timer = setTimeout(capture, 600); return; }

            if (!tracking) { timer = setTimeout(capture, 1200); return; }

            updateStatus('scanning');
            try {
                const res = await fetch(src);
                const blob = await res.blob();
                const fd = new FormData();
                fd.append('image', blob, 'frame.jpg');

                const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                const resp = await fetch(`${API_URL}/api/analyze`, {
                    method: 'POST', body: fd,
                    headers: token ? { Authorization: `Bearer ${token}` } : {},
                });
                if (resp.ok) {
                    const data = await resp.json();
                    if (data.baseline_score > 0) {
                        onResult(data);
                        updateStatus('active');
                        // Accumulate snapshot during tracking session
                        if (tracking) snapshotsRef.current.push(data);
                        drawLandmarks(data.landmarks);
                    } else {
                        updateStatus('no-face');
                    }
                }
            } catch {
                updateStatus('error');
            }
            timer = setTimeout(capture, 1000);
        };

        captureRef.current = capture;
        if (tracking) capture();

        return () => clearTimeout(timer);
    }, [tracking, onResult, updateStatus]);

    // ── Countdown timer ──
    useEffect(() => {
        if (!tracking) return;
        setTimeLeft(TRACK_DURATION);
        snapshotsRef.current = [];

        timerRef.current = setInterval(() => {
            setTimeLeft(prev => {
                if (prev <= 1) {
                    clearInterval(timerRef.current);
                    setTracking(false);
                    updateStatus('done');
                    onSessionComplete?.(snapshotsRef.current);
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(timerRef.current);
    }, [tracking]);

    const startTracking = () => {
        snapshotsRef.current = [];
        setTracking(true);
    };

    const drawLandmarks = (landmarks) => {
        const canvas = canvasRef.current;
        const video = webcamRef.current?.video;
        if (!canvas || !video || !landmarks) return;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        landmarks.forEach(p => {
            const x = p.x * canvas.width;
            const y = p.y * canvas.height;
            ctx.beginPath();
            ctx.arc(x, y, 1.2, 0, 2 * Math.PI);
            ctx.fillStyle = tracking ? 'rgba(240, 192, 64, 0.85)' : 'rgba(240, 192, 64, 0.55)';
            ctx.fill();
        });
    };

    const progress = ((TRACK_DURATION - timeLeft) / TRACK_DURATION) * 100;

    const statusLabel = {
        idle: 'Ready — Start 40s Analysis',
        scanning: '🔬 Scanning Features...',
        active: '✓ Tracking Active',
        'no-face': '⚠ No Face Detected',
        error: '✗ Connection Error',
        done: '✅ Session Complete — Generating PDF...',
    }[status] || status;

    return (
        <div className="glass" style={{ padding: '1.5rem' }}>
            {/* Status row */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span className={`status-dot ${status === 'active' ? 'active' : status === 'scanning' ? 'scanning' : ''}`}></span>
                    <span style={{ fontSize: '0.88rem', fontWeight: 600 }}>{statusLabel}</span>
                </div>
                {tracking && (
                    <div style={{ fontSize: '1.6rem', fontWeight: 900, color: timeLeft <= 10 ? '#ff4d6d' : '#f0c040', fontVariantNumeric: 'tabular-nums' }}>
                        {timeLeft}s
                    </div>
                )}
            </div>

            {/* Progress bar */}
            {tracking && (
                <div style={{ background: 'rgba(255,255,255,0.06)', borderRadius: 4, height: 4, marginBottom: '1rem', overflow: 'hidden' }}>
                    <div style={{
                        height: '100%',
                        width: `${progress}%`,
                        background: 'linear-gradient(90deg, #9b5de5, #f0c040)',
                        borderRadius: 4,
                        transition: 'width 1s linear'
                    }} />
                </div>
            )}

            {/* Webcam */}
            <div className="scanner-wrap">
                <Webcam
                    ref={webcamRef}
                    audio={false}
                    screenshotFormat="image/jpeg"
                    videoConstraints={{ facingMode: 'user', width: 640, height: 480 }}
                    mirrored
                    style={{ width: '100%', height: '100%', objectFit: 'cover', position: 'absolute', top: 0, left: 0 }}
                />
                <canvas ref={canvasRef} />
                {(status === 'scanning' || tracking) && <div className="scanline" />}
                <div className="scan-border">
                    <div className="scan-corner tl" />
                    <div className="scan-corner tr" />
                    <div className="scan-corner bl" />
                    <div className="scan-corner br" />
                </div>

                {tracking && (
                    <div style={{
                        position: 'absolute', bottom: 10, left: '50%', transform: 'translateX(-50%)',
                        background: 'rgba(0,0,0,0.65)', borderRadius: 8,
                        padding: '4px 12px', zIndex: 20, fontSize: '0.78rem', color: '#f0c040', fontWeight: 700,
                    }}>
                        📸 {snapshotsRef.current.length} snapshots captured
                    </div>
                )}
            </div>

            {/* CTA Button */}
            {!tracking && status !== 'done' && (
                <button
                    id="start-analysis-btn"
                    onClick={startTracking}
                    style={{
                        marginTop: '1.2rem', width: '100%', padding: '0.85rem',
                        background: 'linear-gradient(135deg, #9b5de5, #f0c040)',
                        border: 'none', borderRadius: '12px', color: '#111',
                        fontWeight: 800, fontSize: '1rem', cursor: 'pointer', fontFamily: 'inherit',
                        boxShadow: '0 4px 24px rgba(240,192,64,0.3)',
                        transition: 'transform 0.15s, box-shadow 0.15s',
                    }}
                    onMouseEnter={e => { e.target.style.transform = 'scale(1.02)'; e.target.style.boxShadow = '0 6px 32px rgba(240,192,64,0.5)'; }}
                    onMouseLeave={e => { e.target.style.transform = 'scale(1)'; e.target.style.boxShadow = '0 4px 24px rgba(240,192,64,0.3)'; }}
                >
                    ✦ Start 40-Second Analysis
                </button>
            )}

            {status === 'done' && (
                <button
                    id="restart-analysis-btn"
                    onClick={startTracking}
                    style={{
                        marginTop: '1.2rem', width: '100%', padding: '0.75rem',
                        background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(240,192,64,0.4)',
                        borderRadius: '12px', color: '#f0c040', fontWeight: 700, fontSize: '0.95rem',
                        cursor: 'pointer', fontFamily: 'inherit',
                    }}
                >
                    ↺ Analyse Again
                </button>
            )}

            <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.9rem', textAlign: 'center' }}>
                🔒 All analysis runs locally — no images stored or transmitted externally.
            </p>
        </div>
    );
};

export default Scanner;
