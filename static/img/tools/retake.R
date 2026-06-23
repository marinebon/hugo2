# retake.R — retry slow/broken tool screenshots
# usage: source("static/img/tools/retake.R")
#
# Uses chromote directly instead of webshot2. webshot2 blocks until
# Page.loadEventFired, which SPAs and Shiny apps never fire — causing
# timeouts. Here we navigate with wait_ = FALSE (fire-and-forget), sleep
# a fixed delay while Chrome renders, then capture the viewport.

librarian::shelf(chromote, jsonlite, quiet = TRUE)

out_dir <- "static/img/tools"
vwidth <- 1440L
vheight <- 900L

take_shot <- function(slug, url, delay) {
  file <- file.path(out_dir, paste0(slug, ".png"))
  message("screenshotting ", slug, " (delay=", delay, "s) ...")
  tryCatch(
    {
      b <- chromote::ChromoteSession$new()
      on.exit(try(b$close(), silent = TRUE))

      # set viewport — ChromoteSession$new() doesn't accept width/height
      b$Emulation$setDeviceMetricsOverride(
        width = vwidth,
        height = vheight,
        deviceScaleFactor = 1,
        mobile = FALSE
      )

      # navigate without waiting for Page.loadEventFired
      b$Page$navigate(url, wait_ = FALSE)
      Sys.sleep(delay)

      # capture viewport (not full page)
      img <- b$Page$captureScreenshot(
        clip = list(x = 0, y = 0, width = vwidth, height = vheight, scale = 1),
        wait_ = TRUE
      )
      writeBin(jsonlite::base64_dec(img$data), file)
      message("  saved → ", file)
    },
    error = function(e) {
      message("  ERROR: ", conditionMessage(e))
    }
  )
}

retakes <- list(
  list(
    slug = "storymap-fk-fwri-water-quality",
    url = "https://storymaps.arcgis.com/stories/52a114b2d89d4e60ac3fd75d713d90f7",
    delay = 240
  ),
  list(
    slug = "early-alert-dashboard",
    url = "https://mbon-dashboards.marine.usf.edu",
    delay = 20
  ),
  list(
    slug = "pole-to-pole-atlas",
    url = "https://marinebon.org/p2p/",
    delay = 8
  ),
  list(
    slug = "seascapes-viewer",
    url = "https://shiny.marinebon.app/seascapes",
    delay = 120
  ),
  list(
    slug = "climate-dashboard-app",
    url = "https://shiny.marinebon.app/nms-cc/",
    delay = 120
  ),
  list(
    slug = "biotrack-portal",
    url = "https://portal.atn.ioos.us/",
    delay = 120
  )
)

for (p in retakes) {
  take_shot(p$slug, p$url, p$delay)
}

message("retakes complete")
