"""Generate data inventory CSV with file metadata."""

import os
import hashlib
import csv
from pathlib import Path
from datetime import datetime

def calculate_sha256(filepath):
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            # Read file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        return f"Error: {str(e)}"

def get_file_metadata(root_dir):
    """Recursively get all files in raw data directory."""
    inventory = []
    root_path = Path(root_dir)
    
    for filepath in root_path.rglob('*'):
        if filepath.is_file():
            # Skip metadata files and README files for hash calculation efficiency
            relative_path = filepath.relative_to(root_path)
            
            # Get file stats
            stats = filepath.stat()
            size_bytes = stats.st_size
            size_mb = size_bytes / (1024 * 1024)
            modified_time = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d')
            
            # Determine data source from path
            path_parts = relative_path.parts
            data_source = path_parts[0] if len(path_parts) > 0 else "unknown"
            
            # Calculate SHA256 (skip for very large files > 50MB to save time)
            if size_mb < 50:
                sha256 = calculate_sha256(filepath)
            else:
                sha256 = "skipped_large_file"
            
            inventory.append({
                'data_source': data_source,
                'file_path': str(relative_path).replace('\\', '/'),
                'file_name': filepath.name,
                'size_bytes': size_bytes,
                'size_mb': f"{size_mb:.2f}",
                'sha256': sha256,
                'last_modified': modified_time,
                'retrieval_date': modified_time  # Using file modification as proxy
            })
    
    return sorted(inventory, key=lambda x: (x['data_source'], x['file_path']))

def write_inventory_csv(inventory, output_file):
    """Write inventory to CSV file."""
    fieldnames = [
        'data_source',
        'file_path',
        'file_name',
        'size_bytes',
        'size_mb',
        'sha256',
        'last_modified',
        'retrieval_date'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(inventory)

if __name__ == '__main__':
    raw_data_dir = 'data/raw'
    output_file = 'reports/data_inventory.csv'
    
    print(f"Scanning {raw_data_dir}...")
    inventory = get_file_metadata(raw_data_dir)
    
    print(f"Found {len(inventory)} files")
    print(f"Writing inventory to {output_file}...")
    write_inventory_csv(inventory, output_file)
    
    # Print summary statistics
    sources = {}
    for item in inventory:
        source = item['data_source']
        if source not in sources:
            sources[source] = {'count': 0, 'total_mb': 0}
        sources[source]['count'] += 1
        sources[source]['total_mb'] += float(item['size_mb'])
    
    print("\nInventory Summary:")
    print("-" * 60)
    for source, stats in sorted(sources.items()):
        print(f"{source:20s}: {stats['count']:4d} files, {stats['total_mb']:10.2f} MB")
    print("-" * 60)
    print(f"{'TOTAL':20s}: {len(inventory):4d} files, {sum(s['total_mb'] for s in sources.values()):10.2f} MB")
    print(f"\nInventory saved to {output_file}")
