# Hackathon Submission Requirements

## Introduction

This spec documents the transformation of the Africa Debt Dashboard into a hackathon-winning submission for the Kiro Hackathon. The project demonstrates the **Frankenstein** category by stitching together seemingly incompatible technologies: statistical computing (regression, ARIMA forecasting), interactive web dashboards, Excel-based fiscal data, and AI-powered policy recommendations into a unified fiscal intelligence platform.

The submission must showcase how Kiro's agent-driven development (specs, steering, vibe coding) enabled rapid prototyping of a complex analytical system that would typically require weeks of development.

## Glossary

- **Frankenstein Category**: Hackathon category for projects that stitch together incompatible technologies into something unexpectedly powerful
- **Kiro Specs**: Structured development approach using requirements.md, design.md, and tasks.md
- **Vibe Coding**: AI-assisted development where the agent understands context and generates code matching project patterns
- **Steering Docs**: Context files that guide agent behavior and maintain consistency
- **MLR (Multiple Linear Regression)**: Statistical method to identify causal drivers of budget deficits
- **ARIMA**: Time-series forecasting model for predicting future debt trajectories
- **Z-Score Anomaly Detection**: Statistical method to flag outlier countries
- **SDG Mapping**: Linking policy recommendations to UN Sustainable Development Goals
- **Fiscal Intelligence**: The combination of data analysis, prediction, and actionable policy recommendations

## Requirements

### Requirement 1: Frankenstein Technology Integration

**User Story:** As a hackathon judge, I want to see how the project stitches together incompatible technologies, so that I understand the technical complexity and innovation.

#### Acceptance Criteria

1. WHEN reviewing the submission, THE Submission SHALL document the integration of at least 4 distinct technology paradigms: statistical computing (statsmodels), web dashboards (Streamlit), time-series forecasting (ARIMA), and interactive simulation
2. WHEN examining the codebase, THE Submission SHALL show evidence of bridging Excel-based fiscal data with Python analytical pipelines
3. WHEN reviewing the architecture, THE Submission SHALL demonstrate how regression analysis outputs feed into interactive visualizations
4. WHEN examining the simulator, THE Submission SHALL show how financial calculations (annuity formulas) integrate with real-time UI updates
5. WHEN reviewing the DevPost submission, THE Submission SHALL explicitly call out the "Frankenstein" nature of stitching together academic statistics, policy analysis, and web development

### Requirement 2: Kiro Specs Showcase

**User Story:** As a hackathon judge, I want to see how Kiro specs structured the development process, so that I understand the tool's value proposition.

#### Acceptance Criteria

1. WHEN reviewing the submission, THE Submission SHALL include screenshots or documentation of the `.kiro/specs/africa-debt-dashboard/` structure showing requirements.md, design.md, and tasks.md
2. WHEN examining the development process, THE Submission SHALL document how specs enabled incremental development of complex features (regression → forecasting → recommendations)
3. WHEN reviewing the DevPost submission, THE Submission SHALL include a section titled "How We Used Kiro" explaining specs-driven development
4. WHEN examining the tasks.md file, THE Submission SHALL show completed checkboxes demonstrating systematic progress through 100+ implementation tasks
5. WHEN reviewing the submission, THE Submission SHALL explain how property-based testing requirements in design.md ensured correctness

### Requirement 3: Vibe Coding Evidence

**User Story:** As a hackathon judge, I want to see evidence of AI-assisted development, so that I understand how Kiro accelerated the build.

#### Acceptance Criteria

1. WHEN reviewing the submission, THE Submission SHALL document specific examples where Kiro generated complex code (e.g., ARIMA forecasting, regression analysis)
2. WHEN examining the codebase, THE Submission SHALL show consistent patterns across components indicating agent-generated code
3. WHEN reviewing the DevPost submission, THE Submission SHALL include before/after examples showing how Kiro transformed requirements into implementation
4. WHEN examining the development timeline, THE Submission SHALL document that the entire analytical pipeline (regression + forecasting + recommendations) was built in under 6 hours
5. WHEN reviewing the submission, THE Submission SHALL explain how Kiro maintained code quality and consistency across 15+ Python modules

### Requirement 4: Statistical Rigor Showcase

**User Story:** As a hackathon judge, I want to see the statistical analysis capabilities, so that I understand the technical depth beyond typical dashboards.

#### Acceptance Criteria

1. WHEN reviewing the dashboard, THE Dashboard SHALL display regression results with β coefficients, p-values, and R² values for each country
2. WHEN examining the Risk & Forecast page, THE Dashboard SHALL show ARIMA forecasts with confidence intervals for 3-year projections
3. WHEN reviewing the anomaly detection, THE Dashboard SHALL display Z-scores and flag countries exceeding 2 standard deviations
4. WHEN examining the DevPost submission, THE Submission SHALL include screenshots of regression output showing statistical significance
5. WHEN reviewing the methodology, THE Submission SHALL explain how MLR identifies causal drivers (not just correlations)

### Requirement 5: Policy Impact Demonstration

**User Story:** As a hackathon judge, I want to see real-world policy applications, so that I understand the project's practical value.

#### Acceptance Criteria

1. WHEN reviewing the Policy Actions page, THE Dashboard SHALL display country-specific recommendations with quantified targets (e.g., "increase VAT compliance from 60% to 75%")
2. WHEN examining recommendations, THE Dashboard SHALL map each recommendation to specific SDG targets (Goals 1, 2, 8, 9, 16, 17)
3. WHEN reviewing the simulator, THE Dashboard SHALL show fiscal space calculations demonstrating how debt restructuring frees resources for social spending
4. WHEN examining the DevPost submission, THE Submission SHALL include a case study showing how a specific country (e.g., Egypt) can use the tool for policy planning
5. WHEN reviewing the social impact section, THE Dashboard SHALL convert debt payments into tangible units (schools, hospitals, vaccines, teachers)

### Requirement 6: DevPost Submission Quality

**User Story:** As a hackathon organizer, I want a complete DevPost submission, so that judges can evaluate the project fairly.

#### Acceptance Criteria

1. WHEN submitting to DevPost, THE Submission SHALL include a "Frankenstein" category justification explaining the technology stitching
2. WHEN submitting to DevPost, THE Submission SHALL include a "How We Used Kiro" section with specific examples (specs, vibe coding, agent hooks)
3. WHEN submitting to DevPost, THE Submission SHALL include 5-8 screenshots showing: regression results, forecasts, anomaly detection, policy recommendations, simulator, and Kiro specs structure
4. WHEN submitting to DevPost, THE Submission SHALL include a 2-3 minute video demo walking through the dashboard and explaining the Kiro development process
5. WHEN submitting to DevPost, THE Submission SHALL include GitHub repository link with README explaining how to run the dashboard
6. WHEN submitting to DevPost, THE Submission SHALL include a "Challenges" section explaining how Kiro helped overcome data quality and complexity issues
7. WHEN submitting to DevPost, THE Submission SHALL include a "What's Next" section outlining expansion plans (54 countries, real-time APIs, AI advisor)

### Requirement 7: Functionality Proof

**User Story:** As a hackathon judge, I want to verify the project works, so that I can evaluate it fairly.

#### Acceptance Criteria

1. WHEN accessing the GitHub repository, THE Repository SHALL include a requirements.txt file with all dependencies
2. WHEN following the README instructions, THE Dashboard SHALL start successfully with `streamlit run app.py`
3. WHEN the dashboard loads, THE Dashboard SHALL display all 6 pages without errors: Overview, Driver Analysis, Risk & Forecast, Policy Actions, Data Quality, Simulator
4. WHEN clicking through pages, THE Dashboard SHALL load each page within 2 seconds
5. WHEN interacting with filters, THE Dashboard SHALL update visualizations without errors
6. WHEN using the simulator, THE Dashboard SHALL recalculate scenarios in real-time
7. WHEN deployed to Streamlit Cloud, THE Dashboard SHALL be accessible via public URL without authentication

### Requirement 8: New Development Evidence

**User Story:** As a hackathon organizer, I want to verify the project was built during the hackathon period, so that I can ensure fair competition.

#### Acceptance Criteria

1. WHEN reviewing the submission, THE Submission SHALL include a timeline showing when key features were developed (with git commit timestamps if available)
2. WHEN examining the DevPost submission, THE Submission SHALL explain which features existed before the hackathon (basic dashboard) and which were added during (regression, forecasting, recommendations)
3. WHEN reviewing the "What We Built" section, THE Submission SHALL clearly state: "We added 3 major analytical engines during the hackathon: Driver Analysis (MLR), Risk & Forecast (ARIMA), and Policy Recommendations (SDG-mapped)"
4. WHEN examining the codebase, THE Codebase SHALL include files created during hackathon period: `scripts/driver_risk_forecast.py`, `data/processed/fiscal_driver_analysis.csv`, `data/processed/fiscal_forecasts.csv`
5. WHEN reviewing the submission, THE Submission SHALL document the 6-hour sprint that added statistical rigor to the existing dashboard

### Requirement 9: Competitive Differentiation

**User Story:** As a hackathon judge, I want to understand what makes this project unique, so that I can compare it against other submissions.

#### Acceptance Criteria

1. WHEN reviewing the DevPost submission, THE Submission SHALL include a "Competitive Advantages" section listing 5 unique features
2. WHEN examining the competitive advantages, THE Submission SHALL highlight: statistical rigor (regression), predictive capability (forecasting), data quality (audit trail), policy relevance (SDG mapping), and Kiro-powered development speed
3. WHEN reviewing the submission, THE Submission SHALL include a comparison table showing "Most teams vs. You" for key differentiators
4. WHEN examining the methodology, THE Submission SHALL explain why regression (causation) is superior to correlation analysis
5. WHEN reviewing the submission, THE Submission SHALL document the 40-rule data validation pipeline as evidence of quality

### Requirement 10: Presentation Readiness

**User Story:** As a hackathon presenter, I want a polished demo script, so that I can deliver a compelling 3-minute pitch.

#### Acceptance Criteria

1. WHEN preparing for demo, THE Presenter SHALL have a 3-minute script structured as: Problem (30s) → Solution (90s) → Impact (60s)
2. WHEN delivering the demo, THE Presenter SHALL show 3 key screens: Driver Analysis (regression), Risk & Forecast (ARIMA), Policy Actions (recommendations)
3. WHEN explaining the solution, THE Presenter SHALL mention Kiro specs and vibe coding as enablers of rapid development
4. WHEN demonstrating impact, THE Presenter SHALL use a specific example: "Egypt's wage bill drives 51% of deficit variance. Our recommendation: digital census to reduce ghost workers by 5% by 2027"
5. WHEN preparing for Q&A, THE Presenter SHALL have answers ready for: "How did you validate regression?", "Why ARIMA?", "How accurate are forecasts?", "How did Kiro help?"
