# Useful scripts for local testing

We provide a number of scripts that you are free to use for your own local development and
testing.

**You aren't required to use any of these scripts** but they carry out some routine
tasks, so here are a few examples of what you might like to use them for:

- Validating a submission you create with your own code.
- Scoring a submission you create with your own code using the custom metric.

Some of these scripts by default look for data in the locations expected to be mounted within
the Docker container, but we give example invocations of each that you can use locally assuming
you have installed the requirements expected within the container
(see [runtime/py-cpu.yml](runtime/py-cpu.yml) or the simplified [requirements.txt](requirements.txt)
in this dir with a Python 3.8 environment).

(If you see us refer to `/tmp` in any of the invocations below, that means we expect you to
have used one of these scripts to create that file.)

---

## `benchmark/main.py`


This script will create a properly formatted submission, albeit one that is totally random.
It does so using only the `parameters.json` file, meaning that for the purposes of
differential privacy it has not "looked" at the ground truth data at all. (We still provide
an example of loading the ground truth into memory to act as a starting point for solutions
that will use the data.)

### Usage

```
Usage: main.py [OPTIONS]

  Create synthetic data appropriate to be submitted to the Sprint 2
  competition.

Options:
  --parameters-file PATH          [default:
                                  /codeexecution/data/parameters.json]

  --ground-truth-file PATH        [default:
                                  /codeexecution/data/ground_truth.csv]

  --output-file PATH              [default: /codeexecution/submission.csv]
  --random-seed INTEGER           [default: 42]

  --help                          Show this message and exit.
```

### Example for local use 

```
python benchmark/main.py \
  --parameters-file data/parameters.json \
  --ground-truth-file data/ground_truth.csv \
  --output-file /tmp/submission.csv
``` 

---

## `metric.py`

This script will validate and then score a submission, providing warnings if bias penalties
are applied. By default, this will run in serial using a single process but you may wish to pass
``--processes 4`` (or as many CPUs as you have instead of 4) to greatly speed up scoring.

### Usage

```
Usage: metric.py [OPTIONS] GROUND_TRUTH_CSV SUBMISSION_CSV

  Given the ground truth and a valid submission, compute the k-marginal
  score which the user would receive.

Arguments:
  GROUND_TRUTH_CSV  [required]
  SUBMISSION_CSV    [required]

Options:
  --k INTEGER                     Number of columns (in addition to PUMA and
                                  YEAR) to marginalize on  [default: 2]

  --n-permutations INTEGER        Number of different permutations of columns
                                  to average  [default: 50]

  --bias-penalty-cutoff INTEGER   Absolute difference in PUMA-YEAR counts
                                  permitted before applying bias penalty
                                  [default: 250]

  --parameters-json PATH          Path to parameters.json; if provided,
                                  validates the submission using the schema

  --processes INTEGER             Number of parallel processes to run
  --verbose / --no-verbose        [default: True]

  --help                          Show this message and exit.

```

### Example for local use

```
python runtime/scripts/metric.py \
  --verbose \
  --processes 4 \
  --parameters-json data/parameters.json \
  data/ground_truth.csv /tmp/submission.csv 
```