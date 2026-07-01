# TiddlyWiki Customizations

Notes on what's been customized in `sad2021tw/` beyond a stock TiddlyWiki install, and how the templating system works, so future tweaks are easier to reason about.

## Bug fixed: double theme causing "bold/ghosted" sidebar text

`sad2021tw/tiddlywiki.info` used to list two themes:

```json
"themes": [
    "tiddlywiki/vanilla",
    "tiddlywiki/snowwhite"
]
```

TiddlyWiki doesn't gate theme CSS behind "which theme is selected" — `$:/core/ui/PageStylesheet` concatenates *every* tiddler tagged `$:/tags/Stylesheet`, and both themes' base stylesheets carry that tag. So Snow White's CSS was stacking on top of Vanilla's, unconditionally, all the time.

Snow White's stylesheet (`node_modules/tiddlywiki/themes/tiddlywiki/snowwhite/base.tid`) adds:

```css
.tc-sidebar-header {
    text-shadow: 0 1px 0 <<colour sidebar-foreground-shadow>>;
}
```

plus assorted box-shadows/gradients on buttons, tabs, and controls. That produced the "letters duplicated on top of themselves" look in the sidebar — a real `text-shadow` ghost offset, compounded by extra shadows on the icon row and tabs.

**Fix:** removed `"tiddlywiki/snowwhite"` from the `themes` array — only Vanilla is loaded now. All the custom `$:/themes/tiddlywiki/vanilla/metrics/*` tiddlers confirm Vanilla was always the intended theme.

## Inventory of customizations

### Static-build templates (used by `build.sh`)
- **`$:/core/templates/static.tiddler.html`** (`sad2021tw/tiddlers/$__core_templates_static.tiddler.html.tid`) — full override of the core shadow tiddler. Adds a "KB Additions" block: a fixed site-title/subtitle div. The pre-edit version is kept as a backup tiddler titled `$:/core/templates/static.tiddler.html ~ orig` for diffing.
- **`$:/core/templates/static.template.css`** (`sad2021tw/tiddlers/$__core_templates_static.template.css.tid`) — "KB ADDITIONS" here is the real structural change: pins `.tc-sidebar-scrollable` fixed to the right 40% of the viewport and `.tc-story-river` to the left 60%, producing the two-column static-page layout.
- **`$:/core/templates/static.template.html`** — untouched, matches stock.

### Per-tiddler view additions (`$:/tags/ViewTemplate`)
The `list:` field on `$:/tags/ViewTemplate` controls which fragments render for every tiddler, in order: title → unfold → subtitle → WordCount editor hook → tags → WordCount display → classic body → **MetaInfoTemplate** → body → import → plugin → **TagExplorer** → **DateExplorer** → **LinkExplorer**.

Custom fragments (all tagged `$:/tags/ViewTemplate hide`):
- `MetaInfoTemplate.tid` — field table (author/ISBN/publisher/year/URL/etc.) when those fields are present.
- `TagExplorer.tid` — "Tagged with X" list of sibling tiddlers.
- `DateExplorer.tid` — "Also Created This Day" / "Modified This Day" (for tiddlers tagged `EssayADay`).
- `LinkExplorer.tid` — Inbound/Outbound link tables.

### Toolbar/button customization
- `$:/tags/PageControls` — reordered stock buttons, inserted two custom quick-create shortcuts: "New 02021 EAD" and "New Source".
- `$:/tags/EditorToolbar` — includes overridden `linkify`/`transcludify` buttons.

### Palette
- Custom palette exists at `$:/palettes/ContrastLight-BjornMeansTweaks` (`sad2021tw/tiddlers/$__palettes_ContrastLight-BjornMeansTweaks`).
- **Open question:** `$:/palette` currently points to the stock `$:/palettes/ContrastLight`, not the `-BjornMeansTweaks` variant. Worth checking in the Control Panel whether that's intentional — as-is, the tweaked palette values (e.g. `sidebar-foreground-shadow: rgba(0,0,0,0)`) may not be the ones actually applied.

### Custom CSS
- `OOKB Styles.css` (`sad2021tw/tiddlers/OOKB Styles.css`, meta at `OOKB Styles.css.meta`) — 133-line stylesheet tiddler, tagged `$:/tags/Stylesheet hide`. This is the right home for future pure-CSS tweaks.

### Plugins (extend the system, not templates per se)
- `OokTech/WordCount` — word count display + editor hook, wired into `$:/tags/ViewTemplate`.
- `danielo515/ContextPlugin` — custom plugin, source in `sad2021tw/plugins/contextPlugin`.
- `flibbles/relink` and `flibbles/relink-titles` — keep links updated when tiddler titles change.
- `snowgoon88/edit-comptext` — custom plugin, source in `sad2021tw/plugins/edit-comptext`.

## How TiddlyWiki templating works (for future tweaks)

1. **Full override** — give a tiddler the exact same title as a core/theme shadow tiddler (e.g. `$:/core/templates/static.tiddler.html`). Completely replaces the shadow. Powerful, but you own all future drift from upstream. Good practice: keep a backup copy of the original (as done with the `~ orig` tiddler) so you can diff against it later.
2. **List-injection (preferred for additions)** — most page regions are built from a *list* of component tiddlers tagged to a marker tiddler (`$:/tags/ViewTemplate`, `$:/tags/PageTemplate`, `$:/tags/PageControls`, `$:/tags/EditorToolbar`, `$:/tags/SideBarSegment`, etc.). Create a new tiddler, tag it appropriately, then edit the tag tiddler's `list:` field to position it. This is how MetaInfoTemplate/LinkExplorer/etc. were added — non-destructive and composable.
3. **Palette/theme swap** — `$:/palette` and `$:/theme` are pointer tiddlers referencing a `$:/palettes/<name>` or `$:/themes/<name>` tiddler. Create your own palette tiddler, then repoint `$:/palette` to it.
4. **CSS-only** — for pure visual tweaks, prefer adding to `OOKB Styles.css` (tagged `$:/tags/Stylesheet`) over touching template markup — smaller blast radius, easier to revert.
5. **Finding the stock version to diff against** — the installed core/theme source lives in `node_modules/tiddlywiki/core/` and `node_modules/tiddlywiki/themes/` (wherever the `tiddlywiki` package is installed, e.g. via `npm ls -g tiddlywiki` or checking `which tiddlywiki`). Useful for confirming whether a shadow tiddler override actually diverges from default, and for seeing what a theme's stylesheet applies before deciding to disable or override it.
