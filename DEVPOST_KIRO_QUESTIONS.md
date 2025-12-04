# DevPost Kiro Usage Questions - Answers

## Question 1: Vibe Coding

**How did you structure your conversations with Kiro to build your project? What was the most impressive code generation Kiro helped you with?**

### Conversation Structure

We structured our Kiro conversations in three phases:

**Phase 1: Context Setting (Hour 0-1)**
- Started by sharing the Excel data file and explaining the problem: "Governments have fiscal data but lack analytical tools"
- Asked Kiro to analyze the data structure and identify quality issues
- Result: Kiro discovered 396 duplicate records, inconsistent units, and missing data patterns

**Phase 2: Incremental Feature Building (Hour 1-5)**
- Used natural language requirements: "I need regression analysis to identify what drives budget deficits"
- Kiro asked clarifying questions: "Which statistical method? What independent variables?"
- We refined together: "Use Multiple Linear Regression with revenue volatility, wage bills, fiscal burden, and GDP growth as drivers"
- Kiro generated complete implementations, we tested, then moved to next feature

**Phase 3: Integration & Refinement (Hour 5-6)**
- Conversational debugging: "The simulator isn't updating in real-time"
- Kiro diagnosed: "Missing Streamlit state management" and fixed it
- Iterative polish: "Make the regression results more accessible to policymakers"
- Kiro added interpretation text and visual emphasis

### Most Impressive Code Generation

**The Regression & Forecasting Pipeline** (`scripts/driver_risk_forecast.py` - 400+ lines)

**What we asked**:
> "Build a statistical analysis pipeline that:
> 1. Runs Multiple Linear Regression to identify deficit drivers for each country
> 2. Uses ARIMA to forecast debt trajectories 3 years ahead
> 3. Detects anomalies using Z-scores
> 4. Outputs results as CSVs for the dashboard"

**What Kiro generated in ONE iteration**:

```python
# Feature engineering with proper statistical methods
country_data['revenue_volatility'] = country_data['revenue_pct_gdp'].rolling(3).std()
country_data['fiscal_burden'] = (
    country_data['debt_service_usd'] / 
    (country_data['gdp_usd'] * country_data['revenue_pct_gdp'] / 100)
)

# OLS regression with proper error handling
model = sm.OLS(y, X, missing='drop')
results = model.fit()

# ARIMA forecasting with confidence intervals
model = ARIMA(debt_series, order=(1, 1, 1))
fitted_model = model.fit()
forecast_df = fitted_model.get_forecast(steps=3).summary_frame()

# Z-score anomaly detection
z_scores = (df['debt_to_gdp'] - df['debt_to_gdp'].mean()) / df['debt_to_gdp'].std()
anomalies = df[z_scores.abs() > 2]
```

**Why this was impressive**:
- Kiro understood statistical concepts (rolling windows, OLS, ARIMA order selection)
- Added proper error handling for sparse time series
- Implemented confidence intervals correctly
- Formatted outputs for dashboard consumption
- This would have taken us 2-3 days manually - Kiro did it in 5 minutes

**The conversation flow**:
1. We: "I need regression analysis"
2. Kiro: "What's your dependent variable and what drivers should I test?"
3. We: "Deficit is dependent, test revenue volatility, wage bills, fiscal burden, GDP growth"
4. Kiro: *generates complete pipeline with feature engineering*
5. We: "Can you add forecasting too?"
6. Kiro: *adds ARIMA with proper parameter selection*
7. We: "Perfect, now add anomaly detection"
8. Kiro: *adds Z-score analysis*

Total conversation: 10 minutes. Total code generated: 400+ lines of production-ready statistical analysis.

---

## Question 2: Agent Hooks

**What specific workflows did you automate with Kiro hooks? How did these hooks improve your development process?**

**N/A** - We didn't use agent hooks for this project due to the tight hackathon timeline. However, we identified potential hooks for future development:

**Potential hooks we'd add**:
1. **Data Refresh Hook**: Trigger when Excel file is updated → Auto-run data validation and regenerate analytical artifacts
2. **Test Hook**: Trigger on file save → Run property-based tests for that component
3. **Documentation Hook**: Trigger when new function is added → Generate docstring and update API docs

For this hackathon sprint, we focused on specs-driven development instead of hooks, but we see the value for ongoing maintenance.

---

## Question 3: Spec-Driven Development

**How did you structure your spec for Kiro to implement? How did the spec-driven approach improve your development process? How did this compare to vibe coding?**

### Spec Structure

We created a comprehensive spec in `.kiro/specs/africa-debt-dashboard/`:

**1. requirements.md (10 user stories, 50+ acceptance criteria)**

Each requirement followed this pattern:
```markdown
### Requirement 3: Debt Service Pressure Analysis

**User Story:** As a policy analyst, I want to visualize debt service payments 
relative to government revenue, so that I can identify countries facing severe 
fiscal pressure.

#### Acceptance Criteria
1. WHEN the debt service section renders, THE Dashboard SHALL display KPI tiles 
   showing average debt service as percentage of revenue
2. WHEN displaying debt service bars, THE Dashboard SHALL color-code bars as red 
   when >30%, yellow when 20-30%, green when <20%
3. WHEN a user hovers over a debt service bar, THE Dashboard SHALL display the 
   absolute debt service amount in USD
...
```

**Why this worked**: The "WHEN...THE...SHALL" format gave Kiro unambiguous instructions. No interpretation needed.

**2. design.md (Architecture + Data Models + 20 Correctness Properties)**

Included:
- System architecture diagrams
- DataFrame schemas with column types
- Function signatures with type hints
- Correctness properties for testing

Example:
```python
def create_africa_heatmap(df: pd.DataFrame, 
                         metric: str = 'debt_to_gdp',
                         year: int = 2024) -> go.Figure:
    """Create interactive choropleth map of Africa"""
```

**Why this worked**: Kiro knew exactly what inputs/outputs each function needed. No guessing about data structures.

**3. tasks.md (100+ implementation tasks)**

Broke the project into atomic tasks:
```markdown
- [x] 4.1 Create debt service pressure calculation
  - Formula: (debt_service_usd / (gdp_usd * revenue_pct_gdp / 100)) * 100
  - _Requirements: 3.1_

- [x] 4.2 Create opportunity cost calculator
  - Support unit types: school, hospital, vaccine_dose, teacher
  - Return integer division of debt service by unit cost
  - _Requirements: 4.5_
```

Each task referenced specific requirements, creating traceability.

### How Specs Improved Development

**1. Eliminated Ambiguity**
- Without specs: "Build a dashboard" → Kiro asks 20 clarifying questions
- With specs: Kiro knows exactly what to build, how to structure it, what edge cases to handle

**2. Enabled Systematic Execution**
- Kiro worked through 100+ tasks in order
- Each task built on previous ones
- No backtracking or rework

**3. Maintained Consistency**
- Color palette defined once in design.md → Used consistently across 20+ charts
- Naming conventions specified → Applied throughout codebase
- Error handling patterns documented → Replicated everywhere

**4. Prevented Scope Creep**
- If it wasn't in requirements.md, we didn't build it
- Saved us from "just one more feature" trap
- Stayed focused on core value

**5. Created Audit Trail**
- Every line of code traces back to a requirement
- Easy to explain "why does this exist?"
- Critical for policy credibility

### Specs vs. Vibe Coding Comparison

| Aspect | Vibe Coding (Conversational) | Spec-Driven Development |
|--------|------------------------------|-------------------------|
| **Setup Time** | 0 minutes (start immediately) | 60 minutes (write specs) |
| **Clarity** | Requires back-and-forth | Unambiguous from start |
| **Consistency** | Varies by conversation | Enforced by spec |
| **Scope Control** | Easy to drift | Locked by requirements |
| **Traceability** | Lost in chat history | Every task → requirement |
| **Best For** | Exploration, prototyping | Production systems |
| **Our Use** | Initial data exploration | Core dashboard build |

### Our Hybrid Approach

**Hour 0-1: Vibe Coding**
- Explored the data conversationally
- Discovered quality issues through dialogue
- Prototyped visualization ideas

**Hour 1-6: Spec-Driven**
- Wrote comprehensive specs
- Kiro executed systematically
- Built production-ready system

**Result**: Best of both worlds. Vibe coding for discovery, specs for execution.

### Specific Example: Regression Implementation

**Vibe Coding Approach** (what we did initially):
- Us: "Can you do regression analysis?"
- Kiro: "What type? What variables?"
- Us: "Multiple linear regression on deficit"
- Kiro: "What independent variables?"
- Us: "Revenue volatility, wage bills..."
- *10 minutes of back-and-forth*

**Spec-Driven Approach** (what we switched to):

Wrote in requirements.md:
```markdown
WHEN the driver analysis runs, THE System SHALL:
1. Calculate revenue volatility as 3-year rolling standard deviation
2. Calculate fiscal burden as debt_service / (GDP × revenue%)
3. Run OLS regression with deficit as dependent variable
4. Output β coefficients, p-values, R², and observation count
5. Handle countries with <8 years of data gracefully
```

Kiro generated complete implementation in one shot. No questions needed.

### Key Insight

**Specs are an investment that pays 20x returns**:
- 60 minutes writing specs
- 5 hours of flawless execution
- vs. 10+ hours of conversational back-and-forth

For hackathons with tight timelines, specs are actually FASTER because they eliminate iteration cycles.

---

## Question 4: Steering Docs

**How did you leverage steering to improve Kiro's responses? Was there a particular strategy that made the biggest difference?**

**N/A** - We didn't create custom steering docs for this project. We relied on the comprehensive specs (requirements.md, design.md) to guide Kiro's behavior.

**Why we didn't need steering**:
- Our specs were detailed enough to provide all necessary context
- The problem domain (fiscal analysis) didn't require specialized terminology beyond what was in the specs
- Kiro's default behavior worked well for statistical computing and web development

**Where steering would have helped** (for future iterations):
- Policy language conventions (how to phrase recommendations for government audiences)
- Statistical reporting standards (how to present regression results)
- Data quality documentation patterns (how to write audit trails)

For this hackathon sprint, specs were sufficient. For a production system serving multiple governments, we'd add steering docs for domain-specific conventions.

---

## Question 5: MCP (Model Context Protocol)

**How did extending Kiro's capabilities help you build your project? What sort of features or workflow improvements did MCP enable that otherwise would have been difficult or impossible?**

**N/A** - We didn't use MCP extensions for this project. The built-in Kiro capabilities (file operations, code generation, specs execution) were sufficient for our needs.

**Why we didn't need MCP**:
- All data was local (Excel file)
- No external API integrations during development
- No specialized tools required beyond Python standard library + common packages

**Where MCP would be valuable** (for future development):
1. **World Bank API MCP Server**: Direct integration to fetch live fiscal data
2. **IMF Data MCP Server**: Real-time GDP projections and debt forecasts
3. **Statistical Analysis MCP**: Specialized tools for econometric analysis
4. **Policy Database MCP**: Access to historical policy interventions and outcomes

For this hackathon, we focused on demonstrating analytical capabilities with cached data. For production deployment, MCP would enable real-time data integration and expanded analytical tools.

---

## Summary: How Kiro Enabled This Project

**Primary Kiro Usage**: Spec-Driven Development (95% of value)
- Wrote comprehensive specs (requirements, design, tasks)
- Kiro executed 100+ tasks systematically
- Generated 3,000+ lines of production-ready code
- 6 hours total development time

**Secondary Kiro Usage**: Vibe Coding (5% of value)
- Initial data exploration and quality assessment
- Iterative refinement and debugging
- Conversational problem-solving for edge cases

**Not Used** (but valuable for future):
- Agent Hooks (would automate data refresh and testing)
- Steering Docs (would standardize policy language)
- MCP (would enable real-time API integration)

**The Bottom Line**: Specs-driven development with Kiro transformed a 3-week project into a 6-hour sprint. The combination of precise requirements and AI execution is transformative for complex analytical systems.

**Time Breakdown**:
- Writing specs: 1 hour
- Kiro execution: 5 hours
- Manual development estimate: 120 hours
- **Time savings: 95%**

This is the future of software development.
