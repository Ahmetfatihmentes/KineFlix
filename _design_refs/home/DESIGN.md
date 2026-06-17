---
name: Cinema Intelligence
colors:
  surface: '#0f131d'
  surface-dim: '#0f131d'
  surface-bright: '#353944'
  surface-container-lowest: '#0a0e17'
  surface-container-low: '#171c25'
  surface-container: '#1b2029'
  surface-container-high: '#262a34'
  surface-container-highest: '#31353f'
  on-surface: '#dfe2f0'
  on-surface-variant: '#d0c5b2'
  inverse-surface: '#dfe2f0'
  inverse-on-surface: '#2c303b'
  outline: '#99907e'
  outline-variant: '#4d4637'
  surface-tint: '#e6c364'
  primary: '#e6c364'
  on-primary: '#3d2e00'
  primary-container: '#c9a84c'
  on-primary-container: '#503d00'
  inverse-primary: '#755b00'
  secondary: '#adc8f5'
  on-secondary: '#133155'
  secondary-container: '#2f4a70'
  on-secondary-container: '#9fbae6'
  tertiary: '#78daaa'
  on-tertiary: '#003824'
  tertiary-container: '#5cbe90'
  on-tertiary-container: '#004a30'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffe08f'
  primary-fixed-dim: '#e6c364'
  on-primary-fixed: '#241a00'
  on-primary-fixed-variant: '#584400'
  secondary-fixed: '#d5e3ff'
  secondary-fixed-dim: '#adc8f5'
  on-secondary-fixed: '#001c3b'
  on-secondary-fixed-variant: '#2d486d'
  tertiary-fixed: '#93f6c4'
  tertiary-fixed-dim: '#77d9a9'
  on-tertiary-fixed: '#002113'
  on-tertiary-fixed-variant: '#005236'
  background: '#0f131d'
  on-background: '#dfe2f0'
  surface-variant: '#31353f'
typography:
  display-lg:
    fontFamily: Bebas Neue
    fontSize: 64px
    fontWeight: '400'
    lineHeight: '1.1'
    letterSpacing: 0.02em
  headline-lg:
    fontFamily: Bebas Neue
    fontSize: 40px
    fontWeight: '400'
    lineHeight: '1.2'
    letterSpacing: 0.05em
  headline-lg-mobile:
    fontFamily: Bebas Neue
    fontSize: 32px
    fontWeight: '400'
    lineHeight: '1.2'
  title-md:
    fontFamily: Source Serif 4
    fontSize: 20px
    fontWeight: '600'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Source Serif 4
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Source Serif 4
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: 0.1em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 8px
  container-max: 1440px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 64px
---

## Brand & Style
The brand personality is authoritative yet welcoming, bridging the gap between high-end curation and intelligent recommendation. It targets cinephiles who value quality over quantity, evoking a sense of prestige, mystery, and discovery.

The design style is **Modern Cinematic**, a fusion of editorial sophistication and premium digital interfaces. It utilizes a deep, dark base to allow imagery and gold accents to command attention. Key visual motifs include subtle film grain overlays (opacity 3-5%), delicate gold hair-lines, and structured information density that recalls classic film programs and vintage cinema tickets. The atmosphere is warm, nocturnal, and highly polished.

## Colors
The palette is rooted in a deep midnight navy (`#070B14`) to provide maximum contrast for the primary cinematic gold accent (`#C9A84C`). 

- **Primary Gold:** Used exclusively for high-priority actions, star ratings, premium badges, and active navigation states.
- **Surface Navy:** Elements sit on `#0D1520` to create a subtle layered depth against the background.
- **Warm Ivory:** All primary text avoids pure white, using `#F0EDE4` to reduce eye strain and maintain the sophisticated, slightly aged editorial feel.
- **Deep Ocean Blue:** Used for secondary containers, tags, and subtle button states to provide a cooler counterpoint to the gold.

## Typography
The typography strategy creates a distinct hierarchy between "The Spectacle" and "The Information."

- **Headlines:** Use **Bebas Neue** to evoke movie poster aesthetics. These should be set with slightly increased letter spacing and tight line heights. 
- **Body Text:** Use **Source Serif 4** for descriptions and articles. This serif choice reinforces the "Intelligence" aspect of the brand, providing a scholarly and premium reading experience.
- **UI Labels:** Use **Plus Jakarta Sans** for navigation, buttons, and metadata. This sans-serif ensures clarity at small sizes and provides a modern, functional contrast to the serif body.

## Layout & Spacing
The layout follows a **Fluid Grid** system with generous margins to maintain an air of exclusivity and luxury. 

- **Desktop:** 12-column grid with 24px gutters. Use wide margins (64px) to center-weight the content.
- **Mobile:** 4-column grid with 16px margins.
- **Rhythm:** Spacing should follow an 8px base unit. Content-heavy sections (like movie descriptions) should use 32px or 48px vertical padding to allow the typography to breathe. 
- **Special Layouts:** Movie detail pages should utilize an asymmetrical layout, with large-scale imagery on one side and structured metadata in a narrow column, mimicking high-end fashion or film magazines.

## Elevation & Depth
Depth is created through **Tonal Layers** and **Gold Accents** rather than heavy shadows.

- **Surface Levels:** The background is `#070B14`. Secondary surfaces (cards, sidebars) use `#0D1520`. 
- **Borders:** Instead of shadows, use 1px borders. For standard cards, use `#1E3A5F` at 50% opacity. For featured or "Premium" items, use a subtle gold (`#C9A84C`) border.
- **Overlays:** Modals and dropdowns should use a slight backdrop blur (8px) combined with a dark tint to maintain the nocturnal atmosphere.
- **Film Grain:** A global, low-opacity noise texture should be applied to the background to break digital flatness and provide a tactile, analog feel.

## Shapes
The shape language is precise and architectural. 

- **Corners:** Use "Soft" (`0.25rem`) corner radii for most elements to maintain a structured, professional look. 
- **Ticket Motif:** Certain components, such as call-to-action cards or badges, should feature a "ticket-cut" aesthetic—subtle concave notches on the corners or sides—to reinforce the cinema theme.
- **Buttons:** Primary buttons use sharp or minimally rounded corners to feel more like high-end labels than common app buttons.

## Components
- **Buttons:** 
  - *Primary:* Solid Gold (`#C9A84C`) with Dark Navy text. High-contrast, sharp corners.
  - *Secondary:* Ghost style with Deep Ocean Blue (`#1E3A5F`) borders and Ivory text.
- **Cards:** Use a "vertical poster" ratio (2:3) for film covers and a "landscape" ratio (16:9) for editorial content. Include a 1px inner gold border on hover.
- **Badges:** Small, uppercase labels using **Plus Jakarta Sans**. "IMDb" or "Score" badges should be gold-framed.
- **Input Fields:** Dark backgrounds (`#0D1520`) with a bottom-only border in Ocean Blue. When focused, the border transitions to Gold.
- **Chips/Tags:** Small, pill-shaped but with minimal rounding, using the Deep Ocean Blue background to categorize genres or moods.
- **Progress Bars:** For "Watch Progress," use a thin gold line against a navy track, with no rounded caps for a more technical, precise look.