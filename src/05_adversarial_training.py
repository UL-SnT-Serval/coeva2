from joblib import load, dump

from attacks.coeva2.classifier import Classifier
from attacks.coeva2.lcld_constraints import LcldConstraints
from attacks.coeva2.objective_calculator import ObjectiveCalculator
from utils import Pickler, in_out
import numpy as np
from sklearn.base import clone
from sklearn.metrics import matthews_corrcoef, roc_auc_score

config = in_out.get_parameters()


def run(
    MODEL_PATH=config["paths"]["model"],
    RESISTANT_MODEL_PATH=config["paths"]["resistant_model"],
    TRAIN_TEST_DATA_DIR=config["dirs"]["train_test_data"],
    THRESHOLD=config["threshold"],
    X_ADV=config['paths']["x_adv"]
):

    # Load
    model = load(MODEL_PATH)
    model.set_params(verbose=0, n_jobs=1)
    classifier = Classifier(model)
    constraints = LcldConstraints(
        #config["amount_feature_index"],
        config["paths"]["features"],
        config["paths"]["constraints"],
    )
    objective_calculator = ObjectiveCalculator(
        classifier,
        constraints,
        config["threshold"],
        #config["high_amount"],
        #config["amount_feature_index"]
    )

    # Load samples

    # Adv
    # attack_results = Pickler.load_from_file(ATTACK_RESULTS_PATH)
    # X_adv = objective_calculator.get_successful_attacks(attack_results)
    X_adv = np.load(X_ADV)
    y_adv = np.zeros(X_adv.shape[0]) + 1

    # Legits
    X_train = np.load("{}/train_X.npy".format(TRAIN_TEST_DATA_DIR))
    y_train = np.load("{}/train_y.npy".format(TRAIN_TEST_DATA_DIR))

    # Retrain
    resistant_model = clone(model)
    resistant_model.set_params(verbose=2, n_jobs=-1)
    resistant_model.fit(
        np.concatenate([X_train, X_adv]), np.concatenate([y_train, y_adv])
    )
    resistant_model.set_params(verbose=0, n_jobs=1)

    dump(resistant_model, RESISTANT_MODEL_PATH)

    # Evaluate
    X_test = np.load("{}/test_X.npy".format(TRAIN_TEST_DATA_DIR))
    y_test = np.load("{}/test_y.npy".format(TRAIN_TEST_DATA_DIR))

    y_pred_proba = model.predict_proba(X_test)
    y_pred = (y_pred_proba[:, 1] >= THRESHOLD).astype(bool)
    print(
        "Original AUROC: {}, MCC: {}".format(
            roc_auc_score(y_test, y_pred_proba[:, 1]), matthews_corrcoef(y_test, y_pred)
        )
    )
    y_pred_proba = resistant_model.predict_proba(X_test)
    y_pred = (y_pred_proba[:, 1] >= THRESHOLD).astype(bool)
    print(
        "Resistant AUROC: {}, MCC: {}".format(
            roc_auc_score(y_test, y_pred_proba[:, 1]), matthews_corrcoef(y_test, y_pred)
        )
    )


if __name__ == "__main__":
    run()
