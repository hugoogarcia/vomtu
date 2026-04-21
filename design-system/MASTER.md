# Vomtu Master Design System

## Core Aesthetic
**Style**: Cinematic Modernism
**Tone**: High-end, Professional, Direct, Dark-Mode First.

## 🎨 Color Palette
- **Background (Base)**: `#010409` (Deep Obsidian)
- **Background (Surface)**: `#0D1117` (Subtle Slate)
- **Primary (Electric Blue)**: `#0066FF`
- **Secondary (Teal Accent)**: `#14B8A6`
- **Text (Primary)**: `#F0F6FC`
- **Text (Secondary)**: `#8B949E`
- **Border**: `rgba(240, 246, 252, 0.1)`

## 🔠 Typography
- **Headlines**: `Cal Sans`, `Inter Tight` (Bold)
- **Body**: `Geist Sans`, `Inter` (Regular/Medium)
- **Scale**:
  - H1: 64px - 80px (Hero)
  - H2: 48px (Sections)
  - H3: 24px (Cards)
  - Body: 16px (1.6 line-height)

## 🎥 Animation Tokens
- **Duration (Fast)**: 160ms (Buttons, micro-interactions)
- **Duration (Medium)**: 300ms (Modals, reveals)
- **Easing (Out)**: `cubic-bezier(0.23, 1, 0.32, 1)` (Precision snap)
- **Easing (In-Out)**: `cubic-bezier(0.77, 0, 0.175, 1)` (Cinematic flow)
- **Press Feedback**: `scale(0.97)`
- **Entrance Animation**: `opacity: 0; transform: translateY(10px) scale(0.98)` to `opacity: 1; transform: none`

## 💎 Visual Effects
- **Bento Brids**: `0.5px` border with subtle gradient.
- **Blur**: `backdrop-filter: blur(12px)` for glass surfaces.
- **Grain**: `0.05` opacity noise texture on top layer.
- **Shadows**: Large, soft box-shadows (e.g. `0 20px 40px rgba(0,0,0,0.5)`).
