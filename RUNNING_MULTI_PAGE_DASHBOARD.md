# Running the Multi-Page Dashboard

## Quick Start

1. **Ensure you have data**:
   ```bash
   # Generate sample data if you haven't already
   python scripts/generate_sample_data.py
   ```

2. **Start the dashboard**:
   ```bash
   streamlit run app.py
   ```

3. **Navigate between pages**:
   - The dashboard will open in your browser at `http://localhost:8501`
   - Use the sidebar navigation to switch between pages:
     - 🌍 **Overview** - System-level indicators and heatmap
     - 📊 **Debt Service** - Debt service pressure analysis
     - 🏦 **Creditor Mix** - Creditor composition breakdown
     - ❤️ **Social Spending** - Social impact comparison
     - 🔍 **Country Deep Dive** - Individual country analysis

## Page Descriptions

### 🌍 Overview (Main Page)
The landing page showing:
- Four key performance indicators
- Africa risk heatmap
- Debt service pressure charts
- Social impact comparison
- Debt restructuring simulator

### 📊 Debt Service
Focused analysis on debt service burden:
- Average debt service as % of revenue
- Country-by-country breakdown (color-coded)
- Creditor composition over time
- High burden country identification

### 🏦 Creditor Mix
Understanding who holds African debt:
- Multilateral vs Bilateral vs Commercial breakdown
- Stacked bar charts by country
- Creditor characteristics and implications
- Restructuring considerations

### ❤️ Social Spending
The human cost of debt:
- Debt service vs health spending comparison
- Debt service vs education spending comparison
- Opportunity cost calculator (schools, hospitals, vaccines, teachers)
- Countries where debt exceeds health spending

### 🔍 Country Deep Dive
Detailed country-level analysis:
- Select any country from the sidebar
- View historical trends (2014-2024)
- Current debt profile
- Interactive debt restructuring simulator
- Scenario modeling with adjustable parameters

## Features

### Global Filters
Available on most pages:
- **Region Filter**: Focus on specific African regions
- **Year Range**: Analyze specific time periods
- **Country Filter**: Highlight or isolate specific countries

### Interactive Elements
- **Hover**: See detailed data on charts
- **Click**: Some charts support click interactions
- **Sliders**: Adjust restructuring parameters in the simulator
- **Dropdowns**: Select countries and regions

### Data Quality Indicators
- Warnings when data is missing or incomplete
- Low-confidence data flagged with visual indicators
- Data refresh timestamp in sidebar

## Troubleshooting

### "No data available" message
**Solution**: Run the data generation script:
```bash
python scripts/generate_sample_data.py
```

### Page not loading
**Solution**: Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Charts not rendering
**Solution**: Check browser console for errors. Try refreshing the page.

### Slow performance
**Solution**: 
- Reduce the year range filter
- Select a specific region instead of "All Regions"
- Clear Streamlit cache: Press 'C' in the app, then click "Clear cache"

## Tips for Best Experience

1. **Start with Overview**: Get a system-level understanding first
2. **Use filters strategically**: Narrow down to specific regions or time periods
3. **Explore Country Deep Dive**: Select countries of interest for detailed analysis
4. **Try the simulator**: Model different restructuring scenarios
5. **Compare pages**: Switch between pages to see different perspectives on the same data

## Keyboard Shortcuts

When the app is running:
- `R` - Rerun the app
- `C` - Clear cache
- `?` - Show keyboard shortcuts

## Development Mode

To run in development mode with auto-reload:
```bash
streamlit run app.py --server.runOnSave true
```

## Deployment

To deploy to Streamlit Cloud:
1. Push code to GitHub
2. Go to share.streamlit.io
3. Connect your repository
4. Select `app.py` as the main file
5. Deploy!

## Support

For issues or questions:
- Check the implementation documentation: `MULTI_PAGE_IMPLEMENTATION.md`
- Review the spec files in `.kiro/specs/africa-debt-dashboard/`
- Check component documentation in `components/` directory

---

**Enjoy exploring the Africa Sovereign Debt Crisis Dashboard!** 🌍
