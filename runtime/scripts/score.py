import json
from pathlib import Path

from loguru import logger
import pandas as pd
import pytest
import typer

import metric

INDEX_COLS = ["epsilon", "neighborhood", "year", "month"]


def main(
    submission: Path, ground_truth: Path, json_report: bool = False,
):
    logger.info(f"reading submission from {submission} ...")
    submission_format = pd.read_csv(submission, index_col=INDEX_COLS)
    logger.info(f"read dataframe with {len(submission_format):,} rows")

    logger.info(f"reading ground truth from {ground_truth} ...")
    ground_truth = pd.read_csv(ground_truth, index_col=INDEX_COLS)
    logger.info(f"read dataframe with {len(ground_truth):,} rows")

    scorer = metric.Deid2Metric()
    overall_score, row_scores = scorer.score(
        ground_truth.values, submission_format.values, return_individual_scores=True
    )
    logger.success(f"OVERALL SCORE: {overall_score}")

    if json_report:
        row_outcomes = []
        for idx, score in zip(submission_format.index, row_scores):
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
        typer.echo(json.dumps(result, indent=2))


if __name__ == "__main__":
    typer.run(main)
