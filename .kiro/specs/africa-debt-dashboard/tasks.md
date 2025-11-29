# Implementation Plan

**Note**: This dashboard is adapted from the design mockup in `generated-page.html`. The implementation should match the visual design, layout, and user experience shown in that mockup while using Streamlit as the framework.

- [x] 1. Set up project structure and dependencies
  - Create directory structure (data/, components/, utils/, assets/)
  - Create requirements.txt with all dependencies (streamlit, pandas, numpy, plotly, requests, hypothesis, pytest)
  - Create constants.py with African country codes, regions, colors, unit costs, and thresholds
  - _Requirements: 1.1, 1.2, 8.1_

- [x] 2. Create main Streamlit app structure with custom styling
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 2.1 Create app.py with page configuration and custom CSS injection
  - Set up Streamlit page config (wide layout, page title, icon)
  - Load and inject custom CSS from assets/style.css to match design mockup
  - Create sidebar with navigation matching the HTML design
  - Add risk bands legend in sidebar
  - _Requirements: 8.1, 8.2, 8.4, 8.5_

- [x] 2.2 Create top bar with global filters
  - Implement region selector dropdown (matching design)
  - Implement year range selector (2014-2024)
  - Add country search box
  - Style filters to match the mockup design
  - _Requirements: 6.1, 8.5_

- [x] 2.3 Create hero section with title and metadata cards
  - Display dashboard title and description
  - Create 2x2 grid of metadata cards (Scope, Users, Focus, Status)
  - Match the styling from the HTML mockup
  - _Requirements: 8.2, 8.5_

- [ ] 3. Implement data fetching and caching system
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.6, 1.7_

- [x] 3.1 Create World Bank API client in utils/api_client.py
  - Write `fetch_world_bank_data()` function to retrieve indicators for all 54 countries
  - Implement retry logic with exponential backoff for API failures
  - Parse JSON responses into pandas DataFrame
  - _Requirements: 1.1_

- [ ]* 3.2 Write property test for API data completeness
  - **Property 1: API Data Completeness**
  - **Validates: Requirements 1.1, 1.2**

- [x] 3.3 Create IMF API client in utils/api_client.py
  - Write `fetch_imf_data()` function to retrieve GDP projections and debt forecasts
  - Handle IMF API response format differences from World Bank
  - _Requirements: 1.2_

- [x] 3.4 Create data fetching orchestrator in data/fetch_data.py
  - Write `fetch_all_data()` function that calls both API clients
  - Implement data merging logic to combine World Bank, IMF, and static creditor data
  - Use outer joins to preserve all country data
  - Handle duplicate keys by preferring most recent data
  - _Requirements: 1.1, 1.2, 1.3_

- [ ]* 3.5 Write property test for data merge
  - **Property 2: Data Merge Preserves Information**
  - **Validates: Requirements 1.3**

- [x] 3.6 Implement parquet caching in data/fetch_data.py
  - Save merged dataset to data/cached/dashboard_data.parquet
  - Add timestamp metadata for data refresh date
  - _Requirements: 1.4, 1.7_

- [ ]* 3.7 Write property test for parquet round-trip
  - **Property 3: Parquet Round-Trip Preserves Data**
  - **Validates: Requirements 1.4**

- [x] 3.8 Implement forward-fill for missing data in data/process_data.py
  - Write function to fill gaps of 2 years or less
  - Leave larger gaps as null values
  - _Requirements: 1.6_

- [ ]* 3.9 Write property test for forward-fill gap limits
  - **Property 4: Forward-Fill Respects Gap Limits**
  - **Validates: Requirements 1.6**

- [x] 3.10 Create static creditor data CSV
  - Research and compile creditor composition data for African countries
  - Include columns: country_code, creditor_multilateral_pct, creditor_bilateral_pct, creditor_commercial_pct, avg_interest_rate, avg_maturity_years
  - Save as data/creditor_data.csv
  - _Requirements: 1.3_

- [ ] 4. Implement calculation utilities
  - _Requirements: 3.1, 4.5, 5.3, 5.7_

- [x] 4.1 Create debt service pressure calculation in utils/calculations.py
  - Write `calculate_debt_service_pressure()` function
  - Formula: (debt_service_usd / (gdp_usd * revenue_pct_gdp / 100)) * 100
  - _Requirements: 3.1_

- [x] 4.2 Create opportunity cost calculator in utils/calculations.py
  - Write `calculate_opportunity_cost()` function
  - Support unit types: school, hospital, vaccine_dose, teacher
  - Return integer division of debt service by unit cost
  - _Requirements: 4.5_

- [ ]* 4.3 Write property test for opportunity cost calculations
  - **Property 12: Opportunity Cost Calculations**
  - **Validates: Requirements 4.5**

- [x] 4.4 Create annuity payment calculator in utils/calculations.py
  - Write `calculate_annuity_payment()` function using standard formula
  - Handle edge cases: zero interest rate, zero periods
  - _Requirements: 5.7_

- [ ]* 4.5 Write property test for annuity formula correctness
  - **Property 14: Annuity Formula Correctness**
  - **Validates: Requirements 5.7**

- [x] 4.6 Create restructuring scenario calculator in utils/calculations.py
  - Write `calculate_restructuring_impact()` function
  - Calculate new annual payment, fiscal space freed, new debt-to-GDP
  - Apply haircut, maturity extension, and interest rate reduction
  - _Requirements: 5.3_

- [ ]* 4.7 Write property test for scenario calculation consistency
  - **Property 13: Scenario Calculation Consistency**
  - **Validates: Requirements 5.3**

- [x] 5. Build overview section with KPIs and heatmap
  - _Requirements: 2.1, 2.2, 2.3, 2.5, 2.6_

- [x] 5.1 Create KPI tiles matching the design mockup in app.py
  - Display 4 KPI cards in a grid: Debt-to-GDP (median), Debt service/revenue, Health vs debt service, Education vs debt service
  - Style cards with hover effects matching the HTML mockup
  - Add risk indicators (colored dots and labels)
  - Include trend indicators (arrows and percentage changes)
  - Write calculation functions for each KPI
  - _Requirements: 2.1, 8.2, 8.5_

- [ ]* 5.2 Write property test for KPI calculations
  - **Property 5: KPI Calculations Are Correct**
  - **Validates: Requirements 2.1, 3.1, 4.1**

- [x] 5.3 Create Africa heatmap component in components/heatmap.py
  - Write `create_africa_heatmap()` function using plotly.express.choropleth
  - Configure color scale: RdYlGn_r (green-yellow-red) matching design
  - Set geographic scope to Africa
  - Add hover template with country name, debt-to-GDP, total debt
  - Style to match the mockup with card border and header
  - _Requirements: 2.2, 2.3, 8.1_

- [x] 5.4 Implement heatmap highlighting logic in components/heatmap.py
  - Write function to identify top 3 countries by debt-to-GDP
  - Add visual emphasis (border or annotation) to highlighted countries
  - _Requirements: 2.5_

- [ ]* 5.5 Write property test for heatmap highlighting
  - **Property 6: Heatmap Highlights Top Countries**
  - **Validates: Requirements 2.5**

- [x] 5.6 Create insight generation function in utils/calculations.py
  - Write function to analyze data and generate compelling statistics
  - Examples: countries spending more on debt than health, debt payment equivalents
  - Return formatted string with statistic and country reference
  - _Requirements: 2.6_

- [ ]* 5.7 Write property test for insight generation
  - **Property 7: Insight Generation Produces Valid Output**
  - **Validates: Requirements 2.6**

- [ ] 6. Build debt service pressure section
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 6.1 Create debt service bar chart in components/debt_service.py
  - Write `create_debt_service_bar_chart()` function matching the horizontal bar design from mockup
  - Make chart sortable by debt service percentage
  - Add hover template with absolute USD amounts
  - Style bars with color coding (red/yellow/green)
  - _Requirements: 3.2, 3.4, 8.1_

- [x] 6.2 Implement color coding logic in components/debt_service.py
  - Write `assign_debt_service_color()` function
  - Return red for >30%, yellow for 20-30%, green for <20%
  - _Requirements: 3.3_

- [ ]* 6.3 Write property test for color coding thresholds
  - **Property 8: Color Coding Follows Thresholds**
  - **Validates: Requirements 3.3**

- [x] 6.4 Create creditor stacked area chart in components/debt_service.py
  - Write `create_creditor_stacked_area()` function
  - Show debt service by creditor type (multilateral, bilateral, commercial) over time
  - Use consistent colors from COLORS constant: blue, orange, red
  - Match the stacked area design from mockup
  - _Requirements: 3.5, 8.1_

- [ ]* 6.5 Write property test for chart data integrity
  - **Property 9: Chart Data Integrity**
  - **Validates: Requirements 3.2, 3.5, 4.2**

- [ ] 7. Build social impact section
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 7.1 Create comparison bar chart in components/social_impact.py
  - Write `create_comparison_bar_chart()` function
  - Show grouped bars: debt service (red), health (blue), education (green)
  - Sort countries by debt service descending
  - Match the grouped bar chart design from mockup
  - _Requirements: 4.2, 4.3, 8.1_

- [ ]* 7.2 Write property test for sort order correctness
  - **Property 10: Sort Order Correctness**
  - **Validates: Requirements 4.3**

- [x] 7.3 Implement conditional highlighting in components/social_impact.py
  - Write function to identify countries where debt service > health spending
  - Apply visual highlighting (border, background color, or annotation)
  - _Requirements: 4.4_

- [ ]* 7.4 Write property test for conditional highlighting accuracy
  - **Property 11: Conditional Highlighting Accuracy**
  - **Validates: Requirements 4.4**

- [x] 7.5 Create opportunity cost conversion panel in components/social_impact.py
  - Write `create_opportunity_cost_panel()` function
  - Display 4 cards for schools, hospitals, vaccines, teachers matching mockup design
  - Include emoji icons, unit costs, and calculated quantities
  - Style cards to match the mockup with colored icon backgrounds
  - _Requirements: 4.5, 8.2, 8.5_

- [ ] 8. Build country simulator component
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [x] 8.1 Create simulator interface layout in components/simulator.py
  - Write `create_simulator_interface()` function
  - Create two-column layout: current vs scenario comparison (left), controls (right)
  - Match the design from mockup with colored cards for current (gray) and scenario (green)
  - _Requirements: 5.1, 5.2, 8.5_

- [x] 8.2 Implement current state display in components/simulator.py
  - Show current metrics: annual debt service, debt-to-GDP, fiscal space
  - Display in styled card matching mockup
  - _Requirements: 5.1, 8.2_

- [x] 8.3 Create scenario control sliders in components/simulator.py
  - Add 3 sliders: interest rate reduction (0-5%), maturity extension (0-10 years), principal haircut (0-50%)
  - Style sliders to match the mockup design
  - Add descriptive text under each slider
  - _Requirements: 5.2, 8.5_

- [x] 8.4 Wire up scenario calculations in components/simulator.py
  - Connect sliders to `calculate_restructuring_impact()` function
  - Update results display when parameters change
  - Show instant impact summary with 3 metrics
  - _Requirements: 5.3, 5.4_

- [x] 8.5 Create reform scenario results display in components/simulator.py
  - Show new metrics: annual debt service, debt-to-GDP (year 5), fiscal space freed
  - Display in green-tinted card matching mockup
  - Add fiscal space composition bar (health, education, other social)
  - _Requirements: 5.4, 5.5, 8.2_

- [x] 8.6 Set Nigeria as default case study (matching mockup)
  - Pre-populate simulator with Nigeria data from mockup
  - _Requirements: 5.6_

- [ ] 9. Implement filtering and data loading
  - _Requirements: 1.5, 6.1, 6.2, 6.3, 6.4, 7.3_

- [x] 9.1 Implement data loading with caching in app.py
  - Write `load_data()` function with @st.cache_data decorator
  - Load from data/cached/dashboard_data.parquet
  - Verify no API calls are made during load
  - _Requirements: 1.5, 7.3_

- [ ]* 9.2 Write property test for cache loading source
  - **Property 18: Cache Loading Source**
  - **Validates: Requirements 7.3**

- [x] 9.3 Implement filter functions in app.py
  - Write `filter_by_year_range()` function
  - Write `filter_by_region()` function using REGIONS constant
  - Write `filter_by_country()` function
  - _Requirements: 6.2, 6.3, 6.4_

- [ ]* 9.4 Write property test for year range filter correctness
  - **Property 15: Year Range Filter Correctness**
  - **Validates: Requirements 6.2**

- [ ]* 9.5 Write property test for region filter correctness
  - **Property 16: Region Filter Correctness**
  - **Validates: Requirements 6.3**

- [ ]* 9.6 Write property test for country filter isolation
  - **Property 17: Country Filter Isolation**
  - **Validates: Requirements 6.4**

- [x] 9.7 Wire filters to all visualizations in app.py
  - Connect filter controls to data filtering functions
  - Update all sections when filters change
  - Ensure <1 second response time
  - _Requirements: 6.2, 6.3, 6.4, 6.5_

- [ ] 10. Integrate all sections into main app
  - _Requirements: 7.5, 8.5_

- [x] 10.1 Integrate overview section in app.py
  - Add section header matching mockup style
  - Render KPI tiles in 4-column grid
  - Display heatmap with card styling
  - _Requirements: 2.1, 2.2, 2.6, 8.5_

- [x] 10.2 Integrate debt service section in app.py
  - Add section header
  - Create 2-column layout for bar chart (left) and stacked area (right)
  - Match the grid layout from mockup
  - _Requirements: 3.1, 3.2, 3.5, 8.5_

- [x] 10.3 Integrate social impact section in app.py
  - Add section header with subtitle
  - Display comparison bar chart
  - Display opportunity cost cards in 4-column grid
  - _Requirements: 4.1, 4.2, 4.5, 8.5_

- [x] 10.4 Integrate simulator section in app.py
  - Add section header with sync indicator
  - Create 2-column layout: comparison (left), controls (right)
  - Wire up all controls and displays
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 8.5_

- [x] 10.5 Implement error handling for missing data in app.py
  - Wrap visualization functions in try-except blocks
  - Display "No data available" messages when appropriate
  - Flag low-confidence data with visual indicators
  - _Requirements: 7.5_

- [ ]* 10.6 Write property test for graceful handling of missing data
  - **Property 19: Graceful Handling of Missing Data**
  - **Validates: Requirements 7.5**

- [-] 11. Final styling and polish
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 11.1 Enhance custom CSS to match mockup exactly
  - Update assets/style.css to match all design details from HTML mockup
  - Ensure card shadows, borders, and hover effects match
  - Verify typography matches (Inter font, sizes, weights)
  - _Requirements: 8.2, 8.4, 8.5_

- [x] 11.2 Verify color palette consistency across all components
  - Ensure all charts use COLORS constant consistently
  - Verify risk colors (red/yellow/green) match mockup
  - Check creditor colors (blue/orange/red) are consistent
  - _Requirements: 8.1, 8.3_

- [ ]* 11.3 Write property test for color palette consistency
  - **Property 20: Color Palette Consistency**
  - **Validates: Requirements 8.1**

- [x] 11.4 Add loading states and progress indicators
  - Show spinner while data loads
  - Add progress messages during long operations
  - Ensure <3 second load time
  - _Requirements: 1.5, 7.1_

- [x] 11.5 Add footer section matching mockup
  - Create footer with call-to-action text
  - Add action buttons styled to match mockup
  - _Requirements: 8.5_

- [x] 12. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 13. Create sample data for development
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 13.1 Create sample/mock data generator
  - Write script to generate realistic sample data for all 54 countries
  - Include all required columns from design document
  - Save as data/cached/dashboard_data.parquet for development
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 13.2 Create sample creditor data CSV
  - Generate sample creditor composition data
  - Save as data/creditor_data.csv
  - _Requirements: 1.3_

- [x] 14. Test dashboard with sample data
  - _Requirements: 7.1, 7.2_

- [x] 14.1 Run dashboard locally with sample data
  - Execute `streamlit run app.py`
  - Verify load time <3 seconds
  - Test all filters and interactions
  - Verify all visualizations render correctly
  - Compare visual output with HTML mockup
  - _Requirements: 7.1, 7.2_

- [x] 14.2 Create Streamlit config file
  - Create .streamlit/config.toml with theme colors matching mockup
  - Set primaryColor, backgroundColor, textColor from COLORS constant
  - _Requirements: 8.1_

- [x] 15. Final checkpoint - Demo preparation
  - Ensure all tests pass, ask the user if questions arise.
