# RouteScout Icon Vocabulary

## Purpose

This document defines the first shared icon vocabulary for RouteScout.

It is meant to support:
- the web planner
- the iOS app
- Scout Spec cards
- Route Cards

The goal is not to use the exact same icon files on every platform.
The goal is to use the same icon meanings on every platform.

## Platform Rule

- `iOS`: use SF Symbols
- `Web`: use Lucide
- `Route-specific feature badges`: allow a small custom RouteScout badge set where stock icons are
  too weak or too generic

This should be treated as a semantic mapping system, not a strict one-to-one art match.

## Icon Families

The icon system should be split into two layers:

### 1. UI Utility Icons

These are standard interface icons used in navigation, buttons, filters, and controls.

Examples:
- search
- save
- filter
- location
- settings
- compare

These should use stock platform icons.

### 2. Route Meaning Icons

These represent route characteristics and plan priorities.

Examples:
- paved
- lit
- hills
- quiet
- landmark
- trail
- loop

These are the icons that matter most for Scout Specs and Route Cards.

## Recommended Core Set

### Start And Route Structure

| Meaning | Use | Lucide | SF Symbols |
|---|---|---|---|
| `Start proximity` | closer-start priority, start radius, route origin | `MapPinned` | `mappin.and.ellipse` |
| `Route / path` | generic route identity | `Route` | `point.topleft.down.curvedto.point.bottomright.up` |
| `Loop` | loop route shape | `RefreshCw` | `arrow.trianglehead.clockwise` |
| `Navigation clarity` | simple navigation, confidence | `Navigation` | `location.north.line` |

### Distance And Time

| Meaning | Use | Lucide | SF Symbols |
|---|---|---|---|
| `Distance accuracy` | distance-focused plans and route stats | `Ruler` | `ruler` |
| `Duration` | estimated runtime | `Timer` | `timer` |
| `Pace / efficiency` | optional later route stat | `Gauge` | `gauge` |

### Terrain And Surface

| Meaning | Use | Lucide | SF Symbols |
|---|---|---|---|
| `Elevation profile` | training plans, elevation-heavy routes | `Mountain` | `mountain.2` |
| `Flat / low climb` | flatter routes | `Minus` | `minus` |
| `Trail quality` | trail-forward routes | `Trees` | `figure.hiking` |
| `Nature access` | greener / park-adjacent routes | `Trees` | `tree` |

### Place And Discovery

| Meaning | Use | Lucide | SF Symbols |
|---|---|---|---|
| `Landmarks` | explore plans and notable route anchors | `Building2` | `building.columns` |
| `Park / green space` | scenic or park access | `Trees` | `leaf` |
| `City route` | urban route character | `Building2` | `building.2` |

### Confidence And Safety

| Meaning | Use | Lucide | SF Symbols |
|---|---|---|---|
| `Lighting and confidence` | safe early-morning and trust-oriented plans | `ShieldCheck` | `checkmark.shield` |
| `Quiet surroundings` | low-noise environments | `VolumeX` | `speaker.slash` |
| `Low interruptions` | training routes with fewer forced stops | `ShieldMinus` | `minus.circle` |

## Where Custom RouteScout Badges Are Better

Some route concepts are important enough that stock icons are not ideal.

These should be candidates for custom RouteScout badges:
- `Paved surface`
- `Lit route`
- `Low interruptions`
- `Scenic landmark route`
- `Workout route`
- `Confidence route`

Reason:
- stock icon packs do not always have clean, specific symbols for these meanings
- Route Cards should have their own collectible language
- a small badge system will look more intentional than forcing weak metaphors

## Recommendation By Object Type

### Scout Specs

Scout Specs should use icons sparingly.

Good uses:
- top priority marker
- secondary priority marker
- route shape
- surface
- hill intent
- start radius

Scout Specs should feel structured and readable, not decorative.

### Route Cards

Route Cards should use icons more heavily.

Good uses:
- route features row
- key traits
- saved collection identity
- quick scan of route strengths

Route Cards are where the collectible vocabulary belongs.

## Recommended MVP Route Feature Badge Set

For MVP, I recommend a small Route Card badge set:

| Badge meaning | Primary use |
|---|---|
| `PV` paved | strong paved consistency |
| `LT` lit | stronger lighting / confidence fit |
| `FL` flat | flatter route character |
| `HL` hills | climbing-focused route |
| `TR` trail | strong trail character |
| `PK` park | park or green access |
| `LM` landmark | notable route anchor |
| `QT` quiet | lower-noise route feel |
| `LP` loop | clean loop shape |
| `NX` nearby | closer-to-start convenience |

These can start as styled text badges before becoming custom icon art.

## Practical Recommendation

For implementation:

1. use stock Lucide and SF icons for general UI and plan parameters
2. use a small RouteScout badge set for route-feature identity
3. keep the semantic meanings aligned across web and iOS

That gives RouteScout:
- native-feeling controls
- a shared product language
- room for a distinctive collectible Route Card system

## Notes

The Lucide names above are the recommended web counterparts.
The SF Symbol names above are the recommended iOS counterparts.

Before final implementation:
- verify the final SF Symbol names in the SF Symbols app
- verify the final Lucide component names in the icon package actually used by the web app

This doc is the semantic system.
The final asset names can be tightened during implementation.
