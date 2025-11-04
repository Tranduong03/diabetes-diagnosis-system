import { useState } from "react";
import "./index.css"; 

export default function Home() {
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
    dm: "Chưa có kết quả — chưa gọi backend.",
    ml: "Chưa có kết quả — chưa gọi backend.",
    nlp: "Chưa có kết quả — chưa gọi backend.",
    final: "Chưa có kết luận.",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
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
      dm: "Chưa có kết quả — chưa gọi backend.",
      ml: "Chưa có kết quả — chưa gọi backend.",
      nlp: "Chưa có kết quả — chưa gọi backend.",
      final: "Chưa có kết luận.",
    });
  };

  const handlePredict = async () => {
    setResults({
      dm: "Đang chờ backend...",
      ml: "Đang chờ backend...",
      nlp: "Đang chờ backend...",
      final: "Đang chờ backend...",
    });

    await new Promise((r) => setTimeout(r, 700)); // mô phỏng delay

    setResults({
      dm: `Kết quả: Có nguy cơ (approx) — Decision Tree -> Glucose cao & BMI > 25`,
      ml: `Kết quả: 82% nguy cơ — RandomForest confidence: 0.82`,
      nlp: `Triệu chứng phù hợp (khát nước, sụt cân) — TF-IDF + LR score: 0.78`,
      final: `Hệ thống: Có nguy cơ cao mắc tiểu đường (Glucose>${formData.Glucose}, BMI=${formData.BMI})`,
    });
  };

  return (
    <div className="page-container">
      <h1 className="main-title">Diabetes Diagnosis System</h1>

      <div className="app">
        {/* LEFT FORM */}
        <section className="card">
          <div className="title">
            <div className="logo">DIA</div>
            <div>
              <h1>Diabetes Support — Frontend (React Demo)</h1>
              <p className="lead">
                Nhập các chỉ số y tế và mô tả triệu chứng. (Frontend only)
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
                  />
                </div>
              ))}

            <div className="field full">
              <label>Mô tả triệu chứng / Hồ sơ bệnh án</label>
              <textarea
                name="Symptoms"
                value={formData.Symptoms}
                onChange={handleChange}
                placeholder="Ví dụ: khát nước, đi tiểu nhiều..."
              />
            </div>
          </div>

          <div className="actions">
            <button type="button" onClick={handlePredict}>
              Gửi dữ liệu →
            </button>
            <button type="button" className="secondary" onClick={handleClear}>
              Xoá
            </button>
          </div>
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
                <div>Machine Learning</div>
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
