# Process

This repository is currently a personal project. Process is intentionally minimal.

## Changing Reference Rules

Reference rules live in `docs/reference/*` and are the single source of truth.

When you change any Reference rule, you MUST:

- update the corresponding ADR (either create a new ADR or supersede an existing one);
- ensure `docs/README.md` still points to the correct Reference document.

## ADR Discipline (Minimum)

If a change affects any of the following, it requires an ADR update:

- package boundaries or directory layout expectations;
- dependency rules (what can depend on what);
- what counts as "outside the package";
- any rule intended to be mechanically checkable later.

## Pre-change Checklist

- Is the change a rule (Reference) or a motivation/explanation (Explanation)?
- Can the rule be stated unambiguously with MUST/MUST NOT/SHOULD?
- Does it create new exceptions? If yes, can they be removed by refining definitions instead?

