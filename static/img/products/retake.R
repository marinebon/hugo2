# retake.R — retry slow/broken product screenshots
# usage: source("static/img/products/retake.R")

librarian::shelf(webshot2, quiet = TRUE)

out_dir <- "static/img/products"

retakes <- list(
  list(slug = "pole-to-pole-atlas",   url = "https://marinebon.org/p2p/",                delay = 8),
  list(slug = "seascapes-viewer",     url = "https://shiny.marinebon.app/seascapes",     delay = 120),
  list(slug = "climate-dashboard-app",url = "https://shiny.marinebon.app/nms-cc/",       delay = 120),
  list(slug = "biotrack-portal",      url = "https://portal.atn.ioos.us/",               delay = 120)
)

for (p in retakes) {
  file <- file.path(out_dir, paste0(p$slug, ".png"))
  message("screenshotting ", p$slug, " (delay=", p$delay, "s) ...")
  tryCatch(
    webshot2::webshot(
      url     = p$url,
      file    = file,
      vwidth  = 1440,
      vheight = 900,
      delay   = p$delay,
      cliprect = NULL
    ),
    error = function(e) message("  ERROR: ", conditionMessage(e))
  )
  message("  done → ", file)
}

message("retakes complete")
