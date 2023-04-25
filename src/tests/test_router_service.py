"""Test router service."""
from src.router_service import router_service as r


def test_add():
    """Test add function."""
    service = r.RouterService()
    assert service.add(1, 2) == 3
