from pymoo.optimize import minimize

from .venus_attack_generator import create_attack
import copy


def attack(
    index,
    initial_state,
    model,
    scaler,
    encoder,
    n_generation,
    pop_size,
    n_offsprings,
    weight,
):
    # Copying shared resources

    model = copy.deepcopy(model)
    scaler = copy.deepcopy(scaler)
    encoder = copy.deepcopy(encoder)
    weight = copy.deepcopy(weight)

    # Create attack

    problem, algorithm, termination = create_attack(
        initial_state,
        weight,
        model,
        scaler,
        encoder,
        n_generation,
        n_offsprings,
        pop_size,
    )

    # Execute attack

    result = minimize(problem, algorithm, termination, verbose=0, save_history=False,)

    return result