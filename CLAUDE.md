# biashara-ai

## Design Gate — mandatory for any UI work

Before writing UI code for ANY page, app, component, or artifact in this repo:

1. Invoke the `design-gate` skill and emit its 6-line DIRECTION brief. **No code before the brief.**
2. Satisfy the DEPTH line using `web-3d` (tier 0 CSS depth is a valid answer; tier 3 three.js is not the default).
3. Satisfy entrance choreography using `motion-system`.
4. Run the audit before calling the work done:
   ```bash
   python3 .claude/skills/design-gate/scripts/audit.py <file-or-dir>
   ```
   Non-zero exit, or a score below 70, means it is not finished. Fix the findings.

## Rules

- **NEVER ship generic UI.** No purple→blue gradients, no Inter as a display face, no
  centered hero + three identical icon cards, no `rounded-2xl shadow-lg` on everything,
  no gradient-text headlines, no emoji as icons, no "Elevate / Seamlessly / Unlock the
  power of" copy. Full list: `.claude/skills/design-gate/references/anti-slop.md`.
- **NEVER fabricate testimonials, reviews, star ratings, or customer names.**
- **NEVER read, edit, or commit `.env` files.**
- Every page ships reduced-motion handling, real dark mode, visible focus rings, and
  works at 375px with no horizontal scroll.

## Skills in this repo

| Skill | Use for |
|---|---|
| `design-gate` | Art direction brief, anti-slop bans, runnable audit script |
| `web-3d` | three.js / R3F / GLSL / CSS depth recipes with pinned versions |
| `motion-system` | Timing tokens, choreography, scroll reveal, View Transitions |

## Design toolchain — what is connected

| Tool | Status | Use for |
|---|---|---|
| `shadcn` MCP (`.mcp.json`) | installed, handshake verified | `search_items_in_registries`, `view_items_in_registries`, `get_item_examples_from_registries`, `get_audit_checklist` — pull real components instead of hand-rolling |
| Figma MCP | connected + enabled | `create_shader` / `list_shaders`, `get_motion_context`, `search_design_system`, `get_design_context`, `weave_run_model` (image/video gen). Underused — check it before hand-writing GLSL |
| Canva MCP | connected | `generate-image`, `generate-design`, brand templates |
| Vercel / Cloudflare MCP | connected | deploy the result |
| Replit / Wix / B12 MCP | connected | scaffold-and-host routes when a repo is overkill |

Third-party shadcn registries (Magic UI, Aceternity, Origin UI — the sources for 3D cards,
aurora/beam backgrounds, animated components) are added with `npx shadcn registry add`.
Their domains are blocked by this cloud environment's network policy, so add them from a
machine with open network access; the URLs were not verifiable from here.
