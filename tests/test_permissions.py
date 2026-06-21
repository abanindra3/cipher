from jarvis.backend.tools.permissions import PermissionLayer, PermissionLevel


def test_close_app_requires_confirmation():
    decision = PermissionLayer().decide("close_app", {"name": "Chrome"})
    assert decision.level == PermissionLevel.CONFIRM

