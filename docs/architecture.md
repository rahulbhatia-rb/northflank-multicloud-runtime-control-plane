# Architecture

This project models a portable runtime contract for workloads deployed across AWS, GCP, and Azure Kubernetes environments.

The design separates developer intent from provider-specific infrastructure. A workload declares its availability, recovery, observability, storage, identity, and cost requirements. A validation layer checks those requirements before deployment.

## Control areas

1. Cloud placement and identity
2. Namespace and resource boundaries
3. Availability and topology
4. Persistent-data readiness
5. Delivery and rollback
6. Metrics, logs, traces, and SLOs
7. Recovery objectives and tested runbooks
8. Cost ownership and lifecycle controls

## Multi-cloud mapping

- AWS: EKS and IAM workload identity
- GCP: GKE and Workload Identity
- Azure: AKS and managed workload identity

The goal is to keep the developer contract consistent while allowing each cloud implementation to use its native primitives.
