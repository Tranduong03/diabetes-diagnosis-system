import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "./index.css";

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
      // 1. ML PREDICTION (chỉ số y tế)
      // ============================================================
      const mlData = { ...dataToPredict };
      delete mlData.Symptoms;

      const mlResponse = await fetch('http://localhost:8000/api/v1/ai/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(mlData)
      });

      if (!mlResponse.ok) {
        if (mlResponse.status === 401) {
          throw new Error('Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.');
        }
        throw new Error('Không thể kết nối đến server');
      }

      const mlResult = await mlResponse.json();
      
      // ============================================================
      // 2. NLP PREDICTION (triệu chứng - PhoBERT)
      // ============================================================
      let nlpResult = null;
      if (dataToPredict.Symptoms && dataToPredict.Symptoms.trim()) {
        try {
          const nlpResponse = await fetch('http://localhost:8000/api/v1/ai/predict/symptoms', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ symptoms: dataToPredict.Symptoms.trim() })
          });

          if (nlpResponse.ok) {
            nlpResult = await nlpResponse.json();
          }
        } catch (nlpError) {
          console.error('❌ NLP Error:', nlpError);
        }
      }
      
      // ============================================================
      // 3. HIỂN THỊ KẾT QUẢ ML
      // ============================================================
      const mlModels = mlResult.individual_predictions || [];
      const mlResults = mlModels.map(m =>
        `${m.model}: ${m.result} (${(m.confidence * 100).toFixed(0)}%)`
      ).join('\n');

      // ============================================================
      // 4. HIỂN THỊ KẾT QUẢ NLP
      // ============================================================
      let nlpText = "Không có mô tả triệu chứng";
      if (nlpResult && nlpResult.success) {
        const outcome = nlpResult.outcome === 1 ? "Có nguy cơ" : "Không có nguy cơ";
        const stage = nlpResult.stage || 0;
        const stageText = stage === 0 ? "Không có triệu chứng" :
                         stage === 1 ? "Tiền tiểu đường" :
                         stage === 2 ? "Phát triển" : "Nghiêm trọng";
        
        nlpText = `PhoBERT Analysis:
• Kết luận: ${outcome}
• Giai đoạn: ${stageText} (Stage ${stage})
• Độ tin cậy: ${(nlpResult.confidence * 100).toFixed(1)}%
• Phân tích: ${nlpResult.answer}`;
      }

      // ============================================================
      // 5. ENSEMBLE - CÂN BẰNG ML VÀ NLP
      // ============================================================
      let ensembleConf = mlResult.ensemble_confidence;
      let ensemblePred = mlResult.ensemble_prediction;
      let ensembleMethod = "ML only";
      
      if (nlpResult && nlpResult.success) {
        // Chuyển outcome NLP thành risk confidence
        const mlRisk = mlResult.ensemble_confidence;
        const nlpRisk = nlpResult.outcome === 1 
          ? nlpResult.confidence 
          : (1 - nlpResult.confidence);
        
        // CÂN BẰNG 50-50 giữa ML và NLP
        const mlWeight = 0.5;
        const nlpWeight = 0.5;
        
        ensembleConf = (mlRisk * mlWeight) + (nlpRisk * nlpWeight);
        
        // Voting: cả 2 phải đồng ý mới là có nguy cơ cao
        const totalVotes = mlResult.ensemble_prediction + nlpResult.outcome;
        ensemblePred = totalVotes >= 1 ? 1 : 0;
        
        ensembleMethod = "ML + NLP Ensemble (50-50)";
        
        console.log('📊 Balanced Ensemble:');
        console.log(`   ML: pred=${mlResult.ensemble_prediction}, risk=${(mlRisk*100).toFixed(1)}%`);
        console.log(`   NLP: pred=${nlpResult.outcome}, risk=${(nlpRisk*100).toFixed(1)}%`);
        console.log(`   Ensemble: pred=${ensemblePred}, risk=${(ensembleConf*100).toFixed(1)}%`);
      }

      const riskLevel =
        ensembleConf < 0.3 ? "Thấp" :
        ensembleConf < 0.6 ? "Trung bình" :
        "Cao";

      // ============================================================
      // 6. KẾT LUẬN CUỐI CÙNG (CÂN BẰNG)
      // ============================================================
      let finalConclusion = `
🎯 KẾT QUẢ TỔNG HỢP (${ensembleMethod})

📊 Dự đoán: ${ensemblePred === 1 ? 'CÓ NGUY CƠ' : 'KHÔNG CÓ NGUY CƠ'}
📈 Độ tin cậy ML: ${(mlResult.ensemble_confidence * 100).toFixed(1)}%`;

      if (nlpResult && nlpResult.success) {
        finalConclusion += `
📈 Độ tin cậy NLP: ${(nlpResult.confidence * 100).toFixed(1)}%`;
      }

      finalConclusion += `
📈 Độ tin cậy tổng hợp: ${(ensembleConf * 100).toFixed(1)}%
🎚️ Mức độ nguy cơ: ${riskLevel}

`;

      // Phân tích chi tiết
      if (riskLevel === "Cao") {
        finalConclusion += `🔴 CẢNH BÁO: Nguy cơ cao!

Các yếu tố đáng lo ngại:`;
        
        if (mlResult.ensemble_prediction === 1) {
          finalConclusion += `\n• ML phát hiện nguy cơ từ các chỉ số y tế`;
          if (dataToPredict.Glucose > 140) finalConclusion += `\n  - Glucose cao: ${dataToPredict.Glucose}`;
          if (dataToPredict.BMI > 30) finalConclusion += `\n  - BMI cao: ${dataToPredict.BMI}`;
        }
        
        if (nlpResult && nlpResult.outcome === 1) {
          finalConclusion += `\n• PhoBERT phát hiện triệu chứng rõ ràng`;
          if (nlpResult.stage > 0) {
            finalConclusion += `\n  - Giai đoạn: ${nlpResult.stage}`;
          }
        }
        
        finalConclusion += `\n\n🏥 Khuyến nghị:
• Đi khám bác sĩ NGAY để được tư vấn
• Xét nghiệm glucose máu đầy đủ
• Chuẩn bị hồ sơ y tế`;
        
      } else if (riskLevel === "Trung bình") {
        finalConclusion += `🟡 Nguy cơ trung bình

`;
        if (mlResult.ensemble_prediction === 1 && nlpResult && nlpResult.outcome === 0) {
          finalConclusion += `ML phát hiện nguy cơ từ chỉ số y tế, nhưng PhoBERT không thấy triệu chứng rõ ràng.`;
        } else if (mlResult.ensemble_prediction === 0 && nlpResult && nlpResult.outcome === 1) {
          finalConclusion += `PhoBERT phát hiện triệu chứng, nhưng các chỉ số y tế còn ổn.`;
        } else {
          finalConclusion += `Một số yếu tố cần chú ý.`;
        }
        
        finalConclusion += `\n\n👀 Khuyến nghị:
• Theo dõi sức khỏe định kỳ
• Kiểm tra 3-6 tháng/lần
• Duy trì lối sống lành mạnh`;
        
      } else {
        finalConclusion += `🟢 Kết quả tốt!

Cả ML và PhoBERT đều không phát hiện nguy cơ rõ ràng.

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
                    <li key={field}>{field}</li>
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
                <label>{key}</label>
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