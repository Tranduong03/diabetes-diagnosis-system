import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "./index.css";

const FIELD_LABELS = {
  Pregnancies: "Số lần mang thai",
  Glucose: "Nồng độ đường huyết (mg/dL)",
  BloodPressure: "Huyết áp tâm trương (mmHg)",
  SkinThickness: "Độ dày nếp gấp da (mm)",
  Insulin: "Nồng độ Insulin (µU/mL)",
  BMI: "Chỉ số khối cơ thể (BMI)",
  DiabetesPedigreeFunction: "Chỉ số tiền sử gia đình mắc tiểu đường",
  Age: "Tuổi (năm)"
};


// Mean values từ dataset
const MEAN_VALUES = {
  Pregnancies: 4,
  Glucose: 121.7,
  BloodPressure: 72,
  SkinThickness: 29,
  Insulin: 141,
  BMI: 32.5,
  DiabetesPedigreeFunction: 0.472,
  Age: 33
};

const NUMERIC_FIELDS = Object.keys(MEAN_VALUES);

export default function Home() {
  const navigate = useNavigate();
  const warningRef = useRef(null);
  
  const [formData, setFormData] = useState({
    Pregnancies: 0,
    Glucose: 120,
    BloodPressure: 70,
    SkinThickness: 20,
    Insulin: 100,
    BMI: 26.5,
    DiabetesPedigreeFunction: 0.472,
    Age: 34,
    Symptoms: "",
  });
  
  const [results, setResults] = useState({
    ml: "Chưa có kết quả — nhấn 'Chẩn đoán' để bắt đầu.",
    nlp: "Chưa có kết quả — nhấn 'Chẩn đoán' để bắt đầu.",
    final: "Chưa có kết luận.",
  });
  
  const [loading, setLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showWarning, setShowWarning] = useState(false);
  const [missingFields, setMissingFields] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsLoggedIn(!!token);
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'Symptoms'
        ? value
        : value === '' ? '' : parseFloat(value)
    });
  };

  const handleClear = () => {
    setFormData({
      Pregnancies: 0,
      Glucose: 120,
      BloodPressure: 70,
      SkinThickness: 20,
      Insulin: 100,
      BMI: 26.5,
      DiabetesPedigreeFunction: 0.472,
      Age: 34,
      Symptoms: "",
    });
    setResults({
      ml: "Chưa có kết quả — nhấn 'Chẩn đoán' để bắt đầu.",
      nlp: "Chưa có kết quả — nhấn 'Chẩn đoán' để bắt đầu.",
      final: "Chưa có kết luận.",
    });
    setShowWarning(false);
    setMissingFields([]);
  };

  const checkMissingFields = () => {
    const missing = [];
    NUMERIC_FIELDS.forEach(field => {
      const value = formData[field];
      if (
        value === '' || value === null || value === undefined ||
        (field === 'Pregnancies' && value < 0) ||
        (field !== 'Pregnancies' && value <= 0)
      ) {
        missing.push(field);
      }
    });
    return missing;
  };

  const handlePredict = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('⚠️ Vui lòng đăng nhập để sử dụng chức năng chẩn đoán!');
      navigate('/login');
      return;
    }

    const missing = checkMissingFields();
    
    if (missing.length > 0) {
      setMissingFields(missing);
      setShowWarning(true);
      setTimeout(() => {
        warningRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
      return;
    }

    await performPrediction(formData);
  };

  const handleContinueWithMissing = async () => {
    const completedData = { ...formData };
    missingFields.forEach(field => {
      completedData[field] = MEAN_VALUES[field];
    });
    setFormData(completedData);
    setShowWarning(false);
    setMissingFields([]);
    await performPrediction(completedData);
  };

  const handleCancelPrediction = () => {
    setShowWarning(false);
    setMissingFields([]);
  };

  const performPrediction = async (dataToPredict) => {
    const token = localStorage.getItem('token');
    setLoading(true);
    setResults({
      ml: "⏳ Đang phân tích với Machine Learning models...",
      nlp: "⏳ Đang phân tích triệu chứng với PhoBERT...",
      final: "⏳ Đang tổng hợp kết luận...",
    });

    try {
      // ============================================================
      // ✅ SỬ DỤNG ENSEMBLE ENDPOINT MỚI (1 request duy nhất)
      // ============================================================
      const response = await fetch('http://localhost:8000/api/v1/ai/predict/ensemble', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(dataToPredict)  // Gửi tất cả (ML + Symptoms)
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.');
        }
        throw new Error('Không thể kết nối đến server');
      }

      const result = await response.json();
      
      // ============================================================
      // HIỂN THỊ KẾT QUẢ (từ 1 response)
      // ============================================================
      
      // ML results
      const mlModels = result.individual_predictions.filter(p => 
        p.model !== 'PhoBERT'
      );
      const mlResults = mlModels.map(m =>
        `${m.model}: ${m.result} (${(m.confidence * 100).toFixed(0)}%)`
      ).join('\n');

      // NLP results
      let nlpText = "Không có mô tả triệu chứng";
      const nlpModel = result.individual_predictions.find(p => p.model === 'PhoBERT');
      if (nlpModel) {
        nlpText = `PhoBERT Analysis:
• Kết luận: ${nlpModel.result}
• Độ tin cậy: ${(nlpModel.confidence * 100).toFixed(1)}%`;
      }

      // Risk level
      const riskLevel = result.risk_level;
      const ensembleConf = result.ensemble_confidence;
      const ensemblePred = result.ensemble_prediction;

      const riskLevelMap = {
  low: 'Thấp',
  medium: 'Trung bình',
  high: 'Cao',
};

      const riskLevelText = riskLevelMap[riskLevel] || 'Không xác định';
      // Final conclusion
      let finalConclusion = `
KẾT QUẢ TỔNG HỢP

Dự đoán: ${ensemblePred === 1 ? 'CÓ NGUY CƠ' : 'KHÔNG CÓ NGUY CƠ'}
Độ tin cậy: ${(ensembleConf * 100).toFixed(1)}%
Mức độ nguy cơ: ${riskLevelText}

`;

      if (riskLevel === 'high') {
        finalConclusion += `🔴 CẢNH BÁO: Nguy cơ cao!

🏥 Khuyến nghị:
• Đi khám bác sĩ NGAY để được tư vấn
• Xét nghiệm glucose máu đầy đủ
• Chuẩn bị hồ sơ y tế`;
      } else if (riskLevel === 'medium') {
        finalConclusion += `🟡 Nguy cơ trung bình

👀 Khuyến nghị:
• Theo dõi sức khỏe định kỳ
• Kiểm tra 3-6 tháng/lần
• Duy trì lối sống lành mạnh`;
      } else {
        finalConclusion += `🟢 Kết quả tốt!

✅ Khuyến nghị:
• Tiếp tục duy trì lối sống lành mạnh
• Chế độ ăn cân bằng
• Vận động 30 phút/ngày
• Kiểm tra định kỳ hàng năm`;
      }

      setResults({
        ml: mlResults || "Không có dữ liệu từ ML models",
        nlp: nlpText,
        final: finalConclusion.trim(),
      });

    } catch (error) {
      console.error('Prediction error:', error);
      setResults({
        ml: `❌ Lỗi: ${error.message}`,
        nlp: `❌ Lỗi: ${error.message}`,
        final: `❌ Không thể thực hiện chẩn đoán.`,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="nav-header">
        <div className="nav-buttons">
          {isLoggedIn ? (
            <>
              <button onClick={() => navigate('/dashboard')} className="nav-btn">
                Dashboard
              </button>
              <button
                onClick={() => {
                  localStorage.removeItem('token');
                  localStorage.removeItem('user');
                  setIsLoggedIn(false);
                  alert('Đã đăng xuất');
                }}
                className="nav-btn"
              >
                Đăng xuất
              </button>
            </>
          ) : (
            <>
              <button onClick={() => navigate('/login')} className="nav-btn">
                Đăng nhập
              </button>
              <button onClick={() => navigate('/register')} className="nav-btn primary">
                Đăng ký
              </button>
            </>
          )}
        </div>
      </div>

      <h1 className="main-title">Diabetes Diagnosis System</h1>

      <div className="app">
        <section className="card">
          {showWarning && (
            <div ref={warningRef} className="warning-container" style={{
              backgroundColor: '#fef3c7',
              border: '2px solid #f59e0b',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '16px'
            }}>
              <div style={{ marginBottom: '12px' }}>
                <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#92400e', margin: '0 0 8px 0' }}>
                  ⚠️ Bạn nhập không đầy đủ thông tin
                </h3>
                <p style={{ color: '#b45309', margin: '0 0 8px 0' }}>
                  Các chỉ số sau chưa được điền:
                </p>
              </div>

              <div style={{
                backgroundColor: 'white',
                padding: '8px',
                borderRadius: '4px',
                marginBottom: '12px',
                border: '1px solid #fcd34d'
              }}>
                <ul style={{ margin: '0', paddingLeft: '20px', color: '#b45309' }}>
                  {missingFields.map(field => (
                    <li key={field}>{FIELD_LABELS[field]}</li>
                  ))}
                </ul>
              </div>

              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  onClick={handleContinueWithMissing}
                  style={{
                    flex: 1,
                    padding: '8px 16px',
                    backgroundColor: '#f59e0b',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    fontWeight: 'bold',
                    cursor: 'pointer'
                  }}
                >
                  ✓ Tiếp tục
                </button>
                <button
                  onClick={handleCancelPrediction}
                  style={{
                    flex: 1,
                    padding: '8px 16px',
                    backgroundColor: '#9ca3af',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    fontWeight: 'bold',
                    cursor: 'pointer'
                  }}
                >
                  ✕ Hủy
                </button>
              </div>
            </div>
          )}

          <div className="title">
            <div className="logo">DIA</div>
            <div>
              <h1>Hệ thống chẩn đoán bệnh tiểu đường</h1>
              <p className="lead">
                Nhập các chỉ số y tế và mô tả triệu chứng để hệ thống phân tích
              </p>
            </div>
          </div>

          <div className="grid">
            {NUMERIC_FIELDS.map((key) => (
              <div key={key} className="field">
                <label>{FIELD_LABELS[key] || key}</label>
                <input
                  type="number"
                  name={key}
                  value={formData[key]}
                  onChange={handleChange}
                  step={key === 'Pregnancies' || key === 'Age' ? '1' : '0.1'}
                  disabled={loading}
                  placeholder="Nhập giá trị"
                />
              </div>
            ))}
          </div>

          <div className="field full">
            <label>Mô tả triệu chứng / Hồ sơ bệnh án</label>
            <textarea
              name="Symptoms"
              value={formData.Symptoms}
              onChange={handleChange}
              placeholder="Ví dụ: khát nước, đi tiểu nhiều, sụt cân, mệt mỏi..."
              disabled={loading}
            />
          </div>

          <div className="actions">
            <button
              type="button"
              onClick={handlePredict}
              disabled={loading}
            >
              {loading ? 'Đang phân tích...' : 'Gửi dữ liệu →'}
            </button>
            <button
              type="button"
              className="secondary"
              onClick={handleClear}
              disabled={loading}
            >
              Xoá
            </button>
          </div>

          <small className="hint">
            💡 {isLoggedIn
              ? 'Nhập thông tin và nhấn "Gửi dữ liệu" để bắt đầu phân tích'
              : 'Vui lòng đăng nhập để sử dụng chức năng chẩn đoán'}
          </small>
        </section>

        <aside className="panel">
          <div className="result-card">
            <div className="result-row">
              <div>Machine Learning (Chỉ số y tế)</div>
              <div className="chip ml">ML</div>
            </div>
            <div className="placeholder">{results.ml}</div>
          </div>

          <div className="result-card">
            <div className="result-row">
              <div>PhoBERT NLP (Triệu chứng)</div>
              <div className="chip nlp">NLP</div>
            </div>
            <div className="placeholder">{results.nlp}</div>
          </div>

          <div className="result-card">
            <div className="result-row">
              <div>Kết luận (ML + NLP Ensemble)</div>
              <div className="chip final">Ensemble</div>
            </div>
            <div className="placeholder">{results.final}</div>
          </div>
        </aside>
      </div>
    </div>
  );
}