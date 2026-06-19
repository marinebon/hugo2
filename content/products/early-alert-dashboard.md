+++
title   = "Florida Keys NMS Alert Dashboard"
weight  = 5
image   = "img/products/early-alert-dashboard.png"
summary = "Early-warning dashboard combining satellite and buoy data to detect harmful algal blooms and anoxic conditions in the Florida Keys National Marine Sanctuary."
tags    = ["tool:dashboard", "org:nms", "region:south-fl"]
links   = [
  { label = "Open dashboard", url = "https://mbon-dashboards.marine.usf.edu", primary = true },
  { label = "Source code", url = "https://github.com/marinebon/mbon-dashboard-server" },
]
+++

The Florida Keys NMS Alert Dashboard combines satellite-derived products with near-real-time buoy observations to provide early warning of anomalous ecosystem conditions in the Florida Keys National Marine Sanctuary. It flags signals associated with harmful algal blooms and anoxic (low-oxygen) events so resource managers can respond before impacts cascade through the reef system.

The dashboard draws on VIIRS and MODIS satellite data processed by the MBON Dashboard Server — a Docker-based stack that ingests and serves products for multiple MBON observing sites, including the Florida Keys NMS, Flower Garden Banks NMS, and data layers for the Florida Fish and Wildlife Conservation Commission (FWC).

## Data products displayed

- Sea surface temperature (SST) anomalies from VIIRS and MODIS
- Chlorophyll-a concentration and bloom indices
- Colored dissolved organic matter (CDOM)
- In situ buoy records (dissolved oxygen, salinity, temperature)

## Deployment

The server stack is containerized with Docker Compose, making it reproducible and deployable by other MBON nodes. See the [GitHub repository](https://github.com/marinebon/mbon-dashboard-server) for full deployment documentation.
