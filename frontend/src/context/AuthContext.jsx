import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);   // { name, email }
    const [token, setToken] = useState(null);
    const [loading, setLoading] = useState(true);

    // Rehydrate from localStorage on mount
    useEffect(() => {
        const savedToken = localStorage.getItem('aura_token');
        const savedUser = localStorage.getItem('aura_user');
        if (savedToken && savedUser) {
            setToken(savedToken);
            setUser(JSON.parse(savedUser));
        }
        setLoading(false);
    }, []);

    const login = (tokenStr, userData) => {
        setToken(tokenStr);
        setUser(userData);
        localStorage.setItem('aura_token', tokenStr);
        localStorage.setItem('aura_user', JSON.stringify(userData));
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('aura_token');
        localStorage.removeItem('aura_user');
    };

    // Attach token to all fetch calls via a helper
    const authFetch = async (url, options = {}) => {
        return fetch(url, {
            ...options,
            headers: {
                ...(options.headers || {}),
                ...(token ? { Authorization: `Bearer ${token}` } : {}),
            },
        });
    };

    return (
        <AuthContext.Provider value={{ user, token, login, logout, loading, authFetch }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
