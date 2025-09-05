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
    "tigris",
    "rmapshaper"
  )
)

library(magrittr)
library(tidyverse)
library(sf)
library(arrow)
library(xml2)

sf::sf_use_s2(TRUE)

## Data delivered via the FOIA office included two zipped archives in a Box folder:
## USDMcounties.gdb - file 1.zip and USDMcounties.gdb - file 2.zip
## This code demonstrates they are identical.

#Use VSIZIP to read paths inside nested zip archive
fsa_lfp_counties_files <- 
  list(
    file1 =
      file.path("/vsizip",
                "foia",
                "2025-FSA-08431-F Bocinsky",
                "25-08431-F - Bocinsky (3 Dec 25).zip",
                "25-08431-F - Bocinsky (3 Dec 25)",
                "USDMcounties.gdb - file 1.zip"),
    file2 =
      file.path("/vsizip",
                "foia",
                "2025-FSA-08431-F Bocinsky",
                "25-08431-F - Bocinsky (3 Dec 25).zip",
                "25-08431-F - Bocinsky (3 Dec 25)",
                "USDMcounties.gdb - file 2.zip")
  ) %>%
  purrr::map(
    \(x){
      file.path("/vsizip",
                x,
                "USDMcounties.gdb"
      )
    }
  )

fsa_lfp_counties <-
  fsa_lfp_counties_files %>%
  purrr::map(
    \(x){
      sf::read_sf(
        x
      )
    }
  )

# They are identical
identical(fsa_lfp_counties$file1,
          fsa_lfp_counties$file2)

# So, write the first one to a parquet file
fsa_lfp_counties %$%
  file1 %>%
  sf::write_sf(
    "fsa-lfp-counties.parquet",
    driver = "Parquet",
    layer_options = c("COMPRESSION=BROTLI",
                      "GEOMETRY_ENCODING=GEOARROW",
                      "WRITE_COVERING_BBOX=NO"),
  )

sf::gdal_utils(util = "vectortranslate",
               source = fsa_lfp_counties_files$file1,
               destination = "fsa-lfp-counties.gml",
               options = c("-f", "GML",
                           "-sql", "GetLayerMetadata counties_detailed_all_2021"
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

# # Also identical to the NDMC Albers.gdb dataset
# sf::read_sf(
#   "/vsizip//vsicurl/https://sustainable-fsa.github.io/ndmc-counties-albers/Albers.gdb.zip/Albers.gdb", 
#   layer = "counties_detailed_all_2021") %>%
#   dplyr::select(
#     names(fsa_lfp_counties$file1)
#     ) %>%
#   identical(fsa_lfp_counties$file1)

# Knit the readme
rmarkdown::render("README.Rmd")
