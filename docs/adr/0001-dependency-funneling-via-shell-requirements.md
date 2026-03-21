# ADR 0001: Dependency Funneling via Shell Requirements

Status: Accepted

Date: 2026-03-18

## Context

We want a package architecture that:

- is language-agnostic (can apply to many programming languages);
- supports mechanical checking of dependency constraints for formal languages;
- keeps package internals stable and refactorable;
- makes "what does this package depend on externally?" easy to audit.

We also accept that:

- natural language documents are generally not mechanically checkable for dependencies;
- we do not want to force the repository into a single-parent hierarchy or a framework-specific topology model.

## Decision

For each package under `packages/<package>/`, define a fixed architectural layout:

- `product/config/`, `product/impl/`
- `adaptor/config/`, `adaptor/impl/`
- `shell/requirements.<ext>`, `shell/exports.<ext>` (per language)

Define "outside the package" strictly as anything not under `packages/<package>/**`, including standard library dependencies.

Funnel all outside dependencies into `shell/requirements.<ext>`:

- only `shell/requirements.<ext>` may contain dependency statements targeting outside the package;
- all other architectural directories must not directly depend on anything outside the package.

Outside dependencies are not limited to this repository; `requirements` may depend on any dependency resolvable by the language/tooling.

Define internal layering so product logic is insulated from external choices:

- adaptor implementation depends on adaptor config and `requirements`;
- product implementation depends on product config and adaptor implementation;
- exports depends only on product implementation.

See the normative rules in:

- [Package Boundaries and Dependencies (Reference)](../reference/package-boundaries-and-dependencies.md)

## Consequences

Positive:

- external dependencies are centralized and auditable;
- product logic becomes easier to test and refactor;
- the rules can be checked mechanically for formal languages.

Negative / costs:

- standard library usage must be routed through the shell/adaptor boundary;
- some languages may have awkward type-sharing across the `requirements` boundary since `requirements` cannot import internal config types.

## Alternatives Considered

1. Allow external dependencies anywhere in a package.
   - Rejected: auditability and refactorability degrade quickly.
2. Enforce a global package dependency DAG.
   - Rejected: too rigid; not required for the goal of external dependency funneling.
3. Use a framework-specific DI container to manage boundaries.
   - Rejected: not language-agnostic.

## References

- [Why Dependency Funneling (Shell)](../explanation/dependency-funneling-and-shell.md)
