# Package Boundaries and Dependencies (Reference)

Status: **Normative**

Last updated: 2026-03-18

This document defines repository/package layout rules, package-topology rules, and dependency rules. It is intended to be mechanically checkable for formal languages (programming languages, build languages, etc.).

## Scope

These rules apply to all packages under `packages/<package>/`.

This document does **not** attempt to define rules for natural language documents (high-semantic files), where reliable mechanical dependency extraction is not feasible.

## Definitions

**Package root**: `packages/<package>/`.

**Inside the package**: any path under `packages/<package>/**`.

**Outside the package**: anything not under `packages/<package>/**`. This includes:

- standard libraries;
- third-party libraries;
- other packages under `packages/`;
- any repository-root shared code (e.g. `third_party/`, `vendor/`, `libs/`, etc.).
- anything not limited to this repository (any dependency resolvable by the language/tooling, including remote modules).

**Dependency statement** (formal languages): a statement that brings in code/data from elsewhere, such as `import`, `require`, `#include`, `using`, `load`, etc. Exact syntax is language-specific; the intent is that these statements are mechanically detectable.

**Package dependency edge**: a directed edge `A -> B` that exists when a dependency statement in `packages/A/**` targets code/data in `packages/B/**`, whether via relative path, workspace package name, alias, or other repository-local resolution.

**Repository package dependency graph**: the directed graph whose nodes are packages under `packages/` and whose edges are all package dependency edges.

## Repository Layout Rules

1. `packages/` MUST contain only package directories of the form `packages/<package>/`.
2. Repository-level attachments are allowed:
   - `docs/` (repository documentation)
   - `assets/` (repository assets)

## Repository Package Topology

1. The repository package dependency graph MUST be a directed acyclic graph (DAG).
2. A package MAY depend on multiple other packages, and multiple packages MAY depend on the same package, provided the graph remains acyclic.
3. These rules define a graph constraint, not a repository-wide hierarchy:
   - packages are not required to fit into a single-parent tree;
   - packages are not assigned global levels by this document.

## Package Attachment Directories

Within a package root `packages/<package>/`, the following attachment directories are allowed:

- `docs/`
- `assets/`

Attachment directories are not part of the architectural dependency layers defined below, and are out of scope for mechanical dependency enforcement.

## Required Architectural Layout (per package)

Each package MUST expose an architectural layout rooted at:

- `product/config/`
- `product/impl/`
- `adaptor/config/`
- `adaptor/impl/`
- `shell/`

Notes:

- A package MAY contain additional directories, but they are either attachments (`docs/`, `assets/`) or explicitly out of scope for these dependency-layer rules.
- The layer rules below apply to *formal-language* files located under the directories listed above.

## Shell Files (per language)

For each language present in a package, `shell/` MUST contain at most:

- one `requirements.<ext>` file
- one `exports.<ext>` file

The base names MUST be spelled exactly:

- `requirements` (full spelling)
- `exports` (full spelling)

## Dependency Rules (Layering)

### Core Requirement: Funnel All Outside Dependencies

Within `packages/<package>/`, **only** `shell/requirements.<ext>` files MAY contain dependency statements that target **outside the package**.

All other directories/files in the architectural layout MUST NOT directly depend on anything outside the package, including standard library dependencies.

`shell/requirements.<ext>` MAY (and is intended to) depend on **any** outside dependency; "outside" is not limited to this repository.

### Allowed Dependencies Matrix

The rules below allow **intra-layer** dependencies (files within the same directory subtree may depend on each other), plus a small set of cross-layer dependencies.

In the following, "X/**" means any file under that subtree.

1. `product/config/**`
   - MUST depend only on `product/config/**`.
   - MUST NOT depend on anything outside the package.
2. `adaptor/config/**`
   - MUST depend only on `adaptor/config/**`.
   - MUST NOT depend on anything outside the package.
3. `shell/requirements.<ext>`
   - MUST depend only on **outside the package** (not limited to this repository).
   - MUST NOT depend on anything inside the package.
4. `adaptor/impl/**`
   - MAY depend on:
     - `adaptor/impl/**` (intra-layer)
     - `adaptor/config/**`
     - `shell/requirements.<ext>`
   - MUST NOT depend on anything outside the package (directly).
   - MUST NOT depend on `product/**` or `shell/exports.<ext>`.
5. `product/impl/**`
   - MAY depend on:
     - `product/impl/**` (intra-layer)
     - `product/config/**`
     - `adaptor/impl/**`
   - MUST NOT depend on anything outside the package (directly).
   - MUST NOT depend on `adaptor/config/**` or `shell/**` (including `requirements` and `exports`).
6. `shell/exports.<ext>`
   - MAY depend only on `product/impl/**`.
   - MUST NOT depend on anything outside the package.
   - MUST NOT depend on `adaptor/**` or `shell/requirements.<ext>` or any `*/config/**`.

### Recommended (Not Enforced): Consumers Use `shell/exports`

Code outside the package SHOULD depend only on `shell/exports.<ext>` when consuming the package.

Directly depending on internal implementation details is permitted but discouraged, since it weakens encapsulation and makes refactors harder.

## Examples (Illustrative)

These examples are schematic; syntax varies by language.

### Allowed

- `shell/requirements.ts` importing a repository-root third-party lib:
  - `import x from "../../third_party/x"`
- `shell/requirements.py` importing a third-party package (outside the package):
  - `import requests`
- `adaptor/impl/*` importing `shell/requirements.*`:
  - `import { sys } from "../shell/requirements"`
- `product/impl/*` importing `adaptor/impl/*`:
  - `import { AlarmDriver } from "../../adaptor/impl/alarm_driver"`
- `shell/exports.*` importing `product/impl/*`:
  - `export { createAlarm } from "../product/impl/create_alarm"`

### Forbidden

- `product/impl/*` importing standard library (outside package):
  - `import fs from "fs"`
- `adaptor/config/*` importing anything:
  - `import { something } from "..."`
- `shell/requirements.*` importing `product/*`:
  - `import { createAlarm } from "../product/impl/create_alarm"`
