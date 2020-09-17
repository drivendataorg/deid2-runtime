from datetime import datetime
import logging
from multiprocessing import Manager
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import pyvips
from skimage.filters import threshold_otsu
from skimage.color import rgb2hed
from skimage.morphology import binary_dilation
import torch
import torchvision

# We get to see the log output for our execution, so log away!
logging.basicConfig(level=logging.INFO)

ROOT_DIRECTORY = Path(__file__).parent.expanduser().resolve()
MODEL_PATH = ROOT_DIRECTORY / "assets" / "my-awesome-model.pt"

# The images will live in a folder called '/inference/data/test_images' in the container
DATA_DIRECTORY = ROOT_DIRECTORY / "data"
IMAGE_DIRECTORY = DATA_DIRECTORY / "test_images"


def vips2numpy(buffer, format: str, width: int, height: int, bands: int):
    format_to_dtype = {
        "uchar": np.uint8,
        "char": np.int8,
        "ushort": np.uint16,
        "short": np.int16,
        "uint": np.uint32,
        "int": np.int32,
        "float": np.float32,
        "double": np.float64,
        "complex": np.complex64,
        "dpcomplex": np.complex128,
    }
    return np.ndarray(
        buffer=buffer, dtype=format_to_dtype[format], shape=[height, width, bands],
    )


def fetch_region_pyvips(
    path: Path, location: Tuple[int, int], size: Tuple[int, int], level: int = 0
):
    """Loads image regions (faster than using pyvips.Image.crop)
    """
    image = pyvips.Image.new_from_file(str(path), page=level)
    region = pyvips.Region.new(image)
    return vips2numpy(
        region.fetch(location[0], location[1], size[0], size[1]),
        image.format,
        size[0],
        size[1],
        image.bands,
    )


def get_tile_images(x, width, height):
    n_rows, row_remainer = divmod(x.shape[0], height)
    n_columns, column_remainder = divmod(x.shape[1], width)

    assert (row_remainer == 0) and (
        column_remainder == 0
    ), "Array dimensions ({x.shape}) must be divisible by tile dimensions ({height}x{width})."

    return np.lib.stride_tricks.as_strided(
        np.ravel(x),
        shape=(n_rows, n_columns, height, width),
        strides=(height * x.strides[0], width * x.strides[1], *x.strides),
        writeable=False,
    )


def get_tissue_mask(path: Path, level: int = 6):
    """Creates a binary mask of tissue/non-tissue regions by using Otsu's method on the eosin
    color channel"""
    image = pyvips.Image.new_from_file(str(path), page=level)
    array = vips2numpy(
        image.write_to_memory(), image.format, image.width, image.height, image.bands
    )
    eosin = rgb2hed(array)[..., 1]
    threshold = threshold_otsu(eosin)
    return image, binary_dilation(eosin > threshold)


def get_tissue_tile_indices(
    path: Path,
    level: int = 5,
    base_level: int = 0,
    tile_width: int = 512,
    tile_height: int = 512,
    threshold: float = 0.2,
):
    downsample_factor = 2 ** (level - base_level)
    mask_tile_width, remainder = divmod(tile_width, downsample_factor)
    assert (
        remainder == 0
    ), "Tile width {tile_width} not evenly divisible by downsample factor {downsample_factor}"
    mask_tile_height, remainder = divmod(tile_height, downsample_factor)
    assert (
        remainder == 0
    ), "Tile height {tile_height} not evenly divisible by downsample factor {downsample_factor}"

    _, mask = get_tissue_mask(path, level)
    n_columns = (mask.shape[1] - mask_tile_width) // mask_tile_width
    n_rows = (mask.shape[0] - mask_tile_height) // mask_tile_height
    tiles = get_tile_images(
        mask[: n_rows * mask_tile_height, : n_columns * mask_tile_width].copy(),
        mask_tile_width,
        mask_tile_height,
    )

    return (tiles.mean((2, 3)) > threshold).nonzero()


class WholeSlideImageDataset(torch.utils.data.Dataset):
    def __init__(
        self,
        image_directory: Path = IMAGE_DIRECTORY,
        tile_width: int = 512,
        tile_height: int = 512,
        transform=None,
    ):
        indices = []
        image_paths = []
        assert (
            image_directory.exists()
        ), "Image directory {image_directory} does not exist"
        for image_index, image_path in enumerate(image_directory.glob("*.tif")):
            image_paths.append(str(image_path))
            for row, column in zip(*get_tissue_tile_indices(image_path, base_level=1)):
                indices.append(
                    {
                        "filename": image_path.name,
                        "image_index": image_index,
                        "row": row,
                        "column": column,
                    }
                )

        logging.info(
            "Dataset of %d images (%d tiles) images from %s",
            image_index + 1,
            len(indices),
            image_directory,
        )
        manager = Manager()
        self.indices = manager.list(indices)
        self.image_paths = manager.list(image_paths)
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.transform = transform

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, index):
        index = self.indices[index]
        image = pyvips.Image.new_from_file(
            self.image_paths[index["image_index"]], page=1
        )

        tile = pyvips.Region.new(image).fetch(
            index["column"] * self.tile_width,
            index["row"] * self.tile_height,
            self.tile_width,
            self.tile_height,
        )
        tile = vips2numpy(
            tile, image.format, self.tile_width, self.tile_height, image.bands
        )

        if self.transform is not None:
            tile = self.transform(tile)

        return tile, index["filename"]


def perform_inference(batch_size: int = 16, num_dataloader_workers: int = 4):
    """This is the main function executed at runtime in the cloud environment.
    """
    logging.info("Loading model.")
    model = torch.load(str(MODEL_PATH))
    if torch.cuda.is_available():
        model = model.to("cuda")

    logging.info("Loading and processing dataset.")

    transform = torchvision.transforms.ToTensor()
    dataset = WholeSlideImageDataset(transform=transform)

    logging.info("Starting inference.")
    data_generator = torch.utils.data.DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_dataloader_workers,
    )

    # Perform (and time) inference
    inference_start = datetime.now()
    logging.info(
        "Starting inference %s (%d batches)",
        inference_start,
        len(dataset) // batch_size,
    )
    predictions = []
    for batch_index, (batch, slides) in enumerate(data_generator):
        logging.info("Batch %d %s", batch_index, datetime.now())
        if torch.cuda.is_available():
            batch = batch.to("cuda")
        with torch.no_grad():
            preds = model.forward(batch)
        for label, slide in zip(preds.argmax(1), slides):
            predictions.append({"label": int(label), "slide": slide})

    inference_end = datetime.now()
    logging.info(
        "Inference complete at %s (duration %s)",
        inference_end,
        inference_end - inference_start,
    )

    # Check our predictions are in the same order as the submission format
    predictions = pd.DataFrame(predictions)
    submission = predictions.groupby("slide").label.max()
    logging.info("Creating submission.")

    # Preallocate prediction output
    submission_format = pd.read_csv(
        DATA_DIRECTORY / "submission_format.csv", index_col="filename"
    )

    submission = submission.loc[submission_format.index]
    assert (submission.index == submission_format.index).all()

    # We want to ensure all of our data are integers
    submission = submission.astype(np.int)

    # Save out submission to root of directory
    submission.to_csv("submission.csv", index=True)
    logging.info("Submission saved.")


if __name__ == "__main__":
    perform_inference(batch_size=512, num_dataloader_workers=4)
