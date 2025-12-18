"""
Script test để kiểm tra xem models có load được không
"""

from ai.predict_ml import get_predictor

def test_models():
    print("\n" + "="*60)
    print("TESTING MODELS")
    print("="*60 + "\n")
    
    try:
        # Initialize predictor
        predictor = get_predictor()
        
        # Check models loaded
        print(f"   Models loaded: {len(predictor.models)}")
        print(f"   Available: {list(predictor.models.keys())}")
        print(f"   Scaler: {'  Loaded' if predictor.scaler else '  Not found'}")
        
        # Test data
        test_data = {
            'Pregnancies': 0,
            'Glucose': 0,
            'BloodPressure': 0,
            'SkinThickness': 0,
            'Insulin': 0,
            'BMI': 0,
            'DiabetesPedigreeFunction': 0,
            'Age': 0
        }
        
        print(f"\n Test input:")
        for key, value in test_data.items():
            print(f"   {key}: {value}")
        
        # Test ensemble prediction
        print(f"\n Running ensemble prediction...")
        result = predictor.predict_ensemble(test_data)
        
        print(f"\n RESULTS:")
        print(f"   Prediction: {result['result']}")
        print(f"   Confidence: {result['ensemble_confidence']:.2%}")
        print(f"   Risk Level: {result['risk_level']}")
        print(f"   Models used: {result['models_count']}")
        
        print(f"\n Individual predictions:")
        for pred in result['individual_predictions']:
            print(f"   • {pred['model']}: {pred['result']} ({pred['confidence']:.2%})")
        
        print(f"\n{'='*60}")
        print(" TEST PASSED!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f" TEST FAILED: {e}")
        print("="*60 + "\n")
        raise

if __name__ == "__main__":
    test_models()
