import { useState } from 'react';
import { Api, setAuthToken } from '../services/api';

const ConfigDrawer = () => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [message, setMessage] = useState('');

  const handleLogin = async () => {
    try {
      await Api.login(username, password);
      setMessage('认证成功');
    } catch (error) {
      setMessage((error as Error).message);
    }
  };

  const handleManualToken = (token: string) => {
    setAuthToken(token || null);
    setMessage('已更新 Token');
  };

  return (
    <div style={{ marginTop: 16 }}>
      <h3>认证</h3>
      <input value={username} onChange={(e) => setUsername(e.target.value)} style={inputStyle} placeholder="用户名" />
      <input
        value={password}
        type="password"
        onChange={(e) => setPassword(e.target.value)}
        style={inputStyle}
        placeholder="密码"
      />
      <button style={buttonStyle} onClick={handleLogin}>
        登录获取 Token
      </button>
      <input
        placeholder="或手动粘贴 Token"
        onChange={(event) => handleManualToken(event.target.value)}
        style={inputStyle}
      />
      {message && <small style={{ color: '#22d3ee' }}>{message}</small>}
    </div>
  );
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '8px 10px',
  borderRadius: 6,
  border: '1px solid #1e293b',
  marginBottom: 8,
  background: '#0f172a',
  color: '#e2e8f0',
};

const buttonStyle: React.CSSProperties = {
  width: '100%',
  padding: '8px 10px',
  borderRadius: 6,
  border: 'none',
  background: '#14b8a6',
  color: '#0f172a',
  cursor: 'pointer',
  marginBottom: 8,
};

export default ConfigDrawer;
