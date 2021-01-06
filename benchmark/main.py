import csv
import json
from pathlib import Path

from loguru import logger
import numpy as np
import pandas as pd
from tqdm import trange
import typer

ROOT_DIRECTORY = Path("/codeexecution")
RUNTIME_DIRECTORY = ROOT_DIRECTORY / "submission"
DATA_DIRECTORY = ROOT_DIRECTORY / "data"

DEFAULT_GROUND_TRUTH = DATA_DIRECTORY / "ground_truth.csv"
DEFAULT_PARAMS = DATA_DIRECTORY / "parameters.json"
DEFAULT_OUTPUT = ROOT_DIRECTORY / "submission.csv"


def simulate_row(parameters, epsilon=None, sim_individual_id=None):
    """
    Naively create a valid row by picking random but valid values using the parameters file.
    """
    row = {}
    if epsilon is not None:
        row["epsilon"] = epsilon
    for col, d in parameters["schema"].items():
        value = 0
        if "values" in d:
            value = np.random.choice(d["values"])
        elif "min" in d:
            if "int" in d["dtype"]:
                value = np.random.randint(d["min"], d["max"])
            else:
                value = np.random.uniform(d["min"], d["max"])
        elif col in {"HHWT", "PERWT"}:
            value = np.round(np.random.exponential(100), 1)
        elif col in {"INCTOT", "INCWAGE", "INCEARN"}:
            value = int(np.random.exponential(30_000))
        row[col] = value
    if sim_individual_id is not None:
        row["sim_individual_id"] = sim_individual_id
    return row


def main(
        parameters_file: Path = DEFAULT_PARAMS,
        ground_truth_file: Path = DEFAULT_GROUND_TRUTH,
        output_file: Path = DEFAULT_OUTPUT,
        random_seed: int = 42,
):
    """
    Create synthetic data appropriate to be submitted to the Sprint 2 competition.
    """
    np.random.seed(random_seed)

    logger.info(f"reading schema from {parameters_file} ...")
    with parameters_file.open("r") as fp:
        parameters = json.load(fp)

    ########################################################################################
    # NOTE: We don't actually look at the ground truth for this baseline other than to see #
    #       how many rows are present. You must ensure your solution is differentially     #
    #       private if you are using the ground truth.                                     #
    ########################################################################################
    logger.info(f"reading ground truth from {ground_truth_file} ...")
    dtypes = {column_name: d["dtype"] for column_name, d in parameters["schema"].items()}
    ground_truth = pd.read_csv(ground_truth_file, dtype=dtypes)
    logger.info(f"... read ground truth dataframe of shape {ground_truth.shape}")

    n_rows_to_simulate_per_epsilon = len(ground_truth)
    epsilons = [run["epsilon"] for run in parameters["runs"]]
    columns = list(parameters["schema"].keys())
    headers = ["epsilon"] + columns + ["sim_individual_id"]

    # start writing the CSV with headers
    logger.info(f"writing output to {output_file}")
    with output_file.open("w", newline="") as fp:
        output = csv.DictWriter(fp, fieldnames=headers, dialect="unix")
        output.writeheader()
        n_rows = 1
        for epsilon in epsilons:
            logger.info(f"starting simulation for epsilon={epsilon}")
            for i in trange(n_rows_to_simulate_per_epsilon):
                ################################################################################
                # NOTE: Naively simulate only one row per individual (and lazily use iteration #
                #       number as the simulated individual ID).                                #
                ################################################################################
                row = simulate_row(
                    parameters, epsilon=epsilon, sim_individual_id=i
                )
                output.writerow(row)
                n_rows += 1
    logger.success(f"finished writing {n_rows} to {output_file}")

if __name__ == "__main__":
    typer.run(main)
