---
name: production-agent-workflow
description: Turn vague or ambitious agent ideas into production-grade agent development workflows. Use when the user wants to build, plan, productize, or iterate an agent; asks for PRD, plan.md files, /goal prompts, goal-mode execution, consolidation, MVP scope, readiness gates, CLI/Web/Desktop productization, or wants to reuse the "PRD -> plans -> goals -> implementation -> consolidation" process for another agent.
---

# Production Agent Workflow

## Purpose

Use this skill to turn an agent idea into a repeatable product-development loop:

1. Align product intent through focused questions.
2. Write a PRD.
3. Split the PRD into executable `plan.md` files.
4. Convert each plan into strong `/goal` prompts.
5. Switch Codex into goal mode and send one goal prompt at a time.
6. Execute plans incrementally with verification.
7. Consolidate completed work, gaps, and the next loop.

For artifact templates and examples, read `references/workflow-blueprint.md`.

## Operating Rules

- Start with product clarity, not code, unless the user explicitly asks to implement immediately.
- Prefer concrete artifacts over discussion: `PRD.md`, `plans/*/plan.md`, `goals/*.goal.md`, `consolidation.md`.
- Keep MVP scope narrow enough to ship and broad enough to prove the agent's core loop.
- Build the platform first, then domain/tool adapters, then product surfaces.
- Treat "mock works" and "real integration works" as different readiness states.
- Never claim production readiness without tests, diagnostics, and clear limitations.
- If a runtime, API, solver, model, credential, or external service is missing, implement a diagnostic/skip path rather than blocking the whole workflow.

## Phase 1: Product Alignment

Ask only the smallest useful set of questions. If the user already gave enough signal, proceed with assumptions and record them.

Collect:

- Target user and pain.
- Agent outcome and final deliverable.
- Inputs and product surfaces.
- Core workflow stages.
- Quality priorities: stability, accuracy, deployment, test coverage, UX, cost, latency, safety.
- Runtime and integration constraints.
- MVP boundaries and explicitly excluded work.
- First domain/use-case and future expansion path.

After alignment, write `specs/<agent-name>/PRD.md`.

## Phase 2: PRD

The PRD should define the agent as a product, not only a code project.

Include:

- Positioning and one-sentence goal.
- Target users.
- User problems.
- Product goals and non-goals.
- Core concepts and schemas.
- Input and output contracts.
- End-to-end workflow.
- Architecture: platform core, adapters/domain packs, product surfaces.
- MVP scope and future scope.
- Error, diagnostic, and human-review behavior.
- Testing/readiness requirements.

Record assumptions and open questions directly in the PRD.

## Phase 3: Plan Decomposition

Create `specs/<agent-name>/plans/` with numbered plan folders. Use one `plan.md` per independently executable slice.

Default sequence:

1. Product shell and workspace/state model.
2. Canonical schema or task contract.
3. Intake, parsing, classification, and clarification.
4. Registry, adapter, or tool interface.
5. First domain/tool pack.
6. Execution engine and environment handling.
7. Validation, report, and delivery package.
8. Testing and production readiness.
9. Product surface such as CLI, Web, desktop, API, or plugin.

For different agent types, rename the slices but preserve the dependency order: contract before adapters, adapters before execution, execution before readiness.

Each plan must include goal, scope, in/out of scope, tasks, acceptance criteria, test plan, and done definition.

## Phase 4: Goal Prompt Generation

For every plan, create `specs/<agent-name>/goals/<number>-<slug>.goal.md`.

If `qiaomu-goal-meta-skill` is available, use it to draft `/goal` prompts. Otherwise write the same structure manually:

- Outcome.
- Verification.
- Constraints.
- Boundaries.
- Iteration policy.
- Completion evidence.
- Pause/block conditions.

Make the goal prompt operational enough that Codex can execute without re-asking the whole product strategy.

## Phase 5: Goal Mode Execution

Do not treat goal prompt files as executed just because they exist.

For each plan:

- Open the selected `goals/<number>-<slug>.goal.md`.
- Copy the recommended `/goal` block.
- Enter Codex goal mode.
- Send the `/goal` prompt.
- Let Codex work under that active goal until it completes, blocks, or hits a required user decision.
- Record the execution evidence in the matching `plan.md`.

If the environment cannot actually enter goal mode, record this as an explicit limitation in `consolidation.md`.

## Phase 6: Implementation Loop

Execute goals in dependency order. For each goal:

- Read PRD, the selected plan, and existing implementation.
- Implement the smallest complete vertical slice.
- Add focused tests before broad refactors.
- Run verification commands and record results in the plan.
- Update the plan checklist and implementation evidence.
- Preserve limitations honestly.

When multiple plans are now unblocked, continue automatically if the user asked for an autonomous run. Pause only for decisions that materially change product scope, require credentials, require paid services, or need destructive/system-level actions.

## Phase 7: Readiness

Add a release-readiness artifact once the MVP loop exists.

Track:

- Pass/fail/skip/risk items.
- Unit and integration test results.
- Mock full workflow.
- Conditional real smoke tests.
- Missing environments and setup guidance.
- Known limitations.
- Next recommended product/domain slice.

Use readiness states such as:

- `ready`: all MVP gates and real smoke tests passed.
- `ready_with_limitations`: core workflow passed, but optional or environment-dependent gates skipped.
- `not_ready`: required tests, core workflow, or blocking integrations failed.

## Phase 8: Consolidation

After one development loop, create `specs/<agent-name>/consolidation.md`.

Summarize:

- Overall status.
- Plan-by-plan status.
- Implemented capabilities.
- Verification commands and results.
- Current product workflow.
- Known limitations.
- Gaps versus PRD.
- Next iteration priorities.
- Completion judgment.

If consolidation exposes missing MVP functionality, run the loop again: update PRD if needed, add/refine plans, generate goals, execute, verify, consolidate.
