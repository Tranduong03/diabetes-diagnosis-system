import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

const Dashboard = () => {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  if (!user) return <div className="loading">Đang tải...</div>;

  return (
    <div className="dashboard-container">
      <h1 className="main-title">Dashboard</h1>

      {/* Header Card */}
      <div className="dashboard-wrapper">
        <section className="card header-card">
          <div className="title">
            <div className="logo">👤</div>
            <div className="user-info">
              <h1>Xin chào, {user.full_name || user.username}!</h1>
              <p className="lead">
                Chào mừng đến với hệ thống chẩn đoán bệnh tiểu đường
              </p>
            </div>
            <button className="logout-btn" onClick={handleLogout}>
              Đăng xuất
            </button>
          </div>
        </section>

        {/* Main Content Grid */}
        <div className="dashboard-grid">
          {/* Left Column - User Info */}
          <aside className="info-panel">
            <div className="result-card">
              <div className="card-header">
                <h3>Thông tin cá nhân</h3>
                <div className="chip user">User</div>
              </div>
              <div className="info-list">
                <div className="info-item">
                  <span className="info-label">Tên đăng nhập</span>
                  <span className="info-value">{user.username}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Email</span>
                  <span className="info-value">{user.email}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Họ và tên</span>
                  <span className="info-value">{user.full_name || 'Chưa cập nhật'}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Vai trò</span>
                  <span className="info-value">
                    <span className="chip user">{user.role === 'admin' ? 'Admin' : 'User'}</span>
                  </span>
                </div>
                <div className="info-item">
                  <span className="info-label">Trạng thái</span>
                  <span className="info-value">
                    <span className="chip success">Hoạt động</span>
                  </span>
                </div>
              </div>
            </div>

            {/* Statistics */}
            <div className="result-card">
              <div className="card-header">
                <h3>Thống kê</h3>
              </div>
              <div className="stats-grid">
                <div className="stat-item">
                  <div className="stat-value">0</div>
                  <div className="stat-label">Lượt chẩn đoán</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">0</div>
                  <div className="stat-label">Kết quả bình thường</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">0</div>
                  <div className="stat-label">Cần theo dõi</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">0</div>
                  <div className="stat-label">Nguy cơ cao</div>
                </div>
              </div>
            </div>
          </aside>

          {/* Right Column - Actions */}
          <section className="actions-panel">
            <div className="result-card action-card" onClick={() => navigate('/diagnosis')}>
              <div className="action-icon dm">📋</div>
              <h3>Chẩn đoán mới</h3>
              <p>Thực hiện chẩn đoán nguy cơ bệnh tiểu đường</p>
            </div>

            <div className="result-card action-card" onClick={() => navigate('/history')}>
              <div className="action-icon ml">📊</div>
              <h3>Lịch sử chẩn đoán</h3>
              <p>Xem lại các kết quả chẩn đoán trước đây</p>
            </div>

            <div className="result-card action-card" onClick={() => navigate('/info')}>
              <div className="action-icon nlp">📚</div>
              <h3>Thông tin y tế</h3>
              <p>Tìm hiểu về bệnh tiểu đường và phòng ngừa</p>
            </div>

            <div className="result-card action-card" onClick={() => navigate('/settings')}>
              <div className="action-icon final">⚙️</div>
              <h3>Cài đặt</h3>
              <p>Quản lý thông tin cá nhân và tài khoản</p>
              <div className="chip final">Settings</div>
            </div>
          </section>
        </div>

        {/* Recent Activity */}
        <section className="card activity-card">
          <div className="card-header">
            <h3>Hoạt động gần đây</h3>
          </div>
          <div className="activity-list">
            <div className="activity-item">
              <div className="activity-icon">📝</div>
              <div className="activity-content">
                <p className="activity-text">Chưa có hoạt động nào</p>
                <span className="activity-time">Hãy bắt đầu chẩn đoán đầu tiên của bạn!</span>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Dashboard;