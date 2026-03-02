import pickle
import json
import numpy as np
import os

def export_params():
    params = {}

    # 1. Medians (2, 130)
    medians_path = 'preprocessing/medians.pkl'
    if os.path.exists(medians_path):
        medians = pickle.load(open(medians_path, 'rb'))
        params['medians'] = medians.tolist()
        print(f"Exported medians with shape {medians.shape}")

    # 2. Scaler (StandardScaler)
    scaler_path = 'preprocessing/scaler.pkl'
    if os.path.exists(scaler_path):
        scaler = pickle.load(open(scaler_path, 'rb'))
        # Scaler was trained on 135 features (excluding f0) + 6 interactions?
        # Let's check the size
        params['scaler_mean'] = scaler.mean_.tolist()
        params['scaler_scale'] = scaler.scale_.tolist()
        print(f"Exported scaler with {len(scaler.mean_)} features")

    # 3. Models (Optional/Metadata)
    # Since we don't have .ckpt files, we at least prepare the structure
    # if clf_day_trend exists, it's a small RandomForest usually
    for model_name in ['clf_day_trend', 'clf_day_volat']:
        path = f'preprocessing/{model_name}.pkl'
        if os.path.exists(path):
            # We can't easily export a RandomForest to JSON for C++/Rust 
            # without a lot of work, but we can note its presence.
            # For now, we skip as they were for 'experimental' mode.
            print(f"Found {model_name}, skipping JSON export for now (complex structure)")

    with open('preprocessing/params.json', 'w') as f:
        json.dump(params, f)
    print("Saved to preprocessing/params.json")

if __name__ == "__main__":
    export_params()
