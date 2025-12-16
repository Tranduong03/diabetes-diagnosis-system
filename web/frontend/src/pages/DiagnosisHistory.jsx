import { useState } from "react";
import "./DiagnosisHistory.css";

const historyData = [
  {
    id: 1,
    date: "12/12/2025",
    age: 34,
    glucose: 195,
    bmi: 39,
    bp: "85 mmHg",
    insulin: 140,
    model: "Ensemble (KNN + NB + LR)",
    result: "Nguy cơ cao",
    advice: "Nên đi khám bác sĩ chuyên khoa sớm để được tư vấn và điều trị kịp thời."
  },
  {
    id: 2,
    date: "05/12/2025",
    age: 34,
    glucose: 150,
    bmi: 31,
    bp: "80 mmHg",
    insulin: 120,
    model: "KNN + Naive Bayes",
    result: "Cần theo dõi",
    advice: "Điều chỉnh chế độ ăn uống và tăng cường vận động."
  },
  {
    id: 3,
    date: "20/11/2025",
    age: 33,
    glucose: 110,
    bmi: 26,
    bp: "75 mmHg",
    insulin: 95,
    model: "Logistic Regression",
    result: "Bình thường",
    advice: "Duy trì lối sống lành mạnh và kiểm tra định kỳ."
  }
];

export default function DiagnosisHistory() {
  const [selected, setSelected] = useState(null);

  return (
    <div className="page">
      <h1 className="title">Lịch sử chẩn đoán bệnh tiểu đường</h1>

      <div className="layout">
        {/* SIDEBAR */}
        <aside className="sidebar">
          <h3>Bộ lọc</h3>
          <select className="select">
            <option>Tất cả</option>
            <option>Nguy cơ cao</option>
            <option>Cần theo dõi</option>
            <option>Bình thường</option>
          </select>
        </aside>

        {/* CONTENT */}
        <main className="content">
          <div className="row header">
            <span>Ngày</span>
            <span>Chỉ số</span>
            <span>Thuật toán</span>
            <span>Kết luận</span>
            <span></span>
          </div>

          {historyData.map((item) => (
            <div key={item.id} className="row">
              <span>{item.date}</span>
              <span>Glucose {item.glucose} | BMI {item.bmi}</span>
              <span>{item.model}</span>
              <span className={`badge ${badgeColor(item.result)}`}>
                {item.result}
              </span>
              <button className="button" onClick={() => setSelected(item)}>
                Xem
              </button>
            </div>
          ))}
        </main>
      </div>

      {/* MODAL */}
      {selected && (
        <div className="modal">
          <div className="modal-content">
            <h2 className="modal-title">Chi tiết chẩn đoán</h2>

            <div className="grid">
              <div><b>Ngày:</b> {selected.date}</div>
              <div><b>Tuổi:</b> {selected.age}</div>
              <div><b>Glucose:</b> {selected.glucose}</div>
              <div><b>BMI:</b> {selected.bmi}</div>
              <div><b>Huyết áp:</b> {selected.bp}</div>
              <div><b>Insulin:</b> {selected.insulin}</div>
              <div><b>Thuật toán:</b> {selected.model}</div>
              <div><b>Kết luận:</b> {selected.result}</div>
            </div>

            <p className="advice">
              <b>Khuyến nghị:</b> {selected.advice}
            </p>

            <button className="button danger" onClick={() => setSelected(null)}>
              Đóng
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

const badgeColor = (result) => {
  if (result === "Nguy cơ cao") return "high";
  if (result === "Cần theo dõi") return "warning";
  return "normal";
};
