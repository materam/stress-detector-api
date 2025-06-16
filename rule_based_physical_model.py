# rule_based_physical_model.py

import pandas as pd

def predict(features: pd.DataFrame) -> pd.DataFrame:
    def classify(row):
        score = 0
        if row['HR'] > 85:
            score += 1
        if row['TEMP'] < 33:
            score += 1
        if row['GSR'] > 3.5:
            score += 1
        return 1 if score >= 2 else 0

    def confidence(row):
        return 0.9 if row['Predicted_Stress'] == 1 else 0.7

    features['Predicted_Stress'] = features.apply(classify, axis=1)
    features['Confidence'] = features.apply(confidence, axis=1)
    
    return features[['Predicted_Stress', 'Confidence']]
