import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./index.css"; 

export default function Home() {
  const navigate = useNavigate();
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

  // Check login status
  useState(() => {
    const token = localStorage.getItem('token');
    setIsLoggedIn(!!token);
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: parseFloat(value) || value });
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
  };

  const handlePredict = async () => {
    // Check if logged in
    const token = localStorage.getItem('token');
    if (!token) {
      alert('⚠️ Vui lòng đăng nhập để sử dụng chức năng chẩn đoán!');
      navigate('/login');
      return;
    }

    setLoading(true);
    setResults({
      dm: "⏳ Đang phân tích với Data Mining models...",
      ml: "⏳ Đang phân tích với Machine Learning models...",
      nlp: "⏳ Đang phân tích triệu chứng với NLP models...",
      final: "⏳ Đang tổng hợp kết luận...",
    });

    try {
      // Tạo input data (loại bỏ Symptoms cho ML API)
      const mlData = { ...formData };
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
      if (formData.Symptoms && formData.Symptoms.trim()) {
        try {
          const nlpResponse = await fetch('http://localhost:8000/api/v1/ai/predict/symptoms', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ symptoms: formData.Symptoms })
          });

          if (nlpResponse.ok) {
            nlpResult = await nlpResponse.json();
          } else {
            console.error('NLP response error:', nlpResponse.status);
          }
        } catch (nlpError) {
          console.error('NLP fetch error:', nlpError);
        }
      }
      
      // Format kết quả DM
      const dmModels = mlResult.individual_predictions.filter(p => 
        ['ID3', 'Naive Bayes', 'Knn'].includes(p.model)
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

      // Ensemble Result - kết hợp cả ML và NLP
      let ensembleConf = mlResult.ensemble_confidence;
      let ensemblePred = mlResult.ensemble_prediction;
      
      if (nlpResult && nlpResult.success) {
        // Trung bình confidence của ML và NLP
        ensembleConf = (mlResult.ensemble_confidence + nlpResult.ensemble_confidence) / 2;
        // Voting ensemble
        const totalVotes = mlResult.ensemble_prediction + nlpResult.ensemble_prediction;
        ensemblePred = totalVotes >= 1 ? 1 : 0;
      }

      const riskLevel = 
        ensembleConf < 0.3 ? "Thấp" : 
        ensembleConf < 0.6 ? "Trung bình" : 
        "Cao";

      const ensembleResult = `
Kết quả tổng hợp từ ${mlResult.models_count} models ML${nlpResult && nlpResult.success ? ' + NLP' : ''}:
• Dự đoán: ${ensemblePred === 1 ? 'Có nguy cơ' : 'Không có nguy cơ'}
• Độ tin cậy ML: ${(mlResult.ensemble_confidence * 100).toFixed(1)}%${
  nlpResult && nlpResult.success ? `\n• Độ tin cậy NLP: ${(nlpResult.ensemble_confidence * 100).toFixed(1)}%` : ''
}
• Độ tin cậy tổng: ${(ensembleConf * 100).toFixed(1)}%
• Mức độ nguy cơ: ${riskLevel}
      `.trim();

      // Final conclusion
      let finalConclusion = '';
      
      if (riskLevel === "Cao") {
        finalConclusion = `🔴 CẢNH BÁO: Nguy cơ cao mắc bệnh tiểu đường!\n\n`;
        finalConclusion += `Các chỉ số đáng lo ngại:\n`;
        if (formData.Glucose > 140) finalConclusion += `• Glucose: ${formData.Glucose} (cao)\n`;
        if (formData.BMI > 30) finalConclusion += `• BMI: ${formData.BMI} (thừa cân)\n`;
        if (formData.Age > 45) finalConclusion += `• Tuổi: ${formData.Age}\n`;
        if (nlpResult && nlpResult.success && nlpResult.symptom_count > 0) {
          finalConclusion += `• Triệu chứng: ${nlpResult.symptom_count} triệu chứng phát hiện\n`;
        }
        finalConclusion += `\n🏥 Khuyến nghị: Nên đi khám bác sĩ ngay để được tư vấn và điều trị kịp thời.`;
      } else if (riskLevel === "Trung bình") {
        finalConclusion = `🟡 Nguy cơ ở mức trung bình\n\n`;
        finalConclusion += `Các chỉ số cần chú ý:\n`;
        if (formData.Glucose >= 100) finalConclusion += `• Glucose: ${formData.Glucose} (nhẹ cao)\n`;
        if (formData.BMI >= 25) finalConclusion += `• BMI: ${formData.BMI} (thừa cân)\n`;
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
            {Object.keys(formData)
              .filter((key) => key !== "Symptoms")
              .map((key) => (
                <div key={key} className="field">
                  <label>{key}</label>
                  <input
                    type="number"
                    name={key}
                    value={formData[key]}
                    onChange={handleChange}
                    step={key === 'Pregnancies' || key === 'Age' ? '1' : '0.1'}
                    disabled={loading}
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