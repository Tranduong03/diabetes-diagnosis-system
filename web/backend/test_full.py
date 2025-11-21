"""
Script test đầy đủ để kiểm tra ML models, NLP models, và APIs
"""

from ai.predict_ml import get_predictor
from ai.predict_nlp import get_nlp_predictor

def test_ml_models():
    """Test ML models"""
    print("\n" + "="*70)
    print("🧪 TESTING ML MODELS")
    print("="*70 + "\n")
    
    try:
        predictor = get_predictor()
        
        print(f"✅ Models loaded: {len(predictor.models)}")
        print(f"   Available: {list(predictor.models.keys())}")
        # Hiển thị model nào có scaler
        scaler_info = {m: ('✅' if m in predictor.scalers else '❌') for m in predictor.models}
        print(f"   Scalers per model: {scaler_info}\n")
        
        # Test data
        test_data = {
            'Pregnancies': 2,
            'Glucose': 120,
            'BloodPressure': 70,
            'SkinThickness': 20,
            'Insulin': 100,
            'BMI': 26.5,
            'DiabetesPedigreeFunction': 0.472,
            'Age': 34
        }
        
        print("📊 ML Prediction Test:")
        result = predictor.predict_ensemble(test_data)
        
        print(f"   Prediction: {result['result']}")
        print(f"   Confidence: {result['ensemble_confidence']:.2%}")
        print(f"   Risk Level: {result['risk_level']}")
        print(f"   Models: {result['models_count']}\n")
        
        return True
    except Exception as e:
        print(f"❌ ML Test Failed: {e}\n")
        return False

def test_nlp_models():
    """Test NLP models"""
    print("="*70)
    print("🧪 TESTING NLP MODELS")
    print("="*70 + "\n")
    
    try:
        nlp_predictor = get_nlp_predictor()
        
        print(f"✅ NLP Models loaded: {len(nlp_predictor.models)}")
        print(f"   Available: {list(nlp_predictor.models.keys())}")
        print(f"   Vectorizer: {'✅' if nlp_predictor.vectorizer else '❌'}\n")
        
        # Test cases
        test_cases = [
            "Tôi cảm thấy khát nước, đi tiểu nhiều, sụt cân",
            "Không có triệu chứng",
        ]
        
        print("📊 NLP Prediction Tests:")
        for symptoms in test_cases:
            result = nlp_predictor.predict_from_symptoms(symptoms)
            print(f"\n   Text: \"{symptoms}\"")
            if result['success']:
                print(f"   Result: {result['result']}")
                print(f"   Symptoms: {result['symptom_count']}")
                print(f"   Confidence: {result['ensemble_confidence']:.2%}")
            else:
                print(f"   Error: {result.get('error', 'Unknown')}")
        
        print()
        return True
    except Exception as e:
        print(f"❌ NLP Test Failed: {e}\n")
        return False

def test_combined():
    """Test kết hợp ML + NLP"""
    print("="*70)
    print("🧪 TESTING COMBINED ML + NLP")
    print("="*70 + "\n")
    
    try:
        predictor = get_predictor()
        nlp_predictor = get_nlp_predictor()
        
        # ML data
        ml_data = {
            'Pregnancies': 2,
            'Glucose': 150,  # Cao
            'BloodPressure': 80,
            'SkinThickness': 25,
            'Insulin': 120,
            'BMI': 32,  # Cao
            'DiabetesPedigreeFunction': 0.5,
            'Age': 45,  # Cao
        }
        
        # NLP data
        symptoms = "Tôi khát nước, đi tiểu nhiều, mệt mỏi"
        
        # Predictions
        ml_result = predictor.predict_ensemble(ml_data)
        nlp_result = nlp_predictor.predict_from_symptoms(symptoms)
        
        print("📊 Combined Prediction:")
        print(f"\n   ML Result: {ml_result['result']}")
        print(f"   ML Confidence: {ml_result['ensemble_confidence']:.2%}")
        
        if nlp_result['success']:
            print(f"\n   NLP Result: {nlp_result['result']}")
            print(f"   NLP Confidence: {nlp_result['ensemble_confidence']:.2%}")
            print(f"   Symptoms Found: {nlp_result['symptom_count']}")
        
        # Ensemble
        combined_conf = (ml_result['ensemble_confidence'] + nlp_result['ensemble_confidence']) / 2
        combined_pred = ml_result['ensemble_prediction'] or nlp_result['ensemble_prediction']
        
        print(f"\n   ===== ENSEMBLE =====")
        print(f"   Prediction: {'Có nguy cơ' if combined_pred else 'Không có nguy cơ'}")
        print(f"   Combined Confidence: {combined_conf:.2%}")
        print()
        
        return True
    except Exception as e:
        print(f"❌ Combined Test Failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🚀 FULL SYSTEM TEST")
    print("="*70)
    
    ml_ok = test_ml_models()
    nlp_ok = test_nlp_models()
    combined_ok = test_combined()
    
    print("="*70)
    print("\n📊 TEST RESULTS:")
    print(f"  ML Models: {'✅ PASS' if ml_ok else '❌ FAIL'}")
    print(f"  NLP Models: {'✅ PASS' if nlp_ok else '❌ FAIL'}")
    print(f"  Combined: {'✅ PASS' if combined_ok else '❌ FAIL'}")
    print("\n" + "="*70 + "\n")
