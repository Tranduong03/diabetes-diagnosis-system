import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './Login.css';

const Login = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Đăng nhập thất bại');
      }

      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));

      if (data.user.role === 'admin') {
        navigate('/admin/dashboard');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <h1 className="main-title">Đăng Nhập</h1>

      <div className="auth-wrapper">
        <section className="auth-card">
          <div className="title">
            <div className="logo">🔐</div>
            <div>
              <h1>Diabetes Diagnosis System</h1>
              <p className="lead">
                Đăng nhập để sử dụng hệ thống chẩn đoán bệnh tiểu đường
              </p>
            </div>
          </div>

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Tên đăng nhập</label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                placeholder="Nhập tên đăng nhập"
              />
            </div>

            <div className="form-group">
              <label>Mật khẩu</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="Nhập mật khẩu"
              />
            </div>

            <div className="form-footer">
              <label className="remember-me">
                <input type="checkbox" />
                <span>Ghi nhớ đăng nhập</span>
              </label>
              <a href="#" className="forgot-link">Quên mật khẩu?</a>
            </div>

            <div className="actions">
              <button type="submit" disabled={loading}>
                {loading ? 'Đang xử lý...' : 'Đăng nhập →'}
              </button>
            </div>
          </form>

          <div className="auth-switch">
            <p>
              Chưa có tài khoản? <Link to="/register">Đăng ký ngay</Link>
            </p>
          </div>

          <div className="demo-info">
            <p className="demo-title">🎯 Tài khoản demo:</p>
            <div className="demo-grid">
              <div className="demo-item">
                <span className="chip admin">Admin</span>
                <code>admin / admin123</code>
              </div>
              <div className="demo-item">
                <span className="chip user">User</span>
                <code>Đăng ký mới</code>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Login;