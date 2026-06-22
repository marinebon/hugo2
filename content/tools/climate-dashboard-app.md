---
image: img/products/climate-dashboard-app.png
links:
- label: Open app
  primary: true
  url: https://shiny.marinebon.app/nms-cc/
- label: Source code
  url: https://github.com/noaa-onms/climate-dashboard-app
summary: Shiny application with a swipeable "then vs. now" map comparing climatological
  reference periods to the present for each U.S. National Marine Sanctuary.
tags:
- place.us
- type.dashboard
- org.nms
- type.instance
title: Climate Change for Sanctuaries
weight: 18
---

Extends the static [Sanctuaries Climate Dashboard](/tools/climate-dashboard/) with an interactive Shiny interface. The signature view is a swipeable map comparing climatological "then" (1985–2005 reference) to "now" (most recent day-of-year) for each sanctuary; a lower slider steps the comparison through the calendar year. Sanctuary and variable are selectable from the left-hand panel.

The application is packaged as a Docker Compose stack and runs alongside the static dashboard so each absorbs the load it's best suited for: the static site survives Shiny server downtime, while the Shiny app provides exploration where needed. The same ingestion pipeline feeds the [noaa-onms/eco-indicators](https://github.com/noaa-onms/eco-indicators) repository (Copernicus for Sanctuaries), from which derived indicators are generated at monthly cadence.
