"""Static seed content: the 7-phase roadmap, resources and project templates.

Everything here is *shared* content. Per-user progress is created separately
(see :mod:`app.db.seed`).
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Roadmap phases
# ---------------------------------------------------------------------------
# key, title, summary, month_label, duration_months, accent, project_brief
PHASES: list[dict[str, Any]] = [
    {
        "key": "phase-1",
        "title": "Java, SQL and Git",
        "summary": (
            "Build the foundation: write real Java, understand how the JVM runs your code, "
            "speak SQL fluently and put everything under version control."
        ),
        "month_label": "Month 1",
        "duration_months": 1,
        "accent": "amber",
        "project_brief": "Java command-line expense tracker with PostgreSQL.",
    },
    {
        "key": "phase-2",
        "title": "Spring Boot and REST APIs",
        "summary": (
            "Turn the Java foundations into a production-shaped service: dependency injection, "
            "layered architecture, JPA, validation and database migrations."
        ),
        "month_label": "Months 2-3",
        "duration_months": 2,
        "accent": "emerald",
        "project_brief": "Personal finance REST API with PostgreSQL.",
    },
    {
        "key": "phase-3",
        "title": "Security, Testing and Advanced Backend",
        "summary": (
            "Harden the API: authentication, authorization, a full test pyramid, query tuning, "
            "caching and asynchronous processing."
        ),
        "month_label": "Months 4-5",
        "duration_months": 2,
        "accent": "sky",
        "project_brief": "Secure multi-user finance API with automated tests.",
    },
    {
        "key": "phase-4",
        "title": "Linux, Networking and Docker",
        "summary": (
            "Operate what you build: live in the shell, read a network stack, and package the "
            "API into reproducible containers."
        ),
        "month_label": "Month 6",
        "duration_months": 1,
        "accent": "violet",
        "project_brief": "Containerized Spring Boot API and PostgreSQL using Docker Compose.",
    },
    {
        "key": "phase-5",
        "title": "CI/CD and Cloud",
        "summary": (
            "Automate the path to production: pipelines, quality gates, image publishing, "
            "secrets and a real AWS deployment."
        ),
        "month_label": "Months 7-8",
        "duration_months": 2,
        "accent": "orange",
        "project_brief": "Publicly deployed Spring Boot API with automated CI/CD.",
    },
    {
        "key": "phase-6",
        "title": "Kubernetes, Infrastructure and Observability",
        "summary": (
            "Run at scale: schedule workloads, wire ingress, autoscale, provision infrastructure "
            "as code and watch it with metrics, logs and dashboards."
        ),
        "month_label": "Months 9-10",
        "duration_months": 2,
        "accent": "indigo",
        "project_brief": "Kubernetes deployment with monitoring and recovery documentation.",
    },
    {
        "key": "phase-7",
        "title": "Capstone, Interviews and Job Applications",
        "summary": (
            "Ship the portfolio, rehearse the interviews and turn twelve months of work into "
            "an offer."
        ),
        "month_label": "Months 11-12",
        "duration_months": 2,
        "accent": "rose",
        "project_brief": (
            "Production-style backend platform with security, CI/CD, containers, monitoring "
            "and deployment documentation."
        ),
    },
    # --- DSA: a parallel track that runs alongside the core roadmap ---------
    {
        "key": "dsa-1",
        "title": "DSA Foundations",
        "summary": (
            "Build the data-structure vocabulary interviews expect: complexity, arrays, hashing, "
            "two pointers, stacks, linked lists, sorting and trees. Run this track in parallel "
            "with the core roadmap so problem solving grows alongside backend skills."
        ),
        "month_label": "Parallel · months 1-4",
        "duration_months": 4,
        "accent": "cyan",
        "track": "dsa",
        "project_brief": (
            "Keep a personal algorithm notebook: 100 solved problems grouped by pattern, each "
            "with the approach, complexity and one thing you would do differently."
        ),
    },
    {
        "key": "dsa-2",
        "title": "DSA Interview Patterns",
        "summary": (
            "Move from individual data structures to the reusable patterns that show up in "
            "interviews: graphs, heaps, backtracking, greedy, dynamic programming and timed "
            "mock interviews."
        ),
        "month_label": "Parallel · months 5-9",
        "duration_months": 5,
        "accent": "teal",
        "track": "dsa",
        "project_brief": (
            "Complete 150 curated problems and six timed mock interviews, then review every "
            "mistake until the pattern is automatic."
        ),
    },
]

# ---------------------------------------------------------------------------
# Topics
# ---------------------------------------------------------------------------
# (title, description, category, estimated_minutes, subtopics)
TOPICS: dict[str, list[tuple[str, str, str, int, list[str]]]] = {
    "phase-1": [
        (
            "Java syntax, methods, classes and OOP",
            "Variables, control flow, methods, classes, objects, encapsulation, constructors, "
            "static members and the difference between primitives and reference types.",
            "Java",
            240,
            [
                "Variables, types and operators",
                "Conditionals and loops",
                "Methods, parameters and overloading",
                "Classes, objects and constructors",
                "Fields, `this`, static and instance state",
                "Encapsulation with getters/setters",
                "Records and immutable value objects",
                "Maven/Gradle project layout",
            ],
        ),
        (
            "Interfaces, inheritance, abstraction and encapsulation",
            "Contract-first design with interfaces, code reuse through inheritance, abstract "
            "classes and designing for extension without fragile base classes.",
            "Java",
            210,
            [
                "Interfaces and default methods",
                "Abstract classes vs interfaces",
                "Method overriding and polymorphism",
                "The Liskov substitution principle",
                "Designing small, focused interfaces",
                "Composition over inheritance",
            ],
        ),
        (
            "Collections, generics and exception handling",
            "Working with List/Set/Map, writing type-safe generic code, and designing robust "
            "error handling with checked and unchecked exceptions.",
            "Java",
            240,
            [
                "List, Set and Map hierarchies",
                "ArrayList vs LinkedList vs ArrayDeque",
                "HashMap, LinkedHashMap, TreeMap",
                "Type parameters and bounded generics",
                "Try-with-resources",
                "Custom exceptions and error contracts",
            ],
        ),
        (
            "Streams, lambdas and Optional",
            "Functional programming in Java: lambda expressions, method references, the Stream "
            "pipeline and the pitfalls of Optional misuse.",
            "Java",
            180,
            [
                "Functional interfaces and @FunctionalInterface",
                "Lambda syntax and method references",
                "Intermediate vs terminal stream operations",
                "Collectors: grouping, partitioning, joining",
                "Parallel streams and when not to use them",
                "Optional as a return type",
            ],
        ),
        (
            "Basic concurrency and JVM fundamentals",
            "Threads, executors, thread safety and how the JVM manages memory, garbage "
            "collection and class loading.",
            "Java",
            210,
            [
                "Thread lifecycle and Runnable vs Callable",
                "ExecutorService and thread pools",
                "synchronized, volatile and atomic classes",
                "Concurrent collections",
                "JVM memory model and heap vs stack",
                "Garbage collection basics (G1, ZGC)",
                "Reading a thread dump",
            ],
        ),
        (
            "SQL SELECT, filtering, sorting and aggregation",
            "The core of relational thinking: projecting columns, filtering rows, ordering "
            "results and computing aggregates with GROUP BY.",
            "Databases",
            180,
            [
                "SELECT, WHERE and operators",
                "IN, BETWEEN, LIKE and NULL semantics",
                "ORDER BY and LIMIT",
                "COUNT, SUM, AVG, MIN, MAX",
                "GROUP BY and HAVING",
                "Aliases and common table expressions",
            ],
        ),
        (
            "Joins, subqueries, indexes and transactions",
            "Combining tables, nesting queries, making them fast and keeping data consistent "
            "under concurrency.",
            "Databases",
            210,
            [
                "INNER vs LEFT vs FULL JOIN",
                "Self joins and anti-joins",
                "Subqueries vs CTEs",
                "B-tree indexes and read/write trade-offs",
                "Composite and partial indexes",
                "EXPLAIN ANALYZE",
                "ACID, isolation levels and deadlocks",
            ],
        ),
        (
            "Database keys and relationships",
            "Primary keys, foreign keys, cardinality and modelling one-to-many, many-to-many "
            "and one-to-one relationships.",
            "Databases",
            120,
            [
                "Primary keys and natural vs surrogate keys",
                "Foreign keys and referential integrity",
                "One-to-one, one-to-many, many-to-many",
                "Junction tables and resolution strategies",
                "Normalisation 1NF-3NF",
                "Modelling an expense tracker domain",
            ],
        ),
        (
            "Git, GitHub, branches, merges and pull requests",
            "A reliable Git workflow: commits, branches, rebases, merges, pull requests and "
            "resolving conflicts without fear.",
            "CI/CD",
            150,
            [
                "Staging area, commits and the DAG",
                "Branching strategies",
                "Rebase vs merge",
                "Resolving merge conflicts",
                "Pull request review workflow",
                "GitHub issues, projects and actions",
                ".gitignore and repository hygiene",
            ],
        ),
    ],
    "phase-2": [
        (
            "Spring Boot setup and project structure",
            "Bootstrapping a Spring Boot application, understanding auto-configuration, the "
            "starter system and how to structure a multi-module project.",
            "Spring Boot",
            180,
            [
                "Spring Initializr and project anatomy",
                "Auto-configuration and starters",
                "Application properties and profiles",
                "Layered package structure",
                "Maven vs Gradle",
                "Running and packaging the app",
            ],
        ),
        (
            "Dependency injection and configuration",
            "How the IoC container works, constructor injection, component scanning, bean "
            "lifecycles and typed configuration properties.",
            "Spring Boot",
            180,
            [
                "The application context",
                "Bean scopes and lifecycle",
                "Constructor vs field injection",
                "@Component, @Service, @Repository",
                "@Configuration and @Bean",
                "@ConfigurationProperties and validation",
            ],
        ),
        (
            "Controllers, services, repositories and DTOs",
            "Separating concerns across the layers and keeping the domain model away from the "
            "wire format.",
            "Spring Boot",
            210,
            [
                "@RestController and @RequestMapping",
                "Request/response DTOs and mapping",
                "Service layer responsibilities",
                "Entity vs DTO vs VO",
                "ModelMapper / MapStruct",
                "Avoiding anemic domain models",
            ],
        ),
        (
            "REST methods, HTTP status codes and API design",
            "Designing an API that is predictable for consumers: resource naming, verbs, "
            "status codes, pagination conventions and versioning.",
            "Spring Boot",
            180,
            [
                "Resource-oriented URL design",
                "Idempotency and safe methods",
                "Status code selection (200/201/204/400/404/409)",
                "Consistent error payloads",
                "API versioning strategies",
                "OpenAPI specification basics",
            ],
        ),
        (
            "Spring Data JPA and Hibernate",
            "Mapping objects to tables, declaring repositories, understanding entity lifecycle "
            "events and avoiding lazy-loading surprises.",
            "Spring Boot",
            240,
            [
                "Entity, Id, GeneratedValue",
                "Repositories and derived queries",
                "JPQL vs native SQL",
                "Entity lifecycle callbacks",
                "N+1 problems and fetch strategies",
                "Hibernate and JPA dialect differences",
            ],
        ),
        (
            "Entity relationships and transaction management",
            "One-to-many, many-to-many and one-to-one mappings plus the @Transactional "
            "semantics that keep writes atomic.",
            "Spring Boot",
            210,
            [
                "Relationship annotations and cascade",
                "Fetch types and owning side",
                "@Transactional propagation and rollback rules",
                "Read-only transactions",
                "Avoiding lazy initialization exceptions",
                "Testing transactional code",
            ],
        ),
        (
            "Request validation and global exception handling",
            "Bean Validation on the edges and a single, predictable error contract for the "
            "whole API.",
            "Spring Boot",
            150,
            [
                "@Valid and constraint annotations",
                "Custom validators",
                "Handling MethodArgumentNotValidException",
                "@ControllerAdvice and @ExceptionHandler",
                "ProblemDetail / RFC 9457 error format",
                "Consistent error response schema",
            ],
        ),
        (
            "Pagination, sorting and filtering",
            "Returning large collections safely with offset or cursor pagination, dynamic "
            "sorting and filter parameter binding.",
            "Spring Boot",
            120,
            [
                "Spring Data Pageable and Page",
                "Offset vs cursor pagination",
                "Dynamic sorting with Sort",
                "Specification / Criteria API filters",
                "Pagination response metadata",
            ],
        ),
        (
            "Logging and application configuration",
            "Structured, readable logs with correlation IDs plus externalised, "
            "environment-driven configuration.",
            "Spring Boot",
            120,
            [
                "SLF4J and Logback configuration",
                "Log levels and profiles",
                "Externalised configuration precedence",
                "Config validation on startup",
                "Request correlation IDs",
            ],
        ),
        (
            "Flyway database migrations",
            "Version-controlled, repeatable and safe database schema changes with Flyway.",
            "Databases",
            120,
            [
                "Why schema changes are code",
                "Versioned migration scripts",
                "Baseline and repeatable migrations",
                "Running migrations in tests",
                "Rollback strategy and data migrations",
            ],
        ),
    ],
    "phase-3": [
        (
            "Spring Security filter chain",
            "How every request flows through the security filter chain and how to customise "
            "it for a stateless API.",
            "Security",
            210,
            [
                "The filter chain and SecurityFilterChain beans",
                "Stateless session management",
                "Authentication vs authorization filters",
                "Method security",
                "Customising the UserDetailsService",
            ],
        ),
        (
            "Password hashing using BCrypt",
            "Correctly hashing, salting and verifying passwords, and why plaintext or fast "
            "hashes are unacceptable.",
            "Security",
            90,
            [
                "Why one-way hashing for passwords",
                "BCrypt, salt rounds and cost",
                "Verification and constant-time comparison",
                "Password policies and breach checks",
            ],
        ),
        (
            "Authentication and authorization",
            "Authenticating users reliably and enforcing rules that only the owner may "
            "access their own data.",
            "Security",
            210,
            [
                "AuthenticationProvider flow",
                "UserDetailsService and PasswordEncoder beans",
                "Authorization rules with request matchers",
                "Object-level (ownership) authorization",
                "Denial by default",
            ],
        ),
        (
            "JWT access tokens and refresh-token lifecycle",
            "Issuing short-lived access tokens, rotating refresh tokens, and revoking sessions "
            "safely.",
            "Security",
            240,
            [
                "JWT anatomy: header, payload, signature",
                "Claims: sub, exp, iat, jti, scope",
                "Signing algorithms and key management",
                "Refresh token rotation and reuse detection",
                "Revocation and logout",
                "Token storage trade-offs",
            ],
        ),
        (
            "Role-based access control and resource ownership",
            "Combining roles with ownership checks so a valid token is still not enough to "
            "read someone else's records.",
            "Security",
            180,
            [
                "Roles vs authorities",
                "@PreAuthorize and @PostAuthorize",
                "Ownership guards in services",
                "Admin vs regular user flows",
                "IDOR prevention",
            ],
        ),
        (
            "CORS, CSRF and common web vulnerabilities",
            "Browser security primitives and the classic vulnerability classes you must "
            "defend against.",
            "Security",
            150,
            [
                "Same-origin policy and CORS headers",
                "CSRF attacks and when CSRF protection matters",
                "SQL and command injection defences",
                "XSS and output encoding",
                "Rate limiting and brute force protection",
                "Security headers",
            ],
        ),
        (
            "JUnit 5 and Mockito",
            "Fast, readable unit tests for services and controllers using the modern JUnit 5 "
            "platform.",
            "Java",
            180,
            [
                "JUnit 5 lifecycle and assertions",
                "Parametrised and nested tests",
                "Mockito stubs, mocks and verification",
                "Argument captors and lenient stubbing",
                "Test class design and naming",
            ],
        ),
        (
            "Integration testing with Testcontainers",
            "Running real PostgreSQL, Redis and other services in tests so integration bugs "
            "are caught early.",
            "Java",
            210,
            [
                "Why containerised integration tests",
                "Testcontainers lifecycle and reuse",
                "Dynamic properties for the datasource",
                "Testing Flyway migrations in CI",
                "Keeping the test suite fast",
            ],
        ),
        (
            "Spring Security testing",
            "Testing authenticated and unauthorised paths with the Spring Security test "
            "support.",
            "Security",
            150,
            [
                "@WithMockUser and @WithUserDetails",
                "mockMvc and webTestClient security support",
                "Testing 401 vs 403",
                "Testing the JWT filter",
                "Testing authorization rules",
            ],
        ),
        (
            "SQL query optimization and indexing",
            "Reading execution plans and fixing slow queries with the right indexes and query "
            "shapes.",
            "Databases",
            180,
            [
                "EXPLAIN / EXPLAIN ANALYZE",
                "Composite index column order",
                "Covering indexes",
                "Avoiding N+1 in SQL",
                "Pagination performance",
                "Connection pool tuning (HikariCP)",
            ],
        ),
        (
            "Transactions and isolation",
            "Choosing the right isolation level and understanding how concurrency affects "
            "your reads and writes.",
            "Databases",
            150,
            [
                "Isolation levels and anomalies",
                "Optimistic vs pessimistic locking",
                "Deadlock detection and retry",
                "Read consistency patterns",
                "Idempotent write operations",
            ],
        ),
        (
            "Redis caching",
            "Reducing database load with caching, and knowing when a cache becomes a source "
            "of stale truth.",
            "Databases",
            150,
            [
                "Cache-aside and write-through patterns",
                "TTL and eviction policies",
                "Cache invalidation strategies",
                "Avoiding cache stampedes",
                "Spring Data Redis templates",
                "Serialisation formats",
            ],
        ),
        (
            "Asynchronous processing and messaging fundamentals",
            "Moving slow work off the request thread with queues, events and idempotent "
            "consumers.",
            "Spring Boot",
            180,
            [
                "Why async and when not to use it",
                "@Async and task executors",
                "Message brokers and delivery guarantees",
                "Idempotent consumers",
                "Dead letter queues",
                "Outbox pattern",
            ],
        ),
    ],
    "phase-4": [
        (
            "Linux filesystem, permissions, users and groups",
            "Navigating and securing a Linux system: paths, ownership, permissions and the "
            "user/group model.",
            "Linux",
            150,
            [
                "Filesystem hierarchy and FHS",
                "Users, groups and /etc/passwd",
                "chmod, chown and the permission bits",
                "Special bits and umask",
                "File types and symlinks",
            ],
        ),
        (
            "Processes, services, SSH and shell commands",
            "Controlling running processes and remote access with confidence.",
            "Linux",
            150,
            [
                "ps, top, kill and signals",
                "systemd units and systemctl",
                "Cron and systemd timers",
                "SSH keys, config and tunneling",
                "Essential shell commands and pipes",
                "Shell scripting basics",
            ],
        ),
        (
            "CPU, memory, disk and log troubleshooting",
            "Diagnosing a slow or unhealthy machine using the right tools.",
            "Linux",
            150,
            [
                "top, htop and load average",
                "free, vmstat and iostat",
                "df, du and disk inode exhaustion",
                "journalctl and log rotation",
                "strace and lsof",
                "Reading the dmesg output",
            ],
        ),
        (
            "Bash scripting fundamentals",
            "Automating repetitive work reliably with variables, control flow, functions and "
            "error handling.",
            "Linux",
            120,
            [
                "Shebangs, variables and quoting",
                "Conditionals and loops",
                "Functions and argument passing",
                "Exit codes and `set -euo pipefail`",
                "Pipes, redirections and process substitution",
            ],
        ),
        (
            "IP addresses, DNS, TCP, HTTP and TLS",
            "How a request actually travels across the network.",
            "Linux",
            180,
            [
                "IPv4/IPv6 addressing and CIDR",
                "DNS resolution and records",
                "TCP handshake, keepalive and TIME_WAIT",
                "HTTP/1.1 vs HTTP/2 vs HTTP/3",
                "TLS handshake and certificates",
                "curl, dig and traceroute",
            ],
        ),
        (
            "Ports, firewalls and reverse proxies",
            "Exposing a service safely through Nginx or a load balancer.",
            "Linux",
            150,
            [
                "Listening sockets and port binding",
                "iptables and ufw basics",
                "Nginx as a reverse proxy",
                "Proxy headers and X-Forwarded-For",
                "TLS termination at the proxy",
                "Rate limiting at the edge",
            ],
        ),
        (
            "Docker images, containers and Dockerfiles",
            "Packaging an application and its runtime into a reproducible image.",
            "Docker",
            180,
            [
                "Images, layers and the registry",
                "Writing an efficient Dockerfile",
                "Container lifecycle and logs",
                "Volumes and bind mounts",
                "Networking between containers",
                "Container resource limits",
            ],
        ),
        (
            "Docker Compose, volumes and networks",
            "Running the whole stack locally with one command.",
            "Docker",
            120,
            [
                "compose.yaml structure",
                "Service dependencies and healthchecks",
                "Named volumes and data persistence",
                "Custom networks",
                "Environment configuration and .env",
                "Profiles for local variants",
            ],
        ),
        (
            "Multi-stage builds and health checks",
            "Producing small, safe, self-monitoring images.",
            "Docker",
            120,
            [
                "Multi-stage Dockerfiles",
                "Layer caching strategies",
                "Running as a non-root user",
                "HEALTHCHECK definitions",
                "Image size and vulnerability scanning",
            ],
        ),
    ],
    "phase-5": [
        (
            "GitHub Actions workflows",
            "Authoring CI workflows that run on every push and pull request.",
            "CI/CD",
            150,
            [
                "Workflow, job, step and action anatomy",
                "Triggers: push, pull_request, schedule",
                "Matrix builds and caching",
                "Reusable workflows and composite actions",
                "Self-hosted runners",
            ],
        ),
        (
            "Automated builds and tests",
            "Making the pipeline prove the code works on every change.",
            "CI/CD",
            150,
            [
                "Running unit and integration tests",
                "Testcontainers in CI",
                "Caching dependencies and layers",
                "Parallelising the test suite",
                "Publishing test reports",
                "Failing fast on flaky tests",
            ],
        ),
        (
            "Code quality checks",
            "Static analysis, formatting and lint gates that keep the codebase consistent.",
            "CI/CD",
            120,
            [
                "Checkstyle / Spotless / formatting",
                "Static analysis with SpotBugs",
                "Pre-commit hooks",
                "Coverage reports and thresholds",
                "Dependency vulnerability scanning",
            ],
        ),
        (
            "Docker image building and publishing",
            "Building once and promoting the same artifact through environments.",
            "CI/CD",
            150,
            [
                "Building images in the pipeline",
                "Tagging strategies and immutability",
                "Pushing to Docker Hub / GHCR",
                "Caching image layers in CI",
                "Scanning images for CVEs",
            ],
        ),
        (
            "Continuous deployment",
            "Promoting builds automatically and safely to running environments.",
            "CI/CD",
            150,
            [
                "Deployment environments",
                "Pull request previews",
                "Blue/green and rolling strategies",
                "Feature flags",
                "Automated smoke tests after deploy",
                "Rollback procedures",
            ],
        ),
        (
            "Secure secret management",
            "Keeping credentials out of code and logs.",
            "CI/CD",
            120,
            [
                "GitHub Actions secrets vs variables",
                "OIDC / short-lived cloud credentials",
                "Least privilege for CI identities",
                "Rotating secrets",
                "Scanning for committed secrets",
            ],
        ),
        (
            "AWS IAM, VPC, subnets and security groups",
            "The AWS network and identity foundation.",
            "Cloud",
            180,
            [
                "IAM policies, roles and the credential chain",
                "VPC, subnets and route tables",
                "Public vs private subnets",
                "Security groups and NACLs",
                "NAT gateways and egress",
                "Cost implications of network design",
            ],
        ),
        (
            "EC2, S3 and managed databases",
            "Running the workload on proven managed infrastructure.",
            "Cloud",
            180,
            [
                "EC2 instance families and selection",
                "RDS / Aurora PostgreSQL",
                "S3 buckets, policies and lifecycle rules",
                "Elastic Load Balancing",
                "Elastic Beanstalk / App Runner",
                "Autoscaling groups",
            ],
        ),
        (
            "HTTPS and DNS",
            "Serving the application over TLS with a reliable domain.",
            "Cloud",
            120,
            [
                "Route 53 hosted zones and records",
                "Domain registration and DNS propagation",
                "ACM certificates and renewal",
                "ALB with HTTPS listeners",
                "HSTS and secure headers",
            ],
        ),
        (
            "Backups, recovery and cloud cost management",
            "Protecting the data and keeping the bill sane.",
            "Cloud",
            150,
            [
                "RDS automated backups and snapshots",
                "Point-in-time recovery",
                "S3 versioning and lifecycle",
                "Restore drills",
                "Cost Explorer, budgets and tagging",
                "Rightsizing and Spot instances",
            ],
        ),
    ],
    "phase-6": [
        (
            "Kubernetes Pods, Deployments and Services",
            "The core Kubernetes workload objects.",
            "Kubernetes",
            210,
            [
                "Pods and containers",
                "Deployments and rolling updates",
                "ReplicaSets",
                "Services: ClusterIP, NodePort, LoadBalancer",
                "Labels and selectors",
                "Namespaces",
            ],
        ),
        (
            "ConfigMaps, Secrets and Ingress",
            "Externalising configuration and exposing workloads.",
            "Kubernetes",
            180,
            [
                "ConfigMaps and environment variables",
                "Secrets and encryption at rest",
                "Ingress resources and controllers",
                "Ingress TLS termination",
                "Path and host routing",
            ],
        ),
        (
            "Readiness, liveness and startup probes",
            "Teaching Kubernetes when your app is actually able to serve traffic.",
            "Kubernetes",
            120,
            [
                "How the kubelet uses probes",
                "HTTP, TCP and exec probes",
                "Startup probes for slow boot",
                "Probe tuning and failure thresholds",
                "Actuator health endpoints",
            ],
        ),
        (
            "Resource requests and limits",
            "Scheduling your workloads predictably and protecting the node.",
            "Kubernetes",
            120,
            [
                "Requests vs limits",
                "CPU and memory semantics",
                "QoS classes",
                "OOMKilled diagnosis",
                "LimitRange and ResourceQuota",
            ],
        ),
        (
            "Basic autoscaling and Helm",
            "Scaling with demand and packaging manifests for reuse.",
            "Kubernetes",
            180,
            [
                "Horizontal Pod Autoscaler",
                "Vertical Pod Autoscaler basics",
                "Cluster autoscaler",
                "Helm charts, values and templates",
                "Chart releases and upgrades",
                "Kustomize alternatives",
            ],
        ),
        (
            "Terraform fundamentals",
            "Provisioning cloud infrastructure as versioned code.",
            "Cloud",
            180,
            [
                "Providers, resources and data sources",
                "State files and remote backends",
                "Plan/apply workflow",
                "Modules and variables",
                "S3 + DynamoDB backend",
                "Terraform Cloud / CI pipelines",
            ],
        ),
        (
            "Prometheus and Grafana",
            "Collecting and visualising service metrics.",
            "Monitoring",
            180,
            [
                "Prometheus server and pull model",
                "Scrape configs and targets",
                "Metric types: counter, gauge, histogram",
                "Micrometer / Actuator metrics endpoint",
                "PromQL basics",
                "Grafana dashboards and alerts",
            ],
        ),
        (
            "Centralized logs and application metrics",
            "Correlating logs and metrics across services.",
            "Monitoring",
            150,
            [
                "Structured JSON logging",
                "Fluent Bit / Filebeat collection",
                "Loki or Elasticsearch storage",
                "Log levels and sampling",
                "RED and USE metrics",
                "Tracing with OpenTelemetry",
            ],
        ),
        (
            "Backups, recovery and incident troubleshooting",
            "Being ready when something breaks.",
            "Monitoring",
            150,
            [
                "Velero and etcd backups",
                "Pod crash loops and OOM kills",
                "Image pull and scheduling failures",
                "Service and DNS resolution issues",
                "Runbooks and post-mortems",
                "Incident response roles",
            ],
        ),
    ],
    "phase-7": [
        (
            "Refactor and polish portfolio projects",
            "Turning working projects into portfolio-grade repositories.",
            "Java",
            210,
            [
                "Code review of your own work",
                "Refactoring for readability",
                "Removing dead code and duplication",
                "Consistent error handling",
                "Performance and database tuning",
                "Final README polish",
            ],
        ),
        (
            "Architecture diagrams and comprehensive READMEs",
            "Explaining your design so a reviewer understands it in two minutes.",
            "System Design",
            150,
            [
                "C4 model and simple box diagrams",
                "Component and sequence diagrams",
                "ER diagrams",
                "README structure that gets read",
                "Setup instructions and screenshots",
                "Documenting design decisions (ADR)",
            ],
        ),
        (
            "Java and Spring Boot interview preparation",
            "Recollect the core knowledge under interview conditions.",
            "Java",
            240,
            [
                "Collections deep dive",
                "Concurrency and thread pools",
                "JVM memory and GC basics",
                "Dependency injection and bean lifecycle",
                "Transaction propagation",
                "Spring Boot auto-configuration",
            ],
        ),
        (
            "DSA and SQL practice",
            "Sharpening the problem solving skills recruiters test for.",
            "DSA",
            240,
            [
                "Arrays, strings and hash maps",
                "Linked lists and stacks",
                "Trees and graph traversal",
                "Sorting and searching",
                "LeetCode easy/medium patterns",
                "SQL window functions and CTEs",
            ],
        ),
        (
            "Operating systems, networking and database revision",
            "Revisiting the fundamentals that underpin every system question.",
            "System Design",
            180,
            [
                "Processes, threads and scheduling",
                "Memory management and paging",
                "Deadlocks and concurrency primitives",
                "TCP/IP, DNS and HTTP semantics",
                "Normalisation and indexing review",
                "Isolation levels and locking",
            ],
        ),
        (
            "Backend system design fundamentals",
            "Designing systems that scale, with the trade-offs to match.",
            "System Design",
            210,
            [
                "Requirements and capacity estimation",
                "Load balancing and scaling strategies",
                "Caching layers",
                "Database sharding and replication",
                "CAP theorem and consistency trade-offs",
                "Rate limiting and circuit breakers",
                "Event-driven design",
            ],
        ),
        (
            "DevOps and cloud interview questions",
            "Being able to talk about the infrastructure you built.",
            "Cloud",
            180,
            [
                "CI/CD pipeline design questions",
                "Docker and Kubernetes scenarios",
                "Terraform state and drift",
                "Monitoring and on-call questions",
                "AWS service selection",
                "Cost and security trade-off questions",
            ],
        ),
        (
            "Resume, GitHub portfolio and project demonstrations",
            "Making it easy for a recruiter to see your work.",
            "System Design",
            150,
            [
                "ATS-friendly resume structure",
                "Quantifying achievements",
                "GitHub profile README",
                "Pinned repositories and topics",
                "Demo video or live link",
                "Consistent commit history",
            ],
        ),
        (
            "Internship and entry-level job applications",
            "Running the search as a repeatable process.",
            "System Design",
            150,
            [
                "Target company list",
                "Tailoring applications",
                "Networking and referrals",
                "Application tracker",
                "Follow-up cadence",
                "Negotiating an offer",
            ],
        ),
    ],
    # --- DSA parallel track -------------------------------------------------
    "dsa-1": [
        (
            "Complexity analysis and Big-O",
            "Read code and predict how its running time and memory grow. This is the language "
            "every interview answer is measured in.",
            "DSA",
            90,
            [
                "Time vs space complexity",
                "Big-O, Big-Theta and Big-Omega",
                "Analysing loops and nested loops",
                "Amortised analysis",
                "Recursion trees",
                "Space complexity of recursion",
            ],
        ),
        (
            "Arrays and dynamic arrays",
            "Indexing, traversal, in-place updates and the trade-offs behind resizable arrays.",
            "DSA",
            120,
            [
                "Static arrays and indexing",
                "Traversal and in-place updates",
                "Two-dimensional arrays",
                "Prefix sums",
                "Dynamic array growth and amortised cost",
                "Common array pitfalls",
            ],
        ),
        (
            "Strings and character manipulation",
            "String traversal, building and comparison, including the cost of immutable strings.",
            "DSA",
            90,
            [
                "Character encoding basics",
                "String builders vs concatenation",
                "Palindromes and anagrams",
                "Frequency counting",
                "String parsing and tokenising",
                "Common edge cases",
            ],
        ),
        (
            "Hash maps and hash sets",
            "The most reusable interview tool: constant-time lookup, frequency maps and seen sets.",
            "DSA",
            120,
            [
                "Hash functions and collisions",
                "Frequency maps",
                "Seen sets and duplicates",
                "Grouping with map keys",
                "Prefix-sum maps",
                "When hashing is the wrong tool",
            ],
        ),
        (
            "Two pointers",
            "Solve sorted-array and sequence problems with coordinated indices instead of nested loops.",
            "DSA",
            120,
            [
                "Opposite-end pointers",
                "Same-direction pointers",
                "Removing duplicates in place",
                "Three-sum style problems",
                "Merging sorted sequences",
                "Pointer invariants",
            ],
        ),
        (
            "Sliding window",
            "Maintain a moving window over arrays and strings to turn O(n²) scans into O(n).",
            "DSA",
            120,
            [
                "Fixed-size windows",
                "Variable-size windows",
                "Longest/shortest subarray patterns",
                "Window frequency maps",
                "Shrinking conditions",
                "Choosing the right window state",
            ],
        ),
        (
            "Stacks and queues",
            "LIFO and FIFO structures, monotonic stacks and the queue patterns behind BFS.",
            "DSA",
            120,
            [
                "Stack operations and use cases",
                "Queue and deque operations",
                "Balanced brackets",
                "Monotonic stack",
                "Next greater element",
                "Implementing a queue with stacks",
            ],
        ),
        (
            "Linked lists",
            "Pointer manipulation, traversal and the classic interview mutations.",
            "DSA",
            120,
            [
                "Singly and doubly linked lists",
                "Traversal and length",
                "Reversing a list",
                "Cycle detection",
                "Merging and splitting lists",
                "Dummy-head technique",
            ],
        ),
        (
            "Recursion and backtracking basics",
            "Break problems into smaller copies of themselves, then learn to undo choices.",
            "DSA",
            150,
            [
                "Base cases and recursive cases",
                "Call stack and recursion depth",
                "Divide and conquer",
                "Subsets and permutations",
                "Pruning invalid branches",
                "Converting recursion to iteration",
            ],
        ),
        (
            "Sorting algorithms",
            "Know how the standard sorts work, when they are stable and what they cost.",
            "DSA",
            120,
            [
                "Bubble, insertion and selection sort",
                "Merge sort",
                "Quick sort and partitioning",
                "Heap sort overview",
                "Stability and comparator design",
                "Sorting-based interview patterns",
            ],
        ),
        (
            "Binary search",
            "Search ordered data in logarithmic time and recognise the many problems that hide a sorted space.",
            "DSA",
            120,
            [
                "Classic binary search",
                "Lower and upper bounds",
                "Search on answer spaces",
                "Rotated sorted arrays",
                "Boundary and overflow pitfalls",
                "Binary search on monotonic predicates",
            ],
        ),
        (
            "Trees and binary search trees",
            "Traverse hierarchical data and use ordering to search, insert and delete efficiently.",
            "DSA",
            150,
            [
                "Tree terminology and representations",
                "Depth-first traversals",
                "Breadth-first traversal",
                "BST search, insert and delete",
                "Balanced trees overview",
                "Lowest common ancestor",
            ],
        ),
    ],
    "dsa-2": [
        (
            "Heaps and priority queues",
            "Keep the most important element available in logarithmic time, then apply it to top-k and scheduling problems.",
            "DSA",
            120,
            [
                "Heap properties and array layout",
                "Min-heap vs max-heap",
                "Push, pop and heapify",
                "Top-k problems",
                "Two-heap median pattern",
                "Scheduling and merging streams",
            ],
        ),
        (
            "Graph representations and traversal",
            "Model relationships as graphs, then explore them with BFS and DFS.",
            "DSA",
            150,
            [
                "Adjacency lists and matrices",
                "Breadth-first search",
                "Depth-first search",
                "Connected components",
                "Shortest path in unweighted graphs",
                "Grid traversal",
            ],
        ),
        (
            "Topological sort and cycle detection",
            "Order tasks with dependencies and detect when an ordering is impossible.",
            "DSA",
            120,
            [
                "Directed acyclic graphs",
                "Kahn's algorithm",
                "DFS finishing order",
                "Cycle detection in directed graphs",
                "Course-schedule problems",
                "Dependency resolution",
            ],
        ),
        (
            "Union-Find (disjoint sets)",
            "Track connected groups under repeated merges with near-constant-time operations.",
            "DSA",
            120,
            [
                "Parent and rank arrays",
                "Path compression",
                "Union by rank/size",
                "Counting components",
                "Kruskal's algorithm",
                "Dynamic connectivity problems",
            ],
        ),
        (
            "Tries and prefix trees",
            "Store and query strings by prefix for autocomplete and dictionary-style problems.",
            "DSA",
            120,
            [
                "Trie node structure",
                "Insert, search and prefix queries",
                "Wildcard search",
                "Word dictionaries",
                "Memory trade-offs",
                "Trie vs hash map",
            ],
        ),
        (
            "Backtracking patterns",
            "Systematically explore choices, prune bad branches and record complete solutions.",
            "DSA",
            150,
            [
                "Choice, constraint and goal",
                "Combination and permutation templates",
                "N-Queens and Sudoku",
                "Word search",
                "Duplicate handling",
                "Pruning and complexity",
            ],
        ),
        (
            "Greedy algorithms and intervals",
            "Make locally optimal choices that are provably globally optimal, with interval scheduling as the core pattern.",
            "DSA",
            120,
            [
                "Greedy choice property",
                "Interval scheduling",
                "Merge intervals",
                "Meeting rooms",
                "Jump game patterns",
                "When greedy fails",
            ],
        ),
        (
            "Dynamic programming: 1D",
            "Turn overlapping subproblems into a table or rolling state and stop recomputing answers.",
            "DSA",
            180,
            [
                "Recurrence relations",
                "Memoisation vs tabulation",
                "Climbing stairs and house robber",
                "Longest increasing subsequence",
                "Coin change",
                "State design and transitions",
            ],
        ),
        (
            "Dynamic programming: 2D and knapsack",
            "Handle two-dimensional state spaces, grid paths and the classic knapsack family.",
            "DSA",
            180,
            [
                "Grid paths",
                "Longest common subsequence",
                "Edit distance",
                "0/1 knapsack",
                "Unbounded knapsack",
                "Space optimisation",
            ],
        ),
        (
            "Bit manipulation",
            "Use bitwise operations for compact state, fast checks and subsets.",
            "DSA",
            90,
            [
                "Bitwise operators",
                "Set, clear and toggle bits",
                "Counting set bits",
                "Power-of-two checks",
                "XOR tricks",
                "Bitmask subsets",
            ],
        ),
        (
            "SQL and database interview problems",
            "Apply the same problem-solving discipline to joins, aggregation and window functions.",
            "DSA",
            120,
            [
                "Joins and subqueries",
                "Grouping and aggregation",
                "Window functions",
                "Ranking and pagination",
                "Query complexity and indexes",
                "Explaining a query plan",
            ],
        ),
        (
            "Mock interviews and pattern review",
            "Rehearse the full interview loop: clarify, plan, code, test and discuss trade-offs.",
            "DSA",
            120,
            [
                "Clarifying questions",
                "Communicating a plan",
                "Coding under time pressure",
                "Testing edge cases",
                "Complexity discussion",
                "Reviewing mistakes by pattern",
            ],
        ),
    ],
}

# ---------------------------------------------------------------------------
# Resources (verified official documentation)
# ---------------------------------------------------------------------------
# (title, url, description, category, tags)
RESOURCES: list[tuple[str, str, str, str, list[str]]] = [
    (
        "Spring Guides",
        "https://spring.io/guides",
        "Official, hands-on Spring Boot and Spring Cloud tutorials - the fastest way to "
        "learn a new Spring feature.",
        "Spring Boot",
        ["spring", "tutorial", "rest"],
    ),
    (
        "Spring Boot Reference Documentation",
        "https://docs.spring.io/spring-boot/reference/",
        "Complete reference for Spring Boot: auto-configuration, configuration properties, "
        "actuator endpoints and testing.",
        "Spring Boot",
        ["spring-boot", "reference"],
    ),
    (
        "Spring Security Reference",
        "https://docs.spring.io/spring-security/reference/",
        "Official Spring Security documentation covering the filter chain, OAuth2, method "
        "security and testing.",
        "Security",
        ["security", "oauth2", "jwt"],
    ),
    (
        "Spring Data JPA Documentation",
        "https://docs.spring.io/spring-data/jpa/reference/",
        "Repository query derivation, specifications, locking and transaction semantics for "
        "Spring Data JPA.",
        "Spring Boot",
        ["jpa", "hibernate", "repositories"],
    ),
    (
        "Docker Get Started",
        "https://docs.docker.com/get-started/",
        "Official Docker documentation and tutorials for images, containers, Compose and "
        "image best practices.",
        "Docker",
        ["docker", "compose", "containers"],
    ),
    (
        "Docker Compose Specification",
        "https://docs.docker.com/reference/compose-file/",
        "Reference for the compose file format: services, networks, volumes, healthchecks "
        "and configs.",
        "Docker",
        ["docker", "compose"],
    ),
    (
        "GitHub Actions Documentation",
        "https://docs.github.com/en/actions",
        "Official docs for GitHub Actions: workflow syntax, runners, secrets, caching and "
        "deployment workflows.",
        "CI/CD",
        ["github", "actions", "cicd"],
    ),
    (
        "GitHub Actions Marketplace",
        "https://github.com/marketplace?type=actions",
        "Reusable community actions for building, testing, scanning and deploying.",
        "CI/CD",
        ["github", "actions", "marketplace"],
    ),
    (
        "AWS Skill Builder",
        "https://skillbuilder.aws/",
        "Free structured courses and labs for AWS services, well aligned with the cloud "
        "phases of the roadmap.",
        "Cloud",
        ["aws", "certification", "labs"],
    ),
    (
        "AWS Documentation",
        "https://docs.aws.amazon.com/",
        "Complete AWS service reference: EC2, RDS, S3, IAM, VPC, CloudWatch and more.",
        "Cloud",
        ["aws", "reference"],
    ),
    (
        "Kubernetes Tutorials",
        "https://kubernetes.io/docs/tutorials/",
        "Official hands-on tutorials: deployments, services, config, scaling and "
        "stateful workloads.",
        "Kubernetes",
        ["kubernetes", "tutorial"],
    ),
    (
        "Kubernetes Concepts",
        "https://kubernetes.io/docs/concepts/",
        "The conceptual reference behind every Kubernetes object used in Phase 6.",
        "Kubernetes",
        ["kubernetes", "reference"],
    ),
    (
        "PostgreSQL Documentation",
        "https://www.postgresql.org/docs/",
        "The official PostgreSQL manual covering SQL, indexing, transactions, vacuum and "
        "configuration.",
        "Databases",
        ["postgres", "sql", "reference"],
    ),
    (
        "PostgreSQL EXPLAIN",
        "https://www.postgresql.org/docs/current/using-explain.html",
        "How to read query plans and find the missing index.",
        "Databases",
        ["postgres", "performance"],
    ),
    (
        "Git Reference",
        "https://git-scm.com/doc",
        "The official Git documentation: branching, rebasing, internals and the "
        "pro-git book.",
        "CI/CD",
        ["git", "version-control"],
    ),
    (
        "Pro Git Book",
        "https://git-scm.com/book/en/v2",
        "The complete Pro Git book - free to read online.",
        "CI/CD",
        ["git", "book"],
    ),
    (
        "Terraform Tutorials",
        "https://developer.hashicorp.com/terraform/tutorials",
        "Step-by-step Terraform tutorials: state, modules, providers and real cloud "
        "provisioning.",
        "Cloud",
        ["terraform", "iac"],
    ),
    (
        "Terraform Registry",
        "https://registry.terraform.io/",
        "Providers and reusable modules for Terraform.",
        "Cloud",
        ["terraform", "providers"],
    ),
    (
        "Prometheus Overview",
        "https://prometheus.io/docs/introduction/overview/",
        "How Prometheus works: data model, scrape targets, PromQL and alerting rules.",
        "Monitoring",
        ["prometheus", "metrics"],
    ),
    (
        "Prometheus Querying Basics",
        "https://prometheus.io/docs/prometheus/latest/querying/basics/",
        "PromQL reference for building useful recording and alerting rules.",
        "Monitoring",
        ["prometheus", "promql"],
    ),
    (
        "Grafana Documentation",
        "https://grafana.com/docs/",
        "Dashboards, data sources, alerting and the Grafana Agent for logs and metrics.",
        "Monitoring",
        ["grafana", "dashboards"],
    ),
    (
        "Java Documentation (Oracle)",
        "https://docs.oracle.com/en/java/javase/21/docs/",
        "The official Java SE API documentation and language guides.",
        "Java",
        ["java", "javadoc"],
    ),
    (
        "Spring Framework Reference",
        "https://docs.spring.io/spring-framework/reference/",
        "Core Spring Framework concepts: DI, AOP, transactions, MVC and testing.",
        "Spring Boot",
        ["spring", "reference"],
    ),
    (
        "LeetCode",
        "https://leetcode.com/",
        "Practice platform for data structures and algorithms used in the parallel DSA track.",
        "DSA",
        ["dsa", "practice", "interview"],
    ),
    (
        "NeetCode Roadmap",
        "https://neetcode.io/roadmap",
        "A structured, pattern-first DSA roadmap with curated problems and video explanations.",
        "DSA",
        ["dsa", "patterns", "interview"],
    ),
    (
        "Big-O Cheat Sheet",
        "https://www.bigocheatsheet.com/",
        "Quick reference for the time and space complexity of common data structures and sorts.",
        "DSA",
        ["dsa", "complexity", "reference"],
    ),
    (
        "VisuAlgo",
        "https://visualgo.net/en",
        "Interactive visualisations of data structures and algorithms, useful for building intuition.",
        "DSA",
        ["dsa", "visualisation", "algorithms"],
    ),
    (
        "Designing Data-Intensive Applications",
        "https://dataintensive.net/",
        "The classic reference on reliable, scalable and maintainable systems (book).",
        "System Design",
        ["system-design", "book", "architecture"],
    ),
    (
        "System Design Primer",
        "https://github.com/donnemartin/system-design-primer",
        "Open-source system design interview guide with diagrams and worked examples.",
        "System Design",
        ["system-design", "interview"],
    ),
    (
        "Google SRE Book",
        "https://sre.google/sre-book/table-of-contents/",
        "Free book on Site Reliability Engineering, SLIs, SLOs, monitoring and incidents.",
        "Monitoring",
        ["sre", "reliability", "monitoring"],
    ),
    (
        "MDN HTTP Guide",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP",
        "Authoritative HTTP reference: methods, headers, caching and status codes.",
        "System Design",
        ["http", "rest", "networking"],
    ),
    (
        "Fly.io / Docker Networking docs",
        "https://docs.docker.com/engine/network/",
        "Docker networking modes: bridge, host, overlay and DNS resolution.",
        "Docker",
        ["docker", "networking"],
    ),
    (
        "Nginx Admin Guide",
        "https://nginx.org/en/docs/",
        "Official Nginx documentation for reverse proxying, load balancing and TLS.",
        "Linux",
        ["nginx", "proxy", "linux"],
    ),
]

# ---------------------------------------------------------------------------
# Project templates (copied per user on registration)
# ---------------------------------------------------------------------------
# (name, description, required_skills, milestones[(title, description)], checklist[title])
PROJECTS: list[dict[str, Any]] = [
    {
        "name": "Java Expense Tracker",
        "description": (
            "A command-line application that records daily expenses into PostgreSQL, "
            "supports monthly budgets, category filtering and CSV export. The foundation "
            "project for Phase 1 - it proves you can use Java, SQL and Git for something "
            "real."
        ),
        "required_skills": ["Java", "OOP", "Collections", "SQL", "PostgreSQL", "JDBC", "Git"],
        "milestones": [
            ("Project scaffolding and CLI", "Set up the Maven project, argument parsing and a layered structure (cli/service/repository)."),
            ("Database schema and JDBC layer", "Create the expenses table with Flyway-style versioning and a JDBC DAO with prepared statements."),
            ("Expense CRUD operations", "Add, list, update and delete expenses with validation and error handling."),
            ("Reporting and budgets", "Monthly totals by category, budget limits and a simple ASCII report."),
            ("CSV export and documentation", "Export the report to CSV and write a README with usage instructions."),
        ],
        "checklist": [
            "Repository created and public",
            "Meaningful commit history",
            "Unit tests for the service layer",
            "README with screenshots",
            "Sample data seeded",
        ],
    },
    {
        "name": "Personal Finance Spring Boot REST API",
        "description": (
            "A layered Spring Boot REST API for tracking accounts, transactions and budgets, "
            "backed by PostgreSQL with Flyway migrations, Bean Validation, pagination and "
            "OpenAPI documentation."
        ),
        "required_skills": [
            "Spring Boot",
            "Spring Data JPA",
            "REST",
            "Flyway",
            "PostgreSQL",
            "Validation",
            "OpenAPI",
        ],
        "milestones": [
            ("Project and database setup", "Spring Initializr project, Flyway migrations and docker-compose PostgreSQL."),
            ("Domain model and repositories", "Entities, relationships, enums and Spring Data repositories."),
            ("Service and controller layer", "DTOs, mappers, services and REST controllers for accounts and transactions."),
            ("Validation and error handling", "Bean Validation and a global @RestControllerAdvice producing a consistent error contract."),
            ("Pagination, filtering and OpenAPI", "Pageable endpoints, filters and springdoc OpenAPI documentation."),
        ],
        "checklist": [
            "OpenAPI docs published",
            "Postman collection or HTTP client file",
            "Controller and service tests",
            "Docker Compose for local postgres",
            "README with endpoint table",
        ],
    },
    {
        "name": "Secure Multi-user Finance API",
        "description": (
            "The finance API extended with Spring Security, JWT access and refresh tokens, "
            "role-based access control, strict resource ownership rules and a full automated "
            "test suite."
        ),
        "required_skills": [
            "Spring Security",
            "JWT",
            "BCrypt",
            "RBAC",
            "JUnit 5",
            "Mockito",
            "Testcontainers",
        ],
        "milestones": [
            ("User model and registration", "Users, roles and a registration endpoint with hashed passwords."),
            ("JWT authentication flow", "Access and refresh token issuance, rotation and revocation."),
            ("Authorization and ownership", "Role-based rules plus per-resource ownership checks."),
            ("Automated test suite", "Unit, integration and security tests covering the critical paths."),
            ("Hardening and documentation", "Rate limiting, CORS policy and an updated README."),
        ],
        "checklist": [
            "No plaintext passwords stored",
            "Refresh token rotation implemented",
            "Ownership tests for every private resource",
            "Testcontainers used for integration tests",
            "Security checklist documented",
        ],
    },
    {
        "name": "Dockerized API with PostgreSQL",
        "description": (
            "The secured API packaged into a multi-stage Docker image and running alongside "
            "PostgreSQL in Docker Compose with persistent volumes, health checks and a "
            "reverse proxy."
        ),
        "required_skills": ["Docker", "Docker Compose", "Volumes", "Networking", "Health checks", "Nginx"],
        "milestones": [
            ("Multi-stage Dockerfile", "Layered build with a JRE-only runtime image running as a non-root user."),
            ("Compose stack", "API, PostgreSQL and Nginx services with named volumes and networks."),
            ("Health checks and logging", "Docker HEALTHCHECK instructions and structured log output."),
            ("Nginx reverse proxy", "Proxying traffic with TLS-ready configuration and static asset caching."),
            ("Documentation and scripts", "One-command local start plus an operations README."),
        ],
        "checklist": [
            "docker compose up starts the whole stack",
            "Data survives container restarts",
            "Image is under 250MB",
            "Health checks reported as healthy",
            "README includes troubleshooting",
        ],
    },
    {
        "name": "Cloud-deployed API with GitHub Actions",
        "description": (
            "The containerised API shipped to the cloud behind a domain with HTTPS, with a "
            "GitHub Actions pipeline that builds, tests, scans and deploys on every merge to "
            "main."
        ),
        "required_skills": ["GitHub Actions", "AWS", "EC2", "RDS", "S3", "HTTPS", "DNS", "Terraform"],
        "milestones": [
            ("CI pipeline", "Build, test, lint and package the application on every push and pull request."),
            ("Image publishing", "Tag and push the container image to a registry with proper tagging."),
            ("CD pipeline", "Deploy to the cloud environment with environment protection and approvals."),
            ("Cloud infrastructure", "Provision VPC, subnets, security groups, RDS and storage with Terraform."),
            ("Domain, TLS and monitoring", "Attach a domain with ACM certificates and enable uptime monitoring."),
        ],
        "checklist": [
            "Green CI badge in the README",
            "Secrets never stored in the repo",
            "Terraform state stored remotely",
            "Automated database backups enabled",
            "Live URL documented in the README",
        ],
    },
    {
        "name": "Kubernetes and Monitoring Capstone",
        "description": (
            "The full platform running on Kubernetes: Helm chart, ingress, probes, autoscaling, "
            "Prometheus and Grafana dashboards, plus a documented backup and recovery "
            "procedure."
        ),
        "required_skills": [
            "Kubernetes",
            "Helm",
            "Terraform",
            "Prometheus",
            "Grafana",
            "Observability",
        ],
        "milestones": [
            ("Cluster-ready manifests", "Deployment, service, config, secrets, ingress and resource limits."),
            ("Health probes and autoscaling", "Readiness, liveness and startup probes plus an HPA."),
            ("Helm packaging", "A versioned chart with values files for dev and prod."),
            ("Monitoring stack", "Prometheus scrape config, alert rules and Grafana dashboards."),
            ("Backup and recovery runbook", "Backup strategy, restore drill and incident troubleshooting guide."),
        ],
        "checklist": [
            "Deployment rolls forward and back cleanly",
            "Dashboards show request rate, errors and latency",
            "Alerts fire in a controlled test",
            "A restore was performed and documented",
            "Architecture diagram included",
        ],
    },
]

# topic slug -> resource titles that are recommended for it
TOPIC_RESOURCE_MAP: dict[str, list[str]] = {
    "java-syntax-methods-classes-and-oop": ["Java Documentation (Oracle)", "Spring Guides"],
    "collections-generics-and-exception-handling": ["Java Documentation (Oracle)"],
    "streams-lambdas-and-optional": ["Java Documentation (Oracle)"],
    "basic-concurrency-and-jvm-fundamentals": ["Java Documentation (Oracle)"],
    "sql-select-filtering-sorting-and-aggregation": ["PostgreSQL Documentation"],
    "joins-subqueries-indexes-and-transactions": ["PostgreSQL Documentation", "PostgreSQL EXPLAIN"],
    "git-github-branches-merges-and-pull-requests": ["Git Reference", "Pro Git Book"],
    "spring-boot-setup-and-project-structure": [
        "Spring Guides",
        "Spring Boot Reference Documentation",
        "Spring Framework Reference",
    ],
    "dependency-injection-and-configuration": ["Spring Framework Reference", "Spring Guides"],
    "controllers-services-repositories-and-dtos": ["Spring Guides", "Spring Boot Reference Documentation"],
    "rest-methods-http-status-codes-and-api-design": ["MDN HTTP Guide", "Spring Guides"],
    "spring-data-jpa-and-hibernate": ["Spring Data JPA Documentation", "Spring Guides"],
    "flyway-database-migrations": ["PostgreSQL Documentation", "Spring Guides"],
    "spring-security-filter-chain": ["Spring Security Reference"],
    "password-hashing-using-bcrypt": ["Spring Security Reference"],
    "authentication-and-authorization": ["Spring Security Reference"],
    "jwt-access-tokens-and-refresh-token-lifecycle": ["Spring Security Reference"],
    "role-based-access-control-and-resource-ownership": ["Spring Security Reference"],
    "cors-csrf-and-common-web-vulnerabilities": ["Spring Security Reference", "MDN HTTP Guide"],
    "junit-5-and-mockito": ["Spring Framework Reference"],
    "integration-testing-with-testcontainers": ["Spring Data JPA Documentation", "PostgreSQL Documentation"],
    "spring-security-testing": ["Spring Security Reference"],
    "sql-query-optimization-and-indexing": ["PostgreSQL EXPLAIN", "PostgreSQL Documentation"],
    "redis-caching": ["Spring Data JPA Documentation"],
    "linux-filesystem-permissions-users-and-groups": ["Nginx Admin Guide"],
    "processes-services-ssh-and-shell-commands": ["Nginx Admin Guide"],
    "ip-addresses-dns-tcp-http-and-tls": ["MDN HTTP Guide"],
    "ports-firewalls-and-reverse-proxies": ["Nginx Admin Guide"],
    "docker-images-containers-and-dockerfiles": ["Docker Get Started"],
    "docker-compose-volumes-and-networks": ["Docker Compose Specification", "Docker Get Started"],
    "multi-stage-builds-and-health-checks": ["Docker Get Started"],
    "github-actions-workflows": ["GitHub Actions Documentation", "GitHub Actions Marketplace"],
    "automated-builds-and-tests": ["GitHub Actions Documentation"],
    "code-quality-checks": ["GitHub Actions Marketplace"],
    "docker-image-building-and-publishing": ["Docker Get Started", "GitHub Actions Documentation"],
    "continuous-deployment": ["GitHub Actions Documentation"],
    "secure-secret-management": ["GitHub Actions Documentation"],
    "aws-iam-vpc-subnets-and-security-groups": ["AWS Skill Builder", "AWS Documentation"],
    "ec2-s3-and-managed-databases": ["AWS Skill Builder", "AWS Documentation"],
    "https-and-dns": ["AWS Documentation", "MDN HTTP Guide"],
    "backups-recovery-and-cloud-cost-management": ["AWS Skill Builder", "AWS Documentation"],
    "kubernetes-pods-deployments-and-services": ["Kubernetes Tutorials", "Kubernetes Concepts"],
    "configmaps-secrets-and-ingress": ["Kubernetes Tutorials"],
    "readiness-liveness-and-startup-probes": ["Kubernetes Concepts"],
    "resource-requests-and-limits": ["Kubernetes Concepts"],
    "basic-autoscaling-and-helm": ["Kubernetes Tutorials"],
    "terraform-fundamentals": ["Terraform Tutorials", "Terraform Registry"],
    "prometheus-and-grafana": ["Prometheus Overview", "Grafana Documentation"],
    "centralized-logs-and-application-metrics": ["Grafana Documentation", "Prometheus Overview"],
    "backups-recovery-and-incident-troubleshooting": ["Google SRE Book"],
    "architecture-diagrams-and-comprehensive-readmes": ["System Design Primer", "Designing Data-Intensive Applications"],
    "java-and-spring-boot-interview-preparation": ["Spring Framework Reference", "Java Documentation (Oracle)"],
    "dsa-and-sql-practice": ["LeetCode", "PostgreSQL Documentation"],
    "operating-systems-networking-and-database-revision": ["MDN HTTP Guide", "PostgreSQL Documentation"],
    "backend-system-design-fundamentals": [
        "Designing Data-Intensive Applications",
        "System Design Primer",
        "Google SRE Book",
    ],
    "devops-and-cloud-interview-questions": ["Google SRE Book", "AWS Skill Builder"],
    "resume-github-portfolio-and-project-demonstrations": ["System Design Primer"],
    "internship-and-entry-level-job-applications": ["System Design Primer"],
}
