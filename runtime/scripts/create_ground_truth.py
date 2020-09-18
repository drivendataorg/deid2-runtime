import logging
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

ROOT_DIRECTORY = Path("/codeexecution")
DATA_DIRECTORY = ROOT_DIRECTORY / "data"

DEFAULT_SUBMISSION_FORMAT = DATA_DIRECTORY / "submission_format.csv"
DEFAULT_INCIDENTS = DATA_DIRECTORY / "incidents.csv"
DEFAULT_OUTPUT = ROOT_DIRECTORY / "ground_truth.csv"


def get_ground_truth(incidents: pd.DataFrame, submission_format: pd.DataFrame):
    # get actual counts
    logger.debug("... creating pivot table")
    counts = incidents.assign(n=1).pivot_table(
        index=["neighborhood", "year", "month"],
        columns="incident_type",
        values="n",
        aggfunc=np.sum,
        fill_value=0,
    )
    # when you pivot, you only gets rows and columns for things that were actually there --
    # the ground truth may not have all of the neighborhoods, periods, or codes we expected to see,
    # so we'll fix that by reindexing and then filling the missing values
    epsilons = submission_format.index.levels[0]
    index_for_one_epsilon = submission_format.loc[epsilons[0]].index
    columns = submission_format.columns.astype(counts.columns)
    counts = (
        counts.reindex(columns=columns, index=index_for_one_epsilon)
        .fillna(0)
        .astype(np.int32)
    )
    logger.debug(
        "... duplicating the counts for every (neighborhood, year, month) to each epsilon"
    )
    ground_truth = submission_format.copy()
    for epsilon in epsilons:
        ground_truth.loc[epsilon] = counts.values
    return ground_truth


def main(
    incident_csv: Path = DEFAULT_INCIDENTS,
    submission_format_csv: Path = DEFAULT_SUBMISSION_FORMAT,
    output_file: Optional[Path] = DEFAULT_OUTPUT,
):
    logger.info(f"reading submission format from {submission_format_csv} ...")
    submission_format = pd.read_csv(
        submission_format_csv, index_col=["epsilon", "neighborhood", "year", "month"]
    )
    logger.info(f"read dataframe with {len(submission_format):,} rows")

    logger.info(f"reading raw incident data from {incident_csv} ...")
    incidents = pd.read_csv(incident_csv, index_col=0)
    logger.info(f"read dataframe with {len(incidents):,} rows")

    logger.info("aggregating counts from raw incident data")
    ground_truth = get_ground_truth(incidents, submission_format)
    output_file = output_file or sys.stdout
    logger.info(f"writing {len(ground_truth):,} rows out to {output_file}")
    ground_truth.to_csv(output_file, index=True)


if __name__ == "__main__":
    main()
