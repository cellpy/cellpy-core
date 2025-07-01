"""Test that cellpybase can be imported successfully."""

import sys
from pathlib import Path
import pytest

def test_cellpybase_import():
    """Test that cellpybase can be imported."""
    try:
        import cellpybase
        assert cellpybase is not None
        print("✓ cellpybase imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import cellpybase: {e}")


def test_cellpybase_package_structure():
    """Test that cellpybase has the expected package structure."""
    try:
        import cellpybase
        
        # Check that it's a module
        assert hasattr(cellpybase, '__file__')
        assert hasattr(cellpybase, '__name__')
        assert cellpybase.__name__ == 'cellpybase'
        
        # Check that the package directory exists
        package_dir = Path(cellpybase.__file__).parent
        assert package_dir.exists()
        assert package_dir.is_dir()
        
        print(f"✓ cellpybase package structure verified at {package_dir}")
        
    except ImportError as e:
        pytest.fail(f"Failed to import cellpybase for structure test: {e}")


def test_cellpybase_version():
    """Test that cellpybase has a version attribute (if defined)."""
    try:
        import cellpybase
        
        # Check if version is defined (optional)
        if hasattr(cellpybase, '__version__'):
            assert isinstance(cellpybase.__version__, str)
            print(f"✓ cellpybase version: {cellpybase.__version__}")
        else:
            print("ℹ cellpybase has no __version__ attribute (this is optional)")
            
    except ImportError as e:
        pytest.fail(f"Failed to import cellpybase for version test: {e}")


def test_cellpybase_in_sys_modules():
    """Test that cellpybase is properly registered in sys.modules."""
    assert 'cellpybase' in sys.modules
    print("✓ cellpybase found in sys.modules")
