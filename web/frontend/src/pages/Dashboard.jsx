import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [loadingStats, setLoadingStats] = useState(true);

  /* =========================
     LOAD USER INFO
  ========================== */
  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (!userData) {
      navigate('/login');
      return;
    }
    setUser(JSON.parse(userData));
  }, [navigate]);

  /* =========================
     FETCH STATISTICS
  ========================== */
  useEffect(() => {
    const fetchStatistics = async () => {
      const token = localStorage.getItem('token');
      if (!token) return;

      try {
        const response = await fetch(
          'http://localhost:8000/api/v1/ai/predictions/statistics',
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        if (!response.ok) throw new Error('Failed to fetch statistics');

        const data = await response.json();
        setStatistics(data.statistics);
      } catch (error) {
        console.error('Error loading statistics:', error);
      } finally {
        setLoadingStats(false);
      }
    };

    fetchStatistics();
  }, []);

  /* =========================
     LOGOUT
  ========================== */
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  if (!user) return <div className="loading">Đang tải...</div>;

  return (
    <div className="dashboard-container">

      {/* ================= HEADER ================= */}
      <header className="dashboard-header modern">
        <div>
          <h1>Xin chào, {user.full_name || user.username} 👋</h1>
          <p>Hệ thống hỗ trợ chẩn đoán nguy cơ bệnh tiểu đường</p>
        </div>
        <button className="logout-btn" onClick={handleLogout}>
          Đăng xuất
        </button>
      </header>

      {/* ================= NAV ================= */}
      <nav className="dashboard-nav modern">
        <button onClick={() => navigate('/diagnosis')}>📋 Chẩn đoán</button>
        <button onClick={() => navigate('/history')}>📊 Lịch sử</button>
        <button onClick={() => navigate('/info')}>📚 Y tế</button>
        <button onClick={() => navigate('/settings')}>⚙️ Cài đặt</button>
      </nav>

      {/* ================= MAIN ================= */}
      <main className="dashboard-main modern">

        <section className="dashboard-section">

          {/* ===== HERO ===== */}
          <article
            className="card hero-card"
            onClick={() => navigate('/diagnosis')}
          >
            <div className="hero-icon">🩺</div>
            <h2>Chẩn đoán mới</h2>
            <p>Thực hiện chẩn đoán nguy cơ tiểu đường ngay bây giờ</p>
            <span className="hero-cta">Bắt đầu →</span>
          </article>

          {/* ===== STATS ===== */}
          <article className="card stats-card">
            <h3>Thống kê nhanh</h3>

            {loadingStats || !statistics ? (
              <p>Đang tải dữ liệu...</p>
            ) : (
              <div className="stats-grid">
                <div className="stat green">
                  {statistics.low_risk_count}
                  <br />
                  <span>Bình thường</span>
                </div>

                <div className="stat blue">
                  {statistics.medium_risk_count}
                  <br />
                  <span>Cần theo dõi</span>
                </div>

                <div className="stat red">
                  {statistics.high_risk_count}
                  <br />
                  <span>Nguy cơ cao</span>
                </div>
              </div>
            )}

            {statistics && (
              <small className="stats-total">
                Tổng số chẩn đoán: {statistics.total_predictions}
              </small>
            )}
          </article>

          {/* ===== USER INFO ===== */}
          <article className="card info-card">
            <h3>Thông tin cá nhân</h3>
            <p><b>Tài khoản:</b> {user.username}</p>
            <p><b>Email:</b> {user.email}</p>
            <p><b>Vai trò:</b> {user.role}</p>
          </article>

        </section>

        {/* ================= ASIDE ================= */}
        <aside className="dashboard-aside modern">
          <h3>Hoạt động gần đây</h3>

          {!statistics || statistics.total_predictions === 0 ? (
            <>
              <p>📝 Chưa có hoạt động</p>
              <small>Hãy bắt đầu lần chẩn đoán đầu tiên</small>
            </>
          ) : (
            <>
              <p>🧠 Đã có {statistics.total_predictions} lần chẩn đoán</p>
              <button
                className="btn-link"
                onClick={() => navigate('/history')}
              >
                Xem chi tiết →
              </button>
            </>
          )}
        </aside>

      </main>

      {/* ================= FOOTER ================= */}
      <footer className="dashboard-footer">
        © 2025 – Diabetes Diagnosis System
      </footer>

    </div>
  );
};

export default Dashboard;
