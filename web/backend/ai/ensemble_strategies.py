"""
Ensemble Strategies for ML + NLP (with stage info)
Tối ưu cho 2 models: XGBoost + PhoBERT
"""

from typing import Tuple, Dict, Optional


def ensemble_risk_aware(
    ml_pred: int,
    ml_conf: float,
    nlp_pred: int,
    nlp_conf: float,
    nlp_stage: int = 0
) -> Tuple[int, float, str, Dict]:
    """
    Risk-Aware Weighted Fusion
    
    Logic:
    - NLP stage càng cao → nguy cơ càng lớn → tăng trọng số NLP
    - Khi mâu thuẫn → ưu tiên dự đoán có risk cao hơn (cautious approach)
    - Khi đồng thuận → tăng confidence
    
    Args:
        ml_pred: ML prediction (0 hoặc 1)
        ml_conf: ML confidence (0.0 - 1.0)
        nlp_pred: NLP prediction (0 hoặc 1)
        nlp_conf: NLP confidence (0.0 - 1.0)
        nlp_stage: NLP stage (0-3, nếu có)
    
    Returns:
        (ensemble_pred, ensemble_conf, method, details)
    """
    
    # === Stage-based weight adjustment ===
    # Stage càng cao → NLP càng đáng tin (vì có triệu chứng rõ ràng)
    stage_boost = {
        0: 0.0,   # Không rõ ràng → không boost
        1: 0.1,   # Prediabetes → boost nhẹ
        2: 0.15,  # Diabetes → boost trung bình
        3: 0.2    # Severe → boost mạnh
    }
    
    nlp_weight_base = 0.4
    nlp_weight_adjusted = min(0.6, nlp_weight_base + stage_boost.get(nlp_stage, 0))
    ml_weight = 1.0 - nlp_weight_adjusted
    
    # === Confidence-based adjustment ===
    # Model nào tự tin hơn → tăng trọng số
    conf_diff = ml_conf - nlp_conf
    
    if abs(conf_diff) > 0.2:  # Chênh lệch lớn
        if ml_conf > nlp_conf:
            ml_weight += 0.1
            nlp_weight_adjusted -= 0.1
        else:
            nlp_weight_adjusted += 0.1
            ml_weight -= 0.1
    
    # Đảm bảo weights hợp lệ
    ml_weight = max(0.3, min(0.7, ml_weight))
    nlp_weight_adjusted = 1.0 - ml_weight
    
    # === Scenario 1: ĐỒNG THUẬN (cả 2 cùng dự đoán) ===
    if ml_pred == nlp_pred:
        ensemble_pred = ml_pred
        
        # Boost confidence khi đồng thuận
        if ml_pred == 1 and nlp_stage >= 2:
            # Cả 2 đều báo nguy cơ + stage cao → very confident
            ensemble_conf = min(0.95, (ml_conf + nlp_conf) / 2 * 1.15)
            method = f"Strong Agreement (stage {nlp_stage})"
        else:
            # Đồng thuận bình thường
            ensemble_conf = (ml_conf * ml_weight + nlp_conf * nlp_weight_adjusted)
            method = "Agreement"
        
        details = {
            "agreement": True,
            "ml_weight": round(ml_weight, 2),
            "nlp_weight": round(nlp_weight_adjusted, 2),
            "stage_boost": stage_boost.get(nlp_stage, 0)
        }
        
        return ensemble_pred, ensemble_conf, method, details
    
    # === Scenario 2: MÂU THUẪN (predictions khác nhau) ===
    else:
        # Cautious approach: Ưu tiên dự đoán CÓ RISK (pred=1)
        # Vì sai lầm Type 2 (bỏ sót bệnh) nguy hiểm hơn Type 1 (báo nhầm)
        
        if ml_pred == 1:  # ML báo có risk, NLP báo không
            risk_predictor = "ML"
            risk_conf = ml_conf
            safe_conf = nlp_conf
        else:  # NLP báo có risk, ML báo không
            risk_predictor = "NLP"
            risk_conf = nlp_conf
            safe_conf = ml_conf
        
        # Quyết định dựa trên độ chênh lệch confidence
        conf_gap = risk_conf - safe_conf
        
        if conf_gap > 0.15:
            # Model có risk tự tin hơn nhiều → tin model đó
            ensemble_pred = 1  # Ưu tiên có risk
            ensemble_conf = risk_conf * 0.9  # Giảm 10% vì có mâu thuẫn
            method = f"{risk_predictor} wins (confident)"
        
        elif conf_gap < -0.15:
            # Model không có risk tự tin hơn nhiều → tin model đó
            ensemble_pred = 0
            ensemble_conf = safe_conf * 0.9
            method = "Safe prediction wins"
        
        else:
            # Confidence tương đương nhau → CAUTIOUS: chọn có risk
            if nlp_stage >= 2:
                # NLP có stage cao → tin NLP hơn
                ensemble_pred = nlp_pred
                ensemble_conf = nlp_conf * 0.85
                method = f"NLP wins (stage {nlp_stage})"
            else:
                # Weighted voting nhưng boost prediction = 1
                weighted_score = (ml_pred * ml_weight * ml_conf) + \
                                (nlp_pred * nlp_weight_adjusted * nlp_conf)
                
                # Threshold thấp hơn 0.5 để ưu tiên có risk
                ensemble_pred = 1 if weighted_score >= 0.45 else 0
                ensemble_conf = (ml_conf * ml_weight + nlp_conf * nlp_weight_adjusted) * 0.85
                method = "Cautious weighted"
        
        details = {
            "agreement": False,
            "conflict_resolver": method,
            "ml_weight": round(ml_weight, 2),
            "nlp_weight": round(nlp_weight_adjusted, 2),
            "stage_boost": stage_boost.get(nlp_stage, 0),
            "confidence_gap": round(conf_gap, 3)
        }
        
        return ensemble_pred, ensemble_conf, method, details


def ensemble_simple_weighted(
    ml_pred: int,
    ml_conf: float,
    nlp_pred: int,
    nlp_conf: float,
    nlp_stage: int = 0
) -> Tuple[int, float, str, Dict]:
    """
    Simple weighted voting (fallback method)
    Không xét stage, chỉ dùng confidence
    """
    # Fixed weights
    ml_weight = 0.6
    nlp_weight = 0.4
    
    if ml_pred == nlp_pred:
        ensemble_pred = ml_pred
        ensemble_conf = (ml_conf * ml_weight + nlp_conf * nlp_weight)
        method = "Simple Agreement"
    else:
        # Weighted voting
        weighted_score = (ml_pred * ml_weight * ml_conf) + \
                        (nlp_pred * nlp_weight * nlp_conf)
        ensemble_pred = 1 if weighted_score >= 0.5 else 0
        ensemble_conf = (ml_conf * ml_weight + nlp_conf * nlp_weight)
        method = "Simple Weighted"
    
    details = {
        "agreement": ml_pred == nlp_pred,
        "ml_weight": ml_weight,
        "nlp_weight": nlp_weight
    }
    
    return ensemble_pred, ensemble_conf, method, details


def ensemble_conservative(
    ml_pred: int,
    ml_conf: float,
    nlp_pred: int,
    nlp_conf: float,
    nlp_stage: int = 0
) -> Tuple[int, float, str, Dict]:
    """
    Conservative approach: Luôn ưu tiên prediction có risk cao hơn
    Khi mâu thuẫn → chọn prediction = 1
    """
    if ml_pred == nlp_pred:
        ensemble_pred = ml_pred
        ensemble_conf = (ml_conf + nlp_conf) / 2
        method = "Conservative Agreement"
    else:
        # Luôn chọn prediction = 1 (có risk)
        ensemble_pred = 1
        
        # Confidence = model nào predict 1
        if ml_pred == 1:
            ensemble_conf = ml_conf * 0.85
            method = "Conservative (ML)"
        else:
            ensemble_conf = nlp_conf * 0.85
            method = "Conservative (NLP)"
    
    details = {
        "agreement": ml_pred == nlp_pred,
        "strategy": "always_risk_aware"
    }
    
    return ensemble_pred, ensemble_conf, method, details


# ============ MAIN API ============

def get_ensemble_prediction(
    ml_pred: int,
    ml_conf: float,
    nlp_pred: int,
    nlp_conf: float,
    nlp_stage: int = 0,
    strategy: str = "risk_aware"
) -> Tuple[int, float, str, Dict]:
    """
    Main API cho ensemble prediction
    
    Args:
        strategy: "risk_aware" (default), "simple", "conservative"
    
    Returns:
        (prediction, confidence, method, details)
    """
    strategies = {
        "risk_aware": ensemble_risk_aware,
        "simple": ensemble_simple_weighted,
        "conservative": ensemble_conservative
    }
    
    ensemble_fn = strategies.get(strategy, ensemble_risk_aware)
    return ensemble_fn(ml_pred, ml_conf, nlp_pred, nlp_conf, nlp_stage)


# ============ TESTING ============

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING ENSEMBLE STRATEGIES")
    print("=" * 60)
    
    test_cases = [
        # (ml_pred, ml_conf, nlp_pred, nlp_conf, nlp_stage, description)
        (0, 0.85, 0, 0.80, 0, "Both predict NO risk"),
        (1, 0.90, 1, 0.75, 2, "Both predict HIGH risk + stage 2"),
        (1, 0.70, 0, 0.65, 0, "ML says risk, NLP says no (similar conf)"),
        (0, 0.75, 1, 0.80, 3, "ML says no, NLP says risk + stage 3"),
        (1, 0.95, 0, 0.60, 1, "ML very confident risk, NLP low conf no risk"),
        (0, 0.90, 1, 0.55, 0, "ML very confident no risk, NLP low conf risk"),
    ]
    
    for i, (ml_p, ml_c, nlp_p, nlp_c, stage, desc) in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {desc} ---")
        print(f"Input: ML({ml_p}, {ml_c:.2f}) | NLP({nlp_p}, {nlp_c:.2f}, stage={stage})")
        
        pred, conf, method, details = get_ensemble_prediction(
            ml_p, ml_c, nlp_p, nlp_c, stage
        )
        
        print(f"Output: Prediction={pred}, Confidence={conf:.3f}")
        print(f"Method: {method}")
        print(f"Details: {details}")