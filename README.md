# Northflank Multi-Cloud Runtime Control Plane

A Northflank-specific cloud infrastructure engineering proof of work focused on the operational problems behind a self-service, multi-cloud developer platform: secure multi-tenancy, Kubernetes workload governance, workload identity, stateful workload safety, availability, recovery, observability, progressive delivery, and cost ownership.

This project is intentionally more than an architecture diagram. It includes an executable production-readiness validator, positive and negative workload contracts, tests, architecture notes, and a practical 30/60/90 hardening roadmap.

## Why this project

Northflank's Cloud Infrastructure Engineer role sits at the intersection of multi-cloud infrastructure, Kubernetes, Infrastructure as Code, secure multi-tenancy, managed stateful services, CI/CD, availability, disaster recovery, observability, and developer experience.

The goal of this repository is to model one possible control-plane layer that turns those platform requirements into explicit, testable workload contracts before a service is promoted into a production environment.

The central idea is simple:

```text
Developer workload contract
        |
        v
Production-readiness validator
        |
        +--> cloud/platform checks
        +--> workload identity checks
        +--> resource-boundary checks
        +--> HA / topology checks
        +--> backup / restore checks
        +--> observability / SLO checks
        +--> progressive-delivery checks
        +--> cost-ownership checks
        |
        v
ALLOW or DENY
```

A workload that satisfies the platform contract is accepted. A workload missing critical production controls is denied with explicit reasons.

## What is implemented

### 1. Multi-cloud workload contract

The validator accepts workload metadata that represents a deployment targeting a supported cloud environment. The current proof of concept models AWS, GCP, and Azure as target platforms while keeping the policy model cloud-neutral where possible.

This reflects the reality of a platform engineering team that wants consistent operational guarantees even when the underlying infrastructure differs by provider.

### 2. Workload identity

Production workloads are expected to use a defined workload-identity mechanism instead of relying on long-lived static credentials.

The contract checks whether workload identity is explicitly ready before production admission.

In a real implementation this could map to mechanisms such as:

- AWS IAM Roles for Service Accounts / EKS Pod Identity
- GCP Workload Identity
- Azure Workload Identity

The policy intent is the same across clouds: application workloads should receive narrowly scoped, short-lived identity rather than embedded infrastructure credentials.

### 3. Resource and tenant boundaries

Northflank operates a self-service platform, which makes resource boundaries and tenant isolation first-class operational concerns.

The project therefore models resource-boundary readiness as a production requirement. In a production implementation, this would expand into controls such as:

- Kubernetes namespaces and RBAC
- ResourceQuota and LimitRange
- network policies
- workload security contexts
- node-pool / runtime-class isolation where required
- tenant-aware ingress and service exposure
- cloud IAM boundaries

The goal is to prevent one workload from becoming an uncontrolled noisy neighbor or security boundary violation for another.

### 4. High availability

The validator checks that production workloads declare sufficient redundancy and topology awareness.

The current contract models:

- multiple replicas
- spread across failure domains

In a real Northflank-style runtime, this could become enforcement for:

- pod anti-affinity
- topology spread constraints
- multi-zone node pools
- PodDisruptionBudgets
- autoscaling boundaries
- graceful node draining

This is especially important for a platform that abstracts infrastructure away from application developers: the platform should make the safe path the default path.

### 5. Stateful workload safety and disaster recovery

Managed databases and other persistent workloads need stronger guarantees than simply 'the pod restarted successfully.'

The contract therefore requires both:

- backup readiness
- tested restore capability

This distinction matters because a backup that has never been restored is not a proven recovery mechanism.

A production version of the policy could additionally validate:

- backup frequency
- retention windows
- RPO / RTO targets
- replication topology
- encryption
- storage-class requirements
- cross-region recovery
- restore-test recency

### 6. Observability and SLOs

A workload should not reach production if the platform cannot tell whether it is healthy.

The current validator expects:

- metrics
- logs
- traces
- an explicit SLO

This models a platform where observability is part of the deployment contract rather than a post-launch cleanup task.

A production implementation could automatically provision or validate:

- Prometheus metrics
- centralized logs
- OpenTelemetry traces
- dashboards
- alerts
- burn-rate alerts
- service-level objectives
- ownership metadata

### 7. Progressive delivery and rollback

The project treats deployment safety as part of infrastructure readiness.

Production contracts are expected to declare:

- progressive rollout capability
- rollback capability

This can map to patterns such as:

- canary deployments
- blue/green deployments
- Argo Rollouts
- health-based deployment gates
- automated rollback on failed SLO or health signals

The objective is to reduce deployment blast radius rather than relying on a human to manually recover every bad release.

### 8. Cost ownership

Cloud platforms fail operationally when infrastructure cost becomes nobody's responsibility.

The validator therefore requires explicit cost ownership and lifecycle controls.

The current model checks:

- workload cost ownership
- TTL / lifecycle handling

This could be extended into:

- team/project cost attribution
- labels/tags
- budget thresholds
- environment expiry
- preview-environment TTLs
- idle workload detection
- rightsizing signals
- storage lifecycle policies

This matters particularly for self-service infrastructure, where platform convenience can otherwise create invisible long-lived cost.

## Safe and unsafe contracts

The repository deliberately includes both positive and negative examples.

### Production-ready example

`examples/ready.json`

The ready contract represents a workload that has the expected production controls: supported cloud, workload identity, resource boundaries, HA, tested recovery, observability, progressive delivery, rollback, and cost ownership.

The validator should return an allow decision.

### Incomplete example

`examples/not_ready.json`

The incomplete contract deliberately omits production requirements.

The validator should deny it and return the missing controls as human-readable messages.

This is an important design choice: the project demonstrates enforcement behavior instead of showing only the happy path.

## Repository structure

```text
northflank-multicloud-runtime-control-plane/
├── README.md
├── pyproject.toml
├── src/
│   └── northflank_control_plane/
│       ├── __init__.py
│       ├── validator.py
│       └── cli.py
├── examples/
│   ├── ready.json
│   └── not_ready.json
├── tests/
│   └── test_validator.py
└── docs/
    ├── architecture.md
    └── 30-60-90.md
```

## Running the project

Create a virtual environment if desired, then install the package locally:

```bash
python -m pip install -e .
```

Run the validator against the production-ready contract:

```bash
northflank-validate examples/ready.json
```

Run it against the intentionally incomplete contract:

```bash
northflank-validate examples/not_ready.json
```

Run the test suite:

```bash
python -m pytest
```

## Validation behavior

At a high level, the validator evaluates the contract and returns:

```text
Contract
   |
   +-- supported cloud?
   +-- workload identity ready?
   +-- resource boundaries defined?
   +-- HA configured?
   +-- backup + restore tested?
   +-- metrics/logs/traces/SLO present?
   +-- progressive delivery + rollback?
   +-- cost owner + lifecycle policy?
   |
   +-- all true --> ALLOW
   |
   +-- any missing --> DENY + reasons
```

The implementation is deliberately small enough to review quickly while still demonstrating the core platform-engineering pattern: **production requirements should be machine-enforced wherever practical.**

## How I would extend this for a real platform

### Kubernetes admission

Move the workload contract behind an admission layer so policy can be evaluated before Kubernetes resources are accepted.

Potential approaches include:

- OPA Gatekeeper
- Kyverno
- ValidatingAdmissionPolicy
- a dedicated platform admission service

### Multi-cloud provider adapters

Keep the high-level contract provider-neutral while implementing cloud-specific checks underneath it.

For example:

```text
Production contract
      |
      v
Common policy model
   /      |      \
 AWS     GCP    Azure
adapter  adapter adapter
```

This avoids forcing application teams to understand every cloud-specific implementation detail while preserving strong platform guarantees.

### Stateful service classes

Introduce explicit service classes for PostgreSQL, MongoDB, Redis, Kafka, object storage, and other stateful offerings.

Each class could have its own contract covering:

- replication
- backup
- recovery
- storage performance
- maintenance windows
- encryption
- upgrade strategy

### Tenant isolation levels

Not every workload needs the same isolation model. The platform could support explicit tiers such as:

- shared namespace
- dedicated namespace
- dedicated node pool
- sandboxed runtime
- dedicated cluster
- customer-owned cloud / cluster

The admission contract can then enforce the controls associated with the selected isolation tier.

### Runtime isolation

For higher-risk workloads, the platform could introduce additional runtime boundaries using technologies such as:

- gVisor
- Kata Containers
- KVM-backed isolation
- dedicated nodes

This is particularly relevant to self-service platforms where arbitrary customer workloads may share underlying infrastructure.

### Service mesh / network policy

Extend the contract to cover service-to-service communication and workload exposure:

- default-deny ingress and egress
- explicit service dependencies
- mTLS
- workload identity
- Envoy/Istio/Linkerd policy
- controlled external egress

### CI/CD integration

The validator is designed to fit into a deployment pipeline before production promotion:

```text
Pull request
    |
    v
Build + test
    |
    v
Infrastructure / workload contract
    |
    v
Northflank readiness validation
    |
    +-- deny --> PR/deployment fails with reasons
    |
    +-- allow
          |
          v
Progressive deployment
          |
          v
Health / SLO validation
          |
          v
Production
```

The goal is for infrastructure and workload policy to follow the same review-and-deploy workflow as application code.

## Architecture principles demonstrated

### Platform guardrails over platform tickets

Developers should not need to open an infrastructure ticket for every standard deployment concern. The platform should expose a safe contract and automate the implementation behind it.

### Secure defaults

Identity, isolation, observability, recovery, and cost controls should be defaults or enforced requirements—not optional wiki recommendations.

### Explicit ownership

Production workloads need clear service ownership, operational ownership, and cost ownership.

### Recovery must be tested

Backup configuration alone is insufficient. Restore testing should be part of the platform's operational posture.

### Provider abstraction without lowest-common-denominator design

A multi-cloud platform benefits from a common workload contract, but cloud-specific capabilities should still be used behind that abstraction where they improve security, reliability, or performance.

### Stateful infrastructure is a product

Databases and persistent services should have well-defined operational contracts rather than being treated as generic pods with volumes.

## 30 / 60 / 90 day evolution plan

A more complete version of this work would progress approximately as follows.

### First 30 days — establish the production contract

- map existing workload classes and deployment paths
- identify tenant-isolation boundaries
- inventory AWS/GCP/Azure differences
- define minimum production-readiness controls
- standardize workload identity
- baseline metrics/logs/traces/SLO requirements
- inventory stateful offerings and backup posture
- introduce machine-readable service ownership and cost ownership
- establish a common workload contract

### Days 31–60 — automate enforcement

- integrate policy validation into CI/CD
- introduce Kubernetes admission controls
- add cloud-specific provider adapters
- standardize network policies and external exposure
- automate observability registration
- validate backup and restore posture
- add progressive delivery and automated rollback gates
- introduce environment TTLs and cost attribution
- build a platform scorecard showing readiness per service

### Days 61–90 — harden the platform at scale

- introduce isolation tiers for higher-risk workloads
- evaluate gVisor/Kata/KVM where stronger runtime isolation is justified
- harden stateful service classes
- add chaos/failure testing for critical platform paths
- run restore drills and multi-zone/multi-region exercises
- introduce SLO-based deployment gates
- establish platform capacity and cost forecasting
- identify recurring developer friction and turn it into self-service automation

## Why this is relevant to Northflank

Northflank abstracts a substantial amount of cloud infrastructure complexity away from developers while still having to preserve strong guarantees around reliability, tenancy, security, stateful services, delivery, and cost.

That creates an interesting platform-engineering problem: the easier infrastructure becomes to consume, the more important it becomes for the platform itself to encode the correct operational defaults.

This proof of work demonstrates how I think about that problem: turn platform expectations into explicit contracts, make the contracts executable, return understandable failure reasons, and gradually move the controls into the deployment path so developers get a fast self-service experience without bypassing production discipline.

## Background behind the exercise

I built this repository specifically as a hands-on response to Northflank's Cloud Infrastructure Engineer role. My background is in cloud/platform engineering and SRE across AWS and GCP, including Kubernetes/EKS/GKE, Terraform, CI/CD, networking, IAM/security, observability, reliability, production troubleshooting, and infrastructure cost optimization.

The repository is intended to make the application concrete: rather than only saying I have worked on platform infrastructure, it shows the kind of control-plane and production-readiness model I would explore for a multi-cloud developer platform.

---

**Author:** Rahul H Bhatia

LinkedIn: https://www.linkedin.com/in/rahul-h-bhatia/

Portfolio: https://rahulhbhatia.vercel.app

Credly: https://www.credly.com/users/rahul-h-bhatia/badges
