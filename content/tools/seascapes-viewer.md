---
image: img/tools/seascapes-viewer.png
links:
- label: Open Seascapes Viewer
  primary: true
  url: https://shiny.marinebon.app/seascapes
- label: Source code
  url: https://github.com/marinebon/seascape_app
- label: seascapeR package
  url: https://github.com/marinebon/seascapeR
summary: Interactive Shiny application for visualizing global Seascape Classes in
  time and space across U.S. National Marine Sanctuaries.
tags:
- tool.App
- org.NationalMarineSanctuaries
- place.Global
- topic.Seascapes
title: Seascapes Viewer
weight: 2
aliases:
- /products/seascapes-for-sanctuaries/
---

Seascapes are dynamic classes of water masses defined by surface properties obtained via satellite — sea surface temperature, salinity, chlorophyll-a, colored dissolved organic matter (CDOM), and others — combined with an ordination statistical process (Kavanaugh et al. 2016). Each class represents a distinct ocean habitat type that shifts in space and time as water masses move, making Seascapes a powerful proxy predictor for species distributions.

The Seascapes Viewer synchronizes an interactive map with a summarized time series for each National Marine Sanctuary. You can:

- Zoom in and out across space and time
- Click the play button to animate the full record
- Click any time point to update the map to that snapshot
- Select any U.S. National Marine Sanctuary from the left panel

The underlying data are served via ERDDAP and processed by the [seascapeR](https://github.com/marinebon/seascapeR) R package, which provides functions for fetching, analyzing, and visualizing Seascapes data across NOAA Sanctuaries and other MBON regions.

## References

Kavanaugh, M.T., Oliver, M.J., Chavez, F.P., Letelier, R.M., Muller-Karger, F.E., and Doney, S.C. (2016). Seascapes as a new vernacular for pelagic ocean monitoring, management and conservation. *ICES Journal of Marine Science* 73(7): 1839–1850. [https://doi.org/10.1093/icesjms/fsw086](https://doi.org/10.1093/icesjms/fsw086)
