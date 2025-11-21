# ==============================================================================
# FILE: 02_model_architecture.py
# CHỨC NĂNG:
# 1. Định nghĩa Class Dataset: Để nạp dữ liệu vào mô hình.
# 2. Định nghĩa Class Model: Kiến trúc mạng nơ-ron lai (Hybrid ViBERT + Từ điển).
# ==============================================================================

'''
# FILE: 02_model_architecture.py

## 🎯 Chức năng
File này chứa "bản thiết kế" (Class) cho hệ thống, không thực thi code mà được các file khác `import` vào.

## 🏗 Các thành phần chính
### 1. Class `DiabetesDataset`
* **Nhiệm vụ:** Đóng gói dữ liệu text, nhãn (label) và tính toán luôn điểm số từ điển cho từng câu.
* **Input:** Văn bản thô.
* **Output:** Các Tensor (dạng số) sẵn sàng để đưa vào PyTorch.

### 2. Class `DiabetesHybridModel`
* **Nhiệm vụ:** Định nghĩa kiến trúc mạng nơ-ron.
* **Cơ chế lai (Hybrid):**
    * Nhánh 1: Dùng **ViBERT** để hiểu ngữ cảnh câu văn.
    * Nhánh 2: Dùng **Feature Từ điển** để bắt từ khóa trọng điểm.
    * Hai nhánh này được nối lại (Concatenate) trước khi đưa ra quyết định cuối cùng.
'''

import torch
from torch import nn
from torch.utils.data import Dataset
from transformers import AutoModel, AutoTokenizer
import json

# Cấu hình chung cho toàn bộ dự án
MODEL_NAME = "FPTAI/vibert-base-cased" # Mô hình ngôn ngữ tiếng Việt
MAX_LEN = 256                          # Độ dài tối đa của câu (số từ)

# --- PHẦN 1: CLASS DATASET (Người vận chuyển dữ liệu) ---
class DiabetesDataset(Dataset):
    def __init__(self, texts, labels, stages, keyword_weights_path, tokenizer):
        """
        texts: Danh sách các câu văn bản.
        labels: Nhãn bệnh (0: không bệnh hoặc 1: bệnh).
        stages: Giai đoạn bệnh (0, 1, 2, 3).
        keyword_weights_path: Đường dẫn đến file JSON stopword từ điển.
        """
        self.texts = texts
        self.labels = labels
        self.stages = stages
        self.tokenizer = tokenizer
        
        # Load từ điển trọng số (file JSON tạo ra từ bước 1)
        try:
            with open(keyword_weights_path, 'r', encoding='utf-8') as f:
                self.keyword_weights = json.load(f)
        except FileNotFoundError:
            self.keyword_weights = {} # Nếu không tìm thấy thì dùng dict rỗng

    def extract_weighted_features(self, text):
        """Hàm tính tổng điểm nguy hiểm dựa trên từ khóa"""
        text = str(text).lower()
        total_score = 0.0
        
        # Duyệt qua từng từ khóa trong từ điển
        for word, weight in self.keyword_weights.items():
            if word in text:
                total_score += weight
                
        # Chuẩn hóa: Chia cho 10 để điểm số này không quá lớn so với vector của ViBERT
        return [total_score / 15.0]

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, item):
        text = str(self.texts[item])
        label = self.labels[item]
        stage = self.stages[item]
        
        # 1. Tokenize văn bản (Biến chữ thành số ID cho ViBERT hiểu)
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=MAX_LEN,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )

        # 2. Tính điểm đặc trưng từ điển
        dict_feat = self.extract_weighted_features(text)

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'dict_features': torch.tensor(dict_feat, dtype=torch.float),
            'labels': torch.tensor(label, dtype=torch.long),
            'stages': torch.tensor(stage, dtype=torch.long)
        }

# --- PHẦN 2: CLASS MODEL ---
class DiabetesHybridModel(nn.Module):
    def __init__(self, n_classes):
        super(DiabetesHybridModel, self).__init__()
        
        # 1. Nhánh ViBERT (Hiểu ngữ nghĩa sâu)
        self.bert = AutoModel.from_pretrained(MODEL_NAME, force_download=True)
        
        # 2. Tính toán kích thước đầu vào cho tầng phân loại
        # = Kích thước vector ViBERT (768) + Kích thước feature Từ điển (1)
        input_dim = self.bert.config.hidden_size + 1
        
        # 3. Tầng phân loại (Classifier)
        # Đây là nơi tổng hợp thông tin để đưa ra quyết định cuối cùng
        self.classifier = nn.Sequential(
            nn.Linear(input_dim, 256),  # Tầng ẩn: Nén thông tin xuống 256 chiều
            nn.ReLU(),                  # Hàm kích hoạt (giúp học phi tuyến tính)
            nn.Dropout(0.3),            # Kỹ thuật quên bớt để tránh học vẹt
            nn.Linear(256, n_classes)   # Tầng ra: Số lớp cần dự đoán (VD: 2 lớp Bệnh/Ko bệnh)
        )

    def forward(self, input_ids, attention_mask, dict_features):
        # Bước 1: Cho văn bản đi qua ViBERT
        bert_output = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = bert_output.pooler_output # Lấy vector đại diện cho cả câu [Batch, 768]
        
        # Bước 2: Ghép (Concatenate) vector ViBERT với điểm số Từ điển
        # Kết quả là một vector dài hơn [Batch, 769]
        combined_output = torch.cat((pooled_output, dict_features), dim=1)
        
        # Bước 3: Cho qua tầng phân loại để ra kết quả
        output = self.classifier(combined_output)
        
        return output