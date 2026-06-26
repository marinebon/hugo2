# screenshots.R — full-page screenshots of main hugo2 pages
# requires: librarian, webshot2, chromote
# usage: source("static/img/_screenshots/screenshots.R")
# prereq: hugo server must be running on localhost:1313
#         run in terminal: hugo server

librarian::shelf(webshot2, quiet = TRUE)

base_url <- "http://localhost:1313"

pages <- list(
  
  home = "",
  network = "network",
  methods = "methods",
  papers = "papers",
  data = "data",
  tools = "tools",
  news = "news",
  about = "about",
  contact = "contact",
  events = "events",
  search = "search",
  tags = "tags"
)

out_dir <- "static/img/_screenshots"

for (slug in names(pages)) {
  path <- pages[[slug]]
  url <- paste0(base_url, "/", path)
  file <- file.path(out_dir, paste0(slug, ".png"))
  message("screenshotting ", url, " → ", file)
  webshot2::webshot(
    url = url,
    file = file,
    vwidth = 1440,
    vheight = 900,
    delay = 1.5 # allow JS (globe, etc.) to settle
  )
}

message("done — ", length(pages), " screenshots in ", out_dir)
