backend/
├── .env (DB: SQL Server, Secret Key)
├── main.py (App entry, CORS, Router setup)
├── requirements.txt (FastAPI, PyODBC, Scikit-learn 1.7.2...)
├── test_full.py (Script test tích hợp ML + NLP)
├── ai/
│   ├── predict_ml.py (Logic ML: KNN, Naive Bayes, ID3 + Binning)
│   ├── predict_nlp.py (Logic NLP: Keyword counting, Baseline/Logistic Regression)
│   └── routes.py (API: /predict, /predict/symptoms)
├── auth/
│   ├── models.py (SQLAlchemy User model)
│   ├── routes.py (Login, Register)
│   ├── schemas.py (Pydantic models)
│   └── services.py (User CRUD logic)
├── core/
│   ├── config.py (Load settings từ .env)
│   ├── security.py (JWT, Hash pass, Dependencies)
│   └── utils.py (Nội dung: "Comming soon")
├── database/
│   ├── base.py (SQLAlchemy Engine, SessionLocal)
│   ├── crud.py (Nội dung: "Comming soon")
│   └── models.py (Nội dung: "Comming soon")
├── users/
│   ├── routes.py (Profile, Change Pass)
│   ├── schemas.py (UserProfile, UserUpdate)
│   ├── services.py (Logic update user)
│   └── models.py (Nội dung: "Comming soon")
└── tests/
    ├── test_ai.py (Unit test cho ML loader)
    └── test_auth.py (Nội dung: "Comming soon")