# ADR-0004: Frontend stack for the SPA, portals and chat
Status: **Accepted** · Date: 2026-10-26 · Decider: Anupam

**Decision.** Vue 3 + TypeScript + Vite + **Frappe UI 1.x** (pinned), with its Tailwind preset,
design tokens and dark mode, and its data composables (`useDoc`, `useList`, `useCall`). Live
updates through Frappe realtime. Experimental Frappe UI parts (e.g. command palette) are wrapped
in our own components so they can be swapped.

**Patterns we follow from the Frappe app family:** list views with filters, saved views and
Kanban; record page with activity timeline and side details panel; status badges with fixed
categories; charts and dashboards; portal pages for customers and carriers.

**Consequences.** + Native look next to ERPNext v16; least glue code; largest contributor pool in
the Frappe community. − Frappe UI 1.0 is new: pin versions and track its changelog.
