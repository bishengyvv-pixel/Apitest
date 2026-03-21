# ADR 0002: Package Dependency Topology Is a DAG

Status: Accepted

Date: 2026-03-18

## Context

ADR 0001 established the package-internal architecture:

- fixed per-package directories;
- outside dependencies funneled through `shell/requirements.<ext>`;
- product logic insulated from direct external dependencies.

We also need a repository-wide rule for how packages may depend on each other.

Without that rule, package-level cycles remain possible. Cycles weaken the package boundary because they make extraction, independent testing, refactoring, and build ordering harder.

At the same time, we do not want to force the repository into a single-parent tree or a global layer stack. Shared packages should be allowed to serve multiple consumers.

## Decision

The repository package topology is defined as a directed graph:

- nodes are packages under `packages/`;
- an edge `A -> B` exists when code in package `A` depends on code/data in package `B`.

That graph MUST be acyclic. In other words, package dependencies across the repository MUST form a DAG.

This rule defines a graph constraint, not a repository-wide hierarchy:

- a package MAY depend on multiple packages;
- multiple packages MAY depend on the same package;
- the repository is not required to fit a single-parent tree;
- this ADR does not assign packages to global semantic levels.

This ADR extends that package architecture with a repository-wide topology rule. The dependency-funneling decision remains in force, and the DAG rule is added on top of it.

See the normative rules in:

- [Package Boundaries and Dependencies (Reference)](../reference/package-boundaries-and-dependencies.md)

## Consequences

Positive:

- package boundaries are easier to reason about because cross-package cycles are forbidden;
- shared packages remain possible because the topology is a graph rather than a tree;
- build ordering, extraction, and refactoring become more predictable.

Negative / costs:

- cyclic designs must be broken apart before they can be represented as packages;
- some shared code may need to be extracted into a new package to remove a cycle.

## Alternatives Considered

1. Keep package topology unconstrained.
   - Rejected: allows cyclic package coupling, which undermines package isolation.
2. Require a repository-wide hierarchy or tree.
   - Rejected: too rigid; shared packages would fit poorly.
3. Allow cycles but rely on convention.
   - Rejected: hard to audit and easy to regress.

## References

- [Package Boundaries and Dependencies (Reference)](../reference/package-boundaries-and-dependencies.md)
- [Why Dependency Funneling (Shell)](../explanation/dependency-funneling-and-shell.md)
- [ADR 0001: Dependency Funneling via Shell Requirements](./0001-dependency-funneling-via-shell-requirements.md)
