# RouteScout Web Planner Information Architecture

## Purpose

This document defines the structure of the RouteScout web planner.

The web product is planning-first.
Its job is to help users browse plans, customize a plan, generate route candidates, compare them,
and save useful results for later use on iPhone.

This is an information architecture document, not a visual mockup.
It focuses on structure, navigation, layout, and screen states.

## Role Of The Web App

The web app should be optimized for:
- deliberate planning
- larger-screen map review
- route comparison
- plan editing
- saved-plan management

The web app should not be treated as the primary in-run navigation surface.

## Primary User Goals

The web planner should help users do these things well:
- browse starter plans
- filter plans by category
- choose a plan that fits the run they want
- edit plan parameters
- generate several candidate routes
- compare those routes quickly
- inspect one route in detail
- save a plan
- save a preferred route
- return to those saved items later

## Core Content Model

The web planner is built around four objects:

### Plan Category

Examples:
- `Confidence`
- `Explore`
- `Training`
- `Trail`

Purpose:
- organize starter plans
- support browsing and filtering

### Plan

A reusable planning specification.

Examples:
- `Safe Early Morning`
- `City Landmark Run`
- `Race Prep Hills`

Plan types:
- starter plan
- saved plan

### Route Candidate

A generated route option produced from a selected plan.

Each route candidate should have:
- map geometry
- core metrics
- explanation
- score or rank

### Saved Route

A route the user wants to keep and potentially use later on iPhone.

## Top-Level Web Sections

The web app should be intentionally small.

Recommended top-level sections:
- `Planner`
- `Saved Plans`
- `Saved Routes`
- `Account`

This keeps the product understandable while still supporting repeat use.

## Global Navigation

Global navigation should be persistent and simple.

Recommended global nav:
- RouteScout wordmark / home link
- `Planner`
- `Saved Plans`
- `Saved Routes`
- `Account`

Recommended utility actions:
- user avatar or account menu
- optional `Open on iPhone` or `Send to iPhone` action later

The global nav should not be crowded with secondary tools in MVP.

## Primary Web Surface

The `Planner` should be the main product screen.

This should be a workspace, not a step-by-step wizard.

Recommended desktop layout:
- left panel: plan browser and plan editor
- center panel: map
- right panel: route candidates and selected route detail

This layout supports the core planning workflow without forcing constant page changes.

## Planner Workspace Structure

### Left Panel: Plan Panel

Purpose:
- choose and edit the active plan

Recommended contents:
- plan search
- category filters
- starter plan list or cards
- active plan summary
- editable controls
- advanced controls toggle
- `Generate routes` action

This panel is the control center for the planning request.

### Center Panel: Map Panel

Purpose:
- show the planning area and generated routes

Recommended contents:
- main map canvas
- start area visualization
- selected route
- alternative route lines
- lightweight map controls

The map should support planning review, not act as the only place to understand the route.

### Right Panel: Results Panel

Purpose:
- compare route candidates and inspect the selected route

Recommended contents:
- route candidate list
- recommendation indicator
- selected route summary
- route rationale
- route-specific actions such as save or handoff later

This panel is where the user decides which route they trust.

## Planner Workspace States

The planner should be designed around a small set of explicit states.

### 1. Empty State

User has not selected a plan yet.

The screen should emphasize:
- category browsing
- starter plan discovery
- a clear starting point

### 2. Plan Selected State

User has chosen a starter plan, but has not generated routes yet.

The screen should emphasize:
- plan summary
- editable inputs
- clear `Generate routes` action

### 3. Editing State

User is adjusting plan inputs.

The screen should make it easy to:
- tweak basics quickly
- open advanced controls without cluttering the default view

### 4. Generating State

The system is generating candidates.

The screen should communicate:
- that RouteScout is actively working
- that multiple candidates are being compared
- that the user should expect a ranked result, not just one opaque route

### 5. Results State

Candidates are available.

The screen should emphasize:
- ranked comparison
- selected recommendation
- fast scanability

### 6. Selected Route State

One route is actively selected.

The screen should emphasize:
- selected route line on map
- route metrics
- route explanation
- save actions

### 7. Saved Confirmation State

User has saved a plan or route.

The screen should provide:
- confirmation
- next action options
- clear path back to planning

### 8. Error State

Generation failed or no viable routes were returned.

The screen should provide:
- a clear explanation
- likely next adjustments
- a way to retry without losing context

## Recommended Page Inventory

The web MVP only needs a small number of pages.

### 1. Planner

Primary page.

Purpose:
- full planning workspace

### 2. Saved Plans

Purpose:
- browse, reopen, rename, and manage saved plans

This page should feel like a reusable planning library.

### 3. Saved Routes

Purpose:
- browse previously selected routes
- reopen route details
- prepare for later iPhone handoff

### 4. Account

Purpose:
- account basics
- sync status later
- preferences later

This page can stay minimal in MVP.

## Planner Navigation Model

The planner should behave like a workspace with local sections rather than separate full pages for
every sub-step.

Recommended local structure inside `Planner`:
- `Browse Plans`
- `Plan Details`
- `Advanced Options`
- `Results`

These can appear as stacked regions, tabs, or collapsible sections inside the workspace.

Do not turn every small action into a separate page.

## Recommended Interaction Sequence

The web planner should support this default sequence:

1. Open `Planner`
2. Browse plans
3. Filter by category if needed
4. Choose a starter plan
5. Adjust core plan settings
6. Optionally open advanced options
7. Generate route candidates
8. Compare candidates
9. Select one route
10. Save the plan and/or save the route
11. Later open on iPhone

This sequence should feel visible in the structure of the planner itself.

## Route Candidate Presentation

The results panel should be optimized for fast comparison.

Each route candidate should show:
- rank or recommendation status
- total distance
- estimated duration
- elevation gain
- surface summary
- short explanation

Only one route should be selected at a time.
Alternative routes should remain visible but secondary.

## Saved Plans Architecture

The `Saved Plans` section should support:
- saved plan list
- search
- category filter
- last-used or recently edited sorting
- open plan in planner

It should not feel like a dead archive.
It should feel like a reusable planning toolkit.

## Saved Routes Architecture

The `Saved Routes` section should support:
- saved route list
- key route metrics in list view
- reopen route detail
- identify which plan produced the route
- later handoff to iPhone

Saved routes are outcomes.
Saved plans are reusable instructions.
The IA should preserve that difference.

## Search And Filtering

The web planner needs lightweight filtering in two places:

### Plan Filtering

Support:
- category filter
- plan search
- starter vs saved plans later if needed

### Saved Item Filtering

Support:
- search by name
- category filter
- recent vs older sorting

Do not overload the MVP with complex filtering logic beyond this.

## URL And State Model

The web app should eventually support stable URLs for:
- planner
- saved plans
- saved routes
- specific saved plan
- specific saved route

For MVP, the minimum useful route structure is:
- `/planner`
- `/plans`
- `/routes`
- `/account`

Later deep-link targets may include:
- `/planner?plan=...`
- `/plans/:id`
- `/routes/:id`

## Responsive Behavior

This IA is desktop-first because the web app is planning-first.

However, the structure should degrade cleanly on smaller screens:
- left plan panel becomes collapsible
- results panel may become a drawer or tabbed region
- map remains central

The web app does not need to become the primary mobile route-use surface.
iPhone handles that role.

## What The IA Must Make Clear

The web planner should make these distinctions obvious:
- category is for browsing
- plan is the editable request
- route is the generated result
- saved plan is reusable
- saved route is a chosen outcome

If these distinctions are unclear in the IA, the product will feel confusing quickly.

## What To Wireframe Next

The next wireframing pass should cover:
- planner empty state
- plan selected state
- editing state
- generating state
- results state
- selected route detail state
- saved plans page
- saved routes page

## Open Questions

These should be resolved during wireframing:

1. Should starter plans appear as cards, a list, or both?
2. Should the plan editor and plan browser share one left panel or split into tabs?
3. Should the selected route detail live inside the results panel or in a larger drawer/modal?
4. How much advanced editing should appear inline versus behind disclosure?
5. Should saved routes live as a separate section in MVP, or only inside planner history?

## Output Of This Doc

The main architectural recommendation is:
- a small top-level sitemap
- a workspace-style planner
- saved plans and saved routes as separate library sections
- desktop-first planning on web

This should be the basis for the low-fidelity wireframes.
