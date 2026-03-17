# RouteScout Platform Strategy

## Purpose

This document defines how RouteScout should split its experience across platforms.

The product should support both:
- a web app for route planning
- an iOS app for full use, including real-time navigation

## Product Direction

RouteScout should not be treated as a single-surface product.

Instead, it should have two complementary product surfaces:

1. Web app
   Best for planning, comparison, editing, and saving routes ahead of time.
2. iOS app
   Best for full product use, including planning, route review, and in-run navigation.

## Why This Split Makes Sense

Many users will want to plan from a laptop before a run.

This is especially true for:
- travel planning before a trip
- race-prep route planning
- landmark exploration in a new city
- careful route comparison that benefits from more screen space

At the same time, the iPhone remains the most natural device for:
- current-location-aware route planning
- on-the-go review
- starting a run
- following a route during the run

## Platform Roles

### Web App

Primary role:
- planning surface

The web app should be optimized for:
- browsing and filtering plans
- choosing or editing a plan
- comparing route candidates
- reviewing maps on a larger screen
- saving plans
- saving or bookmarking routes

The web app is not the primary real-time navigation surface.

### iOS App

Primary role:
- full RouteScout experience

The iOS app should support:
- all planning functionality
- saved plans and saved routes
- route selection
- pre-run route review
- real-time navigation during the run

The iOS app should be capable of everything the web planner can do, plus navigation.

## Core Product Principle

The web app is a planning-first companion.
The iOS app is the primary full product.

This means:
- no essential planning concepts should exist only on web
- real-time navigation should live in iOS
- plans and routes should sync across both surfaces

## Planning And Navigation Model

Recommended model:
- plan on web or iOS
- save the plan and selected route
- open the route on iPhone when it is time to run
- use iPhone for navigation and in-run interaction

This fits real user behavior well:
- laptop for deliberate planning
- phone for execution

## MVP Implications

### Web MVP

The web app should support:
- plan discovery and filtering
- starter plan selection
- plan editing
- route generation
- route comparison
- route detail review
- saved plans

The web app does not need:
- real-time in-run navigation
- active route-following UI
- phone-specific workout controls

### iOS MVP

The iOS app should support:
- all core planning flows
- route generation
- route comparison
- route detail review
- saved plans
- selected-route access
- navigation-ready route experience

If tradeoffs are required, the iOS app remains the more strategically important product surface.

## Shared Cross-Platform Requirements

The product should maintain consistency across web and iOS for:
- terminology
- plan categories
- plans
- route metrics
- route explanations
- saved plan behavior

Users should feel they are using one product, not two disconnected tools.

## Data And Account Implications

This platform model strongly suggests:
- user accounts
- cloud-synced saved plans
- cloud-synced saved routes
- handoff from web planning to iPhone route use

Even if every part of account infrastructure is not in the first build, the product architecture
should anticipate it.

## UX Implications

### Web UX

The web app can lean into:
- wider map layouts
- side-by-side route comparison
- richer route panels
- more comfortable advanced editing

### iOS UX

The iOS app should lean into:
- faster plan selection
- location-aware planning
- pre-run confidence
- one-handed route review
- navigation-focused route detail

## Strategic Benefit

This split gives RouteScout:
- a better planning environment
- a stronger execution environment
- a more premium multi-device story
- a better fit for both casual and serious runners

It also improves product credibility for users who expect premium consumer software to work across
devices cleanly.

## Recommended Product Statement

RouteScout is a planning-first web experience paired with a full-featured iPhone app for taking the
route into the real world.

## Next Design Docs

After this document, the most useful follow-on docs are:
1. web information architecture
2. iOS navigation experience
3. cross-platform sync and account model
