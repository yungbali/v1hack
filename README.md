# Africa Sovereign Debt Crisis Dashboard

An interactive dashboard that visualizes the sovereign debt crisis across African nations and enables policy scenario modeling.

## Features

- **Interactive Heatmap**: Visualize debt-to-GDP ratios across 54 African countries
- **Debt Service Analysis**: Track debt service pressure and creditor composition
- **Social Impact Comparison**: Compare debt service against health and education spending
- **Country Simulator**: Model debt restructuring scenarios and their fiscal impact
- **Opportunity Cost Calculator**: Translate debt payments into tangible social investments

## Setup

### Prerequisites

- Python 3.10+
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd debt-dashboard
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Fetch and cache data (run once before demo):
```bash
python data/fetch_data.py
```

5. Run the dashboard:
```bash
streamlit run app.py
```

## Project Structure

```
debt-dashboard/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── data/
│   ├── fetch_data.py          # API data fetching
│   ├── process_data.py        # Data cleaning
│   ├── creditor_data.csv      # Static creditor data
│   └── cached/                # Pre-fetched data
├── components/
│   ├── heatmap.py             # Africa heatmap
│   ├── debt_service.py        # Debt service charts
│   ├── social_impact.py       # Social spending comparison
│   └── simulator.py           # Scenario simulator
├── utils/
│   ├── api_client.py          # API wrappers
│   ├── calculations.py        # Debt calculations
│   └── constants.py           # Constants and configs
└── assets/
    └── style.css              # Custom styling
```

## Data Sources

- **World Bank API**: Debt indicators, GDP, social spending (60% coverage)
- **IMF API**: GDP projections, debt forecasts (20% coverage)
- **Static Data**: Creditor composition, interest rates (20% coverage)

## Usage

### Filters

- **Region**: Filter by African sub-region (West, East, Central, Southern, North)
- **Year Range**: Select time period (2014-2024)
- **Country**: Focus on specific country

### Sections

1. **Overview**: High-level KPIs and Africa heatmap
2. **Debt Service Pressure**: Debt service as % of revenue, creditor composition
3. **Social Impact**: Debt vs health/education spending with opportunity costs
4. **Country Simulator**: Interactive debt restructuring scenario modeling

## Development

### Running Tests

```bash
# Unit tests
pytest tests/

# Property-based tests
pytest tests/ -k property
```

### Data Refresh

To update cached data:
```bash
python data/fetch_data.py
```

## License

MIT License

## Contact

For questions or feedback, please open an issue on GitHub.
