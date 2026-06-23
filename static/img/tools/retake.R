# retake.R — retry slow/broken tool screenshots
# usage: source("static/img/tools/retake.R")
#
# All shots use cliprect = "viewport" (1440 x 900) — above-the-fold only,
# consistent with screenshots.R. Adjust delay per tool as needed.

librarian::shelf(webshot2, quiet = TRUE)

out_dir <- "static/img/tools"

retakes <- list(
  list(slug = "early-alert-dashboard",          url = "https://mbon-dashboards.marine.usf.edu",                                            delay =  20),
  list(slug = "storymap-fk-fwri-water-quality", url = "https://storymaps.arcgis.com/stories/52a114b2d89d4e60ac3fd75d713d90f7",            delay =  15),
  list(slug = "pole-to-pole-atlas",             url = "https://marinebon.org/p2p/",                                                        delay =   8),
  list(slug = "seascapes-viewer",               url = "https://shiny.marinebon.app/seascapes",                                             delay = 120),
  list(slug = "climate-dashboard-app",          url = "https://shiny.marinebon.app/nms-cc/",                                               delay = 120),
  list(slug = "biotrack-portal",                url = "https://portal.atn.ioos.us/",                                                       delay = 120)
)

for (p in retakes) {
  file <- file.path(out_dir, paste0(p$slug, ".png"))
  message("screenshotting ", p$slug, " (delay=", p$delay, "s) ...")
  tryCatch(
    webshot2::webshot(
      url      = p$url,
      file     = file,
      vwidth   = 1440,
      vheight  = 900,
      delay    = p$delay,
      cliprect = "viewport"
    ),
    error = function(e) message("  ERROR: ", conditionMessage(e))
  )
  message("  done → ", file)
}

message("retakes complete")
