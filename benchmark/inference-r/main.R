library(data.table)
library(keras)
library(reticulate)
library(futile.logger)

# Set conda environment for reticulate
if ("r-gpu" %in% reticulate::conda_list()[, "name"]) {
    reticulate::use_condaenv("r-gpu")
} else {
    reticulate::use_condaenv("r-cpu")
}

futile.logger::flog.threshold(futile.logger::INFO)

# This must be set to load some images using PIL, which Keras uses.
PIL <- reticulate::import("PIL")
PIL$ImageFile$LOAD_TRUNCATED_IMAGES <- TRUE

MODEL_PATH <- "assets/my_awesome_model.h5"

# The images will live in a folder called 'data' in the container
DATA_PATH <- "data"
TEST_PATH <- "data"

NUM_LABELS <- 54

#' This is the main function executed at runtime in the cloud environment
perform_inference <- function() {
    flog.info("Loading model.")
    model <- keras::load_model_hdf5(MODEL_PATH)

    flog.info("Loading and processing metadata.")

    # Our preprocessing selects the first image for each sequence
    test_metadata_dt <- data.table::fread(file.path(DATA_PATH, "test_metadata.csv"))
    test_metadata_dt <- test_metadata_dt[order(file_name)][, .SD[1], by = "seq_id"]

    # Prepend the path to our filename since our data lives in a separate folder
    test_metadata_dt[, full_path := file.path(TEST_PATH, file_name)]

    # Load the submission format so we can match it exactly
    submission_format_dt <- data.table::fread(
        file.path(DATA_PATH, 'submission_format.csv')
    )

    data.table::setkeyv(test_metadata_dt, "seq_id")
    data.table::setkeyv(submission_format_dt, "seq_id")

    # Check our predictions are in the same order as the submission format
    stopifnot(identical(
        test_metadata_dt[, unique(seq_id)],
        submission_format_dt[, seq_id]
    ))

    flog.info("Starting inference.")

    # Instantiate test data generator
    datagen <- keras::image_data_generator(
        preprocessing_function = keras::nasnet_preprocess_input
    )

    batch_size <- 256
    test_datagen <- keras::flow_images_from_dataframe(
        dataframe = test_metadata_dt,
        x_col = "full_path",
        y_col = NULL,
        generator = datagen,
        class_mode = NULL,
        target_size = c(224, 224),
        batch_size = batch_size,
        shuffle = FALSE
    )

    # Perform (and time) inference
    steps <- ceiling(nrow(test_metadata_dt) / batch_size)
    inference_start <- Sys.time()
    preds <- keras::predict_generator(
        model,
        generator = test_datagen,
        steps = steps,
        verbose = 1,
        workers = 1
    )
    inference_stop <- Sys.time()
    flog.info(sprintf(
        "Inference complete. Took %s.",
        format(inference_stop - inference_start, digits = 7)
    ))

    flog.info("Creating submission.")

    my_submission_dt <- data.table::data.table(
        seq_id = test_metadata_dt[, seq_id]
    )
    pred_col_names <- names(submission_format_dt)[2:ncol(submission_format_dt)]
    # Remember that we are predicting at the sequence, not image level
    data.table::set(
        my_submission_dt,
        j = pred_col_names,
        value = data.table::as.data.table(preds)
    )

    # We want to ensure all of our data are floats, not integers
    for (col in pred_col_names) {
        data.table::set(
            my_submission_dt,
            j = col,
            value = my_submission_dt[, sprintf("%.15f", get(col))]
        )
    }

    # Save out submission
    submission_path <- "submission.csv"
    data.table::fwrite(my_submission_dt, submission_path)
    flog.info(sprintf("Submission saved to %s", submission_path))
}

if (!interactive()) {
    perform_inference()
}
