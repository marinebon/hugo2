+++
title = "{{ replace .Name "-" " " | title }}"
weight = 99
image = "img/photos/ocean-blue.jpg"
summary = "One-sentence summary shown on the product card."
# Facet tags drive the filter on /products. Use values from data/product_filters.yaml.
tags = ["region:global", "type:tool"]
links = [
  { label = "Open product", url = "#", primary = true },
  { label = "Documentation", url = "#" },
]
+++

Full description of the product, screenshots, and links to the live tool,
the data source (OBIS/ERDDAP), and related publications.
