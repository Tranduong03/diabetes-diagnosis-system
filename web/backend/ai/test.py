# Training script
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
import joblib
import pandas as pd

df = pd.read_csv(r"D:\project1(1)\diabetes-diagnosis-system\datasets\raw\symptoms2.csv")

# 1. Load PhoBERT
model = SentenceTransformer('VoVanPhuc/sup-SimCSE-VietNamese-phobert-base')

# 2. Encode texts
X_embeddings = model.encode(df["text"].tolist())

# 3. Train outcome classifier
outcome_clf = LogisticRegression(max_iter=2000)
outcome_clf.fit(X_embeddings, df["outcome"])

# 4. Train stage classifier (chỉ với outcome=1)
df_diab = df[df["outcome"] == 1]
X_stage_embed = model.encode(df_diab["text"].tolist())
stage_clf = LogisticRegression(max_iter=2000)
stage_clf.fit(X_stage_embed, df_diab["stage"])

# 5. Save models
joblib.dump(model, "phobert_encoder.pkl")
joblib.dump(outcome_clf, "outcome_clf.pkl")
joblib.dump(stage_clf, "stage_clf.pkl")