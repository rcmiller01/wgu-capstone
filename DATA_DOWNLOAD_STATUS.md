# Data Download Summary

## Status: Partially Complete ⚠️

### ✅ Completed

- **NHANES**: 8 XPT files downloaded (~10 MB)
- **Synthea**: 5,000 synthetic patients generated (~19 GB)
- **VDH**: 2 CSV files downloaded (~5 MB)
  - Virginia WIC Participation Data
  - Health Opportunity Index (HOI)

### ⚠️ Manual Download Required

#### NIH Chest X-Ray Sample - Medium (~0.7 GB for 2000 images)

**Option A: Kaggle (Recommended for sample)**
1. Create Kaggle account: https://www.kaggle.com
2. Get API token:
   - Go to: https://www.kaggle.com/settings
   - Click "Create New API Token"
   - Save `kaggle.json` to: `C:\Users\rober\.kaggle\kaggle.json`
3. Run in terminal:
   ```powershell
   kaggle datasets download -d nih-chest-xrays/sample-data
   ```
4. Extract to: `data/raw/nih_xray/`

**Option B: Direct Download**
1. Visit: https://www.kaggle.com/datasets/nih-chest-xrays/data
2. Sign in to Kaggle
3. Click "Download" button
4. Extract ZIP to: `data/raw/nih_xray/`
5. For sample only, we can create subset script after download

**Option C: NIH Box (Full dataset only - 42 GB)**
- https://nihcc.app.box.com/v/ChestXray-NIHCC
- Download individual tar.gz files
- Not recommended unless you need full dataset

---

## Summary

**Ready to zip:**
- ✅ NHANES (10 MB)
- ✅ Synthea (19 GB)
- ✅ VDH - Virginia WIC Participation Data & Health Opportunity Index (5 MB)

**Optional - Need to download manually:**
- ⚠️ NIH X-Ray sample (~0.7 GB) or full dataset (~42 GB)

**Total size currently:**
- Without NIH: ~19 GB
- With NIH sample: ~20 GB
- With NIH full: ~61 GB

**Recommendation:**
1. ✅ VDH data now complete (WIC + HOI datasets downloaded)
2. Download NIH sample only if needed for X-ray analysis
3. Skip NIH full dataset unless specifically required

---

## Quick Start

VDH data is now complete! For NIH X-ray data (optional):

### Manual Download from Kaggle

```powershell
# Option 1: With Kaggle CLI (after setting up credentials)
kaggle datasets download -d nih-chest-xrays/sample-data
Expand-Archive data.zip -DestinationPath data/raw/nih_xray/

# Option 2: Manual download from Kaggle website
# Visit: https://www.kaggle.com/datasets/nih-chest-xrays/data
# (easier if you don't want to set up Kaggle CLI)
```

---

Generated: 2025-11-11
