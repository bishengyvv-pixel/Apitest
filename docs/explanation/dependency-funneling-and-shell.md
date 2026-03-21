# Why Dependency Funneling (Shell) (Explanation)

This document explains the reasoning and tradeoffs behind the rules defined in:

- [Package Boundaries and Dependencies (Reference)](../reference/package-boundaries-and-dependencies.md)

## The Core Idea

Within a package, anything outside the package is treated as an **external dependency**, including the standard library.

The package design funnels all external dependencies into a single place per language:

- `shell/requirements.<ext>`

Everything else inside the package can then be reasoned about as a mostly-closed world.

External dependencies are not limited to this repository; they include any dependencies resolvable by the language/tooling (e.g. ecosystem packages, remote modules).

## Why This Works

1. **Encapsulation by default**
   - External code should ideally depend on `shell/exports.<ext>` rather than internal files.
   - This keeps the package's internal refactors from becoming cross-repo breaking changes.
2. **Testability**
   - If all external dependencies are funneled into `requirements`, it becomes easier to replace them in tests via indirection (adaptor layer), without touching product logic.
3. **Auditability**
   - "What does this package rely on outside itself?" becomes a small, reviewable surface area.
4. **Language-agnostic enforcement**
   - The rules are defined by directory boundaries and dependency statements, not by a specific language or framework.

## Why Package Topology Is a DAG

The repository-level package topology is constrained to a directed acyclic graph (DAG).

This adds one repository-wide rule on top of the per-package dependency funnel:

- packages may depend on other packages;
- those dependencies may form a graph;
- the graph must not contain cycles.

The main benefit is that package boundaries remain composable. Cycles make extraction, testing, build ordering, and reuse much harder because two packages stop being independently movable units.

## Why This Is a Graph, Not a Hierarchy

The rule is intentionally weaker than a tree or global layer stack.

- A package may depend on multiple other packages.
- Multiple packages may depend on the same shared package.
- The repository does not need a single root package or a single-parent ownership tree.

This keeps the topology expressive while still ruling out the main failure mode: cyclic coupling.

## Why Standard Library Counts as External

The goal is not to punish standard library usage; it is to make the package boundary absolute:

- if it is not under `packages/<package>/**`, it is external.

This avoids arguing about what is "okay" and keeps the rule mechanically definable.

Practically, this means the adaptor layer is where standard library interaction tends to live, by consuming capabilities provided via `requirements`.

## The Role of `requirements` vs `exports`

### `shell/requirements.<ext>`

- It is the package's "import boundary" from the outside world.
- It depends only on external things.
- It must not depend on package internals.

This design keeps external dependency choices from leaking into product logic.

### `shell/exports.<ext>`

- It is the recommended "consumption boundary" for package users.
- It depends only on `product/impl/**`.

This provides a stable API surface.

## Tradeoffs and Practical Tips

1. **Type-sharing can be awkward in some languages**
   - Because `requirements` cannot import internal `config`, it may have to expose untyped or minimally-typed external handles.
   - The adaptor layer can then wrap/normalize these handles into internal types.
2. **The adaptor layer is the integration layer**
   - If something touches the OS, time, filesystem, network, or third-party libs, it probably belongs behind `requirements` and `adaptor/impl`.
3. **Keep `requirements` small**
   - Prefer exporting a small number of external capabilities rather than re-exporting large third-party APIs.

## What We Deliberately Do Not Solve (Yet)

- Dependencies embedded in natural language documents are not mechanically checkable in general, so we do not enforce rules there.
- The repository package graph is constrained only by acyclicity; this document does not assign packages to repository-wide semantic layers.
