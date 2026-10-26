# Community plan

Building a community is a core goal, not a side effect. We follow the patterns of successful
open-source business software: open governance, steering by area, module/app repositories,
sponsors, events, and a self-hostable, modular product.

## Make it easy to try
- Public demo site with realistic sample data (loads, carriers, lanes), reset nightly.
- One-command dev setup (devcontainer / Docker Compose with bench, ERPNext v16 and Vecto).
- Docs site: user guide, admin guide, API reference (OpenAPI), MCP guide, architecture, ADRs.

## Make it easy to contribute
- `good first issue` and `help wanted` labels kept stocked; each with a clear brief.
- Task briefs and ADRs in the open — contributors see why, not only what.
- PR template, fast first response (target: 2 working days), CI that explains failures.
- **Region maintainers:** compliance adapters (ADR-0005) are owned by contributors from that region
  (US-FMCSA, Canada provinces, Mexico, India, EU…). Same for load boards, ELD and EDI adapters.
- Integrations can live as separate Frappe apps (`vecto_<integration>`) with a listed directory.
- Translations for UI and docs.

## Make it visible
- Public roadmap: GitHub milestones and the project board.
- Release notes every release; monthly community update.
- Discussion space: Frappe Forum category + GitHub Discussions; optional chat server.
- Monthly community call (demo, roadmap, Q&A).
- Contributor recognition in release notes and README.

## Governance (lightweight to start)
- Maintainer: @anupamvs. Add maintainers by area as contributors earn it.
- Decisions through ADRs; anyone can propose one.
- Code of Conduct and Security policy already in the repo.
- Later: steering group, sponsors/donations, commercial hosting and support funding the core.
