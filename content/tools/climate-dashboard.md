---
image: img/tools/climate-dashboard.png
links:
- label: Open dashboard
  primary: true
  url: https://noaa-onms.github.io/climate-dashboard/
- label: Source code
  url: https://github.com/noaa-onms/climate-dashboard
summary: Static flexdashboard rendering climate indicators — sea surface temperature,
  chlorophyll-a, pH, sea-level rise — for each U.S. National Marine Sanctuary.
tags:
- tool.App
- org.NationalMarineSanctuaries
- place.US
- topic.Climate-Change
- topic.Marine-Protected-Areas
title: Sanctuaries Climate Dashboard
weight: 17
aliases:
- /products/climate-dashboard/
---

A flexdashboard-based product that renders climate indicators for each National Marine Sanctuary as a static website hosted on GitHub Pages. The layout follows ecowatch.noaa.gov and supports panels for bottom temperature, sea surface temperature, pH, precipitation, and sea-level rise among others. The dashboard is regenerated on a schedule by pulling from ERDDAP and Copernicus Marine Service endpoints.

The dashboard's principal strength is durability: a static site has no runtime dependencies, no database to corrupt, and costs effectively nothing to host. For interactive exploration — swipeable maps, custom date ranges — see the companion [Climate Change for Sanctuaries](/tools/climate-dashboard-app/) Shiny application.
