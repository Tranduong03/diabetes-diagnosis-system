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
  });

  const [results, setResults] = useState({
    dm: "Chưa có kết quả — nhấn 'Chẩn đoán' để bắt đầu.",
    ml: "Chưa có kết quả — nhấn 'Chẩn đoán' để bắt đầu.",
    ensemble: "Chưa có kết quả — nhấn 'Chẩn đoán' để bắt đầu.",
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
    setFormData({ ...formData, [name]: parseFloat(value) || 0 });
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
    });
    setResults({
      dm: "Chưa có kết quả — nhấn 'Chẩn đoán' để bắt đầu.",
      ml: "Chưa có kết quả — nhấn 'Chẩn đoán' để bắt đầu.",
      ensemble: "Chưa có kết quả — nhấn 'Chẩn đoán' để bắt đầu.",
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
      ensemble: "⏳ Đang tính toán kết quả tổng hợp...",
      final: "⏳ Đang tổng hợp kết luận...",
    });

    try {
      // Gọi API prediction
      const response = await fetch('http://localhost:8000/api/v1/ai/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.');
        }
        throw new Error('Không thể kết nối đến server');
      }

      const data = await response.json();
      
      // Format kết quả
      const dmModels = data.individual_predictions.filter(p => 
        ['Decision Tree', 'Naive Bayes', 'knn'].includes(p.model)
      );
      
      const mlModels = data.individual_predictions.filter(p => 
        ['Random Forest', 'Gradient Boosting', 'Svm', 'Logistic Regression'].includes(p.model)
      );

      // DM Result
      const dmResults = dmModels.map(m => 
        `${m.model}: ${m.result} (${(m.confidence * 100).toFixed(0)}%)`
      ).join('\n');

      // ML Result  
      const mlResults = mlModels.map(m => 
        `${m.model}: ${m.result} (${(m.confidence * 100).toFixed(0)}%)`
      ).join('\n');

      // Ensemble Result
      const ensembleResult = `
Kết quả tổng hợp từ ${data.models_count} models:
• Dự đoán: ${data.result}
• Độ tin cậy: ${(data.ensemble_confidence * 100).toFixed(1)}%
• Mức độ nguy cơ: ${data.risk_level}
      `.trim();

      // Final conclusion
      let finalConclusion = '';
      if (data.risk_level === "Cao") {
        finalConclusion = `🔴 CẢNH BÁO: Nguy cơ cao mắc bệnh tiểu đường!\n\n`;
        finalConclusion += `Các chỉ số đáng lo ngại:\n`;
        if (formData.Glucose > 140) finalConclusion += `• Glucose: ${formData.Glucose} (cao)\n`;
        if (formData.BMI > 30) finalConclusion += `• BMI: ${formData.BMI} (thừa cân)\n`;
        if (formData.Age > 45) finalConclusion += `• Tuổi: ${formData.Age}\n`;
        finalConclusion += `\n🏥 Khuyến nghị: Nên đi khám bác sĩ ngay để được tư vấn và điều trị kịp thời.`;
      } else if (data.risk_level === "Trung bình") {
        finalConclusion = `🟡 Nguy cơ ở mức trung bình\n\n`;
        finalConclusion += `Nên theo dõi sức khỏe và duy trì lối sống lành mạnh.\n`;
        finalConclusion += `📊 Kiểm tra định kỳ 6 tháng/lần.`;
      } else {
        finalConclusion = `🟢 Kết quả tốt - Các chỉ số trong giới hạn bình thường\n\n`;
        finalConclusion += `Tiếp tục duy trì:\n`;
        finalConclusion += `• Chế độ ăn uống cân bằng\n`;
        finalConclusion += `• Vận động thường xuyên\n`;
        finalConclusion += `• Kiểm tra sức khỏe định kỳ hàng năm`;
      }

      setResults({
        dm: dmResults || "Không có dữ liệu từ Data Mining models",
        ml: mlResults || "Không có dữ liệu từ ML models", 
        ensemble: ensembleResult,
        final: finalConclusion,
      });

    } catch (error) {
      console.error('Prediction error:', error);
      setResults({
        dm: `❌ Lỗi: ${error.message}`,
        ml: `❌ Lỗi: ${error.message}`,
        ensemble: `❌ Lỗi: ${error.message}`,
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
                Nhập các chỉ số y tế để hệ thống phân tích và đưa ra kết luận
              </p>
            </div>
          </div>

          <div className="grid">
            {Object.keys(formData).map((key) => (
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

          <div className="actions">
            <button 
              type="button" 
              onClick={handlePredict}
              disabled={loading}
            >
              {loading ? 'Đang phân tích...' : 'Chẩn đoán →'}
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
              ? 'Nhập thông tin và nhấn "Chẩn đoán" để bắt đầu phân tích' 
              : 'Vui lòng đăng nhập để sử dụng chức năng chẩn đoán'}
          </small>
        </section>

        {/* RIGHT PANEL */}
        <aside className="panel">
          <div className="result-card">
            <div className="result-row">
              <div>
                <div>Data Mining (Decision Tree / Naive Bayes / KNN)</div>
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
                <div>Ensemble (Tổng hợp từ tất cả models)</div>
              </div>
              <div className="chip nlp">Ensemble</div>
            </div>
            <div className="placeholder">{results.ensemble}</div>
          </div>

          <div className="result-card">
            <div className="result-row">
              <div>
                <div>Kết luận hệ thống</div>
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