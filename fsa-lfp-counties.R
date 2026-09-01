# update.packages(repos = "https://cran.rstudio.com/",
#                 ask = FALSE)
# 
# install.packages("pak",
#                  repos = "https://cran.rstudio.com/")
# 
# # installed.packages() |>
# #   rownames() |>
# #   pak::pkg_install(upgrade = TRUE,
# #                  ask = FALSE)
# 
# pak::pak(
#   c(
#     "arrow?source",
#     "sf?source",
#     "curl",
#     "tidyverse",
#     "archive",
#     "digest",
#     "rmapshaper", # For README example
#     "tigris" # For TopoJSON state names and README example
#   )
# )

library(magrittr)
library(tidyverse)
library(sf)
library(arrow)
library(xml2)

source("R/s3-archive.R")
s3_preflight()

s3_bucket <- Sys.getenv("S3_BUCKET", unset = "sustainable-fsa")
s3_prefix <- Sys.getenv("S3_PREFIX", unset = "fsa-lfp-counties")

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
    layer_options = c("COMPRESSION=ZSTD",
                      "COMPRESSION_LEVEL=13"),
    delete_dsn = TRUE
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


## Create a full-detail TopoJSON version, following the pattern of
## fsa-counties-dd17 and fsa-counties-dd22. Unlike those datasets, this
## version is neither simplified nor clipped to the coastline, and Alaska,
## Hawaii, and Puerto Rico stay in true position: the USDM drought statistics
## that drive LFP eligibility are tabulated against these exact polygons, so
## the TopoJSON preserves them at full resolution — only reprojected to WGS 84
## and quantized to a ~60 cm grid.

## State names are not in the FOIA release — join them from the Census,
## pinned to a vintage so nothing here floats with a tigris release.
state_names <-
  tigris::states(cb = TRUE,
                 year = 2024,
                 progress_bar = FALSE) %>%
  sf::st_drop_geometry() %>%
  dplyr::select(StateFIPS = STATEFP,
                state = NAME)

fsa_lfp_counties %>%
  dplyr::left_join(state_names) %>%
  dplyr::select(id = CountyFIPS,
                state,
                county = CountyName) %>%
  sf::st_transform("WGS84") %>%
  sf::write_sf("fsa-lfp-counties.geojson",
               delete_dsn = TRUE)

## gap-fill-area=0: these counties are not edge-matched — unioning them leaves
## 491 pinhole gaps where neighbors fail to meet. They are part of the record,
## so unlike dd17/dd22 the -clean passes must not fill them.
system(
  "
mapshaper \\
  fsa-lfp-counties.geojson \\
  -clean rewind gap-fill-area=0 \\
  -rename-layers counties \\
  -dissolve field=state copy-fields='id' + name=states \\
  -each 'id=id.slice(0,2)' target=states \\
  -clean gap-fill-area=0 target=counties,states \\
  -rename-layers counties,states target=counties,states \\
  -o format=topojson quantization=1e7 fix-geometry id-field='id' bbox target=* fsa-lfp-counties.topojson
"
)

unlink("fsa-lfp-counties.geojson")

# sf::read_sf("fsa-lfp-counties.topojson", layer = "counties") %>%
#   mapview::mapview()

# # Also identical to the NDMC Albers.gdb dataset
# sf::read_sf(
#   "/vsizip//vsicurl/https://sustainable-fsa.com/ndmc-counties-albers/Albers.gdb.zip/Albers.gdb",
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

## Publish the archive to S3 (dual-write alongside the git mirror)
s3_put(bucket = s3_bucket,
       key = paste0(s3_prefix, "/fsa-lfp-counties.parquet"),
       file = "fsa-lfp-counties.parquet",
       content_type = "application/vnd.apache.parquet",
       cache_control = "max-age=3600")

s3_put(bucket = s3_bucket,
       key = paste0(s3_prefix, "/fsa-lfp-counties.topojson"),
       file = "fsa-lfp-counties.topojson",
       ## TopoJSON is JSON. Without this, s3_put() falls back to
       ## application/octet-stream, which CloudFront will not compress.
       content_type = "application/json",
       cache_control = "max-age=3600")

s3_put(bucket = s3_bucket,
       key = paste0(s3_prefix, "/fsa-lfp-counties.xml"),
       file = "fsa-lfp-counties.xml",
       content_type = "application/xml",
       cache_control = "max-age=3600")

s3_push(bucket = s3_bucket,
        prefix = paste0(s3_prefix, "/foia"),
        local_dir = "foia",
        delete = TRUE)

s3_write_manifest(bucket = s3_bucket,
                  prefix = s3_prefix)

cf_invalidate(
  paths = c(
    paste0("/", s3_prefix, "/fsa-lfp-counties.parquet"),
    paste0("/", s3_prefix, "/fsa-lfp-counties.topojson"),
    paste0("/", s3_prefix, "/_manifest.txt")
  )
)
