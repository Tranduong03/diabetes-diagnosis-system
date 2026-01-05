import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './PredictionHistory.css';

const FIELD_LABELS = {
  HighBP: "Huyết áp cao",
  HighChol: "Cholesterol cao",
  Smoker: "Hút thuốc",
  HeartDiseaseorAttack: "Bệnh tim/Đau tim",
  PhysActivity: "Hoạt động thể chất",
  GenHlth: "Sức khỏe tổng quát",
  MentHlth: "Sức khỏe tinh thần",
  PhysHlth: "Sức khỏe thể chất",
  DiffWalk: "Khó khăn đi bộ",
  Age: "Nhóm tuổi"
};

const FIELD_DESCRIPTIONS = {
  HighBP: "Bạn có bị huyết áp cao?",
  HighChol: "Cholesterol cao?",
  Smoker: "Bạn có hút thuốc không?",
  HeartDiseaseorAttack: "Tiền sử bệnh tim?",
  PhysActivity: "Bạn có hoạt động thể chất trong 30 ngày không?",
  GenHlth: "Rất tốt → Kém",
  MentHlth: "Trong 30 ngày qua, sức khỏe tinh thần của bạn không tốt ở mức độ nào?",
  PhysHlth: "Trong 30 ngày qua, sức khỏe thể chất của bạn không tốt ở mức độ nào?",
  DiffWalk: "Gần đây bạn đi bộ hoặc leo cầu thang có nhanh mệt không?",
  Age: "Chọn độ tuổi của bạn"
};

const AGE_GROUPS = [
  { value: 1, label: "18-24 tuổi" },
  { value: 2, label: "25-29 tuổi" },
  { value: 3, label: "30-34 tuổi" },
  { value: 4, label: "35-39 tuổi" },
  { value: 5, label: "40-44 tuổi" },
  { value: 6, label: "45-49 tuổi" },
  { value: 7, label: "50-54 tuổi" },
  { value: 8, label: "55-59 tuổi" },
  { value: 9, label: "60-64 tuổi" },
  { value: 10, label: "65-69 tuổi" },
  { value: 11, label: "70-74 tuổi" },
  { value: 12, label: "75-79 tuổi" },
  { value: 13, label: "80+ tuổi" }
];

const HEALTH_OPTIONS = [
  { value: 1, label: "Rất tốt" },
  { value: 2, label: "Tốt" },
  { value: 3, label: "Bình thường" },
  { value: 4, label: "Kém" },
  { value: 5, label: "Rất kém" }
];

const MEN_HLTH_OPTIONS = [
  { value: 0, label: "Không bao giờ" },
  { value: 3, label: "Hiếm khi" },
  { value: 9, label: "Thỉnh thoảng" },
  { value: 16, label: "Thường xuyên" },
  { value: 30, label: "Liên tục" }
];

const PHYS_HLTH_OPTIONS = [
  { value: 0, label: "Không bao giờ" },
  { value: 3, label: "Hiếm khi" },
  { value: 9, label: "Thỉnh thoảng" },
  { value: 16, label: "Thường xuyên" },
  { value: 30, label: "Liên tục" }
];

const booleanFields = ['HighBP','HighChol','Smoker','HeartDiseaseorAttack','PhysActivity','DiffWalk'];



const PredictionHistory = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [totalCount, setTotalCount] = useState(0);
  const [selectedPrediction, setSelectedPrediction] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  
  // Filters
  const [filters, setFilters] = useState({
    predictionType: '',
    riskLevel: '',
    days: ''
  });
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    fetchHistory();
    fetchStatistics();
  }, [filters, currentPage]);

  const fetchHistory = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    setLoading(true);
    try {
      const skip = (currentPage - 1) * itemsPerPage;
      let url = `http://localhost:8000/api/v1/ai/predictions/history?skip=${skip}&limit=${itemsPerPage}`;
      
      if (filters.predictionType) url += `&prediction_type=${filters.predictionType}`;
      if (filters.riskLevel) url += `&risk_level=${filters.riskLevel}`;
      if (filters.days) url += `&days=${filters.days}`;

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Failed to fetch history');

      const data = await response.json();
      setHistory(data.history || []);
      setTotalCount(data.total_count || 0);
    } catch (error) {
      console.error('Error fetching history:', error);
      alert('Không thể tải lịch sử. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch('http://localhost:8000/api/v1/ai/predictions/statistics', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Failed to fetch statistics');

      const data = await response.json();
      setStatistics(data.statistics);
    } catch (error) {
      console.error('Error fetching statistics:', error);
    }
  };

  const fetchPredictionDetail = async (predictionId) => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`http://localhost:8000/api/v1/ai/predictions/history/${predictionId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Failed to fetch detail');

      const data = await response.json();
      setSelectedPrediction(data.prediction);
      setShowDetailModal(true);
    } catch (error) {
      console.error('Error fetching detail:', error);
      alert('Không thể tải chi tiết. Vui lòng thử lại.');
    }
  };

  const deletePrediction = async (predictionId) => {
    if (!confirm('Bạn có chắc muốn xóa kết quả này?')) return;

    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`http://localhost:8000/api/v1/ai/predictions/history/${predictionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Failed to delete');

      alert('Đã xóa thành công!');
      fetchHistory();
      fetchStatistics();
    } catch (error) {
      console.error('Error deleting:', error);
      alert('Không thể xóa. Vui lòng thử lại.');
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('vi-VN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getRiskBadge = (riskLevel) => {
    const badges = {
      'low': { text: 'Thấp', class: 'badge-low' },
      'medium': { text: 'Trung bình', class: 'badge-medium' },
      'high': { text: 'Cao', class: 'badge-high' }
    };
    return badges[riskLevel] || { text: 'N/A', class: 'badge-default' };
  };

  const getTypeBadge = (type) => {
    const badges = {
      'ml_only': { text: 'ML', class: 'type-ml' },
      'nlp_only': { text: 'NLP', class: 'type-nlp' },
      'ensemble': { text: 'Ensemble', class: 'type-ensemble' }
    };
    return badges[type] || { text: 'N/A', class: 'type-default' };
  };

  const totalPages = Math.ceil(totalCount / itemsPerPage);

  return (
    <div className="history-container">
      {/* Header */}
      <header className="history-header">
        <div>
          <h1>📊 Lịch sử chẩn đoán</h1>
          <p>Xem lại các kết quả dự đoán trước đây</p>
        </div>
        <button className="btn-back" onClick={() => navigate('/dashboard')}>
          ← Quay lại
        </button>
      </header>

      {/* Statistics */}
      {statistics && (
        <div className="stats-section">
          <div className="stat-card">
            <div className="stat-icon">📝</div>
            <div>
              <h3>{statistics.total_predictions}</h3>
              <p>Tổng dự đoán</p>
            </div>
          </div>
          <div className="stat-card green">
            <div className="stat-icon">✅</div>
            <div>
              <h3>{statistics.low_risk_count}</h3>
              <p>Nguy cơ thấp</p>
            </div>
          </div>
          <div className="stat-card yellow">
            <div className="stat-icon">⚠️</div>
            <div>
              <h3>{statistics.medium_risk_count}</h3>
              <p>Nguy cơ TB</p>
            </div>
          </div>
          <div className="stat-card red">
            <div className="stat-icon">🔴</div>
            <div>
              <h3>{statistics.high_risk_count}</h3>
              <p>Nguy cơ cao</p>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="filters-section">
        <select
          value={filters.predictionType}
          onChange={(e) => {
            setFilters({ ...filters, predictionType: e.target.value });
            setCurrentPage(1);
          }}
        >
          <option value="">Tất cả loại</option>
          <option value="ml_only">Chẩn đoán từ chỉ số sức khỏe</option>
          <option value="nlp_only">Chẩn đoán từ các triệu chứng</option>
          <option value="ensemble">Kết hợp 2 loại chẩn đoán</option>
        </select>

        <select
          value={filters.riskLevel}
          onChange={(e) => {
            setFilters({ ...filters, riskLevel: e.target.value });
            setCurrentPage(1);
          }}
        >
          <option value="">Tất cả mức độ</option>
          <option value="low">Nguy cơ thấp</option>
          <option value="medium">Nguy cơ trung bình</option>
          <option value="high">Nguy cơ cao</option>
        </select>

        <select
          value={filters.days}
          onChange={(e) => {
            setFilters({ ...filters, days: e.target.value });
            setCurrentPage(1);
          }}
        >
          <option value="">Tất cả thời gian</option>
          <option value="7">7 ngày gần đây</option>
          <option value="30">30 ngày gần đây</option>
          <option value="90">90 ngày gần đây</option>
        </select>
      </div>

      {/* History List */}
      {loading ? (
        <div className="loading">Đang tải...</div>
      ) : history.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <h3>Chưa có lịch sử chẩn đoán</h3>
          <p>Hãy thực hiện chẩn đoán đầu tiên của bạn</p>
          <button className="btn-primary" onClick={() => navigate('/')}>
            Chẩn đoán ngay
          </button>
        </div>
      ) : (
        <>
          <div className="history-list">
            {history.map((item) => {
              const riskBadge = getRiskBadge(item.risk_level);
              const typeBadge = getTypeBadge(item.prediction_type);

              return (
                <div key={item.id} className="history-item">
                  <div className="item-header">
                    <div>
                      {/* <span className={`badge ${typeBadge.class}`}>
                        {typeBadge.text}
                      </span> */}
                      <span className={`badge ${riskBadge.class}`}>
                        {riskBadge.text}
                      </span>
                    </div>
                    <span className="item-date">{formatDate(item.created_at)}</span>
                  </div>

                  <div className="item-body">
                    <div className="item-info">
                      <p>
                        <strong>Kết quả:</strong>{' '}
                        {item.ensemble_prediction === 1 ? (
                          <span className="result-positive">Có nguy cơ</span>
                        ) : (
                          <span className="result-negative">Không có nguy cơ</span>
                        )}
                      </p>
                      <p>
                        <strong>Độ tin cậy:</strong>{' '}
                        {(item.ensemble_confidence * 100).toFixed(1)}%
                      </p>
                      {item.input_summary && (
                        <div className="input-summary">
                          {item.input_summary.glucose && (
                            <span>Glucose: {item.input_summary.glucose}</span>
                          )}
                          {item.input_summary.bmi && (
                            <span>BMI: {item.input_summary.bmi}</span>
                          )}
                          {item.input_summary.age && (
                            <span>Tuổi: {item.input_summary.age}</span>
                          )}
                          {item.input_summary.has_symptoms && (
                            <span>✓ Có triệu chứng</span>
                          )}
                        </div>
                      )}
                    </div>

                    <div className="item-actions">
                      <button
                        className="btn-detail"
                        onClick={() => fetchPredictionDetail(item.id)}
                      >
                        Chi tiết
                      </button>
                      <button
                        className="btn-delete"
                        onClick={() => deletePrediction(item.id)}
                      >
                        Xóa
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              <button
                disabled={currentPage === 1}
                onClick={() => setCurrentPage(currentPage - 1)}
              >
                ← Trước
              </button>
              <span>
                Trang {currentPage} / {totalPages}
              </span>
              <button
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage(currentPage + 1)}
              >
                Sau →
              </button>
            </div>
          )}
        </>
      )}

      {/* Detail Modal */}
      {showDetailModal && selectedPrediction && (
        <div className="modal-overlay" onClick={() => setShowDetailModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Chi tiết dự đoán</h2>
              <button className="modal-close" onClick={() => setShowDetailModal(false)}>
                ✕
              </button>
            </div>

            <div className="modal-body">
              {/* Input Data */}
              <section className="detail-section">
                <h3>📝 Dữ liệu đầu vào</h3>
                <div className="detail-grid">
                  {Object.entries(selectedPrediction.input_data).map(([key, value]) => {
                    if (value === null || value === undefined) return null;

                    let displayValue = value;
                    if (booleanFields.includes(key)) {
                      displayValue = value === 1 ? 'Có' : 'Không';
                    }

                    // Nếu là tuổi, hiển thị theo nhóm tuổi
                    if (key === 'Age') {
                      const ageGroup = AGE_GROUPS.find((g) => g.value === value);
                      displayValue = ageGroup ? ageGroup.label : value;
                    }

                    // Nếu là sức khỏe tổng quát
                    if (key === 'GenHlth') {
                      const option = HEALTH_OPTIONS.find((o) => o.value === value);
                      displayValue = option ? option.label : value;
                    }

                    // Nếu là sức khỏe tinh thần
                    if (key === 'MentHlth') {
                      const option = MEN_HLTH_OPTIONS.find((o) => o.value === value);
                      displayValue = option ? option.label : value;
                    }

                    // Nếu là sức khỏe thể chất
                    if (key === 'PhysHlth') {
                      const option = PHYS_HLTH_OPTIONS.find((o) => o.value === value);
                      displayValue = option ? option.label : value;
                    }

                    return (
                      <div key={key} className="input-item">
                        <strong>{FIELD_LABELS[key] || key}:</strong>{' '}
                        <span title={FIELD_DESCRIPTIONS[key] || ''}>{displayValue}</span>
                      </div>
                    );
                  })}
                </div>
              </section>

              {/* ML Results */}
              {selectedPrediction.ml_results && (
                <section className="detail-section">
                  <h3>Dự đoán từ chỉ số sức khỏe</h3>
                  <p>
                    <strong>Dự đoán:</strong>{' '}
                    {selectedPrediction.ml_results.prediction === 1
                      ? 'Có nguy cơ'
                      : 'Không có nguy cơ'}
                  </p>
                  <p>
                    <strong>Độ tin cậy:</strong>{' '}
                    {(selectedPrediction.ml_results.confidence * 100).toFixed(1)}%
                  </p>
                </section>
              )}

              {/* NLP Results */}
              {selectedPrediction.nlp_results && (
                <section className="detail-section">
                  <h3>Dự đoán từ các triệu chứng</h3>
                  <p>
                    <strong>Dự đoán:</strong>{' '}
                    {selectedPrediction.nlp_results.prediction === 1
                      ? 'Có nguy cơ'
                      : 'Không có nguy cơ'}
                  </p>
                  {selectedPrediction.nlp_results.stage !== null && (
                    <p>
                      <strong>Giai đoạn:</strong> Stage {selectedPrediction.nlp_results.stage}
                    </p>
                  )}
                  <p>
                    <strong>Độ tin cậy:</strong>{' '}
                    {(selectedPrediction.nlp_results.confidence * 100).toFixed(1)}%
                  </p>
                  {selectedPrediction.nlp_results.answer && (
                    <div className="nlp-answer">
                      <strong>Phân tích:</strong>
                      <p>{selectedPrediction.nlp_results.answer}</p>
                    </div>
                  )}
                </section>
              )}

              {/* Ensemble Results */}
              <section className="detail-section ensemble-section">
                <h3>🎯 Kết luận tổng hợp</h3>
                <div className="ensemble-result">
                  <p>
                    <strong>Kết quả cuối cùng:</strong>{' '}
                    <span
                      className={
                        selectedPrediction.ensemble_results.prediction === 1
                          ? 'result-positive'
                          : 'result-negative'
                      }
                    >
                      {selectedPrediction.ensemble_results.prediction === 1
                        ? 'Có nguy cơ tiểu đường'
                        : 'Không có nguy cơ tiểu đường'}
                    </span>
                  </p>
                  <p>
                    <strong>Độ tin cậy:</strong>{' '}
                    {(selectedPrediction.ensemble_results.confidence * 100).toFixed(1)}%
                  </p>
                </div>
              </section>

              {/* Recommendations */}
              {selectedPrediction.recommendations &&
                selectedPrediction.recommendations.length > 0 && (
                  <section className="detail-section">
                    <h3>💡 Khuyến nghị</h3>
                    <ul className="recommendations-list">
                      {selectedPrediction.recommendations.map((rec, idx) => (
                        <li key={idx}>{rec}</li>
                      ))}
                    </ul>
                  </section>
                )}
            </div>

            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowDetailModal(false)}>
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictionHistory;