+++
title   = "Sanctuaries Climate Dashboard"
weight  = 17
image   = "img/products/climate-dashboard.png"
summary = "Static flexdashboard rendering climate indicators — sea surface temperature, chlorophyll-a, pH, sea-level rise — for each U.S. National Marine Sanctuary."
tags    = ["region:us", "tool:dashboard", "org:nms", "type:instance"]
links   = [
  { label = "Open dashboard", url = "https://noaa-onms.github.io/climate-dashboard/", primary = true },
  { label = "Source code", url = "https://github.com/noaa-onms/climate-dashboard" },
]
+++

A flexdashboard-based product that renders climate indicators for each National Marine Sanctuary as a static website hosted on GitHub Pages. The layout follows ecowatch.noaa.gov and supports panels for bottom temperature, sea surface temperature, pH, precipitation, and sea-level rise among others. The dashboard is regenerated on a schedule by pulling from ERDDAP and Copernicus Marine Service endpoints.

The dashboard's principal strength is durability: a static site has no runtime dependencies, no database to corrupt, and costs effectively nothing to host. For interactive exploration — swipeable maps, custom date ranges — see the companion [Climate Change for Sanctuaries](/products/climate-dashboard-app/) Shiny application.
