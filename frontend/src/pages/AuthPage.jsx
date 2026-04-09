import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';

let API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
if (API.endsWith('/')) API = API.slice(0, -1);
if (!API.startsWith('http')) API = `https://${API}`;


const slide = {
    initial: { opacity: 0, x: 60 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -60 },
};

const InputField = ({ id, label, type = 'text', value, onChange, placeholder, maxLength }) => (
    <div style={{ marginBottom: '1.1rem' }}>
        <label htmlFor={id} style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: '0.4rem' }}>{label}</label>
        <input
            id={id}
            type={type}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            maxLength={maxLength}
            style={{
                width: '100%', padding: '0.8rem 1rem', background: 'rgba(255,255,255,0.05)',
                border: '1px solid rgba(255,255,255,0.1)', borderRadius: '10px',
                color: '#f0f0f5', fontSize: '1rem', fontFamily: 'inherit', outline: 'none',
                transition: 'border-color 0.2s', boxSizing: 'border-box',
            }}
            onFocus={e => e.target.style.borderColor = '#f0c040'}
            onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
        />
    </div>
);

const SubmitBtn = ({ label, loading, onClick }) => (
    <button
        onClick={onClick}
        disabled={loading}
        style={{
            width: '100%', padding: '0.9rem', marginTop: '0.5rem',
            background: loading ? 'rgba(240,192,64,0.4)' : 'linear-gradient(135deg, #9b5de5, #f0c040)',
            border: 'none', borderRadius: '12px', color: '#111',
            fontWeight: 800, fontSize: '1rem', cursor: loading ? 'not-allowed' : 'pointer',
            fontFamily: 'inherit', transition: 'opacity 0.2s, transform 0.15s',
            boxShadow: '0 4px 24px rgba(240,192,64,0.25)',
        }}
    >
        {loading ? '⏳ Please wait...' : label}
    </button>
);

// ── Step 1: Sign Up ────────────────────────────────────────────────────────
function SignupStep({ onSuccess, onSwitchLogin }) {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [pass, setPass] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async () => {
        if (!name || !email || !pass) { setError('All fields are required.'); return; }
        if (pass.length < 6) { setError('Password must be at least 6 characters.'); return; }
        setLoading(true); setError('');
        try {
            const r = await fetch(`${API}/auth/signup`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password: pass }),
            });
            const data = await r.json();
            if (!r.ok) throw new Error(data.detail || 'Signup failed');
            onSuccess(email, name);
        } catch (e) { setError(e.message); }
        setLoading(false);
    };

    return (
        <motion.div key="signup" {...slide} transition={{ duration: 0.3 }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '0.3rem' }}>Create Account</h2>
            <p style={{ color: '#6b7280', fontSize: '0.88rem', marginBottom: '1.8rem' }}>Join AuraScore — your AI glow-up coach.</p>
            <InputField id="su-name" label="Full Name" value={name} onChange={e => setName(e.target.value)} placeholder="Alex Johnson" />
            <InputField id="su-email" label="Email Address" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="alex@example.com" />
            <InputField id="su-pass" label="Password" type="password" value={pass} onChange={e => setPass(e.target.value)} placeholder="Min 6 characters" />
            {error && <p style={{ color: '#ff4d6d', fontSize: '0.82rem', marginBottom: '0.5rem' }}>⚠ {error}</p>}
            <SubmitBtn label="Create Account & Send OTP" loading={loading} onClick={handleSubmit} />
            <p style={{ textAlign: 'center', marginTop: '1.2rem', fontSize: '0.85rem', color: '#6b7280' }}>
                Already have an account?{' '}
                <span onClick={onSwitchLogin} style={{ color: '#f0c040', cursor: 'pointer', fontWeight: 600 }}>Log In</span>
            </p>
        </motion.div>
    );
}

// ── Step 2: OTP Verify ────────────────────────────────────────────────────
function OtpStep({ email, name, onSuccess, onResend }) {
    const [otp, setOtp] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [resent, setResent] = useState(false);

    const handleVerify = async () => {
        if (otp.length !== 6) { setError('Enter the 6-digit code.'); return; }
        setLoading(true); setError('');
        try {
            const r = await fetch(`${API}/auth/verify`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, otp }),
            });
            const data = await r.json();
            if (!r.ok) throw new Error(data.detail || 'Verification failed');
            onSuccess(data.access_token, { name: data.user_name, email: data.user_email });
        } catch (e) { setError(e.message); }
        setLoading(false);
    };

    const handleResend = async () => {
        await fetch(`${API}/auth/resend-otp`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email }),
        });
        setResent(true);
        setTimeout(() => setResent(false), 5000);
    };

    return (
        <motion.div key="otp" {...slide} transition={{ duration: 0.3 }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '0.3rem' }}>Check Your Email</h2>
            <p style={{ color: '#6b7280', fontSize: '0.88rem', marginBottom: '0.8rem' }}>
                We sent a 6-digit code to <strong style={{ color: '#f0c040' }}>{email}</strong>
            </p>
            <p style={{ color: '#4b5563', fontSize: '0.78rem', marginBottom: '1.8rem' }}>
                💡 No email? Check your spam folder or check the backend terminal for the OTP (dev mode).
            </p>

            {/* OTP Input — big centered boxes */}
            <div style={{ marginBottom: '1.2rem' }}>
                <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: '0.8rem' }}>Verification Code</label>
                <input
                    id="otp-input"
                    type="text"
                    inputMode="numeric"
                    maxLength={6}
                    value={otp}
                    onChange={e => setOtp(e.target.value.replace(/\D/g, ''))}
                    placeholder="000000"
                    style={{
                        width: '100%', padding: '1rem', textAlign: 'center',
                        fontSize: '2rem', fontWeight: 900, letterSpacing: '10px',
                        background: 'rgba(240,192,64,0.06)', border: '2px solid rgba(240,192,64,0.4)',
                        borderRadius: '12px', color: '#f0c040', fontFamily: 'inherit',
                        outline: 'none', boxSizing: 'border-box',
                    }}
                />
            </div>

            {error && <p style={{ color: '#ff4d6d', fontSize: '0.82rem', marginBottom: '0.5rem' }}>⚠ {error}</p>}
            {resent && <p style={{ color: '#26ff8a', fontSize: '0.82rem', marginBottom: '0.5rem' }}>✓ New OTP sent!</p>}
            <SubmitBtn label="Verify Email & Enter" loading={loading} onClick={handleVerify} />
            <p style={{ textAlign: 'center', marginTop: '1.2rem', fontSize: '0.85rem', color: '#6b7280' }}>
                Didn't receive it?{' '}
                <span onClick={handleResend} style={{ color: '#f0c040', cursor: 'pointer', fontWeight: 600 }}>Resend OTP</span>
            </p>
        </motion.div>
    );
}

// ── Step 3: Log In ─────────────────────────────────────────────────────────
function LoginStep({ onSuccess, onSwitchSignup }) {
    const [email, setEmail] = useState('');
    const [pass, setPass] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleLogin = async () => {
        if (!email || !pass) { setError('Enter email and password.'); return; }
        setLoading(true); setError('');
        try {
            const r = await fetch(`${API}/auth/login`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password: pass }),
            });
            const data = await r.json();
            if (!r.ok) throw new Error(data.detail || 'Login failed');
            onSuccess(data.access_token, { name: data.user_name, email: data.user_email });
        } catch (e) { setError(e.message); }
        setLoading(false);
    };

    return (
        <motion.div key="login" {...slide} transition={{ duration: 0.3 }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '0.3rem' }}>Welcome Back</h2>
            <p style={{ color: '#6b7280', fontSize: '0.88rem', marginBottom: '1.8rem' }}>Sign in to your AuraScore account.</p>
            <InputField id="li-email" label="Email Address" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="alex@example.com" />
            <InputField id="li-pass" label="Password" type="password" value={pass} onChange={e => setPass(e.target.value)} placeholder="Your password" />
            {error && <p style={{ color: '#ff4d6d', fontSize: '0.82rem', marginBottom: '0.5rem' }}>⚠ {error}</p>}
            <SubmitBtn label="Log In" loading={loading} onClick={handleLogin} />
            <p style={{ textAlign: 'center', marginTop: '1.2rem', fontSize: '0.85rem', color: '#6b7280' }}>
                New here?{' '}
                <span onClick={onSwitchSignup} style={{ color: '#f0c040', cursor: 'pointer', fontWeight: 600 }}>Create Account</span>
            </p>
        </motion.div>
    );
}

// ── Main AuthPage ──────────────────────────────────────────────────────────
export default function AuthPage() {
    const { login } = useAuth();
    const [step, setStep] = useState('signup'); // 'signup' | 'otp' | 'login'
    const [pendingEmail, setPendingEmail] = useState('');
    const [pendingName, setPendingName] = useState('');

    const handleSignupSuccess = (email, name) => {
        setPendingEmail(email);
        setPendingName(name);
        setStep('otp');
    };

    const handleVerifySuccess = (token, userData) => login(token, userData);
    const handleLoginSuccess = (token, userData) => login(token, userData);

    return (
        <div style={{
            minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
            padding: '2rem',
            background: 'radial-gradient(ellipse 80% 60% at 50% -10%, rgba(155,93,229,0.25) 0%, transparent 70%), #080810',
        }}>
            <div style={{ width: '100%', maxWidth: 420 }}>
                {/* Logo */}
                <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
                    <h1 style={{
                        fontSize: '2.4rem', fontWeight: 900, letterSpacing: '-1px', margin: 0,
                        background: 'linear-gradient(135deg, #f0c040, #ff8c42, #9b5de5)',
                        WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
                    }}>✦ AuraScore</h1>
                    <p style={{ color: '#4b5563', fontSize: '0.85rem', marginTop: '0.3rem' }}>AI Personal Glow-Up Coach</p>
                </div>

                {/* Card */}
                <div style={{
                    background: 'rgba(18,18,30,0.75)', backdropFilter: 'blur(20px)',
                    border: '1px solid rgba(255,255,255,0.08)', borderRadius: '20px',
                    padding: '2.2rem', boxShadow: '0 20px 60px rgba(0,0,0,0.5)',
                    overflow: 'hidden',
                }}>
                    {/* Progress dots */}
                    <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginBottom: '1.8rem' }}>
                        {['signup', 'otp', 'login'].map(s => (
                            <div key={s} style={{
                                width: s === step ? 24 : 8, height: 8, borderRadius: 4,
                                background: s === step ? 'linear-gradient(90deg,#9b5de5,#f0c040)' : 'rgba(255,255,255,0.1)',
                                transition: 'all 0.3s',
                            }} />
                        ))}
                    </div>

                    <AnimatePresence mode="wait">
                        {step === 'signup' && (
                            <SignupStep
                                onSuccess={handleSignupSuccess}
                                onSwitchLogin={() => setStep('login')}
                            />
                        )}
                        {step === 'otp' && (
                            <OtpStep
                                email={pendingEmail}
                                name={pendingName}
                                onSuccess={handleVerifySuccess}
                                onResend={() => { }}
                            />
                        )}
                        {step === 'login' && (
                            <LoginStep
                                onSuccess={handleLoginSuccess}
                                onSwitchSignup={() => setStep('signup')}
                            />
                        )}
                    </AnimatePresence>
                </div>

                <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.74rem', color: '#374151', lineHeight: 1.6 }}>
                    🔒 Your data is private. Facial analysis runs locally — no images are stored.
                </p>
            </div>
        </div>
    );
}
