import numpy as np
import pickle
import json
import glob

# Using pickle


def pickle_from_file(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def pickle_from_dir(input_dir, handler=None):
    files_regex = input_dir + "/*.pickle"
    files = glob.glob(files_regex)
    obj_list = []

    for file_i, file in enumerate(files):
        with open(file, "rb") as f:
            obj = pickle.load(f)
            if handler is None:
                obj_list.append(obj)
            else:
                obj_list.append(handler(file_i, obj))
    return obj_list


def pickle_to_file(obj, path):
    with open(path, "wb") as f:
        pickle.dump(obj, f)


# Using numpy array


def load_from_file(path):
    return np.load(path)


def load_from_dir(input_dir, handler=None):
    files_regex = input_dir + "/*.npy"
    files = glob.glob(files_regex)
    obj_list = []

    for file_i, file in enumerate(files):
        obj = np.load(file)
        if handler is None:
            obj_list.append(obj)
        else:
            obj_list.append(handler(file_i, obj))
    return obj_list


def save_to_file(obj, path):
    with open(path, "wb") as f:
        np.save(f, obj)


# Using json files


def json_from_file(path):
    with open(path, "r") as f:
        return json.load(f)


def json_to_file(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f)


def json_from_dir(input_dir, handler=None):
    files_regex = input_dir + "/*.json"
    files = glob.glob(files_regex)
    obj_list = []

    for file_i, file in enumerate(files):
        with open(file, "rb") as f:
            obj = json.load(f)
            if handler is None:
                obj_list.append(obj)
            else:
                obj_list.append(handler(file_i, obj))
    return obj_list
