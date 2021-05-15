import pandas as pd
from joblib import load
import numpy as np

from attacks.coeva2.classifier import Classifier
from src.examples.lcld.lcld_constraints import LcldConstraints
from attacks.coeva2.objective_calculator import ObjectiveCalculator
from utils import in_out
from utils.in_out import pickle_from_dir

config = in_out.get_parameters()


out_columns = [
    "alpha",
    "beta",
    "gamma",
    "delta",
    "o1",
    "o2",
    "o3",
    "o4",
]


def process(results, objective_calculator):

    success_rates = objective_calculator.success_rate(results)
    # Backward compatibility
    if hasattr(results[0], "weights"):
        return np.concatenate(
            [
                np.array(
                    [
                        results[0].weights["alpha"],
                        results[0].weights["beta"],
                        results[0].weights["gamma"],
                        results[0].weights["delta"],
                    ]
                ),
                success_rates,
            ]
        )
    elif hasattr(results[0], "weight"):
        return np.concatenate(
            [
                np.array(
                    [
                        results[0].weight["alpha"],
                        results[0].weight["beta"],
                        results[0].weight["gamma"],
                        results[0].weight["delta"],
                    ]
                ),
                success_rates,
            ]
        )


def run():

    classifier = Classifier(load(config["paths"]["model"]))
    constraints = LcldConstraints(
        #config["amount_feature_index"],
        config["paths"]["features"],
        config["paths"]["constraints"],
    )
    objective_calculator = ObjectiveCalculator(
        classifier,
        constraints,
        config["threshold"],
        config["high_amount"],
        #config["amount_feature_index"]
    )

    success_rates = np.array(
        pickle_from_dir(
            config["dirs"]["attack_results"],
            handler=lambda i, x: process(x, objective_calculator),
            n_jobs=10
        )
    )

    success_rates_df = pd.DataFrame(success_rates, columns=out_columns)
    success_rates_df.to_csv(config["paths"]["objectives"], index=False)


if __name__ == "__main__":
    run()
