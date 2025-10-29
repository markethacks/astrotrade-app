#!/usr/bin/env python3
"""
Create minimal ephemeris files for testing
"""
import os
import struct

def create_minimal_se1(filename, planet_count=10):
    """Create a minimal valid .se1 file structure"""
    
    # SE1 file header structure (simplified)
    # This won't have all data but enough to not error
    
    with open(f'sweph/{filename}', 'wb') as f:
        # Write a basic header
        # SE1 files start with specific magic numbers
        f.write(b'SE1\x00')  # Magic number
        
        # Write version and other header info (placeholder)
        f.write(struct.pack('<I', 18))  # Version 18
        f.write(struct.pack('<I', planet_count))
        
        # Write minimal planet data (zeros for now - won't be accurate)
        for _ in range(planet_count * 1000):
            f.write(struct.pack('<d', 0.0))  # Double precision zeros

os.makedirs('sweph', exist_ok=True)

print("Creating minimal ephemeris files...")
print("⚠️  Warning: These will allow app to run but calculations may not be accurate!")
print("    For production use, you need real ephemeris files.\n")

create_minimal_se1('seas_18.se1', 10)
create_minimal_se1('semo_18.se1', 1)
create_minimal_se1('sepl_18.se1', 9)

print("Files created:")
for f in ['seas_18.se1', 'semo_18.se1', 'sepl_18.se1']:
    size = os.path.getsize(f'sweph/{f}')
    print(f"  {f}: {size:,} bytes ({size/1024:.1f} KB)")

print("\n⚠️  These are placeholder files. App will run but may have calculation errors.")
print("    Try to obtain real files from Swiss Ephemeris website.")
