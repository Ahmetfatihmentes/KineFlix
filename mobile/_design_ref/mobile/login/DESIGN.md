---
name: Cinematic Noir
colors:
  surface: '#16130d'
  surface-dim: '#16130d'
  surface-bright: '#3d3931'
  surface-container-lowest: '#100e08'
  surface-container-low: '#1e1b15'
  surface-container: '#221f19'
  surface-container-high: '#2d2a23'
  surface-container-highest: '#38342d'
  on-surface: '#e9e1d7'
  on-surface-variant: '#d0c5b2'
  inverse-surface: '#e9e1d7'
  inverse-on-surface: '#343029'
  outline: '#99907e'
  outline-variant: '#4d4637'
  surface-tint: '#e6c364'
  primary: '#ffe090'
  on-primary: '#3d2e00'
  primary-container: '#e6c364'
  on-primary-container: '#665000'
  inverse-primary: '#755b00'
  secondary: '#e6c364'
  on-secondary: '#3d2e00'
  secondary-container: '#785d00'
  on-secondary-container: '#fdd977'
  tertiary: '#d9e2ff'
  on-tertiary: '#162f5e'
  tertiary-container: '#b0c6ff'
  on-tertiary-container: '#3b5183'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffe08f'
  primary-fixed-dim: '#e6c364'
  on-primary-fixed: '#241a00'
  on-primary-fixed-variant: '#584400'
  secondary-fixed: '#ffe08f'
  secondary-fixed-dim: '#e6c364'
  on-secondary-fixed: '#241a00'
  on-secondary-fixed-variant: '#584400'
  tertiary-fixed: '#d9e2ff'
  tertiary-fixed-dim: '#b0c6ff'
  on-tertiary-fixed: '#001944'
  on-tertiary-fixed-variant: '#2f4576'
  background: '#16130d'
  on-background: '#e9e1d7'
  surface-variant: '#38342d'
typography:
  display-lg:
    fontFamily: Bebas Neue
    fontSize: 48px
    fontWeight: '400'
    lineHeight: 48px
    letterSpacing: 0.02em
  headline-lg:
    fontFamily: Bebas Neue
    fontSize: 32px
    fontWeight: '400'
    lineHeight: 32px
    letterSpacing: 0.03em
  headline-md:
    fontFamily: Bebas Neue
    fontSize: 24px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0.04em
  title-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '700'
    lineHeight: 24px
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  margin-mobile: 20px
  gutter-mobile: 12px
---

## Brand & Style
The design system is engineered for a premium, high-end mobile cinema experience. The brand personality is authoritative, sophisticated, and immersive, targeting film enthusiasts who value curation and aesthetic excellence.

The design style is a hybrid of **Minimalism** and **Cinematic Noir**. It utilizes deep blacks and metallic golds to create a high-contrast, prestigious environment. A subtle film grain overlay (3-4% opacity) is applied globally to the background to provide texture and prevent "digital flatness." All UI elements prioritize content, using sharp edges and generous negative space to evoke the feeling of a professional film editing suite or a luxury theater lobby.

## Colors
The palette is strictly nocturnal, designed to make film key-art and video content pop.
- **Primary Gold (#e6c364):** Used for primary actions, active states, and critical branding elements. It represents luxury and the "golden age" of cinema.
- **Secondary Gold (#c9a84c):** A muted metallic used for hover states (where applicable), gradients, and secondary accents to provide depth.
- **Background (#0f131d):** A deep, cold navy-black that serves as the canvas.
- **Surface (#1b2029):** Used for cards, navigation bars, and modals to create subtle separation from the background.
- **Text (#dfe2f0):** An off-white with a slight blue tint to reduce eye strain while maintaining high legibility against dark backgrounds.

## Typography
The typography strategy creates a clear hierarchy between "Theatrical" and "Functional" elements.
- **Bebas Neue** is reserved for headlines and impactful display moments. Its condensed, tall structure mimics classic film titles and posters.
- **Plus Jakarta Sans** handles all functional UI, body copy, and metadata. Its modern, open letterforms ensure high readability on mobile screens at small sizes.
- Tracking (letter spacing) should be increased slightly for all Bebas Neue instances to maintain an editorial, premium feel.

## Layout & Spacing
This design system utilizes a **Fluid Grid** optimized for a 390px mobile viewport.
- **Structure:** A 4-column grid system with 20px outside margins and 12px gutters.
- **Vertical Rhythm:** All spacing increments are multiples of 4px. 16px (md) is the default padding for most containers.
- **Touch Targets:** Minimum touch targets for interactive elements are 44x44px, regardless of the visual size of the icon or label.

## Elevation & Depth
Depth is achieved through **Tonal Layering** and **Subtle Outlines** rather than traditional shadows.
- **Level 0 (Background):** #0f131d with film grain.
- **Level 1 (Cards/Surfaces):** #1b2029. Surfaces should use a 1px solid border of #ffffff (10% opacity) to define edges against the dark background.
- **Level 2 (Modals/Popovers):** #1b2029 with a subtle #000000 shadow (40% opacity, 20px blur) to provide a soft lift.
- **Glassmorphism:** Bottom navigation bars and top app bars should use a background blur (20px) with 80% opacity of the Surface color to maintain context of content scrolling beneath.

## Shapes
The shape language is strictly **Sharp**. 
- All buttons, input fields, images, and cards must have 0px corner radii. 
- This geometric rigidity reinforces the professional, technical feel of filmmaking equipment (cameras, monitors, clapperboards).
- Dividers should be 1px thin lines using the Surface color or a low-opacity white.

## Components
- **Buttons:** Primary buttons use the Gold (#e6c364) background with black text. Secondary buttons use a 1px Gold outline with Gold text. All are sharp-edged.
- **Cards:** Movie posters/thumbnails should be sharp-edged with a 1px inner border. Metadata (title, year) sits below or as an overlay with a dark-to-transparent gradient.
- **Inputs:** Underlined or fully boxed with sharp corners. The active state uses a Primary Gold bottom border.
- **Chips:** Small, sharp-edged rectangles with a #1b2029 background and Plus Jakarta Sans labels.
- **Lists:** Clean, edge-to-edge separators with 20px horizontal padding.
- **Progress Bars:** For "Continue Watching," use a 2px height bar. The background is a 20% opacity Gold, while the progress is 100% Primary Gold.
- **Film Grain Overlay:** A global `div` with a fixed position, 100vw/100vh, pointer-events: none, and a noise texture at 3% opacity.