# screenshots.R — tool page screenshots for hugo2 tools
# usage: source("static/img/tools/screenshots.R")
# requires: chromote, jsonlite
#
# Uses chromote directly (not webshot2) so SPAs/dashboards that never fire
# Page.loadEventFired don't time out. Navigate with wait_ = FALSE, sleep a
# fixed delay, then capture the viewport (1440 x 900) above-the-fold only.

librarian::shelf(chromote, jsonlite, quiet = TRUE)

out_dir <- "static/img/tools"
vwidth  <- 1440L
vheight <- 900L

take_shot <- function(slug, url, delay) {
  file <- file.path(out_dir, paste0(slug, ".png"))
  message("screenshotting ", slug, " → ", file)
  tryCatch({
    b <- chromote::ChromoteSession$new()
    on.exit(try(b$close(), silent = TRUE))

    b$Emulation$setDeviceMetricsOverride(
      width             = vwidth,
      height            = vheight,
      deviceScaleFactor = 1,
      mobile            = FALSE
    )

    b$Page$navigate(url, wait_ = FALSE)
    Sys.sleep(delay)

    img <- b$Page$captureScreenshot(
      clip = list(x = 0, y = 0, width = vwidth, height = vheight, scale = 1),
      wait_ = TRUE
    )
    writeBin(jsonlite::base64_dec(img$data), file)
  }, error = function(e) {
    message("  ERROR: ", conditionMessage(e))
  })
}

tools <- list(
  list(slug = "edna-explorer",                  url = "https://mbon.ioos.us/",                                                             delay = 12),
  list(slug = "coastwatch-obis",                url = "https://cwcgom.aoml.noaa.gov/OBIS/",                                                delay =  5),
  list(slug = "early-alert-dashboard",          url = "https://mbon-dashboards.marine.usf.edu",                                            delay = 20),
  list(slug = "pole-to-pole-atlas",             url = "https://marinebon.org/p2p/",                                                        delay =  8),
  list(slug = "sanctuary-condition-reports",    url = "https://sanctuarywatch.ioos.us",                                                    delay =  8),
  list(slug = "seascapes-viewer",               url = "https://shiny.marinebon.app/seascapes",                                             delay = 10),
  list(slug = "biotrack-portal",                url = "https://portal.atn.ioos.us/",                                                       delay = 12),
  list(slug = "infographiq",                    url = "https://marinebon.org/infographiq/",                                                delay =  5),
  list(slug = "climate-dashboard",              url = "https://noaa-onms.github.io/climate-dashboard/",                                    delay =  6),
  list(slug = "climate-dashboard-app",          url = "https://shiny.marinebon.app/nms-cc/",                                               delay = 10),
  list(slug = "seascapr",                       url = "https://shiny.marinebon.app/seascapes/",                                            delay = 10),
  list(slug = "infographic-cinms",              url = "https://noaa-onms.github.io/cinms/",                                                delay =  6),
  list(slug = "infographic-florida-keys-esr",   url = "https://noaa-iea.github.io/fk-esr-info/infographic.html",                          delay =  6),
  list(slug = "infographic-iea-alaska",         url = "https://noaa-iea.github.io/ak-info/",                                              delay =  6),
  list(slug = "infographic-ocnms",              url = "https://noaa-onms.github.io/ocnms/index.html",                                     delay =  6),
  list(slug = "storymap-fk-fwri-water-quality", url = "https://storymaps.arcgis.com/stories/52a114b2d89d4e60ac3fd75d713d90f7",            delay = 15),
  # data portals where MBON datasets live (see content/data/ + the Data landing page)
  list(slug = "obis",                           url = "https://obis.org",                                                                 delay =  8),
  list(slug = "gbif",                           url = "https://www.gbif.org",                                                             delay =  8),
  list(slug = "edi",                            url = "https://edirepository.org",                                                        delay =  6),
  list(slug = "erddap",                         url = "https://www.ncei.noaa.gov/erddap/index.html",                                      delay =  6)
)

for (p in tools) {
  take_shot(p$slug, p$url, p$delay)
}

message("done — ", length(tools), " tool screenshots in ", out_dir)
