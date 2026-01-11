import torch
import torch.nn as nn
import xgboost as xgb
import joblib
import json
import numpy as np
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "ml_models")

class InferenceService:
    def __init__(self):
        try:
            with open(os.path.join(MODEL_DIR, "features.json"), "r") as f:
                self.features = json.load(f)
            with open(os.path.join(MODEL_DIR, "thresholds.json"), "r") as f:
                self.thresholds = json.load(f)

            # 2. تحميل الـ Scaler
            self.scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))

            # 3. تحميل نموذج XGBoost
            self.xgb_model = xgb.Booster()
            self.xgb_model.load_model(os.path.join(MODEL_DIR, "xgb_model.json"))

            # 4. تحميل نموذج LSTM
            self.device = torch.device("cpu") 
            self.lstm_model = self.load_lstm()
            print("✅ AI Engine: All models loaded successfully!")
        except Exception as e:
            print(f"❌ AI Engine Error: {str(e)}")
            self.lstm_model = None 

    def load_lstm(self):
        # الهيكل المصحح ليتطابق مع أوزان الملف المحفوظ (head.3.weight)
        class LSTMClassifier(nn.Module):
            def __init__(self, n_features):
                super().__init__()
                self.lstm = nn.LSTM(input_size=n_features, hidden_size=64, num_layers=2, batch_first=True)
                self.head = nn.Sequential(
                    nn.Linear(64, 64),  
                    nn.ReLU(),          
                    nn.Dropout(0.2),    
                    nn.Linear(64, 1)    
                )
            def forward(self, x):
                out, _ = self.lstm(x)
                return self.head(out[:, -1, :]).squeeze(-1)

        model = LSTMClassifier(n_features=len(self.features))
        model.load_state_dict(torch.load(os.path.join(MODEL_DIR, "lstm_model.pt"), map_location=self.device))
        model.to(self.device)
        model.eval()
        return model

    def predict(self, df_input: pd.DataFrame):
        if self.lstm_model is None:
            return {"error": "Model not loaded"}
            
        X_scaled = self.scaler.transform(df_input[self.features])
        
        # توقع XGBoost
        dmatrix = xgb.DMatrix(pd.DataFrame(X_scaled, columns=self.features).tail(1))
        xgb_return = self.xgb_model.predict(dmatrix)[0]

        # توقع LSTM
        X_seq = torch.tensor(X_scaled[-48:], dtype=torch.float32).unsqueeze(0).to(self.device)
        with torch.no_grad():
            lstm_logits = self.lstm_model(X_seq)
            lstm_prob = torch.sigmoid(lstm_logits).item()

        p_thr = self.thresholds.get("p_thr", 0.55)
        trend = "Up" if lstm_prob >= p_thr else "Steady/Down"
        
        return {
            "predicted_return": round(float(xgb_return), 6),
            "trend": trend,
            "confidence": f"{round(lstm_prob * 100)}%"
        }

inference_engine = InferenceService()