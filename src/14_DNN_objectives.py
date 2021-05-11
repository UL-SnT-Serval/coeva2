from pathlib import Path

import joblib
import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score, matthews_corrcoef

from attacks.coeva2.lcld_constraints import LcldConstraints
from utils import in_out, Pickler
import pandas as pd
import logging

config = in_out.get_parameters()


def run(
    MODEL_PATH=config["paths"]["model"],
    X_ATTACK_CANDIDATES_PATH=config["paths"]["x_candidates"],
    ATTACK_RESULTS_PATH=config["paths"]["attack_results"],
    N_INITIAL_STATE=config["n_initial_state"],
    INITIAL_STATE_OFFSET=config["initial_state_offset"],
    THRESHOLD=config["threshold"],
    SCALER_PATH=config["paths"]["scaler"],
    OBJECTIVES_PATH=config["paths"]["objectives"],

):
    logging.basicConfig(level=logging.INFO)
    # tf.compat.v1.disable_eager_execution()
    Path(ATTACK_RESULTS_PATH).parent.mkdir(parents=True, exist_ok=True)

    # ----- Load and Scale

    X_initial_states = np.load(X_ATTACK_CANDIDATES_PATH)
    if N_INITIAL_STATE > -1:
        X_initial_states = X_initial_states[
                           INITIAL_STATE_OFFSET: INITIAL_STATE_OFFSET + N_INITIAL_STATE
                           ]
    X_attacks = np.load(ATTACK_RESULTS_PATH)
    scaler = joblib.load(SCALER_PATH)
    model = tf.keras.models.load_model(MODEL_PATH)

    # Verification
    if X_initial_states.shape[0] != X_attacks.shape[0]:
          raise Exception(f"Number of initial state ({X_initial_states.shape[0]}) is different from the number of attacks ({X_attacks.shape[0]})")

    # ----- Predict
    y_attack_proba = model.predict(X_attacks)
    y_pred_proba = model.predict(scaler.transform(X_initial_states))

    y_attack = (y_attack_proba[:, 1] >= THRESHOLD).astype(bool)
    y_pred = (y_pred_proba[:, 1] >= THRESHOLD).astype(bool)


    # Misclassification (O2)
    misclasiffication_i = (y_attack != y_pred)
    X_misclassified = X_attacks[misclasiffication_i]
    misclassification_rate = X_misclassified.shape[0] / X_attacks.shape[0]

    # Constraints (O3)
    constraints_evaluator = LcldConstraints(
        # config["amount_feature_index"],
        config["paths"]["features"],
        config["paths"]["constraints"],
    )
    constraints = constraints_evaluator.evaluate(scaler.inverse_transform(X_misclassified))
    constraints[:, 0] = constraints[:, 0] - 5
    constraints_violated = constraints.sum(axis=1) > 0
    constraints_rate = (1 - constraints_violated).sum() / X_attacks.shape[0]
    X_missclassified_constraints = X_misclassified[(1 - constraints_violated).astype(bool)]
    misclasiffication_constraints_rate = X_missclassified_constraints.shape[0] / X_attacks.shape[0]

    # Distance
    distances = np.linalg.norm(X_attacks-X_initial_states, axis=1)
    distance_mean = distances.mean()

    # Shape and save metrics
    objectives = {
        "n_sample": np.array([X_initial_states.shape[0]]),
        "o1": np.array([constraints_rate]),
        "o2": np.array([misclassification_rate]),
        "o3": np.array([misclasiffication_constraints_rate]),
        "L2_distance": np.array([distance_mean])
    }
    objectives_df = pd.DataFrame.from_dict(objectives)

    logging.info(objectives)
    objectives_df.to_csv(OBJECTIVES_PATH)


if __name__ == "__main__":
    run()