# RouteScout Visual Design System

## Purpose

This document defines the first visual design system for RouteScout.

It translates the brand direction into concrete UI guidance for an iPhone-first product with a
premium dark theme, restrained color, and high contrast.

## Design Principles

The visual system should feel:
- sleek
- premium
- precise
- calm
- athletic
- native to iPhone

The UI should prioritize:
- legibility
- contrast
- hierarchy
- focus
- spatial clarity

The UI should avoid:
- visual noise
- excessive color
- decorative clutter
- soft low-contrast ambiguity

## Theme Model

Default theme:
- dark theme

Design intent:
- near-black backgrounds
- layered charcoal surfaces
- bright, readable typography
- a single restrained accent family

The app should look premium in low-light environments and early-morning usage contexts.

## Color System

### Core Neutrals

Primary background:
- `bg.canvas = #050607`

Secondary background:
- `bg.base = #0B0D0F`

Primary surface:
- `surface.default = #111417`

Secondary surface:
- `surface.raised = #171B1F`

Tertiary surface:
- `surface.overlay = #1D2227`

Strong divider:
- `border.strong = #2A3138`

Soft divider:
- `border.subtle = #1E242A`

These neutrals should create depth through layering, not through obvious gradients.

### Text Colors

Primary text:
- `text.primary = #F5F7FA`

Secondary text:
- `text.secondary = #B4BCC6`

Muted text:
- `text.muted = #7D8793`

Inverse text:
- `text.inverse = #050607`

Disabled text:
- `text.disabled = #5F6872`

### Accent Family

Primary accent:
- `accent.primary = #E6FF4D`

Primary accent pressed:
- `accent.primaryPressed = #D3F03D`

Accent soft background:
- `accent.soft = rgba(230, 255, 77, 0.14)`

Accent border:
- `accent.border = rgba(230, 255, 77, 0.32)`

This accent should be used sparingly.
It should feel sharp and athletic without turning the entire interface neon.

### Semantic Colors

Success:
- `success = #3DDC97`

Warning:
- `warning = #FFB84D`

Error:
- `error = #FF5C7A`

Info:
- `info = #73B8FF`

These colors should appear mostly in secondary contexts such as alerts, route warnings, or status
indicators, not as competing primary brand accents.

## Color Usage Rules

Use the accent for:
- selected tabs or chips
- primary CTA buttons
- active map route emphasis
- highlighted key metrics

Do not use the accent for:
- large background fills
- every interactive control
- multiple unrelated highlights on one screen

The interface should mostly rely on:
- neutrals for structure
- white and gray for clarity
- accent for emphasis

## Surface System

### Surface Roles

`Canvas`
- the app background
- deepest and darkest layer

`Base`
- the main screen background within content areas

`Default Surface`
- cards
- panels
- bottom sheets

`Raised Surface`
- selected cards
- active filter groups
- important metrics blocks

`Overlay Surface`
- modals
- floating controls
- transient panels

### Surface Treatment

Surfaces should feel:
- solid
- refined
- slightly soft at the edges
- layered with subtle contrast

Use:
- gentle corner radii
- subtle borders
- restrained shadows or elevation

Avoid:
- obvious glassmorphism
- frosted effects as a default material
- heavy shadows
- glossy gradients

## Typography System

### Typography Direction

Typography should feel:
- premium
- compact
- modern
- precise
- slightly kinetic in select hero moments

Recommended platform approach:
- use the iOS system font stack for native performance and familiarity
- rely on weight, spacing, and hierarchy instead of novelty fonts
- use italic or slight forward slant only as an accent treatment, not as the default heading style

This supports the Apple-compatible goal while keeping the product credible in a performance context.

### Type Scale

Display:
- `display.l = 40 / 44`
- use sparingly for hero moments or onboarding

Heading 1:
- `heading.xl = 32 / 36`

Heading 2:
- `heading.l = 24 / 30`

Heading 3:
- `heading.m = 20 / 26`

Heading 4:
- `heading.s = 17 / 22`

Body large:
- `body.l = 17 / 24`

Body:
- `body.m = 15 / 22`

Body small:
- `body.s = 13 / 18`

Caption:
- `caption = 12 / 16`

Metric large:
- `metric.l = 28 / 30`

Metric medium:
- `metric.m = 20 / 24`

Metric small:
- `metric.s = 15 / 18`

The format above is:
- `font-size / line-height`

### Typography Usage

Headings:
- short
- confident
- never verbose
- upright by default

Display and featured titles:
- may use a subtle italic or forward slant
- should suggest motion and anticipation without feeling aggressive
- should be reserved for hero moments, featured route names, or selected-plan emphasis

Body text:
- concise
- readable
- secondary to route metrics and route decisions

Metrics:
- highly scannable
- slightly tighter
- visually more technical than body text

### Font Weight Guidance

Recommended weights:
- regular for body copy
- medium for labels and secondary emphasis
- semibold for section headings and key metrics
- bold only for hero emphasis or very important numeric values

Avoid overusing bold.
The interface should feel disciplined, not shouty.

Avoid overusing slanted typography.
Too much slant will make the product feel stressed instead of energizing.

## Spacing System

Use an 8-point base system.

Core spacing scale:
- `4`
- `8`
- `12`
- `16`
- `24`
- `32`
- `40`
- `48`

### Spacing Usage

Tight spacing:
- `4` to `8`
- icon and label groupings
- chip padding adjustments

Standard spacing:
- `12` to `16`
- control padding
- card internal spacing
- component gaps

Section spacing:
- `24` to `32`
- separation between major content blocks

Large spacing:
- `40` to `48`
- top-of-screen breathing room
- major onboarding or hero layouts

### Layout Rhythm

The app should feel:
- compact enough for dense route information
- open enough to feel premium

Avoid:
- cramped metrics
- oversized whitespace that weakens scan speed

## Corner Radius System

Recommended radii:
- `radius.sm = 10`
- `radius.md = 14`
- `radius.lg = 20`
- `radius.xl = 28`

Usage:
- small chips and pills: `10`
- cards and panels: `14`
- bottom sheets and major containers: `20`
- large hero surfaces: `28`

The radius system should feel modern and smooth, but not cartoonishly rounded.

## Border And Elevation

Borders:
- use subtle border definition on dark surfaces
- prefer thin, low-contrast outlines to hard frames

Elevation:
- use minimal shadow
- rely more on value contrast between surfaces than on blur-heavy shadow

Recommended approach:
- dark UI depth should come mostly from layered tones, not bright edge lighting

## Component Guidance

### Buttons

Primary button:
- accent fill
- dark text
- medium-large height
- strong contrast

Secondary button:
- raised dark surface
- subtle border
- light text

Ghost button:
- no heavy fill
- text-led
- used only for less important actions

### Chips And Filters

Unselected:
- dark raised surface
- subtle border

Selected:
- accent soft background
- accent border
- brighter text or icon

### Scout Spec Cards

Scout Specs are the card-format presentation of plans.

They should feel like:
- structured
- technical
- parameter-led
- calm and readable

Scout Specs should not use a hero image.

They should focus on:
- plan name
- category
- top priority
- secondary priority
- supporting parameters
- route shape and default constraints

Scout Specs should read like a clear planning brief, not a collectible object.

### Route Cards

Route cards should feel like:
- premium collectible cards
- specific enough to feel worth saving
- richer and more object-like than Scout Specs

Each route card should support:
- route rank
- distance
- duration
- elevation
- feature icons
- route-specific traits
- short explanation
- selection state

Selected cards should gain:
- stronger border contrast
- slightly brighter surface
- clearer accent treatment

Route cards may use a top-half visual area.
That area can include:
- route overview graphics
- route-specific landmark imagery
- terrain cues
- other route identity signals

The route card is where the more collectible trading-card language belongs.

### Maps

The map should sit inside the visual system instead of feeling like a foreign embedded tool.

Principles:
- dark map styling
- restrained labels
- strong route line contrast
- candidate routes visually subordinate to the selected route

Selected route:
- brightest and most emphasized

Alternative routes:
- dimmer, thinner, quieter

## Iconography

Icons should be:
- simple
- sharp
- consistent in stroke weight
- utility-focused

Avoid:
- overly playful icon sets
- mixed icon styles
- decorative illustration language in core product flows

## Accessibility Guidance

Even with a premium dark theme, the app must remain highly legible.

Requirements:
- strong text contrast
- clear tap targets
- color not being the only signal
- route states distinguishable beyond accent color alone

High contrast must be a product feature, not just a visual preference.

## Visual Tone Summary

The final system should feel like:
- a premium running tool
- built for iPhone
- visually quiet but highly intentional
- technically credible
- compatible with Apple and Nike ecosystems without mimicking them

## Next Design Docs

After this document, the most useful next visual docs are:
1. iOS screen architecture
2. component inventory
3. route card design spec
4. map styling spec
