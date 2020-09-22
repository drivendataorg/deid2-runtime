import json
from pathlib import Path

import jinja2
import requests
from loguru import logger
import typer

JINJA_TEMPLATE_URL = "https://drivendata-competition-deid2-public.s3.amazonaws.com/visualization/report.jinja2"


def main(json_report: Path, parameters: Path):
    logger.info(f"reading report from {json_report} ...")
    json_report = json.loads(json_report.read_text())

    logger.info(f"reading parameters from {parameters} ...")
    parameters = json.loads(parameters.read_text())
    # remove unnecessary clutter we don't use in the visualization
    parameters["schema"].pop("incident_type")

    logger.info(f"downloading template from {JINJA_TEMPLATE_URL}...")
    r = requests.get(JINJA_TEMPLATE_URL)
    if not r.status_code == 200:
        logger.error(f"could not download template! error {r.status_code}")
    template_text = r.content.decode("utf8")

    context = {"report": json.dumps(json_report), "parameters": json.dumps(parameters)}

    logger.info("rendering html...")
    env = jinja2.Environment()
    template = env.from_string(template_text)
    html = template.render(**context)
    typer.echo(html)


if __name__ == "__main__":
    typer.run(main)
