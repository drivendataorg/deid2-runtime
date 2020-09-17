# ============ CONFIGURATION ============
# Add conda executables to PATH
Sys.setenv(PATH=paste0("/opt/conda/envs/r-gpu/bin:", Sys.getenv("PATH")))

# Set CRAN repo
r = getOption("repos")
r["CRAN"] = "https://cloud.r-project.org/"
options(repos = r)

install.packages("remotes", quiet = T)
library(remotes)

# ============ IMAGE LIBRARIES ============
install.packages("opencv", quiet = T)
install.packages("OpenImageR", quiet = T)

remotes::install_github("bnosac/image", subdir = "image.ContourDetector", build_vignettes = F, quiet = T)
remotes::install_github("bnosac/image", subdir = "image.darknet", build_vignettes = F, quiet = T)

# Keras -- 2.2.4.1 has a preprocessing function incompatibility with current python keras
remotes::install_github("rstudio/keras", build_vignettes = F, quiet = T)
