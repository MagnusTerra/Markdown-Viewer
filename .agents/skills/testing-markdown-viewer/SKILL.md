---
name: testing-markdown-viewer
description: Test Markdown Viewer UI features end-to-end using preview deployments. Use when verifying toolbar, editor, preview, or settings changes.
---

# Testing Markdown Viewer

## Overview
Markdown Viewer is a static client-side app (HTML/CSS/JS, no build step). It deploys to Cloudflare Pages and Vercel automatically on PRs.

## Setup
1. Create a PR with your changes — CI runs automatically.
2. Use `git_pr_checks` to wait for deployment. Look for the Cloudflare Pages preview URL in the check details.
3. Open the preview URL in the browser for testing.

## Testing Approach
- This is a purely frontend app with no backend. All state is stored in `localStorage`.
- Test directly on the Cloudflare Pages preview deployment (no local server setup needed).
- For mobile testing, use Chrome DevTools device toolbar (`Ctrl+Shift+M` with DevTools open).
- The mobile hamburger menu appears at viewport widths below the `md` Bootstrap breakpoint (~768px).

## Key Areas to Test
- **Header toolbar**: View mode toggles, sync scrolling, import/export, copy, share, theme toggle.
- **Formatting toolbar**: Text formatting, alignment, headings, lists, links, code, emoji, etc.
- **Editor/Preview panes**: Text direction (RTL/LTR), content rendering, scroll sync.
- **Tab management**: New/close/rename/duplicate/reorder tabs.
- **Persistence**: Settings and tab state persist in `localStorage` — reload the page to verify.
- **Mobile menu**: All toolbar features are mirrored in the mobile hamburger menu.

## State Persistence
- Global state (theme, direction, sync scrolling) is stored under `markdownViewerGlobalState` in `localStorage`.
- Tab content and metadata are stored separately in `localStorage`.
- To test persistence, change a setting, reload the page, and verify the setting is restored.

## Tips
- No linter or test suite is configured — validation is manual/visual.
- The app uses Bootstrap 5 for responsive layout and Bootstrap Icons for toolbar icons.
- Mermaid diagrams, MathJax, and emoji rendering require network access to CDNs.
- When testing scoped changes (e.g., RTL only affecting editor/preview), verify that unaffected areas (header, toolbar, modals) are not impacted.

## Devin Secrets Needed
None — the app is fully client-side with no authentication.
