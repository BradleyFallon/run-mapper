# RouteScout Web Planner Wireframe Spec

## Purpose

This document turns the web planner information architecture into a low-fidelity wireframe spec.

It defines:
- the key web planner screens and states
- the major regions within each screen
- what content belongs in each region
- what needs to be validated in wireframing

This is still low fidelity.
It should not be treated as final UI design or visual polish.

## Scope

This wireframe pass covers:
- planner workspace empty state
- planner workspace with a selected starter plan
- planner workspace while generating routes
- planner workspace with candidate results
- planner workspace with one selected route in detail
- saved plans page
- saved routes page

This pass does not yet cover:
- visual styling details
- full account settings
- iPhone navigation flows

## Wireframing Goals

The wireframes should answer these questions:
- Can a user understand how to start planning quickly?
- Is the relationship between category, plan, and route clear?
- Can users compare multiple routes without getting lost?
- Is the planner workspace balanced, or does one panel dominate awkwardly?
- Can saved plans and saved routes be understood as different things?

## Core Layout Recommendation

Use a desktop workspace with three persistent regions:
- left panel: plan browsing and plan editing
- center panel: map
- right panel: route candidates and route detail

Recommended width balance:
- left: 28%
- center: 42%
- right: 30%

This does not need to be exact in implementation, but the map should not be squeezed into a minor
role and the results panel should not overwhelm the planner controls.

## Global Shell

Each screen should share a simple top shell:

```text
+----------------------------------------------------------------------------------------------+
| RouteScout | Planner | Saved Plans | Saved Routes | Account                       User Menu |
+----------------------------------------------------------------------------------------------+
```

The shell should remain stable across the planner and library pages.

## Screen 1: Planner Empty State

### Purpose

This is the first-use planning state.
The user has not selected a plan yet.

### What The Screen Must Do

- make it obvious that the user should start from a plan
- expose plan categories without making category feel like the main object
- preview starter plans clearly
- keep the map present but secondary until a plan is chosen

### Layout

```text
+--------------------------+-----------------------------------+---------------------------+
| Browse Plans             | Map Area                          | Results                   |
|                          |                                   |                           |
| Search plans             | [ subdued map / planning area ]   | No routes yet             |
| [ input.............. ]  |                                   |                           |
|                          |                                   | Choose a plan to start.   |
| Categories               |                                   | Route candidates will     |
| [Confidence] [Explore]   |                                   | appear here after         |
| [Training]   [Trail]     |                                   | generation.               |
|                          |                                   |                           |
| Starter Plans            |                                   |                           |
| - Safe Early Morning     |                                   |                           |
| - City Landmark Run      |                                   |                           |
| - Race Prep Hills        |                                   |                           |
| - Trail Confidence Loop  |                                   |                           |
+--------------------------+-----------------------------------+---------------------------+
```

### What To Validate

- whether starter plans should be shown as list rows or card blocks
- whether category filters belong above the plan list or in a horizontal chip row
- whether the right panel should be mostly empty or show an explainer on first load

## Screen 2: Planner With Starter Plan Selected

### Purpose

The user has chosen a starter plan and is preparing to generate routes.

### What The Screen Must Do

- clearly show the selected plan
- make the editable inputs obvious
- keep advanced options available but not intrusive
- make the main action unmistakable

### Layout

```text
+--------------------------+-----------------------------------+---------------------------+
| Active Plan              | Map Area                          | Results                   |
|                          |                                   |                           |
| Safe Early Morning       | [ planning area map ]             | No routes yet             |
| Category: Confidence     |                                   |                           |
|                          |                                   | Generate routes to see    |
| Basics                   |                                   | recommendations.          |
| Distance     [ 3.0    ]  |                                   |                           |
| Tolerance    [ 0.5    ]  |                                   |                           |
| Start Radius [ 0.2    ]  |                                   |                           |
| Surface      [ Paved  ]  |                                   |                           |
| Terrain      [ Flatter]  |                                   |                           |
|                          |                                   |                           |
| [ Show Advanced ]        |                                   |                           |
| [ Generate Routes ]      |                                   |                           |
+--------------------------+-----------------------------------+---------------------------+
```

### What To Validate

- whether the plan browser and the plan editor should share one column cleanly
- whether plan summary should stay pinned at the top while controls scroll
- whether advanced options should expand inline or open a secondary panel

## Screen 3: Planner Generating State

### Purpose

The system is generating and comparing route candidates.

### What The Screen Must Do

- reassure the user that the system is working
- communicate that multiple routes are being evaluated
- prevent the screen from feeling frozen

### Layout

```text
+--------------------------+-----------------------------------+---------------------------+
| Active Plan              | Map Area                          | Results                   |
|                          |                                   |                           |
| Safe Early Morning       | [ map with soft activity state ]  | Generating routes...      |
|                          |                                   |                           |
| Basics                   |                                   | Comparing candidates      |
| [ editable but subdued ] |                                   | for distance, surface,    |
|                          |                                   | simplicity, and fit.      |
|                          |                                   |                           |
| [ Generating... ]        |                                   | [ skeleton route card ]   |
|                          |                                   | [ skeleton route card ]   |
|                          |                                   | [ skeleton route card ]   |
+--------------------------+-----------------------------------+---------------------------+
```

### What To Validate

- whether the left panel should stay editable during generation
- whether the map should show tentative activity or stay visually quiet
- whether route skeleton cards help users understand the upcoming results

## Screen 4: Planner Results State

### Purpose

The system has returned candidate routes and one is recommended.

### What The Screen Must Do

- make route comparison easy
- make the recommendation clear
- keep alternatives visible
- connect the candidate list to the map

### Layout

```text
+--------------------------+-----------------------------------+---------------------------+
| Active Plan              | Map Area                          | Route Candidates          |
|                          |                                   |                           |
| Safe Early Morning       | [ selected route highlighted ]    | Recommended               |
| Category: Confidence     | [ 2-3 alt routes dimmer ]         | 1. Route A                |
|                          |                                   | 3.1 mi | 34 min | 120 ft |
| Basics / Advanced        |                                   | Flat, paved, simple       |
| [ collapsed summary ]    |                                   |                           |
|                          |                                   | 2. Route B                |
| [ Regenerate ]           |                                   | 2.8 mi | 31 min | 150 ft |
| [ Save Plan ]            |                                   | Slightly greener          |
|                          |                                   |                           |
|                          |                                   | 3. Route C                |
|                          |                                   | 3.4 mi | 36 min | 110 ft |
+--------------------------+-----------------------------------+---------------------------+
```

### What To Validate

- whether route cards should show score explicitly or only explanation and metrics
- how much summary text can fit before cards become heavy
- whether recommendation should be shown as a badge, pinned top card, or both

## Screen 5: Planner Selected Route Detail

### Purpose

The user has clicked one candidate and wants to inspect it more closely.

### What The Screen Must Do

- deepen confidence in the selected route
- show why it was recommended
- support save actions
- keep the candidate list accessible enough for quick switching

### Layout

```text
+--------------------------+-----------------------------------+---------------------------+
| Active Plan              | Map Area                          | Selected Route            |
|                          |                                   |                           |
| Safe Early Morning       | [ selected route emphasized ]     | Route A                   |
|                          |                                   | Recommended               |
| [ Save Plan ]            |                                   |                           |
| [ Regenerate ]           |                                   | 3.1 mi                    |
|                          |                                   | 34 min                    |
|                          |                                   | 120 ft gain               |
|                          |                                   | Mostly paved              |
|                          |                                   |                           |
|                          |                                   | Why it fits               |
|                          |                                   | - close to your start     |
|                          |                                   | - flatter than alt B      |
|                          |                                   | - easier to follow        |
|                          |                                   |                           |
|                          |                                   | [ Save Route ]            |
|                          |                                   | [ Open on iPhone later ]  |
+--------------------------+-----------------------------------+---------------------------+
```

### What To Validate

- whether the candidate list should collapse into tabs when a route is selected
- how much explanation text is necessary before it becomes repetitive
- whether route actions belong in the detail panel or near the map

## Screen 6: Saved Plans Page

### Purpose

This is the reusable planning library.

### What The Screen Must Do

- separate saved plans from generated routes
- make it easy to reopen and reuse a plan
- support lightweight organization and filtering

### Layout

```text
+----------------------------------------------------------------------------------------------+
| Saved Plans                                                                                  |
|----------------------------------------------------------------------------------------------|
| Search [....................]   Category [All v]   Sort [Recent v]                           |
|----------------------------------------------------------------------------------------------|
| Safe Early Morning - Hotel      Confidence     Last used: Yesterday     [ Open ] [ Rename ]  |
| Race Prep Hills 5 Mile          Training       Last used: 3 days ago    [ Open ] [ Rename ]  |
| Race Prep Hills Long Climb      Training       Last used: 1 week ago    [ Open ] [ Rename ]  |
| City Landmark Run - Portland    Explore        Last used: 2 weeks ago   [ Open ] [ Rename ]  |
+----------------------------------------------------------------------------------------------+
```

### What To Validate

- whether this should be table-like or card-like
- whether rename belongs inline or in a lightweight modal
- whether duplication should be visible in MVP or deferred

## Screen 7: Saved Routes Page

### Purpose

This is the library of selected route outcomes.

### What The Screen Must Do

- distinguish saved routes from saved plans
- make route metrics visible at a glance
- preserve connection back to the originating plan

### Layout

```text
+----------------------------------------------------------------------------------------------+
| Saved Routes                                                                                 |
|----------------------------------------------------------------------------------------------|
| Search [....................]   Category [All v]   Sort [Recent v]                           |
|----------------------------------------------------------------------------------------------|
| Downtown Morning Loop         3.1 mi | 34 min | 120 ft | Plan: Safe Early Morning  [ Open ] |
| Portland Landmark Run         5.8 mi | 58 min | 240 ft | Plan: City Landmark Run   [ Open ] |
| Hill Session South            8.0 mi | 74 min | 620 ft | Plan: Race Prep Hills     [ Open ] |
+----------------------------------------------------------------------------------------------+
```

### What To Validate

- whether saved routes need small thumbnail maps in list view
- whether “Plan:” linkage is enough or whether the category should also be shown
- whether a dedicated handoff action should appear in MVP

## Cross-Screen Component Inventory

These are the key components that should recur across the wireframes:
- global nav bar
- category filter chips
- plan list items or starter-plan cards
- active plan summary block
- basic control stack
- advanced options disclosure
- generate button
- map canvas
- route candidate cards
- selected route summary panel
- save actions
- list rows for saved plans and saved routes

## Low-Fidelity Rules

During wireframing:
- stay grayscale
- use simple boxes and labels
- do not apply the full visual system yet
- focus on structure, density, and clarity
- keep route metrics readable even in rough form

## Questions To Resolve During Wireframing

1. Should starter plans appear as cards or rows in the left panel?
2. Should the left panel switch from `Browse` to `Edit`, or should both remain visible together?
3. Should the right panel mix candidate list and selected route detail in one column, or should it
   split into stacked sections?
4. How much of the planner should remain visible when one route is selected?
5. Does the planner feel balanced, or does one panel become a dumping ground?

## Recommended Next Artifact

After this wireframe spec, the next useful design doc is:
- `launch-plan-catalog.md`

But before that, the team should sketch these wireframes quickly in low fidelity and test whether
the planner structure feels clear.
