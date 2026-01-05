"""
Script kiểm tra XGBoost model với các trường hợp thực tế từ dataset
"""

import joblib
import numpy as np
from pathlib import Path

def load_model():
    """Load model"""
    # Tìm model path (điều chỉnh nếu cần)
    project_root = Path(__file__).resolve().parents[0]
    model_path = project_root / "models" / "se" / "xgboost_12feat.pkl"
    
    if not model_path.exists():
        print(f"❌ Không tìm thấy model tại: {model_path}")
        print("Vui lòng điều chỉnh đường dẫn trong script")
        return None
    
    print(f"✅ Loading model từ: {model_path}")
    model = joblib.load(model_path)
    return model

def test_cases():
    """Các test case từ dataset - tất cả đều có Diabetes_binary = 1"""
    cases = [
        {
            "name": "Case 1 - Severe",
            "data": [1, 1, 30, 1, 1, 0, 5, 30, 30, 1, 9],
            "features": "HighBP=1, HighChol=1, BMI=30, Smoker=1, Heart=1, PhysActivity=0, GenHlth=5, MentHlth=30, PhysHlth=30, DiffWalk=1, Age=9"
        },
        {
            "name": "Case 2 - Elderly",
            "data": [0, 0, 25, 1, 0, 1, 3, 0, 0, 0, 13],
            "features": "HighBP=0, HighChol=0, BMI=25, Smoker=1, Heart=0, PhysActivity=1, GenHlth=3, MentHlth=0, PhysHlth=0, DiffWalk=0, Age=13"
        },
        {
            "name": "Case 3 - Multiple Risk",
            "data": [1, 1, 28, 0, 0, 0, 4, 0, 0, 1, 11],
            "features": "HighBP=1, HighChol=1, BMI=28, Smoker=0, Heart=0, PhysActivity=0, GenHlth=4, MentHlth=0, PhysHlth=0, DiffWalk=1, Age=11"
        },
        {
            "name": "Case 4 - Young Smoker",
            "data": [0, 0, 23, 1, 0, 1, 2, 0, 0, 0, 7],
            "features": "HighBP=0, HighChol=0, BMI=23, Smoker=1, Heart=0, PhysActivity=1, GenHlth=2, MentHlth=0, PhysHlth=0, DiffWalk=0, Age=7"
        },
        {
            "name": "Case 5 - Elderly Good Health",
            "data": [1, 0, 27, 0, 0, 1, 1, 0, 0, 0, 13],
            "features": "HighBP=1, HighChol=0, BMI=27, Smoker=0, Heart=0, PhysActivity=1, GenHlth=1, MentHlth=0, PhysHlth=0, DiffWalk=0, Age=13"
        },
        {
            "name": "Case 6 - Multiple Conditions",
            "data": [1, 1, 37, 1, 1, 0, 5, 0, 0, 1, 10],
            "features": "HighBP=1, HighChol=1, BMI=37, Smoker=1, Heart=1, PhysActivity=0, GenHlth=5, MentHlth=0, PhysHlth=0, DiffWalk=1, Age=10"
        },
        {
            "name": "Case 7 - Heart Disease",
            "data": [1, 1, 28, 1, 1, 0, 4, 0, 0, 0, 12],
            "features": "HighBP=1, HighChol=1, BMI=28, Smoker=1, Heart=1, PhysActivity=0, GenHlth=4, MentHlth=0, PhysHlth=0, DiffWalk=0, Age=12"
        },
        {
            "name": "Case 8 - Mental/Physical Health Issues",
            "data": [1, 1, 27, 1, 0, 0, 4, 20, 20, 1, 8],
            "features": "HighBP=1, HighChol=1, BMI=27, Smoker=1, Heart=0, PhysActivity=0, GenHlth=4, MentHlth=20, PhysHlth=20, DiffWalk=1, Age=8"
        }
    ]
    return cases

def test_model():
    """Chạy test cases"""
    model = load_model()
    
    if model is None:
        return
    
    print(f"\n{'='*80}")
    print("THÔNG TIN MODEL")
    print(f"{'='*80}")
    print(f"Type: {type(model)}")
    print(f"Classes: {model.classes_}")
    print(f"Number of classes: {model.n_classes_}")
    
    # Kiểm tra feature importance
    if hasattr(model, 'feature_importances_'):
        print(f"\nFeature importances:")
        feature_names = ['HighBP', 'HighChol', 'BMI', 'Smoker', 'HeartDisease', 
                        'PhysActivity', 'GenHlth', 'MentHlth', 'PhysHlth', 'DiffWalk', 'Age']
        for name, importance in zip(feature_names, model.feature_importances_):
            print(f"  {name}: {importance:.4f}")
    
    print(f"\n{'='*80}")
    print("KIỂM TRA TEST CASES (Tất cả đều có Diabetes_binary = 1 trong dataset)")
    print(f"{'='*80}\n")
    
    cases = test_cases()
    correct = 0
    total = len(cases)
    
    for case in cases:
        X = np.array([case['data']])
        
        # Predict
        prediction = int(model.predict(X)[0])
        probabilities = model.predict_proba(X)[0]
        confidence = float(probabilities[prediction])
        
        # Check if correct
        expected = 1  # Tất cả cases đều là Diabetes = 1
        is_correct = (prediction == expected)
        if is_correct:
            correct += 1
        
        status = "✅ ĐÚNG" if is_correct else "❌ SAI"
        
        print(f"{case['name']}")
        print(f"  Input: {case['features']}")
        print(f"  Prediction: {prediction} (Expected: {expected}) {status}")
        print(f"  Confidence: {confidence:.4f} ({confidence*100:.2f}%)")
        print(f"  Probabilities: No Diabetes={probabilities[0]:.4f}, Diabetes={probabilities[1]:.4f}")
        print()
    
    print(f"{'='*80}")
    print(f"KẾT QUẢ TỔNG HỢP: {correct}/{total} đúng ({correct/total*100:.1f}%)")
    print(f"{'='*80}\n")
    
    # Phân tích nếu model predict sai nhiều
    if correct < total * 0.5:  # Nếu sai > 50%
        print("⚠️ CẢNH BÁO: Model đang predict sai nhiều trường hợp!")
        print("\nCó thể nguyên nhân:")
        print("1. Model được train với data không đúng hoặc không cân bằng")
        print("2. Features không khớp với model (thiếu/thừa features)")
        print("3. Thứ tự features không đúng")
        print("4. Model cần được retrain với data tốt hơn")
        print("\nGợi ý:")
        print("- Kiểm tra lại dataset train")
        print("- Kiểm tra class distribution trong training data")
        print("- Thử train lại model với SMOTE hoặc class_weight")

def test_normal_case():
    """Test với trường hợp không có tiểu đường"""
    model = load_model()
    if model is None:
        return
    
    print(f"\n{'='*80}")
    print("KIỂM TRA TRƯỜNG HỢP BÌNH THƯỜNG (Không có tiểu đường)")
    print(f"{'='*80}\n")
    
    # Người trẻ, khỏe mạnh, không có risk factors
    normal_case = [0, 0, 22, 0, 0, 1, 1, 0, 0, 0, 3]  # Age 30-34
    
    X = np.array([normal_case])
    prediction = int(model.predict(X)[0])
    probabilities = model.predict_proba(X)[0]
    
    print("Case: Người trẻ khỏe mạnh")
    print("  HighBP=0, HighChol=0, BMI=22, Smoker=0, Heart=0")
    print("  PhysActivity=1, GenHlth=1, MentHlth=0, PhysHlth=0, DiffWalk=0, Age=3")
    print(f"\nPrediction: {prediction}")
    print(f"Probabilities: No Diabetes={probabilities[0]:.4f}, Diabetes={probabilities[1]:.4f}")
    
    if prediction == 0:
        print("✅ Predict đúng: Không có tiểu đường")
    else:
        print("❌ Predict sai: Model predict có tiểu đường cho người khỏe mạnh!")

if __name__ == "__main__":
    print("🔍 BẮT ĐẦU KIỂM TRA MODEL\n")
    
    # Test với các case có diabetes
    test_model()
    
    # Test với case bình thường
    test_normal_case()
    
    print("\n✅ HOÀN THÀNH KIỂM TRA")