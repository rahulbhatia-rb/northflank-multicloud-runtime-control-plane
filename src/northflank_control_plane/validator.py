from dataclasses import dataclass


@dataclass(frozen=True)
class Result:
    ok: bool
    messages: list[str]


def validate(spec: dict) -> Result:
    messages: list[str] = []

    if spec.get("cloud") not in {"aws", "gcp", "azure"}:
        messages.append("supported cloud is required")

    if not spec.get("identity_ready"):
        messages.append("workload identity is required")

    if not spec.get("resource_boundaries"):
        messages.append("resource boundaries are required")

    availability = spec.get("availability", {})
    if availability.get("replicas", 0) < 2:
        messages.append("production workloads require at least two replicas")
    if not availability.get("spread"):
        messages.append("topology spread is required")

    recovery = spec.get("recovery", {})
    if not recovery.get("backup"):
        messages.append("backup is required")
    if not recovery.get("restore_tested"):
        messages.append("restore verification is required")

    telemetry = spec.get("telemetry", {})
    for item in ("metrics", "logs", "traces", "slo"):
        if not telemetry.get(item):
            messages.append(f"missing telemetry requirement: {item}")

    delivery = spec.get("delivery", {})
    if not delivery.get("progressive"):
        messages.append("progressive delivery is required")
    if not delivery.get("rollback"):
        messages.append("rollback support is required")

    cost = spec.get("cost", {})
    if not cost.get("owner"):
        messages.append("cost owner is required")
    if not cost.get("ttl"):
        messages.append("resource lifecycle TTL is required")

    return Result(ok=not messages, messages=messages)
