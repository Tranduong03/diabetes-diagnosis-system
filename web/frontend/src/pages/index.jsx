import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./index.css";

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

export default function Home() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    HighBP: 0,
    HighChol: 0,
    Smoker: 0,
    HeartDiseaseorAttack: 0,
    PhysActivity: 1,
    GenHlth: 3,
    MentHlth: 0,
    PhysHlth: 0,
    DiffWalk: 0,
    Age: 9,
    Symptoms: "",
    weight: 70,    // kg
    height: 170    // cm
  });

  const [calculatedBMI, setCalculatedBMI] = useState(24.2);

  const [results, setResults] = useState({
    ml: "Chưa có kết quả — nhấn 'Chẩn đoán' để bắt đầu.",
    nlp: "Chưa có kết quả — nhấn 'Chẩn đoán' để bắt đầu.",
    final: "Chưa có kết luận."
  });

  const [loading, setLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Tính BMI tự động khi weight hoặc height thay đổi
  useEffect(() => {
    if (formData.height > 0 && formData.weight > 0) {
      const heightInMeters = formData.height / 100;
      const bmi = formData.weight / (heightInMeters * heightInMeters);
      setCalculatedBMI(bmi.toFixed(1));
    } else {
      setCalculatedBMI(0);
    }
  }, [formData.weight, formData.height]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsLoggedIn(!!token);
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'Symptoms' ? value : parseFloat(value) || 0
    });
  };

  const handleClear = () => {
    setFormData({
      HighBP: 1,
      HighChol: 1,
      Smoker: 1,
      HeartDiseaseorAttack: 1,
      PhysActivity: 1,
      GenHlth: 3,
      MentHlth: 25,
      PhysHlth: 25,
      DiffWalk: 0,
      Age: 9,
      Symptoms: "",
      weight: 70,
      height: 170
    });
    setResults({
      ml: "Chưa có kết quả — nhấn 'Chẩn đoán' để bắt đầu.",
      nlp: "Chưa có kết quả — nhấn 'Chẩn đoán' để bắt đầu.",
      final: "Chưa có kết luận."
    });
  };

  const handlePredict = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('⚠️ Vui lòng đăng nhập để sử dụng chức năng chẩn đoán!');
      navigate('/login');
      return;
    }

    // Tính BMI trước khi gửi
    let bmi = 28; // fallback
    if (formData.height > 0 && formData.weight > 0) {
      const heightInMeters = formData.height / 100;
      bmi = formData.weight / (heightInMeters * heightInMeters);
    }

    const dataToPredict = {
      ...formData,
      BMI: parseFloat(bmi.toFixed(1))
    };

    await performPrediction(dataToPredict);
  };

  const performPrediction = async (dataToPredict) => {
    const token = localStorage.getItem('token');
    setLoading(true);
    setResults({
      ml: "⏳ Đang phân tích với Machine Learning models...",
      nlp: "⏳ Đang phân tích triệu chứng với PhoBERT...",
      final: "⏳ Đang tổng hợp kết luận..."
    });

    try {
      const response = await fetch('http://localhost:8000/api/v1/ai/predict/ensemble', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(dataToPredict)
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.');
        }
        throw new Error('Không thể kết nối đến server');
      }

      const result = await response.json();

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
          console.error('NLP Error:', nlpError);
        }
      }

      const mlModels = result.individual_predictions.filter(p => p.model !== 'PhoBERT');
      const mlResults = mlModels.map(m =>
        `${m.model}: ${m.result} (${(m.confidence * 100).toFixed(0)}%)`
      ).join('\n');

      let nlpText = "Không có mô tả triệu chứng";
      const nlpModel = result.individual_predictions.find(p => p.model === 'PhoBERT');
      if (nlpModel) {
        nlpText = `PhoBERT Analysis:\n• Kết luận: ${nlpModel.result}\n• Độ tin cậy: ${(nlpModel.confidence * 100).toFixed(1)}%`;
      }

      const riskLevel = result.risk_level;
      const ensembleConf = result.ensemble_confidence;
      const ensemblePred = result.ensemble_prediction;

      const riskLevelMap = { low: 'Thấp', medium: 'Trung bình', high: 'Cao' };
      const riskLevelText = riskLevelMap[riskLevel] || 'Không xác định';

      const diagnosisMap = {
        0: 'KHÔNG CÓ TIỂU ĐƯỜNG',
        1: 'CÓ NGUY CƠ TIỂU ĐƯỜNG',
      };

      let finalConclusion = `
KẾT QUẢ TỔNG HỢP

Chẩn đoán: ${diagnosisMap[ensemblePred] || 'Không xác định'}
Độ tin cậy: ${(ensembleConf * 100).toFixed(1)}%
Mức độ nguy cơ: ${riskLevelText}

`;

      if (ensemblePred === 1 || riskLevel === 'high') {
        finalConclusion += `🔴 CẢNH BÁO: Nguy cơ cao!\n\n🏥 Khuyến nghị:\n• Đi khám bác sĩ NGAY để được tư vấn\n• Xét nghiệm glucose máu đầy đủ\n• Chuẩn bị hồ sơ y tế`;
      } else if (ensemblePred === 1 || riskLevel === 'medium') {
        finalConclusion += `🟡 Tiền tiểu đường / Nguy cơ trung bình\n\n👀 Khuyến nghị:\n• Theo dõi đường huyết định kỳ\n• Thay đổi lối sống: ăn uống, vận động\n• Kiểm tra 3-6 tháng/lần\n• Giảm cân nếu thừa cân`;
      } else {
        finalConclusion += `🟢 Kết quả tốt!\n\n✅ Khuyến nghị:\n• Tiếp tục duy trì lối sống lành mạnh\n• Chế độ ăn cân bằng, ít đường\n• Vận động 30 phút/ngày\n• Kiểm tra định kỳ hàng năm`;
      }

      setResults({
        ml: mlResults || "Không có dữ liệu từ ML models",
        nlp: nlpText,
        final: finalConclusion.trim()
      });

    } catch (error) {
      console.error('Prediction error:', error);
      setResults({
        ml: `❌ Lỗi: ${error.message}`,
        nlp: `❌ Lỗi: ${error.message}`,
        final: `❌ Không thể thực hiện chẩn đoán.`
      });
    } finally {
      setLoading(false);
    }
  };

  const getBMICategory = (bmi) => {
    if (bmi < 18.5) return { text: "Gầy", color: "#60a5fa" };
    if (bmi < 25) return { text: "Bình thường", color: "#34d399" };
    if (bmi < 30) return { text: "Thừa cân", color: "#fbbf24" };
    return { text: "Béo phì", color: "#ef4444" };
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

      <h1 className="main-title">Hệ thống Chẩn đoán Tiểu đường</h1>

      <div className="app">
        <section className="card">
          <div className="title">
            <div className="logo">DIA</div>
            <div>
              <h1>Đánh giá nguy cơ tiểu đường</h1>
              <p className="lead">Nhập thông tin sức khỏe để hệ thống phân tích nguy cơ</p>
            </div>
          </div>

          <div className="form-section">
            {/* Thông tin y tế */}
            <div className="section-group">
              <h3 className="section-title">Thông tin y tế</h3>
              <div className="grid-2">
                {['HighBP', 'HighChol', 'Smoker', 'HeartDiseaseorAttack', 'PhysActivity', 'DiffWalk'].map(key => (
                  <div className="field-compact" key={key}>
                    <label className="field-label-compact">
                      {FIELD_LABELS[key]}
                      <span className="field-hint">{FIELD_DESCRIPTIONS[key]}</span>
                    </label>
                    <select
                      name={key}
                      value={formData[key]}
                      onChange={handleChange}
                      disabled={loading}
                      className="select-input"
                    >
                      {key === 'PhysActivity' || key === 'DiffWalk' ? (
                        <>
                          <option value="0">Không</option>
                          <option value="1">Có</option>
                        </>
                      ) : (
                        <>
                          <option value="0">Không rõ</option>
                          <option value="1">Có</option>
                        </>
                      )}
                    </select>
                  </div>
                ))}
              </div>
            </div>

            {/* Chỉ số sức khỏe */}
            <div className="section-group">
              <h3 className="section-title">Chỉ số sức khỏe</h3>
              <div className="grid-2">
                {/* Cân nặng & Chiều cao */}
                <div className="field-compact full-width">
                  <label className="field-label-compact">
                    Cân nặng & Chiều cao
                    <span className="field-hint">Hệ thống sẽ tự động tính chỉ số BMI</span>
                  </label>
                  <div className="bmi-input-group">
                    <div className="bmi-input-wrapper">
                      <input
                        type="number"
                        name="weight"
                        value={formData.weight}
                        onChange={handleChange}
                        min="30"
                        max="200"
                        step="0.1"
                        placeholder="Cân nặng"
                        disabled={loading}
                        className="number-input-compact"
                      />
                      <span className="unit">kg</span>
                    </div>

                    <div className="bmi-input-wrapper">
                      <input
                        type="number"
                        name="height"
                        value={formData.height}
                        onChange={handleChange}
                        min="100"
                        max="250"
                        step="1"
                        placeholder="Chiều cao"
                        disabled={loading}
                        className="number-input-compact"
                      />
                      <span className="unit">cm</span>
                    </div>
                  </div>

                  {calculatedBMI > 0 && (
                    <div className="bmi-result">
                      <strong>Chỉ số BMI: {calculatedBMI}</strong>
                      <span
                        className="bmi-category"
                        style={{ color: getBMICategory(calculatedBMI).color }}
                      >
                        {' '}({getBMICategory(calculatedBMI).text})
                      </span>
                    </div>
                  )}
                </div>


                <div className="field-compact">
                  <label className="field-label-compact">
                    {FIELD_LABELS.PhysHlth}
                    <span className="field-hint">{FIELD_DESCRIPTIONS.PhysHlth}</span>
                  </label>
                  <select name="PhysHlth" value={formData.PhysHlth} onChange={handleChange} disabled={loading} className="select-input">
                    {PHYS_HLTH_OPTIONS.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
                <div className="field-compact">
                  <label className="field-label-compact">
                    {FIELD_LABELS.MentHlth}
                    <span className="field-hint">{FIELD_DESCRIPTIONS.MentHlth}</span>
                  </label>
                  <select name="MentHlth" value={formData.MentHlth} onChange={handleChange} disabled={loading} className="select-input">
                    {MEN_HLTH_OPTIONS.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>

                <div className="field-compact">
                  <label className="field-label-compact">
                    {FIELD_LABELS.GenHlth}
                    <span className="field-hint">{FIELD_DESCRIPTIONS.GenHlth}</span>
                  </label>
                  <select name="GenHlth" value={formData.GenHlth} onChange={handleChange} disabled={loading} className="select-input">
                    {HEALTH_OPTIONS.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>

                <div className="field-compact">
                  <label className="field-label-compact">
                    {FIELD_LABELS.Age}
                    <span className="field-hint">{FIELD_DESCRIPTIONS.Age}</span>
                  </label>
                  <select name="Age" value={formData.Age} onChange={handleChange} disabled={loading} className="select-input">
                    {AGE_GROUPS.map(group => (
                      <option key={group.value} value={group.value}>{group.label}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Triệu chứng */}
            <div className="section-group">
              <h3 className="section-title">Triệu chứng (tùy chọn)</h3>
              <textarea
                name="Symptoms"
                value={formData.Symptoms}
                onChange={handleChange}
                placeholder="Mô tả các triệu chứng: khát nước, đi tiểu nhiều, mệt mỏi, sụt cân..."
                disabled={loading}
                className="textarea-input"
              />
            </div>
          </div>

          <div className="actions">
            <button
              type="button"
              onClick={handlePredict}
              disabled={loading}
              className="btn-primary"
            >
              {loading ? '⏳ Đang phân tích...' : '🔍 Chẩn đoán ngay'}
            </button>
            <button
              type="button"
              className="btn-secondary"
              onClick={handleClear}
              disabled={loading}
            >
              🔄 Làm mới
            </button>
          </div>

          <small className="hint">
            💡 {isLoggedIn
              ? 'Điền đầy đủ thông tin để có kết quả chính xác nhất'
              : 'Vui lòng đăng nhập để sử dụng chức năng chẩn đoán'}
          </small>
        </section>

        <aside className="panel">
          <div className="result-card">
            <div className="result-row">
              <div>Machine Learning</div>
              <div className="chip ml">ML</div>
            </div>
            <div className="placeholder">{results.ml}</div>
          </div>

          <div className="result-card">
            <div className="result-row">
              <div>PhoBERT NLP</div>
              <div className="chip nlp">NLP</div>
            </div>
            <div className="placeholder">{results.nlp}</div>
          </div>

          <div className="result-card">
            <div className="result-row">
              <div>Kết luận</div>
              <div className="chip final">Ensemble</div>
            </div>
            <div className="placeholder">{results.final}</div>
          </div>
        </aside>
      </div>
    </div>
  );
}