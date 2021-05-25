from pathlib import Path
import joblib
import numpy as np
from tqdm import tqdm

from src.examples.botnet.botnet_constraints import BotnetConstraints
from src.examples.malware.malware_constraints import MalwareConstraints
from src.utils import Pickler, in_out, filter_initial_states
from art.utils import projection

config = in_out.get_parameters()


def apply_random_perturbation(x_init, n_repetition, mask, l2_max):
    x_perturbed = np.repeat(x_init[np.newaxis, :], n_repetition, axis=0)
    x_perturbation = np.random.random((n_repetition, mask.sum())) * 2 - 1

    x_perturbation = projection(x_perturbation, l2_max, 2)

    x_perturbed[:, mask] = x_perturbed[:, mask] + x_perturbation

    x_perturbed = np.clip(x_perturbed, 0.0, 1.0)

    return x_perturbed


def run():
    Path(config["paths"]["attack_results"]).parent.mkdir(parents=True, exist_ok=True)

    scaler = joblib.load(config["paths"]["min_max_scaler"])

    x_initial = np.load(config["paths"]["x_candidates"])
    x_initial = filter_initial_states(
        x_initial, config["initial_state_offset"], config["n_initial_state"]
    )

    l2_max = config["thresholds"]["f2"]

    x_initial_scaled = scaler.transform(x_initial)

    np.random.seed(config["seed"])

    constraints = BotnetConstraints(
        config["paths"]["features"],
        config["paths"]["constraints"],
    )
    mask = constraints.get_mutable_mask()

    iterable = x_initial_scaled
    if config["verbose"] > 0:
        iterable = tqdm(iterable, total=len(x_initial_scaled))

    x_attack_scaled = np.array(
        [
            apply_random_perturbation(x_init, config["n_repetition"], mask, l2_max)
            for x_init in iterable
        ]
    )
    shape = x_attack_scaled.shape
    x_attack_scaled = x_attack_scaled.reshape(-1, shape[2])
    x_attack = scaler.inverse_transform(x_attack_scaled)
    mask_int = constraints.get_feature_type() != "real"
    x_attack[:, mask_int] = np.floor(x_attack[:, mask_int] + 0.5)

    x_attack = x_attack.reshape(shape)
    print(x_attack.shape)
    np.save(config["paths"]["attack_results"], x_attack)


if __name__ == "__main__":
    run()
