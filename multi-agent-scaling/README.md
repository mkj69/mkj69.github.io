# Beyond More Agents: Multi-Agent Scaling Atlas

A living, evidence-led research atlas at https://mkj69.github.io/multi-agent-scaling/

## Scope

**Questions:** Does adding agents reliably increase system capability? How do base-model skill, agent count, communication overhead, task coupling and costs jointly determine outcomes? Which organizational designs dominate naive agent-count expansion? Does an agent scaling law exist?

The public page contains six sections: thesis; competing empirical results; mechanistic taxonomy; transparent token-cost lab; filterable literature leads; proposed experimental agenda.

## Evidence hygiene

- **Direct empirical evidence:** reported performance/cost claims from source papers. Distinguish preprints from the 2026 Nature Machine Intelligence version of *Towards a science of scaling agent systems*; do not combine old and updated sample sizes.
- **Literature leads:** some entries link to an arXiv **search**, not a verified paper record. These are explicitly marked SEARCH and should be resolved before use in a formal literature review.
- **Synthesis:** no consensus universal monotonic scaling law follows from currently mixed results.
- **Hypothesis:** optimum team size is task-, model-, topology- and budget-dependent.
- **Interactive lab:** simple directed-edge accounting, **not** a validated task-accuracy predictor.

## Controlled study checklist

1. Compare independent samples/best-of-N, single-agent self-consistency and real coordinated teams.
2. Fix model, task, verifier, tool access and resource limits across architectures.
3. Cross n, agent skill, task decomposability, topology, routing, rounds and message content.
4. Report quality at the same total tokens and same wall-clock budget.
5. Capture trajectory-level checkpoints, errors transmitted, shared-workspace interference, redundant exploration and verifier feedback.
6. Estimate quality–cost–latency Pareto frontiers with task-level uncertainty.

## File layout

- `index.html`: paper-backed research narrative
- `style.css`: responsive design
- `app.js`: bibliography explorer and transparent communication calculator

## Publication

Hosted under the author's existing GitHub Pages repository as a project directory. A separate GitHub repository has **not** been created; the available connected GitHub tools support updating files but not creating repositories. This site is therefore not yet a standalone repository.

Maintained by Kaijing Ma. Initial version: 19 October 2026.
