import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './PredictionHistory.css';

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
          <option value="ml_only">Chỉ ML</option>
          <option value="nlp_only">Chỉ NLP</option>
          <option value="ensemble">Ensemble</option>
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
                      <span className={`badge ${typeBadge.class}`}>
                        {typeBadge.text}
                      </span>
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
                  {selectedPrediction.input_data.pregnancies !== null && (
                    <div>
                      <strong>Số lần mang thai:</strong>{' '}
                      {selectedPrediction.input_data.pregnancies}
                    </div>
                  )}
                  {selectedPrediction.input_data.glucose && (
                    <div>
                      <strong>Glucose:</strong> {selectedPrediction.input_data.glucose}
                    </div>
                  )}
                  {selectedPrediction.input_data.blood_pressure && (
                    <div>
                      <strong>Huyết áp:</strong>{' '}
                      {selectedPrediction.input_data.blood_pressure}
                    </div>
                  )}
                  {selectedPrediction.input_data.bmi && (
                    <div>
                      <strong>BMI:</strong> {selectedPrediction.input_data.bmi}
                    </div>
                  )}
                  {selectedPrediction.input_data.age && (
                    <div>
                      <strong>Tuổi:</strong> {selectedPrediction.input_data.age}
                    </div>
                  )}
                </div>
                {selectedPrediction.input_data.symptoms_text && (
                  <div className="symptoms-text">
                    <strong>Triệu chứng:</strong>
                    <p>{selectedPrediction.input_data.symptoms_text}</p>
                  </div>
                )}
              </section>

              {/* ML Results */}
              {selectedPrediction.ml_results && (
                <section className="detail-section">
                  <h3>🤖 Kết quả Machine Learning</h3>
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
                  {selectedPrediction.ml_results.individual_results && (
                    <div className="models-list">
                      <strong>Chi tiết từng model:</strong>
                      {selectedPrediction.ml_results.individual_results.map((model, idx) => (
                        <div key={idx} className="model-result">
                          <span>{model.model}:</span>
                          <span>{model.result}</span>
                          <span>({(model.confidence * 100).toFixed(0)}%)</span>
                        </div>
                      ))}
                    </div>
                  )}
                </section>
              )}

              {/* NLP Results */}
              {selectedPrediction.nlp_results && (
                <section className="detail-section">
                  <h3>💬 Kết quả NLP (PhoBERT)</h3>
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
                  <p>
                    <strong>Phương pháp:</strong>{' '}
                    {selectedPrediction.ensemble_results.method}
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