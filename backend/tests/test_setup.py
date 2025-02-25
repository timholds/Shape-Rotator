import pytest
import os

def test_environment():
    """Check if test environment is properly set up."""
    # This test validates that pytest is working
    assert True

def test_import_paths():
    """Check if imports work correctly."""
    try:
        # Try importing your core modules
        # breakpoint()
        import backend
        import spaces_storage
        print("✓ Successfully imported core modules")
    except ImportError as e:
        pytest.fail(f"Failed to import modules: {str(e)}")

@pytest.mark.skipif(not os.getenv("SPACES_KEY"), 
                   reason="Skipping Spaces storage tests without credentials")
def test_spaces_credentials():
    """Check if Spaces credentials are set (optional)."""
    # This test only runs if you have SPACES_KEY environment variable
    assert os.getenv("SPACES_KEY"), "SPACES_KEY not set"
    assert os.getenv("SPACES_SECRET"), "SPACES_SECRET not set"
    assert os.getenv("SPACES_BUCKET"), "SPACES_BUCKET not set"
    print("✓ Spaces credentials are configured")