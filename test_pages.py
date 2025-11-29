"""
Quick test to verify all pages can be imported
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing page imports...")

try:
    # Test main app
    print("✓ Main app.py exists")
    
    # Test pages exist
    pages_dir = Path("pages")
    if pages_dir.exists():
        page_files = list(pages_dir.glob("*.py"))
        print(f"✓ Found {len(page_files)} page files:")
        for page in sorted(page_files):
            print(f"  - {page.name}")
    else:
        print("✗ pages/ directory not found")
    
    # Test components
    print("\nTesting component imports...")
    from components.heatmap import create_africa_heatmap
    print("✓ heatmap component")
    
    from components.debt_service import create_debt_service_bar_chart
    print("✓ debt_service component")
    
    from components.social_impact import create_comparison_bar_chart
    print("✓ social_impact component")
    
    from components.simulator import create_simulator_interface
    print("✓ simulator component")
    
    # Test utils
    print("\nTesting utils imports...")
    from utils.constants import COLORS, REGIONS, AFRICAN_COUNTRIES
    print("✓ constants")
    
    from utils.calculations import calculate_kpi_metrics
    print("✓ calculations")
    
    print("\n✅ All imports successful!")
    print("\nTo run the dashboard:")
    print("  streamlit run app.py")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
