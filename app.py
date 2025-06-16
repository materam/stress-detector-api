from flask import Flask, request, jsonify
from flask_cors import CORS  # <-- 🔥 Import CORS
import pandas as pd
import joblib
from rule_based_physical_model import predict as physical_model_predict

# Load trained models
psych_model = joblib.load("Models/pss_rf_model.pkl")  # PSS model
meta_model = joblib.load("Models/MetaModel.pkl")  # Final classifier

# PSS feature names
PSS_ITEMS = [
    'pss_unexp', 'pss_contr', 'pss_stress', 'pss_confid',
    'pss_yourw', 'pss_cope', 'pss_irritati', 'pss_top',
    'pss_anger', 'pss_difficu'
]

# Flask setup
app = Flask(__name__)
CORS(app)  # <-- 🔥 Allow requests from any frontend

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    input_df = pd.DataFrame([data])
    print("Received JSON:", data)

    # --- Psychological Stress ---
    pss_features = input_df[PSS_ITEMS]
    pss_pred = int(psych_model.predict(pss_features)[0])  # 0 = Low, 1 = Medium, 2 = High

    # --- Physical Stress ---
    biosensor_df = input_df[['HR', 'TEMP', 'GSR']]
    physical_output = physical_model_predict(biosensor_df)
    phys_pred = int(physical_output.iloc[0]['Predicted_Stress'])

    # --- Meta Model Prediction ---
    meta_input = pd.DataFrame([[phys_pred, pss_pred]], columns=['physical', 'psychological'])
    final_class = int(meta_model.predict(meta_input)[0])

    # --- Interpretations ---
    interpretations = {
        0: ("No stress", "No action needed"),
        1: ("Mild psychological stress", "Try mindfulness / breathing exercises"),
        2: ("High psychological stress", "Seek therapy / psychological support"),
        3: ("Physical stress", "Physical rest / hydration / medical check-up"),
        4: ("Critical (High mental + physical)", "Seek medical + psychological intervention ASAP"),
    }

    interpretation, recommendation = interpretations[final_class]

    return jsonify({
        "physical_stress": phys_pred,
        "psychological_stress": pss_pred,
        "meta_class": final_class,
        "interpretation": interpretation,
        "recommendation": recommendation
    })

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
