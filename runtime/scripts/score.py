import json
import logging
from pathlib import Path

import pandas as pd

from metric import Deid2Metric
from create_ground_truth import get_ground_truth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

INDEX_COLS = ["epsilon", "neighborhood", "year", "month"]

ROOT_DIRECTORY = Path("/codeexecution")
DATA_DIRECTORY = ROOT_DIRECTORY / "data"

DEFAULT_INCIDENTS = DATA_DIRECTORY / "incidents.csv"
DEFAULT_GROUND_TRUTH = DATA_DIRECTORY / "ground_truth.csv"
DEFAULT_SUBMISSION = ROOT_DIRECTORY / "submission.csv"


def main(
    incidents_path: Path = DEFAULT_INCIDENTS,
    submission_path: Path = DEFAULT_SUBMISSION,
    json_report: bool = False,
):
    logger.info(f"reading incidents from {incidents_path} ...")
    incidents = pd.read_csv(incidents_path, index_col=0)

    logger.info(f"reading submission from {submission_path} ...")
    submission = pd.read_csv(submission_path, index_col=INDEX_COLS)
    logger.info(f"read dataframe with {len(submission):,} rows")

    logger.info("computing ground truth ...")
    ground_truth = get_ground_truth(incidents, submission)
    logger.info(f"read dataframe with {len(ground_truth):,} rows")

    scorer = Deid2Metric()
    overall_score, row_scores = scorer.score(
        ground_truth.values, submission.values, return_individual_scores=True
    )
    logger.info(f"OVERALL SCORE: {overall_score}")

    if json_report:
        row_outcomes = []
        for idx, score in zip(submission.index, row_scores):
            epsilon, neighborhood, year, month = idx
            row_outcomes.append(
                {
                    "epsilon": epsilon,
                    "neighborhood": neighborhood,
                    "year": year,
                    "month": month,
                    "score": score,
                }
            )
        result = {"score": overall_score, "details": row_outcomes}
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
