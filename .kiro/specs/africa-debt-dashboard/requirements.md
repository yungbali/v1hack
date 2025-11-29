# Requirements Document

## Introduction

The Africa Sovereign Debt Crisis Dashboard is an interactive web application designed to visualize the sovereign debt crisis across African nations and enable policy scenario modeling. Built for a 48-hour hackathon, the system aims to communicate complex debt data through compelling visualizations and demonstrate the tangible impact of debt restructuring policies. The dashboard targets three primary audiences: civil society organizations tracking debt transparency, journalists covering debt crises, and finance ministries modeling policy scenarios.

## Glossary

- **Dashboard**: The web application system that displays debt crisis data and enables scenario modeling
- **Heatmap**: A choropleth map visualization showing debt-to-GDP ratios across African countries
- **Simulator**: The interactive component that models debt restructuring scenarios
- **World Bank API**: The primary data source providing debt and economic indicators
- **IMF API**: The secondary data source providing GDP projections and debt forecasts
- **Debt-to-GDP Ratio**: Total public debt as a percentage of Gross Domestic Product
- **Debt Service**: Annual payments made on debt obligations (principal plus interest)
- **Fiscal Space**: Government revenue available for discretionary spending after debt obligations
- **Debt Restructuring**: Modification of debt terms including maturity extension, interest rate reduction, or principal haircut
- **Creditor**: Entity that has lent money to a government (multilateral, bilateral, or commercial)
- **Streamlit**: The Python framework used for building the web application
- **Parquet Cache**: Pre-fetched data stored locally for instant dashboard loading

## Requirements

### Requirement 1: Data Acquisition and Management

**User Story:** As a dashboard developer, I want to fetch and cache debt data from multiple sources, so that the dashboard loads instantly during demonstrations without API dependency.

#### Acceptance Criteria

1. WHEN the data fetching script executes, THE Dashboard SHALL retrieve debt indicators from the World Bank API for all 54 African countries covering years 2014-2024
2. WHEN the data fetching script executes, THE Dashboard SHALL retrieve GDP projections and debt forecasts from the IMF API for all 54 African countries
3. WHEN data is successfully fetched, THE Dashboard SHALL merge World Bank data, IMF data, and static creditor composition data into a unified dataset
4. WHEN the merged dataset is created, THE Dashboard SHALL save the data in parquet format to the cached data directory
5. WHEN the dashboard application starts, THE Dashboard SHALL load all data from the parquet cache within 3 seconds
6. WHEN data contains gaps for specific countries or years, THE Dashboard SHALL forward-fill missing values for gaps of 2 years or less
7. WHEN displaying data, THE Dashboard SHALL show a timestamp indicating the data refresh date

### Requirement 2: Overview Visualization

**User Story:** As a judge or user, I want to see the debt crisis overview immediately upon loading the dashboard, so that I understand the crisis magnitude within 30 seconds.

#### Acceptance Criteria

1. WHEN the dashboard loads, THE Dashboard SHALL display four KPI tiles showing total public debt, median debt-to-GDP ratio, count of countries in distress, and upcoming debt service obligations
2. WHEN the overview section renders, THE Dashboard SHALL display an Africa choropleth heatmap colored by debt-to-GDP ratio using a green-yellow-red scale
3. WHEN a user hovers over a country on the heatmap, THE Dashboard SHALL display the country name, debt-to-GDP ratio, and total debt amount
4. WHEN a user clicks on a country in the heatmap, THE Dashboard SHALL navigate to the detailed country simulator section for that country
5. WHEN the heatmap renders, THE Dashboard SHALL automatically highlight the three countries with highest debt-to-GDP ratios using visual emphasis
6. WHEN the overview section displays, THE Dashboard SHALL show an auto-generated insight highlighting the most significant debt crisis statistic

### Requirement 3: Debt Service Pressure Analysis

**User Story:** As a policy analyst, I want to visualize debt service payments relative to government revenue, so that I can identify countries facing severe fiscal pressure.

#### Acceptance Criteria

1. WHEN the debt service section renders, THE Dashboard SHALL display KPI tiles showing average debt service as percentage of revenue and the top 5 countries by debt service burden
2. WHEN the debt service section displays, THE Dashboard SHALL show a sortable bar chart of all countries with debt service as percentage of government revenue
3. WHEN displaying debt service bars, THE Dashboard SHALL color-code bars as red when debt service exceeds 30 percent of revenue, yellow when between 20-30 percent, and green when below 20 percent
4. WHEN a user hovers over a debt service bar, THE Dashboard SHALL display the absolute debt service amount in USD
5. WHEN the debt service section renders, THE Dashboard SHALL display a stacked area chart showing annual debt service payments from 2014-2024 segmented by creditor type (multilateral, bilateral, commercial)

### Requirement 4: Social Impact Comparison

**User Story:** As a civil society advocate, I want to compare debt service payments against social spending, so that I can communicate the human cost of debt obligations.

#### Acceptance Criteria

1. WHEN the social impact section renders, THE Dashboard SHALL display KPI tiles comparing median health spending versus debt service and education spending versus debt service
2. WHEN the social impact section displays, THE Dashboard SHALL show a grouped bar chart with three bars per country representing debt service, health spending, and education spending as percentages of GDP
3. WHEN displaying the comparison chart, THE Dashboard SHALL sort countries by debt service in descending order
4. WHEN displaying the comparison chart, THE Dashboard SHALL visually highlight countries where debt service exceeds health spending
5. WHEN a country is selected, THE Dashboard SHALL display an opportunity cost conversion panel showing how debt payments could alternatively fund schools, hospitals, vaccines, or teachers
6. WHEN calculating opportunity costs, THE Dashboard SHALL use realistic unit costs (primary school at $875k, district hospital at $11.6M, vaccine dose at $50, teacher annual salary at $8k)

### Requirement 5: Country Scenario Simulator

**User Story:** As a finance ministry official, I want to model debt restructuring scenarios for my country, so that I can evaluate policy options and their fiscal impact.

#### Acceptance Criteria

1. WHEN a user selects a country in the simulator, THE Dashboard SHALL display current state metrics including debt-to-GDP ratio, annual debt service, creditor composition, and social spending levels
2. WHEN the simulator displays, THE Dashboard SHALL provide interactive sliders for maturity extension (0-10 years), interest rate reduction (0-5 percentage points), and principal haircut (0-50 percent)
3. WHEN a user adjusts scenario parameters, THE Dashboard SHALL recalculate and display the new debt-to-GDP ratio, fiscal space freed annually, and potential social spending increase
4. WHEN scenario calculations complete, THE Dashboard SHALL update the debt service timeline chart to reflect new payment schedule
5. WHEN scenario results display, THE Dashboard SHALL show the fiscal space freed in both absolute USD terms and as equivalent social spending units
6. WHEN the simulator loads, THE Dashboard SHALL pre-populate Zambia as the default case study with current debt-to-GDP of 123 percent and debt service of $2.1 billion annually
7. WHEN calculating restructuring scenarios, THE Dashboard SHALL use standard annuity formulas to compute new annual payment obligations based on modified terms

### Requirement 6: User Interface and Filtering

**User Story:** As a dashboard user, I want to filter and navigate the data by time period and region, so that I can focus on specific countries or timeframes of interest.

#### Acceptance Criteria

1. WHEN the dashboard loads, THE Dashboard SHALL display a sidebar with filter controls including year range slider, region dropdown, and country search box
2. WHEN a user adjusts the year range slider, THE Dashboard SHALL update all visualizations to reflect only data within the selected year range
3. WHEN a user selects a region filter, THE Dashboard SHALL update all visualizations to show only countries within that region (West, East, Central, Southern, or North Africa)
4. WHEN a user searches for a country, THE Dashboard SHALL filter visualizations to highlight or isolate the selected country
5. WHEN filters are applied, THE Dashboard SHALL update all charts and metrics within 1 second

### Requirement 7: Performance and Reliability

**User Story:** As a hackathon presenter, I want the dashboard to load quickly and run reliably without internet dependency, so that my demonstration succeeds without technical failures.

#### Acceptance Criteria

1. WHEN the dashboard application starts, THE Dashboard SHALL load the initial view within 3 seconds
2. WHEN a user interacts with any component, THE Dashboard SHALL respond and update visualizations within 1 second
3. WHEN the dashboard runs, THE Dashboard SHALL load all data from local parquet cache rather than making live API calls
4. WHEN deployed to Streamlit Cloud, THE Dashboard SHALL remain accessible via public URL without authentication requirements
5. WHEN the dashboard encounters missing data, THE Dashboard SHALL display the visualization with available data and flag low-confidence data points with visual indicators

### Requirement 8: Visual Design and Styling

**User Story:** As a dashboard user, I want clear, professional visualizations with consistent styling, so that I can easily interpret the data and understand the narrative.

#### Acceptance Criteria

1. WHEN any chart renders, THE Dashboard SHALL use a consistent color palette with red for debt metrics, blue for health spending, green for education spending, and gray for GDP
2. WHEN displaying text, THE Dashboard SHALL use bold 24px fonts for section headers, 36px bold fonts for KPI values, and 14px regular fonts for body text
3. WHEN rendering the heatmap, THE Dashboard SHALL use a diverging color scale from green (low debt) through yellow (moderate debt) to red (high debt)
4. WHEN displaying KPI tiles, THE Dashboard SHALL render them with light gray backgrounds, rounded corners, and centered text
5. WHEN the dashboard loads, THE Dashboard SHALL apply custom CSS styling for consistent spacing, typography, and component appearance
