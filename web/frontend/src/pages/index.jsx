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
    dm: "Chưa có kết quả — nhấn 'Chẩn đoán' để bắt đầu.",
    ml: "Chưa có kết quả — nhấn 'Chẩn đoán' để bắt đầu.",
    nlp: "Chưa có kết quả — nhấn 'Chẩn đoán' để bắt đầu.",
    final: "Chưa có kết luận.",
  });

  const [loading, setLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showWarning, setShowWarning] = useState(false);
  const [missingFields, setMissingFields] = useState([]);
  const [pendingData, setPendingData] = useState(null);

  // Check login status
  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsLoggedIn(!!token);
  }, []);

const handleChange = (e) => {
  const { name, value } = e.target;
  
  setFormData({ 
    ...formData, 
    [name]: name === 'Symptoms' 
      ? value  // Giữ nguyên text
      : (value === '' ? '' : (parseFloat(value) || ''))  // Parse số
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
      dm: "Chưa có kết quả — nhấn 'Chẩn đoán' để bắt đầu.",
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
      if (value === '' || value === null || value === undefined) {
        missing.push(field);
      }
    });
    return missing;
  };

  const handlePredict = async () => {
    // Check login
    const token = localStorage.getItem('token');
    if (!token) {
      alert('⚠️ Vui lòng đăng nhập để sử dụng chức năng chẩn đoán!');
      navigate('/login');
      return;
    }

    // Check missing fields
    const missing = checkMissingFields();
    
    if (missing.length > 0) {
      setMissingFields(missing);
      setShowWarning(true);
      
      // Scroll to warning
      setTimeout(() => {
        warningRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
      return;
    }

    // Nếu không có missing fields, tiếp tục predict
    await performPrediction(formData);
  };

  const handleContinueWithMissing = async () => {
    // Thay thế các giá trị missing bằng mean values
    const completedData = { ...formData };
    missingFields.forEach(field => {
      completedData[field] = MEAN_VALUES[field];
    });

    setFormData(completedData);
    setShowWarning(false);
    setMissingFields([]);

    // Tiếp tục predict
    await performPrediction(completedData);
  };

  const handleCancelPrediction = () => {
    setShowWarning(false);
    setMissingFields([]);
    setPendingData(null);
  };

  const performPrediction = async (dataToPredict) => {
    const token = localStorage.getItem('token');

    setLoading(true);
    setResults({
      dm: "⏳ Đang phân tích với Data Mining models...",
      ml: "⏳ Đang phân tích với Machine Learning models...",
      nlp: "⏳ Đang phân tích triệu chứng với NLP models...",
      final: "⏳ Đang tổng hợp kết luận...",
    });

    try {
      // Tạo input data (loại bỏ Symptoms cho ML API)
      const mlData = { ...dataToPredict };
      delete mlData.Symptoms;

      // Gọi ML prediction
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
      
      // Gọi NLP prediction nếu có mô tả triệu chứng
      let nlpResult = null;
      if (dataToPredict.Symptoms && dataToPredict.Symptoms.trim()) {
        try {
          const symptomsText = dataToPredict.Symptoms.trim();
          const requestBody = { symptoms: symptomsText };
          
          const nlpResponse = await fetch('http://localhost:8000/api/v1/ai/predict/symptoms', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(requestBody)
          });

          if (nlpResponse.ok) {
            nlpResult = await nlpResponse.json();
          }
        } catch (nlpError) {
          console.error('❌ NLP Error:', nlpError);
        }
      }
      
      // Format kết quả DM
      const dmModels = mlResult.individual_predictions.filter(p => 
        ['Naive Bayes','Knn'].includes(p.model)
      );
      
      const dmResults = dmModels.map(m => 
        `${m.model}: ${m.result} (${(m.confidence * 100).toFixed(0)}%)`
      ).join('\n');

      // Format kết quả ML
      const mlModels = mlResult.individual_predictions.filter(p => 
        ['Random Forest', 'Gradient Boosting', 'Svm', 'Logistic Regression'].includes(p.model)
      );

      const mlResults = mlModels.map(m => 
        `${m.model}: ${m.result} (${(m.confidence * 100).toFixed(0)}%)`
      ).join('\n');

      // Format kết quả NLP (nếu có)
      let nlpText = "Không có mô tả triệu chứng";
      if (nlpResult && nlpResult.success) {
        const nlpModels = nlpResult.individual_predictions || [];
        nlpText = nlpModels.map(m =>
          `${m.model}: ${m.result} (${(m.confidence * 100).toFixed(0)}%)`
        ).join('\n');
        
        if (nlpResult.symptom_count > 0) {
          nlpText += `\n\nTriệu chứng phát hiện: ${nlpResult.symptom_count}`;
          nlpText += `\nMức độ nghiêm trọng: ${(nlpResult.severity_score * 100).toFixed(0)}%`;
        }
      }

      // Ensemble Result
      let ensembleConf = mlResult.ensemble_confidence;
      let ensemblePred = mlResult.ensemble_prediction;
      
      if (nlpResult && nlpResult.success) {
        ensembleConf = (mlResult.ensemble_confidence + nlpResult.ensemble_confidence) / 2;
        const totalVotes = mlResult.ensemble_prediction + nlpResult.ensemble_prediction;
        ensemblePred = totalVotes >= 1 ? 1 : 0;
      }

      const riskLevel = 
        ensembleConf < 0.3 ? "Thấp" : 
        ensembleConf < 0.55 ? "Trung bình" : 
        "Cao";

      const ensembleResult = `
Kết quả tổng hợp từ ${mlResult.models_count} models ML${nlpResult && nlpResult.success ? ' + NLP' : ''}:
- Dự đoán: ${ensemblePred === 1 ? 'Có nguy cơ' : 'Không có nguy cơ'}
- Độ tin cậy ML: ${(mlResult.ensemble_confidence * 100).toFixed(1)}%${
  nlpResult && nlpResult.success ? `\n• Độ tin cậy NLP: ${(nlpResult.ensemble_confidence * 100).toFixed(1)}%` : ''
}
- Độ tin cậy tổng: ${(ensembleConf * 100).toFixed(1)}%
- Mức độ nguy cơ: ${riskLevel}
      `.trim();

      // Final conclusion
      let finalConclusion = '';
      
      if (riskLevel === "Cao") {
        finalConclusion = `🔴 CẢNH BÁO: Nguy cơ cao mắc bệnh tiểu đường!\n\n`;
        finalConclusion += `Các chỉ số đáng lo ngại:\n`;
        if (dataToPredict.Glucose > 140) finalConclusion += `• Glucose: ${dataToPredict.Glucose} (cao)\n`;
        if (dataToPredict.BMI > 30) finalConclusion += `• BMI: ${dataToPredict.BMI} (thừa cân)\n`;
        if (dataToPredict.Age > 45) finalConclusion += `• Tuổi: ${dataToPredict.Age}\n`;
        if (nlpResult && nlpResult.success && nlpResult.symptom_count > 0) {
          finalConclusion += `• Triệu chứng: ${nlpResult.symptom_count} triệu chứng phát hiện\n`;
        }
        finalConclusion += `\n🏥 Khuyến nghị: Nên đi khám bác sĩ ngay để được tư vấn và điều trị kịp thời.`;
      } else if (riskLevel === "Trung bình") {
        finalConclusion = `🟡 Nguy cơ ở mức trung bình\n\n`;
        finalConclusion += `Các chỉ số cần chú ý:\n`;
        if (dataToPredict.Glucose > 140) finalConclusion += `• Glucose: ${dataToPredict.Glucose} (cao)\n`;
        else if (dataToPredict.Glucose >= 100) finalConclusion += `• Glucose: ${dataToPredict.Glucose} (cao nhẹ)\n`;
        if (dataToPredict.BMI >= 25) finalConclusion += `• BMI: ${dataToPredict.BMI} (thừa cân)\n`;
        finalConclusion += `\n👀 Nên theo dõi sức khỏe và duy trì lối sống lành mạnh.`;
        finalConclusion += `\n📊 Kiểm tra định kỳ 6 tháng/lần.`;
      } else {
        finalConclusion = `🟢 Kết quả tốt - Các chỉ số trong giới hạn bình thường\n\n`;
        finalConclusion += `Tiếp tục duy trì:\n`;
        finalConclusion += `• Chế độ ăn uống cân bằng\n`;
        finalConclusion += `• Vận động thường xuyên (ít nhất 30 phút/ngày)\n`;
        finalConclusion += `• Kiểm tra sức khỏe định kỳ hàng năm`;
      }

      setResults({
        dm: dmResults || "Không có dữ liệu từ Data Mining models",
        ml: mlResults || "Không có dữ liệu từ ML models", 
        nlp: nlpText,
        final: finalConclusion,
      });

    } catch (error) {
      console.error('Prediction error:', error);
      setResults({
        dm: `❌ Lỗi: ${error.message}`,
        ml: `❌ Lỗi: ${error.message}`,
        nlp: `❌ Lỗi: ${error.message}`,
        final: `❌ Không thể thực hiện chẩn đoán. Vui lòng thử lại sau.`,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      {/* Navigation Header */}
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
        {/* LEFT FORM */}
        <section className="card">
          {/* Warning Modal */}
          {showWarning && (
            <div ref={warningRef} className="warning-container" style={{
              backgroundColor: '#fef3c7',
              border: '2px solid #f59e0b',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '16px',
              animation: 'slideIn 0.3s ease-out'
            }}>
              <div style={{ marginBottom: '12px' }}>
                <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#92400e', margin: '0 0 8px 0' }}>
                  ⚠️ Bạn nhập không đầy đủ thông tin
                </h3>
                <p style={{ color: '#b45309', margin: '0 0 8px 0' }}>
                  Các chỉ số sau chưa được điền hoặc bị bỏ trống:
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
                    <li key={field} style={{ marginBottom: '4px' }}>
                      {field}
                    </li>
                  ))}
                </ul>
              </div>

              <p style={{ color: '#b45309', fontWeight: 'bold', margin: '0 0 8px 0' }}>
                Các chỉ số missing sẽ được thay bằng giá trị bình thường từ cơ sở dữ liệu:
              </p>

              <div style={{
                backgroundColor: 'white',
                padding: '8px',
                borderRadius: '4px',
                marginBottom: '12px',
                border: '1px solid #fcd34d',
                fontSize: '13px'
              }}>
                <table style={{ width: '100%', color: '#b45309' }}>
                  <tbody>
                    {missingFields.map(field => (
                      <tr key={field}>
                        <td style={{ paddingRight: '16px' }}>{field}:</td>
                        <td style={{ fontWeight: 'bold', fontFamily: 'monospace' }}>
                          {MEAN_VALUES[field].toFixed(4)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <p style={{ color: '#b45309', margin: '0 0 12px 0' }}>
                ⚠️ <strong>Lưu ý:</strong> Kết quả dự đoán có thể bị ảnh hưởng do sử dụng giá trị thay thế.
              </p>

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

        {/* RIGHT PANEL */}
        <aside className="panel">
          <div className="result-card">
            <div className="result-row">
              <div>
                <div>Data Mining (ID3 / NB / KNN)</div>
              </div>
              <div className="chip dm">DM</div>
            </div>
            <div className="placeholder">{results.dm}</div>
          </div>

          <div className="result-card">
            <div className="result-row">
              <div>
                <div>Machine Learning (RF / GB / SVM / LR)</div>
              </div>
              <div className="chip ml">ML</div>
            </div>
            <div className="placeholder">{results.ml}</div>
          </div>

          <div className="result-card">
            <div className="result-row">
              <div>
                <div>NLP (triệu chứng)</div>
              </div>
              <div className="chip nlp">NLP</div>
            </div>
            <div className="placeholder">{results.nlp}</div>
          </div>

          <div className="result-card">
            <div className="result-row">
              <div>
                <div>Kết luận hệ thống (Ensemble)</div>
              </div>
              <div className="chip final">Final</div>
            </div>
            <div className="placeholder">{results.final}</div>
          </div>
        </aside>
      </div>
    </div>
  );
}