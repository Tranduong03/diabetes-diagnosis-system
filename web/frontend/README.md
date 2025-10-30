# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

diabetes-diagnosis-frontend/
│
├── src/
│   ├── assets/                # Hình ảnh, logo, fonts, ...
│   │   ├── logo.png
│   │   └── styles/
│   │       └── base.css       # Biến màu, shadow, font chung
│   │
│   ├── components/            # Các thành phần tái sử dụng
│   │   ├── FormInput.jsx      # Thẻ nhập liệu
│   │   ├── ResultPanel.jsx    # Bảng kết quả chẩn đoán
│   │   ├── Navbar.jsx         # Thanh menu điều hướng
│   │   ├── ChartLine.jsx      # Biểu đồ theo dõi
│   │   └── Card.jsx           # Component card chung
│   │
│   ├── pages/                 # Các trang chính
│   │   ├── Dashboard.jsx      # Trang tổng quan
│   │   ├── Diagnosis.jsx      # Form nhập liệu & kết quả
│   │   ├── Tracking.jsx       # Theo dõi kết quả (biểu đồ, lịch sử)
│   │   ├── Explanation.jsx    # Giải thích & gợi ý
│   │   └── About.jsx          # Giới thiệu hệ thống
│   │
│   ├── data/
│   │   └── mockData.js        # Dữ liệu giả lập để demo
│   │
│   ├── routes/
│   │   └── AppRouter.jsx      # Định nghĩa routes cho toàn app
│   │
│   ├── App.jsx                # Gốc ứng dụng
│   ├── main.jsx               # Điểm khởi động React
│   └── index.css              # Import Tailwind, base style
│
├── public/                    # File tĩnh
│   ├── favicon.ico
│   └── manifest.json
│
├── package.json
├── tailwind.config.js
├── vite.config.js
└── README.md
