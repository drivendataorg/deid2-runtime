import logging
import importlib

logging.getLogger('').setLevel(logging.INFO)

logging.info("Testing if Python packages can be loaded correctly.")

packages = [
    "fastai",
    "lightgbm",
    "mahotas",
    "cv2",  # opencv
    "pandas",
    "PIL",  # pillow
    "dotenv",
    "numpy",
    "torch",  # pytorch
    "skimage",  # scikit-image
    "sklearn",  # scikit-learn
    "scipy",
    "tensorflow",
    "torchvision",
    "xgboost",
    # ADD ADDITIONAL REQUIREMENTS BELOW HERE #

    ##########################################
]

for package in packages:
    logging.info("Testing if {} can be loaded...".format(package))
    importlib.import_module(package)

logging.info("All required packages successfully loaded.")
