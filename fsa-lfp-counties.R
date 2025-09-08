# update.packages(repos = "https://cran.rstudio.com/",
#                 ask = FALSE)

install.packages("pak",
                 repos = "https://cran.rstudio.com/")

# installed.packages() |>
#   rownames() |>
#   pak::pkg_install(upgrade = TRUE,
#                  ask = FALSE)

pak::pak(
  c(
    "arrow?source",
    "sf?source",
    "curl",
    "tidyverse",
    "archive",
    "digest",
    "rmapshaper", # For README example
    "tigris" # For README example
  )
)

library(magrittr)
library(tidyverse)
library(sf)
library(arrow)
library(xml2)

sf::sf_use_s2(TRUE)

## Data delivered via the FOIA office included two zipped archives in a Box folder:
## USDM_Counties_data.gdb.zip and scripts.zip
## This code extracts both, and writes them as a Parquet and associated metadata.

# Extract outer Zip to a temporary directory
archive::archive_extract(
  archive = file.path("foia",
                      "2025-FSA-08431-F Bocinsky",
                      "25-08431-F - Bocinsky (3 Dec 25).zip"),
  dir = tempdir()
)

#Use VSIZIP to read paths inside nested zip archive
fsa_lfp_counties_file <-
  file.path(
    "/vsizip",
    tempdir(),
    "25-08431-F - Bocinsky (3 Dec 25)",
    "USDM_Counties_data.gdb.zip",
    "USDM_Counties_data.gdb")

fsa_lfp_counties <-
  fsa_lfp_counties_file %>%
  sf::read_sf() %>%
  dplyr::arrange(CountyFIPS) %T>%
  sf::write_sf(
    "fsa-lfp-counties.parquet",
    driver = "Parquet",
    layer_options = c("COMPRESSION=BROTLI",
                      "GEOMETRY_ENCODING=GEOARROW",
                      "WRITE_COVERING_BBOX=NO"),
  )

sf::gdal_utils(util = "vectortranslate",
               source = fsa_lfp_counties_file,
               destination = "fsa-lfp-counties.gml",
               options = 
                 c("-f", "GML",
                   "-sql", "GetLayerMetadata counties_detailed_total_2021"
                 )
)

xml2::read_xml("fsa-lfp-counties.gml") %>%
  xml2::xml_text(trim = TRUE) %>%
  xml2::read_xml() %>%
  xml2::write_xml("fsa-lfp-counties.xml")

unlink(
  c(
    "fsa-lfp-counties.gml",
    "fsa-lfp-counties.xsd"
  )
)

# Extract and rename the scripts
archive::archive_extract(
  file.path(
    tempdir(),
    "25-08431-F - Bocinsky (3 Dec 25)",
    "scripts.zip"
  )
)

file.rename(from = c("usdm_data.py",
                     "usdm_tabulatestats.py"),
            to = c(
              "fsa-lfp-counties-usdm_data.py",
              "fsa-lfp-counties-usdm_tabulatestats.py"
            ))


# # Also identical to the NDMC Albers.gdb dataset
# sf::read_sf(
#   "/vsizip//vsicurl/https://sustainable-fsa.github.io/ndmc-counties-albers/Albers.gdb.zip/Albers.gdb",
#   layer = "counties_detailed_total_2021") %>%
#   dplyr::select(
#     names(fsa_lfp_counties_file %>%
#             sf::read_sf())
#   ) %>%
#   dplyr::arrange(CountyFIPS) %>%
#   tibble::as_tibble() %>%
#   dplyr::rename(Albers = Shape) %>%
#     dplyr::select(CountyFIPS, Albers) %>%
#   dplyr::left_join(
#     fsa_lfp_counties %>%
#       dplyr::arrange(CountyFIPS) %>%
#       tibble::as_tibble() %>%
#       dplyr::rename(FOIA = Shape) %>%
#       dplyr::select(CountyFIPS, FOIA)
#   ) %>%
#   dplyr::rowwise() %>%
#   dplyr::filter(!identical(Albers,FOIA))

# Knit the readme
rmarkdown::render("README.Rmd")
