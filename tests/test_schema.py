from pathlib import Path

def test_project_layout():
    for p in ["src","notebooks","data/raw","data/interim","data/processed","docs","references"]:
        assert Path(p).exists(), f"Missing expected path: {p}"
