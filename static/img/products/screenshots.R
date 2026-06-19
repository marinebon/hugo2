# screenshots.R — product page screenshots for hugo2 products
# usage: source("static/img/products/screenshots.R")
# requires: librarian, webshot2, chromote

librarian::shelf(webshot2, quiet = TRUE)

out_dir <- "static/img/products"

products <- list(
  list(slug = "edna-explorer",              url = "https://mbon.ioos.us/",                                                               delay = 12),
  list(slug = "coastwatch-obis",            url = "https://cwcgom.aoml.noaa.gov/OBIS/",                                                  delay = 5),
  list(slug = "early-alert-dashboard",      url = "https://mbon-dashboards.marine.usf.edu",                                              delay = 8),
  list(slug = "pole-to-pole-atlas",         url = "https://marinebon.org/p2p/",                                                          delay = 8),
  list(slug = "sanctuary-condition-reports",url = "https://sanctuarywatch.ioos.us",                                                      delay = 8),
  list(slug = "seascapes-viewer",           url = "https://shiny.marinebon.app/seascapes",                                               delay = 10),
  list(slug = "biotrack-portal",            url = "https://portal.atn.ioos.us/",                                                         delay = 12),
  list(slug = "infographiq",               url = "https://marinebon.org/infographiq/",                                                   delay = 5),
  list(slug = "climate-dashboard",          url = "https://noaa-onms.github.io/climate-dashboard/",                                      delay = 6),
  list(slug = "climate-dashboard-app",      url = "https://shiny.marinebon.app/nms-cc/",                                                  delay = 10),
  list(slug = "seascapr",                   url = "https://shiny.marinebon.app/seascapes/",                                               delay = 10),
  list(slug = "infographic-cinms",          url = "https://noaa-onms.github.io/cinms/",                                                   delay = 6),
  list(slug = "infographic-florida-keys-esr",url = "https://noaa-iea.github.io/fk-esr-info/infographic.html",                            delay = 6),
  list(slug = "infographic-iea-alaska",     url = "https://noaa-iea.github.io/ak-info/",                                                  delay = 6),
  list(slug = "infographic-ocnms",          url = "https://noaa-onms.github.io/ocnms/index.html",                                         delay = 6),
  list(slug = "storymap-fk-fwri-water-quality", url = "https://storymaps.arcgis.com/stories/52a114b2d89d4e60ac3fd75d713d90f7",           delay = 120)
)

for (p in products) {
  file <- file.path(out_dir, paste0(p$slug, ".png"))
  message("screenshotting ", p$slug, " → ", file)
  tryCatch(
    webshot2::webshot(
      url    = p$url,
      file   = file,
      vwidth = 1440,
      vheight = 900,
      delay  = p$delay,
      cliprect = NULL
    ),
    error = function(e) message("  ERROR: ", conditionMessage(e))
  )
}

message("done — ", length(products), " product screenshots in ", out_dir)
