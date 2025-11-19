import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/auth/users', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch users');
      }

      const data = await response.json();
      setUsers(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleStatus = async (userId, currentStatus) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://localhost:8000/api/v1/auth/users/${userId}/status?is_active=${!currentStatus}`,
        {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to update user status');
      }

      fetchUsers();
    } catch (err) {
      alert('Lỗi: ' + err.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const stats = {
    total: users.length,
    active: users.filter(u => u.is_active).length,
    admins: users.filter(u => u.role === 'admin').length,
    users: users.filter(u => u.role === 'user').length,
  };

  return (
    <div className="dashboard-container">
      <h1 className="main-title">Admin Dashboard</h1>

      <div className="dashboard-wrapper">
        {/* Header */}
        <section className="card header-card">
          <div className="title">
            <div className="logo">👨‍💼</div>
            <div className="user-info">
              <h1>Quản trị hệ thống</h1>
              <p className="lead">
                Quản lý người dùng và giám sát hoạt động hệ thống
              </p>
            </div>
            <div className="header-actions">
              <button className="nav-btn" onClick={() => navigate('/dashboard')}>
                Dashboard
              </button>
              <button className="logout-btn" onClick={handleLogout}>
                Đăng xuất
              </button>
            </div>
          </div>
        </section>

        {/* Statistics Cards */}
        <div className="stats-cards">
          <div className="result-card stat-card">
            <div className="stat-icon dm">👥</div>
            <div className="stat-content">
              <div className="stat-value">{stats.total}</div>
              <div className="stat-label">Tổng người dùng</div>
            </div>
          </div>

          <div className="result-card stat-card">
            <div className="stat-icon ml">✅</div>
            <div className="stat-content">
              <div className="stat-value">{stats.active}</div>
              <div className="stat-label">Đang hoạt động</div>
            </div>
          </div>

          <div className="result-card stat-card">
            <div className="stat-icon nlp">🔐</div>
            <div className="stat-content">
              <div className="stat-value">{stats.admins}</div>
              <div className="stat-label">Quản trị viên</div>
            </div>
          </div>

          <div className="result-card stat-card">
            <div className="stat-icon final">👤</div>
            <div className="stat-content">
              <div className="stat-value">{stats.users}</div>
              <div className="stat-label">Người dùng</div>
            </div>
          </div>
        </div>

        {/* Users Table */}
        <section className="card table-card">
          <div className="card-header">
            <h3>Danh sách người dùng</h3>
            <div className="chip dm">{users.length} users</div>
          </div>

          {loading ? (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Đang tải dữ liệu...</p>
            </div>
          ) : error ? (
            <div className="error-state">
              <p>⚠️ Lỗi: {error}</p>
            </div>
          ) : (
            <div className="table-wrapper">
              <table className="users-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Họ tên</th>
                    <th>Vai trò</th>
                    <th>Trạng thái</th>
                    <th>Hành động</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td>{user.id}</td>
                      <td className="username-cell">
                        <span className="user-avatar">
                          {user.username.charAt(0).toUpperCase()}
                        </span>
                        {user.username}
                      </td>
                      <td className="email-cell">{user.email}</td>
                      <td>{user.full_name || '-'}</td>
                      <td>
                        <span className={`chip ${user.role === 'admin' ? 'admin' : 'user'}`}>
                          {user.role === 'admin' ? 'Admin' : 'User'}
                        </span>
                      </td>
                      <td>
                        <span className={`chip ${user.is_active ? 'success' : 'danger'}`}>
                          {user.is_active ? 'Hoạt động' : 'Vô hiệu'}
                        </span>
                      </td>
                      <td>
                        <button
                          onClick={() => handleToggleStatus(user.id, user.is_active)}
                          className={`action-btn ${user.is_active ? 'danger' : 'success'}`}
                        >
                          {user.is_active ? 'Vô hiệu hóa' : 'Kích hoạt'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default AdminDashboard;