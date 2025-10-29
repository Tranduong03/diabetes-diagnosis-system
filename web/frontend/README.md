frontend/
│
├── index.html                # Trang chính (Form nhập liệu + kết quả)
├── dashboard.html            # Dashboard (tổng quan)
├── tracking.html             # Trang Theo dõi kết quả (biểu đồ, lịch sử)
├── explain.html              # Trang Giải thích & tư vấn
├── about.html                # Trang Giới thiệu / Hướng dẫn sử dụng
│
├── assets/
│   ├── css/
│   │   ├── base.css          # Các biến màu, reset, class chung
│   │   ├── form.css          # Style riêng cho form
│   │   ├── result.css        # Style riêng cho phần kết quả
│   │   └── chart.css         # Style cho biểu đồ
│   │
│   ├── js/
│   │   ├── main.js           # Script dùng chung (menu, darkmode,…)
│   │   ├── predict.js        # Logic riêng cho trang index (form predict)
│   │   ├── tracking.js       # Vẽ biểu đồ (Recharts/Chart.js)
│   │   └── mockData.js       # Dữ liệu giả lập (demo)
│   │
│   ├── img/
│   │   └── logo.png
│   │
│   └── fonts/
│       └── inter.woff2
│
└── README.md
