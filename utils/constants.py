# African country codes and names (54 countries)
AFRICAN_COUNTRIES = {
    'DZA': 'Algeria',
    'AGO': 'Angola',
    'BEN': 'Benin',
    'BWA': 'Botswana',
    'BFA': 'Burkina Faso',
    'BDI': 'Burundi',
    'CMR': 'Cameroon',
    'CPV': 'Cape Verde',
    'CAF': 'Central African Republic',
    'TCD': 'Chad',
    'COM': 'Comoros',
    'COG': 'Congo',
    'COD': 'Democratic Republic of Congo',
    'CIV': "Côte d'Ivoire",
    'DJI': 'Djibouti',
    'EGY': 'Egypt',
    'GNQ': 'Equatorial Guinea',
    'ERI': 'Eritrea',
    'SWZ': 'Eswatini',
    'ETH': 'Ethiopia',
    'GAB': 'Gabon',
    'GMB': 'Gambia',
    'GHA': 'Ghana',
    'GIN': 'Guinea',
    'GNB': 'Guinea-Bissau',
    'KEN': 'Kenya',
    'LSO': 'Lesotho',
    'LBR': 'Liberia',
    'LBY': 'Libya',
    'MDG': 'Madagascar',
    'MWI': 'Malawi',
    'MLI': 'Mali',
    'MRT': 'Mauritania',
    'MUS': 'Mauritius',
    'MAR': 'Morocco',
    'MOZ': 'Mozambique',
    'NAM': 'Namibia',
    'NER': 'Niger',
    'NGA': 'Nigeria',
    'RWA': 'Rwanda',
    'STP': 'São Tomé and Príncipe',
    'SEN': 'Senegal',
    'SYC': 'Seychelles',
    'SLE': 'Sierra Leone',
    'SOM': 'Somalia',
    'ZAF': 'South Africa',
    'SSD': 'South Sudan',
    'SDN': 'Sudan',
    'TZA': 'Tanzania',
    'TGO': 'Togo',
    'TUN': 'Tunisia',
    'UGA': 'Uganda',
    'ZMB': 'Zambia',
    'ZWE': 'Zimbabwe'
}

# Regional groupings
REGIONS = {
    'West Africa': ['BEN', 'BFA', 'CPV', 'CIV', 'GMB', 'GHA', 'GIN', 'GNB', 'LBR', 'MLI', 'MRT', 'NER', 'NGA', 'SEN', 'SLE', 'TGO'],
    'East Africa': ['BDI', 'COM', 'DJI', 'ERI', 'ETH', 'KEN', 'MDG', 'MWI', 'MUS', 'MOZ', 'RWA', 'SYC', 'SOM', 'SSD', 'TZA', 'UGA', 'ZMB', 'ZWE'],
    'Central Africa': ['AGO', 'CMR', 'CAF', 'TCD', 'COG', 'COD', 'GNQ', 'GAB', 'STP'],
    'Southern Africa': ['BWA', 'LSO', 'NAM', 'ZAF', 'SWZ'],
    'North Africa': ['DZA', 'EGY', 'LBY', 'MAR', 'SDN', 'TUN']
}

# Color palette (matching the design)
COLORS = {
    'debt': '#E74C3C',        # Red
    'health': '#3498DB',      # Blue
    'education': '#2ECC71',   # Green
    'gdp': '#95A5A6',         # Gray
    'multilateral': '#3498DB',
    'bilateral': '#F39C12',   # Orange
    'commercial': '#E74C3C',
    'background': '#F9FAFB',
    'text': '#2C3E50',
    'border': '#E2E8F0'
}

# Unit costs for opportunity cost calculations
UNIT_COSTS = {
    'school': 875_000,         # Primary school construction
    'hospital': 11_600_000,    # District hospital
    'vaccine_dose': 50,        # Single vaccine dose
    'teacher': 8_000           # Annual teacher salary
}

# Debt distress thresholds
THRESHOLDS = {
    'debt_to_gdp_high': 60,    # High risk threshold (%)
    'debt_to_gdp_moderate': 40, # Moderate risk threshold (%)
    'debt_service_high': 30,    # High burden (% of revenue)
    'debt_service_moderate': 20 # Moderate burden (% of revenue)
}

# World Bank API indicators
WB_INDICATORS = {
    'DT.DOD.DECT.CD': 'external_debt_stock',
    'GC.DOD.TOTL.GD.ZS': 'debt_to_gdp',
    'NY.GDP.MKTP.CD': 'gdp_usd',
    'NY.GDP.MKTP.KD.ZG': 'gdp_growth',
    'GC.REV.XGRT.GD.ZS': 'revenue_pct_gdp',
    'DT.TDS.DECT.CD': 'debt_service_usd',
    'SH.XPD.CHEX.GD.ZS': 'health_pct_gdp',
    'SE.XPD.TOTL.GD.ZS': 'education_pct_gdp'
}

# IMF API indicators
IMF_INDICATORS = {
    'NGDP_RPCH': 'real_gdp_growth',
    'GGXWDG_NGDP': 'general_govt_debt',
    'PCPIPCH': 'inflation'
}

# Year range
YEAR_START = 2014
YEAR_END = 2024
