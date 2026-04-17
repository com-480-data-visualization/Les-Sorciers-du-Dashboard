<div align="center">

# **Milestone 2: Visualizing 30 Years of Global Commodity Trade**


## **Team members**

Coralie Banuls
Jason  
Jaime Lopez  
Lucas Martiniano

<br>

17/04/2025

</div>

The goal is to visualize and analyze the trade relations between different countries and study the reflection in world trade of different historical events. We'll break it in the following points:

## Project breakdown

### Page 1: Global Map - Country Pop-Up

#### Sketch
We will implement a 3D interactive globe with clickable countries. Inspired by the navigation of Google Earth, this interface allows users to select individual nations to trigger a contextual dashboard (pop-up). This detailed view provides a comprehensive trade profile, including:

* **National Identity & Snapshot:** Country flag and name.
* **Trade Portfolio:** A breakdown of the Top 3 Exports and Imports for the most recent recorded year.
* **The Trade Balance** (calculated as a 10-year rolling average of Exports minus Imports) to visualize structural deficits or surpluses.
* **Dual-Axis Temporal Analysis:** Interactive line charts showing the evolution of Trade Value (USD) versus Trade Weight (kg) over the last decade.
* **Ranked Granularity:** A dynamic list of the Top 10 Export Categories per year, allowing for deep dives into specific commodity shifts.

![Sketch of the 3D global map and country pop-up dashboard](page%201%20sketch.png)

#### Relevant Lectures
* **Lecture 4.2 (D3.js):** Essential for drawing the geographical map, line charts, and binding your dataset to the DOM elements.
* **Lecture 5.1 (Interaction):** Covers the "Details on Demand" concept (the pop-up dashboard) and "Select" interactions (clicking a country).
* **Lecture 5.2 (More interactive D3):** Needed for setting up the scales for the dual-axis temporal analysis.

### Page 2: Global Map - Commodity Export

#### Sketch
We will build an interactive 3D global dashboard where users can visualize the export hierarchy of various commodities. The map dynamically re-colors nations based on user-selected criteria (material, year, and metric (value vs. weight)) providing an intuitive overview of which nations act as the primary engines of global trade.

![Sketch of the 3D global map with the commodity export visualisation](page%202%20sketch.png)

#### Relevant Lectures
* **Lecture 6.1 (Perception, Color):** Crucial for selecting the correct color mapping (e.g., sequential vs. diverging scales) to ensure users can accurately interpret the differences in export volumes across nations.
* **Lecture 6.2 (Mark & Channels):** Helps justify how to encode the chosen metrics (Value vs. Weight) onto the map visually.
* **Lecture 5.2 (More interactive D3):** Essential for dynamically updating the D3 color scales (d3.scaleLinear or sequential scales) on the fly as the user changes their filter criteria.

## Page 3: Data Analysis Dashboard (over time) - Extra Idea

#### Sketch
We will implement a page that lets the user explore global trades for each year, selected via a big horizontal slider. When you pick a specific year using the slider, all the charts and maps on the page instantly update to show what the world's trades looked like at that time.

![Sketch of the data analysis dashboard over time](page%203%20sketch.png)

Key visualisations will include:
* Top 10 biggest exporters by weight/value.
* Top 10 most exported commodity.
* A treemap showing the market share of different commodity categories (Technology, Agriculture, Fossil Fuels).
* Pop-ups alerts of big historical events that explain sudden changes.

#### Relevant Lectures
* **Lecture 5.1 (Interaction):** Covers linked views and the theory behind filtering data over time.
* **Lecture 4.2 (D3.js):** Covers the specific hierarchical layouts needed to generate the Treemap.
* **Lecture 7.1 (Designing Viz) & 7.2 (Do's and Don'ts):** Critical for arranging a complex, multi-chart dashboard without clutter ("chartjunk"), ensuring graphical integrity, and properly formatting the historical event annotations.

## Tools
Here we present the tools that will be used to render the visualizations of our project. They are presented together as they are shared across multiple of them:

* **Javascript Framework - Vue, Nuxt:** We decided to build our website leveraging Nuxt and Vue as it made it easier to modularize all of the complex visualizations we are trying to do.
* **Map library - Mapbox:** Provides easy interactive visuals for a world globe.
* **Charts and rendering - svg/d3:** A combination of basic svg for easy plots and d3 for more complicated visuals.
* **Styling - vanilla css:** Right now we are only planning to use vanilla css as our styling needs are fairly basic. If time allows we will switch to use tailwind css to add more complex styles.

## MVP

Our MVP is hosted at the following link: 
*[GeoFlux](https://geoflux-delta.vercel.app/)*

![Current MVP implementation - world map](page%201%20mvp%20world%20map.png)

![Current MVP implementation - popup](page%201%20mvp%20popup.png)