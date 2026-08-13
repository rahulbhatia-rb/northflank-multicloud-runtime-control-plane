from northflank_control_plane import validate


def test_ready_contract_is_allowed():
    spec = {
        "cloud": "gcp",
        "identity_ready": True,
        "resource_boundaries": True,
        "availability": {"replicas": 2, "spread": True},
        "recovery": {"backup": True, "restore_tested": True},
        "telemetry": {"metrics": True, "logs": True, "traces": True, "slo": True},
        "delivery": {"progressive": True, "rollback": True},
        "cost": {"owner": True, "ttl": True},
    }
    assert validate(spec).ok is True


def test_incomplete_contract_is_rejected():
    spec = {"cloud": "aws"}
    result = validate(spec)
    assert result.ok is False
    assert result.messages
