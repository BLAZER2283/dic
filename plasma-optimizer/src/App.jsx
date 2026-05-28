import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, ComposedChart
} from 'recharts';

axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const getLossesColor = (v) => {
  if (v < 8) return 'text-green';
  if (v < 12) return 'text-yellow';
  return 'text-red';
};
const getGrainColor = (v) => {
  if (v >= 100 && v <= 140) return 'text-green';
  if (v >= 80 && v <= 160) return 'text-yellow';
  return 'text-red';
};
const getStabilityColor = (v) => {
  if (v >= 80) return 'text-green';
  if (v >= 60) return 'text-yellow';
  return 'text-red';
};

const App = () => {
  const defaultParams = {
    material: 'ОТ4',
    diameter: 58.0,
    length: 700.0,
    mass_total: 66.0,
    I_target: 1390.0,
    n_electrode: 30000.0,
    plasma_offset: 0.0,
    plasma_angle: 86.0,
    gas_flow: 2.6,
    pusher_speed: 45.0,
    vibration_level: 2.0,
    n_ogark: 26000.0,
    time_from_last_cleaning: 0,
    roller_wear_mm: 0.0,
    ambient_T: 20.0,
  };

  const [params, setParams] = useState(defaultParams);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [calcId, setCalcId] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const pollingRef = useRef(null);
  const [username, setUsername] = useState(null);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const decodeTokenPayload = (token) => {
    try {
      const parts = token.split('.');
      if (parts.length !== 3) return null;
      const b = parts[1].replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(b).split('').map(c => '%'+('00'+c.charCodeAt(0).toString(16)).slice(-2)).join(''));
      return JSON.parse(jsonPayload);
    } catch (err) {
      return null;
    }
  };

  const getUsernameFromToken = (token) => {
    const payload = decodeTokenPayload(token);
    if (!payload) return null;
    return (
      payload.username ||
      payload.preferred_username ||
      payload.user?.username ||
      payload.email ||
      payload.name ||
      null
    );
  };

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get('/api/auth/me/');
      if (response.data?.username) {
        setUsername(response.data.username);
        return;
      }
      if (response.data?.user?.username) {
        setUsername(response.data.user.username);
        return;
      }
    } catch (err) {
      // ignore; fallback to token decode below
    }

    const token = localStorage.getItem('access_token');
    setUsername(token ? getUsernameFromToken(token) : null);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setIsAuthenticated(false);
    setUsername(null);
    setShowUserMenu(false);
    window.location.href = '/dic/login';
  };

  const toggleUserMenu = (event) => {
    event.stopPropagation();
    setShowUserMenu((prev) => !prev);
  };

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setIsAuthenticated(!!token);

    const initAuth = async () => {
      if (token) {
        await fetchCurrentUser();
      } else {
        setUsername(null);
      }
    };

    initAuth();

    const path = window.location.pathname;
    const match = path.match(/\/ucrp\/(\d+)/);
    if (match) {
      const id = parseInt(match[1]);
      setCalcId(id);
      fetchCalculationById(id);
    } else {
      loadHistory();
    }
  }, []);

  useEffect(() => {
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    const handleDocumentClick = (event) => {
      const target = event.target;
      if (showUserMenu && !target.closest('.user-menu-wrapper')) {
        setShowUserMenu(false);
      }
    };

    window.addEventListener('click', handleDocumentClick);
    return () => {
      window.removeEventListener('click', handleDocumentClick);
    };
  }, [showUserMenu]);

  const startPolling = (id) => {
    if (pollingRef.current) clearInterval(pollingRef.current);
    pollingRef.current = setInterval(async () => {
      try {
        const res = await axios.get(`/api/calculations/${id}/`);
        if (res.data?.results) {
          setResult(res.data);
          setLoading(false);
          clearInterval(pollingRef.current);
          pollingRef.current = null;
        }
      } catch (e) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
        setLoading(false);
      }
    }, 2000);
  };

  const fetchCalculationById = async (id) => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`/api/calculations/${id}/`);
      setResult(res.data);
      if (res.data.results) {
        setLoading(false);
        return;
      }
      startPolling(id);
      if (res.data.material) {
        setParams({
          material: res.data.material,
          diameter: res.data.diameter,
          length: res.data.length,
          mass_total: res.data.mass_total,
          I_target: res.data.I_target,
          n_electrode: res.data.n_electrode,
          plasma_offset: res.data.plasma_offset || 0,
          plasma_angle: res.data.plasma_angle || 86,
          gas_flow: res.data.gas_flow || 2.6,
          pusher_speed: res.data.pusher_speed || 45,
          vibration_level: res.data.auxiliary_params?.vibration_level || 2,
          n_ogark: res.data.auxiliary_params?.n_ogark || 26000,
          time_from_last_cleaning: res.data.auxiliary_params?.time_from_last_cleaning || 0,
          roller_wear_mm: res.data.auxiliary_params?.roller_wear_mm || 0,
          ambient_T: res.data.auxiliary_params?.ambient_T || 20,
        });
      }
    } catch (err) {
      setError('Расчёт не найден');
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    try {
      const res = await axios.get('/api/calculations/');
      const items = Array.isArray(res.data) ? res.data : res.data.results || [];
      setHistory(items);
      if (items.length > 0 && !result) {
        const lastCompleted = items.find(i => i.calculated_at);
        if (lastCompleted) {
          setResult(lastCompleted);
        }
      }
    } catch (e) {}
  };

  const validateParam = (name, value) => {
    const ranges = {
      diameter: { min: 54, max: 60 },
      length: { min: 650, max: 720 },
      mass_total: { min: 1, max: 300 },
      I_target: { min: 1150, max: 1600 },
      n_electrode: { min: 27000, max: 34400 },
      plasma_offset: { min: 0, max: 20 },
      plasma_angle: { min: 70, max: 95 },
      gas_flow: { min: 2.0, max: 3.0 },
      pusher_speed: { min: 35, max: 60 },
      vibration_level: { min: 0, max: 10 },
      n_ogark: { min: 23000, max: 30000 },
      time_from_last_cleaning: { min: 0, max: 100 },
      roller_wear_mm: { min: 0, max: 2.5 },
      ambient_T: { min: 10, max: 45 },
    };
    if (ranges[name]) {
      if (value < ranges[name].min) return ranges[name].min;
      if (value > ranges[name].max) return ranges[name].max;
    }
    return value;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    let parsedValue = e.target.type === 'number' ? parseFloat(value) : value;
    if (e.target.type === 'number' && !isNaN(parsedValue)) {
      parsedValue = validateParam(name, parsedValue);
    }
    setParams(prev => ({ ...prev, [name]: parsedValue }));
  };

  const generateXAxisTicks = (length) => {
    const step = 50;
    const ticks = [];
    for (let i = 0; i <= length; i += step) {
      ticks.push(i);
    }
    if (ticks[ticks.length - 1] !== length) {
      ticks.push(length);
    }
    return ticks;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const parts = token.split('.');
          if (parts.length === 3) {
            const b = parts[1].replace(/-/g, '+').replace(/_/g, '/');
            const payload = JSON.parse(decodeURIComponent(atob(b).split('').map(c => '%'+('00'+c.charCodeAt(0).toString(16)).slice(-2)).join('')));
            if (payload.exp && Date.now() >= payload.exp * 1000) {
              localStorage.removeItem('access_token');
              setLoading(false);
              setError('Токен истёк — выполните вход заново.');
              return;
            }
          }
        } catch (err) {}
      }

      const response = await axios.post('/api/calculations/', params, {
        headers: { 'Content-Type': 'application/json' }
      });
      const newId = response.data.calculation_id;
      window.history.pushState(null, '', `/ucrp/${newId}`);
      setCalcId(newId);
      setResult(null);
      startPolling(newId);
      try {
        const h = await axios.get('/api/ucrp/calculations/');
        setHistory(Array.isArray(h.data) ? h.data : h.data.results || []);
      } catch (e) {}
    } catch (err) {
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 401) {
          localStorage.removeItem('access_token');
          setError('Неавторизован: токен недействителен или истёк. Войдите снова.');
        } else {
          setError(err.response?.data?.detail || err.message);
        }
      } else if (err.message === 'Failed to fetch') {
        setError('Не удалось соединиться с сервером.');
      } else {
        setError(err.message);
      }
      setLoading(false);
    }
  };
  
  const resetForm = () => {
    setParams(defaultParams);
    setResult(null);
    setCalcId(null);
    window.history.replaceState(null, '', '/ucrp/');
  };

  const getRes = (r) => (r?.results) || r;
  const getInternal = (r) => r?.internal_data || {};
  const getWarnings = (r) => r?.warnings_data || {};

  const getChartData = (resItem) => {
    if (!resItem) return [];
    const res = getRes(resItem);
    if (!res?.x_grid) return [];
    const internal = getInternal(resItem);
    return (res.x_grid || []).map((x, idx) => ({
      x: x,
      current: res?.optimal_I_by_length?.[idx],
      speed: res?.optimal_n_by_length?.[idx],
      temperature: internal?.T_profile ? internal.T_profile[idx] : null,
    }));
  };

  const xAxisTicks = generateXAxisTicks(params.length);

  const resData = result ? getRes(result) : null;
  
  return (
    <div className="app">
      <header className="header">
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1>Plasma Optimizer</h1>
            <p>Автоматизация расчёта оптимальных параметров Установки Центробежного Распыления (УЦР)</p>
          </div>
          <div style={{ display: 'flex', gap: '10px', position: 'relative' }}>
            {isAuthenticated ? (
              <div className="user-menu-wrapper" style={{ position: 'relative' }}>
                <button
                  type="button"
                  className="btn-secondary btn-user"
                  style={{ padding: '8px 16px', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '6px' }}
                  onClick={toggleUserMenu}
                >
                  {username || 'ADMIN'}
                  <span style={{ fontSize: '12px' }}>▾</span>
                </button>
                {showUserMenu && (
                  <div className="user-menu-dropdown">
                    <button type="button" className="user-menu-item" onClick={handleLogout}>
                      Выйти
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <a href="/dic/login" target="_blank" style={{ color: '#fff', textDecoration: 'none' }}>
                <button className="btn-secondary" style={{ padding: '8px 16px', fontSize: '14px' }}>
                  Войти
                </button>
              </a>
            )}
            <a href="/dic/" target="_blank" style={{ color: '#fff', textDecoration: 'none' }}>
              <button className="btn-secondary" style={{ padding: '8px 16px', fontSize: '14px' }}>
                DIC Analyzer
              </button>
            </a>
          </div>
        </div>
      </header>
      
      <div className="container">
        <div className="grid">
          <div className="form-card">
            <h2 className="form-title">Параметры процесса</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Материал</label>
                <select name="material" value={params.material} onChange={handleChange}>
                  <option value="ОТ4">ОТ4 (титановый сплав)</option>
                  <option value="ВТ6">ВТ6 / Ti-6Al-4V</option>
                  <option value="ЭП741НП">ЭП741НП (никелевый сплав)</option>
                </select>
              </div>
              
              <div className="form-row">
                <div className="form-group">
                  <label>Диаметр (мм)</label>
                  <input type="number" name="diameter" value={params.diameter} onChange={handleChange} step="0.5" />
                  <div className="hint">54–60 мм</div>
                </div>
                <div className="form-group">
                  <label>Длина (мм)</label>
                  <input type="number" name="length" value={params.length} onChange={handleChange} step="10" />
                  <div className="hint">650–720 мм</div>
                </div>
              </div>
              
              <div className="form-row">
                <div className="form-group">
                  <label>Ток (А)</label>
                  <input type="number" name="I_target" value={params.I_target} onChange={handleChange} step="10" />
                  <div className="hint">1150–1600 А</div>
                </div>
                <div className="form-group">
                  <label>Скорость (об/мин)</label>
                  <input type="number" name="n_electrode" value={params.n_electrode} onChange={handleChange} step="100" />
                  <div className="hint">27000–34400</div>
                </div>
              </div>
              
              <div className="form-row">
                <div className="form-group">
                  <label>Смещение плазмы (мм)</label>
                  <input type="number" name="plasma_offset" value={params.plasma_offset} onChange={handleChange} step="1" />
                  <div className="hint">0–20 мм</div>
                </div>
                <div className="form-group">
                  <label>Угол плазмы (°)</label>
                  <input type="number" name="plasma_angle" value={params.plasma_angle} onChange={handleChange} step="1" />
                  <div className="hint">70–95°</div>
                </div>
              </div>
              
              <div className="form-row">
                <div className="form-group">
                  <label>Газ (л/с)</label>
                  <input type="number" name="gas_flow" value={params.gas_flow} onChange={handleChange} step="0.1" />
                  <div className="hint">2.0–3.0 л/с</div>
                </div>
                <div className="form-group">
                  <label>Подача (мм/мин)</label>
                  <input type="number" name="pusher_speed" value={params.pusher_speed} onChange={handleChange} step="1" />
                  <div className="hint">35–60 мм/мин</div>
                </div>
              </div>
              
              <details>
                <summary>Дополнительные параметры</summary>
                <div style={{ marginTop: '12px' }}>
                  <div className="form-row">
                    <div className="form-group">
                      <label>Вибрация (мм/с)</label>
                      <input type="number" name="vibration_level" value={params.vibration_level} onChange={handleChange} step="0.1" />
                      <div className="hint">0–10 мм/с</div>
                    </div>
                    <div className="form-group">
                      <label>Скорость огарка</label>
                      <input type="number" name="n_ogark" value={params.n_ogark} onChange={handleChange} step="100" />
                      <div className="hint">23000–30000</div>
                    </div>
                  </div>
                  <div className="form-row">
                    <div className="form-group">
                      <label>Плавок без чистки</label>
                      <input type="number" name="time_from_last_cleaning" value={params.time_from_last_cleaning} onChange={handleChange} />
                      <div className="hint">0–100 циклов</div>
                    </div>
                    <div className="form-group">
                      <label>Износ ролика (мм)</label>
                      <input type="number" name="roller_wear_mm" value={params.roller_wear_mm} onChange={handleChange} step="0.1" />
                      <div className="hint">0–2.5 мм</div>
                    </div>
                  </div>
                </div>
              </details>
              
              <div className="button-group">
                <button type="submit" disabled={loading} className="btn-primary">
                  {loading ? 'Расчёт...' : 'Рассчитать'}
                </button>
                <button type="button" onClick={resetForm} className="btn-secondary">
                  Сброс
                </button>
              </div>
            </form>
          </div>
          
          <div className="results-area">
            {error && (
              <div style={{ background: '#fee2e2', border: '1px solid #fecaca', color: '#991b1b', padding: '12px', marginBottom: '16px' }}>
                <strong>Ошибка:</strong> {error}
              </div>
            )}
            
            {!result && !loading && (
              <div className="empty-state">
                <p>Введите параметры и нажмите «Рассчитать»</p>
                <p style={{ fontSize: '12px', marginTop: '8px' }}>Программа рассчитает оптимальные параметры УЦР и даст рекомендации</p>
              </div>
            )}

            {history && history.length > 0 && Array.isArray(history) && (
              <div className="history-list" style={{ marginTop: '18px' }}>
                <h3 style={{ marginBottom: '8px' }}>Завершённые расчёты</h3>
                <ul>
                  {history.map(item => (
                    <li key={item?.id || Math.random()} style={{ marginBottom: '6px' }}>
                      <a href={`/ucrp/${item?.id}`} style={{ color: '#3d6b3d' }}>
                        <strong>#{item?.id}</strong> {item?.material} — {item?.diameter} мм
                      </a>
                      {(item?.calculated_at) ? ` — ${new Date(item.calculated_at).toLocaleString()}` : ' — в процессе'}
                      {(item?.results) ? (
                        <div style={{ fontSize: '12px', color: '#6b5e4a' }}>Потери: {item?.results?.predicted_losses_pct}% — Размер: {Math.round(item?.results?.predicted_grain_size)} мкм</div>
                      ) : null}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {loading && !result?.results && (
              <div className="loading">
                <div className="spinner"></div>
                <p style={{ marginTop: '12px' }}>
                  {result ? 'Расчёт выполняется...' : 'Идёт расчёт...'}
                </p>
              </div>
            )}
            
            {result?.results && resData && (
              <>
                {calcId && (
                  <div style={{ marginBottom: '12px', fontSize: '14px', color: '#6b5e4a' }}>
                    Расчёт #{calcId}
                  </div>
                )}
                <div className="kpi-grid">
                  <div className="kpi-card">
                    <div className="kpi-label">Потери материала</div>
                    <div className={`kpi-value ${getLossesColor(resData.predicted_losses_pct)}`}>
                      {resData.predicted_losses_pct}%
                    </div>
                    <div className="kpi-sub">норма {'<10%'}</div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-label">Размер гранул</div>
                    <div className={`kpi-value ${getGrainColor(resData.predicted_grain_size)}`}>
                      {resData.predicted_grain_size} мкм
                    </div>
                    <div className="kpi-sub">цель 100–140 мкм</div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-label">Целевая фракция</div>
                    <div className="kpi-value text-blue">
                      {resData.frac_100_140_pct}%
                    </div>
                    <div className="kpi-sub">100–140 мкм</div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-label">Стабильность</div>
                    <div className={`kpi-value ${getStabilityColor(resData.stability_index)}`}>
                      {resData.stability_index}
                    </div>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${resData.stability_index}%` }}></div>
                    </div>
                  </div>
                </div>
                
                {getWarnings(result) && Object.values(getWarnings(result)).some(v => v === true) && (
                  <div className="warning-box">
                    <div className="warning-title">ПРЕДУПРЕЖДЕНИЯ</div>
                    <div>
                      {getWarnings(result).deposits && <span className="warning-badge badge-yellow">Налипания</span>}
                      {getWarnings(result).vibration && <span className="warning-badge badge-red">Вибрация</span>}
                      {getWarnings(result).cracking && <span className="warning-badge badge-red">Риск раскрытия</span>}
                      {getWarnings(result).overheating && <span className="warning-badge badge-orange">Перегрев</span>}
                    </div>
                  </div>
                )}
                
                <div className="chart-card">
                  <div className="chart-title">Оптимальные параметры по длине электрода</div>
                  <ResponsiveContainer width="100%" height={380}>
                    <ComposedChart data={getChartData(result)} margin={{ top: 25, right: 55, left: 55, bottom: 45 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#b8aa95" />
                      <XAxis 
                        dataKey="x" 
                        label={{ value: 'Длина электрода (мм)', position: 'bottom', offset: 10, style: { fontSize: '11px', fill: '#2c2c2c', fontFamily: 'Montserrat' } }}
                        domain={[0, params.length]}
                        ticks={xAxisTicks}
                        tick={{ fontSize: 10, fill: '#2c2c2c' }}
                      />
                      <YAxis 
                        yAxisId="left" 
                        label={{ value: 'Ток (А)', angle: -90, position: 'insideLeft', offset: -5, style: { fontSize: '11px', fill: '#2c2c2c', fontFamily: 'Montserrat' } }}
                        domain={[1000, 1600]}
                        tickCount={7}
                        tick={{ fontSize: 10, fill: '#2c2c2c' }}
                        width={50}
                      />
                      <YAxis 
                        yAxisId="right" 
                        orientation="right" 
                        label={{ value: 'Скорость (об/мин)', angle: 90, position: 'insideRight', offset: -5, style: { fontSize: '11px', fill: '#2c2c2c', fontFamily: 'Montserrat' } }}
                        domain={[25000, 32000]}
                        tickCount={7}
                        tick={{ fontSize: 10, fill: '#2c2c2c' }}
                        width={55}
                      />
                      <Tooltip 
                        formatter={(value, name) => {
                          if (name === 'Ток') return [`${value} А`, 'Ток'];
                          if (name === 'Скорость') return [`${value} об/мин`, 'Скорость'];
                          return [value, name];
                        }}
                        labelFormatter={(label) => `Длина: ${label} мм`}
                        contentStyle={{ fontSize: '11px', fontFamily: 'Montserrat', background: '#fffdf9', border: '1px solid #b8aa95', borderRadius: 0 }}
                      />
                      <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '11px', fontFamily: 'Montserrat' }} />
                      <Line 
                        yAxisId="left" 
                        type="monotone" 
                        dataKey="current" 
                        stroke="#3d6b3d" 
                        name="Ток" 
                        strokeWidth={2}
                        dot={{ r: 3, fill: '#3d6b3d' }}
                        activeDot={{ r: 5 }}
                      />
                      <Line 
                        yAxisId="right" 
                        type="monotone" 
                        dataKey="speed" 
                        stroke="#3a5c6b" 
                        name="Скорость" 
                        strokeWidth={2}
                        dot={{ r: 3, fill: '#3a5c6b' }}
                        activeDot={{ r: 5 }}
                      />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
                
                {getInternal(result).T_profile && (
                  <div className="chart-card">
                    <div className="chart-title">Температурный профиль</div>
                    <ResponsiveContainer width="100%" height={350}>
                      <LineChart data={getChartData(result)} margin={{ top: 25, right: 55, left: 55, bottom: 45 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#b8aa95" />
                        <XAxis 
                          dataKey="x" 
                          label={{ value: 'Длина электрода (мм)', position: 'bottom', offset: 10, style: { fontSize: '11px', fill: '#2c2c2c', fontFamily: 'Montserrat' } }}
                          domain={[0, params.length]}
                          ticks={xAxisTicks}
                          tick={{ fontSize: 10, fill: '#2c2c2c' }}
                        />
                        <YAxis 
                          label={{ value: 'Температура (°C)', angle: -90, position: 'insideLeft', offset: -5, style: { fontSize: '11px', fill: '#2c2c2c', fontFamily: 'Montserrat' } }}
                          domain={['auto', 'auto']}
                          tickCount={8}
                          tick={{ fontSize: 10, fill: '#2c2c2c' }}
                          width={55}
                        />
                        <Tooltip 
                          formatter={(value) => [`${value.toFixed(0)}°C`, 'Температура']}
                          labelFormatter={(label) => `Длина: ${label} мм`}
                          contentStyle={{ fontSize: '11px', fontFamily: 'Montserrat', background: '#fffdf9', border: '1px solid #b8aa95', borderRadius: 0 }}
                        />
                        <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '11px', fontFamily: 'Montserrat' }} />
                        <Line 
                          type="monotone" 
                          dataKey="temperature" 
                          stroke="#8b3a3a" 
                          name="Температура" 
                          strokeWidth={2}
                          dot={{ r: 3, fill: '#8b3a3a' }}
                          activeDot={{ r: 5 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}
                
                <div className="recommendations-box">
                  <div className="recommendations-title">РЕКОМЕНДАЦИИ ОПЕРАТОРУ</div>
                  {result.recommendations && result.recommendations.length > 0 ? (
                    <ul className="recommendations-list">
                      {result.recommendations.map((rec, idx) => (
                        <li key={idx}>{rec}</li>
                      ))}
                    </ul>
                  ) : (
                    <p style={{ fontSize: '12px', color: '#6b5e4a' }}>Нет рекомендаций. Параметры в оптимальном диапазоне.</p>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;