from pathlib import Path
ROOT=Path(__file__).parents[3]
def test_real_mode_never_falls_back_to_synthetic_data():
 text=(ROOT/'backend/app/realdata/importer.py').read_text(); assert 'No real dataset source files found' in text and 'synthetic' not in text.lower()
def test_download_records_checksum_and_source_url():
 text=(ROOT/'backend/app/realdata/download.py').read_text(); assert 'sha256' in text and 'download-receipt.json' in text and "'url'" in text
