from pathlib import Path
import numpy as np
import tensorflow as tf
from art.classifiers import KerasClassifier as kc
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score, matthews_corrcoef
from utils import in_out
from art.attacks.evasion import CarliniL2Method as CW2
import logging

config = in_out.get_parameters()


def run(
    MODEL_PATH=config["paths"]["model"],
    X_ATTACK_CANDIDATES_PATH=config["paths"]["x_candidates"],
    ATTACK_RESULTS_PATH=config["paths"]["attack_results"],
    N_INITIAL_STATE=config["n_initial_state"],
    INITIAL_STATE_OFFSET=config["initial_state_offset"],
    THRESHOLD=config["threshold"]
):
    logging.basicConfig(level=logging.INFO)
    tf.compat.v1.disable_eager_execution()
    Path(ATTACK_RESULTS_PATH).parent.mkdir(parents=True, exist_ok=True)

    # ----- Load and Scale

    X_initial_states = np.load(X_ATTACK_CANDIDATES_PATH)
    if INITIAL_STATE_OFFSET > - 1:
        X_initial_states = X_initial_states[
                           INITIAL_STATE_OFFSET: INITIAL_STATE_OFFSET + N_INITIAL_STATE
                           ]

    logging.info(f"Attacking with {X_initial_states.shape[0]} initial states.")

    # ----- Load Model

    model = tf.keras.models.load_model(MODEL_PATH)

    # ----- Attack

    kc_classifier = kc(model)
    pgd = CW2(kc_classifier, targeted=True, verbose=True, confidence=0.90, batch_size=128)
    attacks = pgd.generate(x=X_initial_states, y=np.zeros(X_initial_states.shape[0]))

    logging.info(f"{attacks.shape[0]} attacks generated")
    np.save(ATTACK_RESULTS_PATH, attacks)


if __name__ == "__main__":
    run()
