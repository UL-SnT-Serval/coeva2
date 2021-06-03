import warnings
from src.attacks.moeva2.constraints_only_problem import ConstraintsOnlyProblem
from src.attacks.moeva2.constraints_problem import ConstraintsProblem
from src.examples.botnet.botnet_constraints import BotnetConstraints
from pathlib import Path
import numpy as np

from src.utils import Pickler, in_out, filter_initial_states
from src.attacks.moeva2.moeva2 import Moeva2
from datetime import datetime

warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=RuntimeWarning)

config = in_out.get_parameters()


def run():
    Path(config["paths"]["attack_results"]).parent.mkdir(parents=True, exist_ok=True)

    save_history = True
    if "save_history" in config:
        save_history = config["save_history"]

    # ----- Load and create necessary objects

    X_initial_states = np.load(config["paths"]["x_candidates"])
    X_initial_states = filter_initial_states(
        X_initial_states, config["initial_state_offset"], config["n_initial_state"]
    )

    constraints = BotnetConstraints(
        config["paths"]["features"],
        config["paths"]["constraints"],
    )

    # ----- Check constraints

    constraints.check_constraints_error(X_initial_states)

    # ----- Copy the initial states n_repetition times
    X_initial_states = np.repeat(X_initial_states, config["n_repetition"], axis=0)

    # Initial state loop (threaded)

    moeva2 = Moeva2(
        None,
        constraints,
        l2_ball_size=config["l2_ball_size"],
        problem_class=ConstraintsProblem,
        n_gen=config["n_gen"],
        n_pop=config["n_pop"],
        n_offsprings=config["n_offsprings"],
        scale_objectives=True,
        save_history=save_history,
        seed=config["seed"],
        n_jobs=config["n_jobs"],
        verbose=1,
    )
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)

    efficient_results = moeva2.generate(X_initial_states, 1)
    Pickler.save_to_file(efficient_results, config["paths"]["attack_results"])

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)


if __name__ == "__main__":
    run()