# diabetes-diagnosis-system
Diabetes Diagnosis System — An AI-powered system for predicting diabetes risk using Data Mining, Machine Learning, and Natural Language Processing techniques.


# 🩺 HỆ THỐNG CHẨN ĐOÁN TIỂU ĐƯỜNG (DIABETES DIAGNOSIS SYSTEM)

**Diabetes Diagnosis System** là một ứng dụng trí tuệ nhân tạo (AI) được phát triển nhằm **dự đoán nguy cơ mắc bệnh tiểu đường** dựa trên **các chỉ số y tế của bệnh nhân** và **mô tả triệu chứng bằng ngôn ngữ tự nhiên**.  
Dự án kết hợp ba hướng nghiên cứu chính: **Khai phá dữ liệu (Data Mining)**, **Học máy (Machine Learning)** và **Xử lý ngôn ngữ tự nhiên (NLP)** để xây dựng một hệ thống chẩn đoán y tế thông minh.

---

## 🎯 MỤC TIÊU
- Phân tích và tiền xử lý dữ liệu y tế phục vụ cho bài toán dự đoán tiểu đường.  
- Áp dụng các **thuật toán Data Mining** kinh điển: ID3, Naive Bayes, KNN.  
- Cài đặt và so sánh **các mô hình Machine Learning** hiện đại: Logistic Regression, Random Forest, XGBoost, Neural Network.  
- Ứng dụng **Xử lý ngôn ngữ tự nhiên (NLP)** để phân tích mô tả triệu chứng trong hồ sơ bệnh án.  
- Tích hợp kết quả từ nhiều mô hình để đưa ra **chẩn đoán cuối cùng** với độ tin cậy cao.

---

## ⚙️ CHỨC NĂNG CHÍNH
- Nhập dữ liệu bệnh nhân gồm các chỉ số: `Glucose`, `BMI`, `Age`, `Insulin`, v.v.  
- Nhập thêm phần mô tả triệu chứng (nếu có) dưới dạng văn bản.  
- Hệ thống chạy song song 3 mô-đun:
  - **Data Mining**: Dự đoán bằng các thuật toán truyền thống.  
  - **Machine Learning**: Dự đoán bằng các mô hình hiện đại.  
  - **NLP**: Phân tích văn bản mô tả triệu chứng để hỗ trợ chẩn đoán.  
- Hệ thống hiển thị:
  - Kết quả dự đoán của từng mô hình.  
  - Quyết định tổng hợp cuối cùng (Có/Không mắc tiểu đường).  
  - Giải thích lý do dự đoán (theo các thuộc tính quan trọng).  
- Giao diện web thân thiện giúp người dùng nhập liệu và xem kết quả trực quan.

---

## 🧠 CÔNG NGHỆ SỬ DỤNG
- **Ngôn ngữ:** Python  
- **Thư viện:**
  - Xử lý dữ liệu: `pandas`, `numpy`, `matplotlib`, `seaborn`
  - Machine Learning: `scikit-learn`, `xgboost`
  - NLP: `nltk`, `scikit-learn TF-IDF`, `transformers` (tùy chọn)
  - Web: `Flask` hoặc `Streamlit`
- **Dữ liệu sử dụng:**
  - [Pima Indians Diabetes Dataset](https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database)
  - [Early Stage Diabetes Risk Prediction Dataset](https://www.kaggle.com/datasets/ishandutta/early-stage-diabetes-risk-prediction-dataset)

---

## 📊 KẾT QUẢ MONG ĐỢI
- Hệ thống web có khả năng dự đoán nguy cơ mắc tiểu đường với độ chính xác cao.  
- So sánh được hiệu suất giữa các thuật toán Data Mining và ML.  
- Minh họa ứng dụng thực tế của trí tuệ nhân tạo trong lĩnh vực **chẩn đoán y tế**.

---

## 📁 CẤU TRÚC THƯ MỤC DỰ ÁN

diabetes-diagnosis-system/
│
├── datasets/ # Dữ liệu gốc và dữ liệu sau tiền xử lý
├── notebooks/ # Jupyter notebooks dùng để phân tích và huấn luyện
├── models/ # Các mô hình đã huấn luyện (pickle/joblib)
├── web/ # Mã nguồn ứng dụng web (Flask/Streamlit)
├── docs/ # Tài liệu báo cáo, slide, biểu đồ
├── requirements.txt # Danh sách thư viện Python cần cài
└── README.md # Giới thiệu dự án


---

## 👨‍💻 TÁC GIẢ
- **Họ và tên:** Trần Nguyễn Phi Dương
-             ** Trần Quân Bảo
-             ** Huỳnh Thiên Huy
-             ** Nguyễn Viết Ái Nhi  
- **Trường:** Đại học Giao thông vận tải phân hiệu tại Thành phố Hồ Chí Minh 
- **Môn học:** Khai phá dữ liệu (Data Mining), Machine Learning, NLP  
- **Năm học:** 2025  

---

## 🧩 GHI CHÚ
Dự án hướng đến việc xây dựng một hệ thống trí tuệ nhân tạo có thể mở rộng cho nhiều loại bệnh khác trong tương lai, thông qua việc kết hợp **dữ liệu có cấu trúc** (các chỉ số y tế) và **dữ liệu phi cấu trúc** (văn bản triệu chứng).

