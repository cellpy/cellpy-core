"""Test that cellpycore can be imported successfully."""

import sys
from pathlib import Path
import pytest

def test_cellpycore_import():
    """Test that cellpycore can be imported."""
    try:
        import cellpycore
        assert cellpycore is not None
        print("✓ cellpycore imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import cellpycore: {e}")


def test_cellpycore_package_structure():
    """Test that cellpycore has the expected package structure."""
    try:
        import cellpycore
        
        # Check that it's a module
        assert hasattr(cellpycore, '__file__')
        assert hasattr(cellpycore, '__name__')
        assert cellpycore.__name__ == 'cellpycore'
        
        # Check that the package directory exists
        package_dir = Path(cellpycore.__file__).parent
        assert package_dir.exists()
        assert package_dir.is_dir()
        
        print(f"✓ cellpycore package structure verified at {package_dir}")
        
    except ImportError as e:
        pytest.fail(f"Failed to import cellpycore for structure test: {e}")


def test_cellpycore_version():
    """Test that cellpycore has a version attribute (if defined)."""
    try:
        import cellpycore
        
        # Check if version is defined (optional)
        if hasattr(cellpycore, '__version__'):
            assert isinstance(cellpycore.__version__, str)
            print(f"✓ cellpycore version: {cellpycore.__version__}")
        else:
            print("ℹ cellpycore has no __version__ attribute (this is optional)")
            
    except ImportError as e:
        pytest.fail(f"Failed to import cellpycore for version test: {e}")


def test_cellpycore_in_sys_modules():
    """Test that cellpycore is properly registered in sys.modules."""
    assert 'cellpycore' in sys.modules
    print("✓ cellpycore found in sys.modules")
