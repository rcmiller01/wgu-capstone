"""
Download NIH Chest X-Ray sample dataset (2000 images).
"""

import sys
from pathlib import Path

print("=" * 70)
print("NIH CHEST X-RAY SAMPLE - DOWNLOAD INSTRUCTIONS")
print("=" * 70)

kaggle_config = Path.home() / '.kaggle' / 'kaggle.json'

if not kaggle_config.exists():
    print("\n⚠️  Kaggle API credentials not found!")
    print("\nTo download NIH X-ray data, you need to set up Kaggle API:")
    print("\n1. Go to: https://www.kaggle.com/settings")
    print("2. Scroll to 'API' section")
    print("3. Click 'Create New API Token'")
    print("4. Save the downloaded 'kaggle.json' to:")
    print(f"   {kaggle_config}")
    print("\n5. Then run this script again")
    print("\nAlternative - Manual Download:")
    print("   → https://www.kaggle.com/datasets/nih-chest-xrays/data")
    print("   → Click 'Download' (requires Kaggle account)")
    print("   → Extract to: data/raw/nih_xray/")
    sys.exit(1)

print("\n✓ Kaggle credentials found!")
print("\nDownloading NIH Chest X-Ray dataset...")
print("Note: This is the FULL dataset (~42 GB). It will take a while.")
print("\nDo you want to continue? (y/n): ", end='')

# For automated download, uncomment below:
# import kaggle
# nih_dir = Path('data/raw/nih_xray')
# nih_dir.mkdir(parents=True, exist_ok=True)
# 
# kaggle.api.dataset_download_files(
#     'nih-chest-xrays/data',
#     path=str(nih_dir),
#     unzip=True
# )

print("\n" + "=" * 70)
print("MANUAL STEPS REQUIRED")
print("=" * 70)
print("\nFor now, I recommend manual download:")
print("1. Visit: https://www.kaggle.com/datasets/nih-chest-xrays/data")
print("2. Click 'Download' (sign in if needed)")
print("3. Extract ZIP to: data/raw/nih_xray/")
print("4. For sample only (2000 images), we can create a script to subset")
print("\n" + "=" * 70)
