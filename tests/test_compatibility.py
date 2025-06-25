#!/usr/bin/env python3
"""Test backward compatibility of save_links_to_file function"""

from app.fast_discovery import save_links_to_file
import tempfile
from pathlib import Path

def test_backward_compatibility():
    """Test that old signature still works (backward compatibility)"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_filename = temp_file.name

    try:
        # Test old signature without fmt parameter - should default to 'txt'
        test_urls = ['https://example.com/page1', 'https://example.com/page2']
        save_links_to_file(test_urls, temp_filename, verbose=False)
        
        # Read back the content to verify it worked
        content = Path(temp_filename).read_text(encoding='utf-8')
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if lines == test_urls:
            print('✓ Backward compatibility test passed - old signature works')
        else:
            print('✗ Backward compatibility test failed')
            print(f'Expected: {test_urls}')
            print(f'Got: {lines}')
            
        # Test new signature with txt format
        save_links_to_file(test_urls, temp_filename, verbose=False, fmt='txt')
        content = Path(temp_filename).read_text(encoding='utf-8')
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if lines == test_urls:
            print('✓ New signature with fmt="txt" works')
        else:
            print('✗ New signature with fmt="txt" failed')
            
        # Test new signature with csv format
        csv_filename = temp_filename.replace('.txt', '.csv')
        save_links_to_file(test_urls, csv_filename, verbose=False, fmt='csv')
        content = Path(csv_filename).read_text(encoding='utf-8')
        # CSV should have one URL per line, each as a single field
        lines = [line.strip().strip('"') for line in content.split('\n') if line.strip()]
        
        if lines == test_urls:
            print('✓ New signature with fmt="csv" works')
        else:
            print('✗ New signature with fmt="csv" failed')
            print(f'Expected: {test_urls}')
            print(f'Got: {lines}')
            
        Path(csv_filename).unlink()
            
    finally:
        # Clean up
        try:
            Path(temp_filename).unlink()
        except OSError:
            pass

if __name__ == "__main__":
    test_backward_compatibility()
