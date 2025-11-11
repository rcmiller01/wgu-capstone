"""
Download Virginia Department of Health datasets.
"""

import requests
import pandas as pd
from pathlib import Path
import json

# VDH data directory
vdh_dir = Path('data/raw/vdh')
vdh_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("DOWNLOADING VIRGINIA DEPARTMENT OF HEALTH DATA")
print("=" * 70)

# Dataset 1: COVID-19 Cases by Health District
print("\n1. Downloading COVID-19 cases by health district...")
covid_url = "https://data.virginia.gov/resource/bre9-aqqr.json"
try:
    response = requests.get(covid_url, params={"$limit": 50000})
    response.raise_for_status()
    covid_data = response.json()
    
    df = pd.DataFrame(covid_data)
    output_file = vdh_dir / 'covid_cases_by_district.csv'
    df.to_csv(output_file, index=False)
    print(f"   ✓ Downloaded {len(df)} records")
    print(f"   ✓ Saved to: {output_file}")
except Exception as e:
    print(f"   ✗ Error downloading COVID data: {e}")
    print("   → Try manual download from: https://data.virginia.gov/Government/VDH-COVID-19-PublicUseDataset-Cases/bre9-aqqr")

# Dataset 2: Chronic Disease Indicators
print("\n2. Downloading chronic disease indicators...")
chronic_url = "https://data.virginia.gov/resource/96y7-bnr5.json"
try:
    response = requests.get(chronic_url, params={"$limit": 50000})
    response.raise_for_status()
    chronic_data = response.json()
    
    df = pd.DataFrame(chronic_data)
    output_file = vdh_dir / 'chronic_disease_indicators.csv'
    df.to_csv(output_file, index=False)
    print(f"   ✓ Downloaded {len(df)} records")
    print(f"   ✓ Saved to: {output_file}")
except Exception as e:
    print(f"   ✗ Error downloading chronic disease data: {e}")
    print("   → Try manual download from: https://data.virginia.gov/Health/Chronic-Disease-Indicators/96y7-bnr5")

print("\n" + "=" * 70)
print("VDH DATA DOWNLOAD COMPLETE")
print("=" * 70)
