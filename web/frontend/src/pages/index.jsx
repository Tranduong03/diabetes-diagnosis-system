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
    weight: 70,
    height: 170
  });

  const [calculatedBMI, setCalculatedBMI] = useState(24.2);
  const [showHeightWeightWarning, setShowHeightWeightWarning] = useState(false);
  const [heightWeightWarningData, setHeightWeightWarningData] = useState({
    field: '',
    value: null,
    fieldKey: ''
  });

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

  // Kiểm tra chiều cao và cân nặng khi người dùng blur khỏi trường nhập
  const checkHeightWeight = (name, value) => {
    const numValue = parseFloat(value);
    
    if ((name === 'height' && (isNaN(numValue) || numValue === 0 || value === '')) ||
        (name === 'weight' && (isNaN(numValue) || numValue === 0 || value === ''))) {
      
      const fieldName = name === 'height' ? 'Chiều cao' : 'Cân nặng';
      const defaultValue = name === 'height' ? 170 : 70;
      const fieldKey = name;
      
      setHeightWeightWarningData({
        field: fieldName,
        value: defaultValue,
        fieldKey: fieldKey
      });
      setShowHeightWeightWarning(true);
      return false;
    }
    
    return true;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    // Xử lý đặc biệt cho chiều cao và cân nặng
    if (name === 'height' || name === 'weight') {
      const newValue = value === '' ? '' : value;
      setFormData({
        ...formData,
        [name]: newValue
      });
    } else {
      setFormData({
        ...formData,
        [name]: name === 'Symptoms' ? value : parseFloat(value) || 0
      });
    }
  };

  const handleBlur = (e) => {
    const { name, value } = e.target;
    
    if (name === 'height' || name === 'weight') {
      checkHeightWeight(name, value);
    }
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
    setShowHeightWeightWarning(false);
  };

  // Hàm xử lý khi người dùng chọn dùng giá trị mặc định
  const handleUseDefaultValue = () => {
    const { fieldKey, value } = heightWeightWarningData;
    
    setFormData(prev => ({
      ...prev,
      [fieldKey]: value
    }));
    
    setShowHeightWeightWarning(false);
  };

  // Hàm xử lý khi người dùng chọn nhập lại
  const handleInputAgain = () => {
    setShowHeightWeightWarning(false);
    // Focus vào trường nhập liệu tương ứng sau khi modal đóng
    setTimeout(() => {
      const inputId = heightWeightWarningData.fieldKey === 'height' ? 'height-input' : 'weight-input';
      const inputElement = document.getElementById(inputId);
      if (inputElement) {
        inputElement.focus();
        inputElement.select();
      }
    }, 100);
  };

  const handlePredict = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('⚠️ Vui lòng đăng nhập để sử dụng chức năng chẩn đoán!');
      navigate('/login');
      return;
    }

    // Kiểm tra chiều cao
    if (!checkHeightWeight('height', formData.height)) {
      return;
    }

    // Kiểm tra cân nặng
    if (!checkHeightWeight('weight', formData.weight)) {
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
      weight: parseFloat(formData.weight),
      height: parseFloat(formData.height),
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

// Hàm xác định icon cho ML
const getMLIcon = (prediction, confidence) => {
  if (prediction === 0) return "🟢";
  if (prediction === 1 && confidence >= 0.75) return "🔴";
  if (prediction === 1 && confidence < 0.75) return "🟡";
  return "⚪"; // fallback
};

// Hàm xác định icon cho NLP
const getNLPIcon = (outcome, stage) => {
  if (outcome === 0) return "🟢"; // Không bệnh
  // outcome === 1 => có bệnh
  switch(stage) {
    case 1:
      return "🟠"; // stage nhẹ → vàng cam
    case 2:
    case 3:
      return "🔴"; // stage nặng → đỏ
    default:
      return "🟡"; // stage không xác định → vàng
  }
};


const mlModels = result.individual_predictions.filter(p => p.model !== 'PhoBERT');
    
    // Chỉ hiển thị kết quả và độ tin cậy, không hiển thị tên model
    let mlResults = "Không có dữ liệu từ thông tin y tế";
    
    if (mlModels.length > 0) {
      const ml = mlModels[0];
      const mlText = ml.result === "Không có tiểu đường" ? "Không có tiểu đường" : "Có nguy cơ tiểu đường";
      const mlIcon = getMLIcon(ml.prediction, ml.confidence);
      mlResults = `${mlText} ${mlIcon}\nĐộ tin cậy: ${(ml.confidence * 100).toFixed(1)}%`;
    }

    let nlpText = "Không có mô tả triệu chứng";
    
    const nlpModel = result.individual_predictions.find(p => p.model === 'PhoBERT');
    const nlpIcon = getNLPIcon(nlpModel.outcome, nlpModel.stage);
    
    if (nlpModel) {
      nlpText = `Kết luận: ${nlpModel.result} ${nlpIcon}\nĐộ tin cậy: ${(nlpModel.confidence * 100).toFixed(1)}%`;
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

      let finalConclusion = `KẾT QUẢ TỔNG HỢP

Chẩn đoán: ${diagnosisMap[ensemblePred] || 'Không xác định'}
Độ tin cậy: ${(ensembleConf * 100).toFixed(1)}%
Mức độ nguy cơ: ${riskLevelText}
`;

        const recommendationsText = result.recommendations
          ?.map(r => `• ${r}`)
          .join('\n') || 'Không có khuyến nghị';

        setResults({
          ml: mlResults,
          nlp: nlpText,
          final: `${finalConclusion}\n🏥 KHUYẾN NGHỊ:\n${recommendationsText}`
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
      {/* Modal cảnh báo */}
      {showHeightWeightWarning && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Cảnh báo nhập liệu</h3>
            </div>
            <div className="modal-body">
              <p>
                <strong>{heightWeightWarningData.field}</strong> đang có giá trị không hợp lệ (0 hoặc trống).
                Bạn có muốn sử dụng giá trị mặc định ({heightWeightWarningData.value} 
                {heightWeightWarningData.field === 'Chiều cao' ? 'cm' : 'kg'}) không?
              </p>
              <div className="modal-actions">
                <button 
                  onClick={handleUseDefaultValue}
                  className="modal-btn modal-btn-primary"
                >
                  Dùng giá trị mặc định
                </button>
                <button 
                  onClick={handleInputAgain}
                  className="modal-btn modal-btn-secondary"
                >
                  Nhập lại
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

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
                    {(formData.height === '' || formData.height === 0 || formData.height === null) && (
                      <span className="warning-text">⚠️ Chiều cao không hợp lệ</span>
                    )}
                    {(formData.weight === '' || formData.weight === 0 || formData.weight === null) && (
                      <span className="warning-text">⚠️ Cân nặng không hợp lệ</span>
                    )}
                  </label>
                  <div className="bmi-input-group">
                    <div className="bmi-input-wrapper">
                      <input
                        id="weight-input"
                        type="number"
                        name="weight"
                        value={formData.weight}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        min="30"
                        max="200"
                        step="0.1"
                        placeholder="Cân nặng"
                        disabled={loading}
                        className={`number-input-compact ${
                          (formData.weight === '' || formData.weight === 0 || formData.weight === null) ? 'input-warning' : ''
                        }`}
                      />
                      <span className="unit">kg</span>
                    </div>

                    <div className="bmi-input-wrapper">
                      <input
                        id="height-input"
                        type="number"
                        name="height"
                        value={formData.height}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        min="100"
                        max="250"
                        step="1"
                        placeholder="Chiều cao"
                        disabled={loading}
                        className={`number-input-compact ${
                          (formData.height === '' || formData.height === 0 || formData.height === null) ? 'input-warning' : ''
                        }`}
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
              <h3 className="section-title">Mô tả tình trạng sức khỏe (tùy chọn)</h3>
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
              <div>Dự đoán từ thông tin y tế & chỉ số sức khỏe</div>
            </div>
            <div className="placeholder">{results.ml}</div>
          </div>

          <div className="result-card">
            <div className="result-row">
              <div>Dự đoán từ mô tả tình trạng sức khỏe</div>
            </div>
            <div className="placeholder">{results.nlp}</div>
          </div>

          <div className="result-card">
            <div className="result-row">
              <div>Kết luận</div>
            </div>
            <div className="placeholder">{results.final}</div>
          </div>
        </aside>
      </div>
    </div>
  );
}
