"""
Script test để kiểm tra xem models có load được không
"""

from ai.predict_ml import get_predictor

def test_models():
    print("\n" + "="*60)
    print("🧪 TESTING MODELS")
    print("="*60 + "\n")
    
    try:
        # Initialize predictor
        predictor = get_predictor()
        
        # Check models loaded
        print(f"✅ Models loaded: {len(predictor.models)}")
        print(f"   Available: {list(predictor.models.keys())}")
        print(f"   Scaler: {'✅ Loaded' if predictor.scaler else '❌ Not found'}")
        
        # Test data
        test_data = {
            'Pregnancies': 1,
            'Glucose': 85,
            'BloodPressure': 66,
            'SkinThickness': 29,
            'Insulin': 125,
            'BMI': 26.6,
            'DiabetesPedigreeFunction': 0.351,
            'Age': 31
        }
        
        print(f"\n📊 Test input:")
        for key, value in test_data.items():
            print(f"   {key}: {value}")
        
        # Test ensemble prediction
        print(f"\n🔮 Running ensemble prediction...")
        result = predictor.predict_ensemble(test_data)
        
        print(f"\n✅ RESULTS:")
        print(f"   Prediction: {result['result']}")
        print(f"   Confidence: {result['ensemble_confidence']:.2%}")
        print(f"   Risk Level: {result['risk_level']}")
        print(f"   Models used: {result['models_count']}")
        
        print(f"\n📋 Individual predictions:")
        for pred in result['individual_predictions']:
            print(f"   • {pred['model']}: {pred['result']} ({pred['confidence']:.2%})")
        
        print(f"\n{'='*60}")
        print("✅ TEST PASSED!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ TEST FAILED: {e}")
        print("="*60 + "\n")
        raise

if __name__ == "__main__":
    test_models()

"""
Script test để kiểm tra xem NLP models có load được không
"""

# from ai.predict_nlp import get_nlp_predictor

# def test_nlp_models():
#     print("\n" + "="*60)
#     print("🧪 TESTING NLP MODELS")
#     print("="*60 + "\n")
    
#     try:
#         # Initialize NLP predictor
#         predictor = get_nlp_predictor()
        
#         # Check models loaded
#         print(f"✅ Models loaded: {len(predictor.models)}")
#         print(f"   Available: {list(predictor.models.keys())}")
#         print(f"   Vectorizer: {'✅ Loaded' if predictor.vectorizer else '❌ Not found (maybe inside pipeline)'}")
        
#         # Test input
#         test_data = {
#             "text": "Bệnh nhân cảm thấy mệt mỏi, tiểu nhiều và khát nước liên tục."
#         }
        
#         print(f"\n📄 Test Input Text:")
#         print(f"   {test_data['text']}")
        
#         # Test single model predictions
#         print("\n🔍 Testing predictions for each individual model...")
#         for model_name in predictor.models.keys():
#             res = predictor.predict_single_model(model_name, test_data)
#             print(f"   • {model_name}: {res['prediction_label']} ({res['confidence']:.2%})")
        
#         # Test ensemble
#         print("\n🔮 Running NLP ensemble prediction...")
#         ensemble = predictor.predict_ensemble(test_data)
        
#         print(f"\n✅ ENSEMBLE RESULT:")
#         print(f"   Prediction: {ensemble['result_label']}")
#         print(f"   Confidence: {ensemble['ensemble_confidence']:.2%}")
#         print(f"   Models used: {ensemble['models_count']}")
        
#         print("\n📋 Individual model details:")
#         for item in ensemble['individual']:
#             print(f"   • {item['model']}: {item['prediction']} ({item['confidence']:.2%})")
        
#         print("\n" + "="*60)
#         print("✅ NLP TEST PASSED!")
#         print("="*60 + "\n")
    
#     except Exception as e:
#         print("\n" + "="*60)
#         print(f"❌ NLP TEST FAILED: {e}")
#         print("="*60 + "\n")
#         raise


# if __name__ == "__main__":
#     test_nlp_models()
