# TiddlyWiki Customizations

Notes on what's been customized in `sad2021tw/` beyond a stock TiddlyWiki install, and how the templating system works, so future tweaks are easier to reason about.

First written 2026-07-01. The view-template, palette and CSS sections were brought up to date on 2026-10-08. The static-build section has not been re-checked since July and predates the Wjerk redesign of 2026-10-04 (header, nav, `.wjerk-tiddler-columns`, the `Wjerk`, `WjerkNav` and `IndexPageBody` tiddlers); for that work see "Using the kit in a TiddlyWiki static site" in `~/Code/color-system-and-guidelines/RULES.md`.

## Editing while the dev server is running

`tiddlywiki sad2021tw --listen` reads the `.tid` files once, at startup. It does not watch them.

- **A file edited on disk while the server runs is invisible to the wiki**, and the server will overwrite it the next time that tiddler is saved from the browser.
- So with the server running, change tiddlers through the browser or through its HTTP API (`PUT /recipes/default/tiddlers/<title>` with the header `X-Requested-With: TiddlyWiki`). The server then writes the file itself.
- With the server stopped, edit the files directly. Changes load on the next start.
- Check which case you are in first: `pgrep -f "tiddlywiki sad2021tw"`.

To try a template change without touching the live wiki, copy `tiddlywiki.info`, `tiddlers/` and `plugins/` to a scratch folder and render there with `tiddlywiki <copy> --render`. Templates that call global macros such as `<<list-links>>` need them imported in the test (`\import [all[shadows+tiddlers]tag[$:/tags/Macro]!has[draft.of]]`), or the lists come out empty.

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
- `MetaInfoTemplate.tid` — the field table at the top of a tiddler (author, ISBN, publisher, year, URL and so on). Since 2026-10-08 it has no block per field; it loops over the list in `MetaInfoFields` (below) and prints a row for each listed field the tiddler has a value for.
- `TagExplorer.tid` — "Tagged with X" list of sibling tiddlers.
- `DateExplorer.tid` — "Also Created This Day" / "Modified This Day" (for tiddlers tagged `EssayADay`).
- `LinkExplorer.tid` — Inbound/Outbound link tables. Since 2026-10-08 it also counts links stored in fields (below).

These fragments run on the published static pages too: the static tiddler template renders `$:/core/ui/ViewTemplate`.

### The field table: `MetaInfoFields` and `Field Audit`

- **`MetaInfoFields`** (a dictionary tiddler, saved as `MetaInfoFields` + `MetaInfoFields.meta`, tagged `hide`) is the one place that decides what the top matter prints.
  - Its **`list` field** names the fields to print, in display order.
  - Its **text** gives each a label, one per line: `monoskop: Monoskop`. A field with no label line prints under its own name.
  - Its **`ignore` field** names fields that should never be offered (internal ones like `tmap.id`, `caption`, `subtitle`).
- **To print a new field:** add its name to the `list` field, or open `Field Audit` and click **show**. No template editing.
- **`Field Audit`** (tagged `hide`) lists every field in use on non-system tiddlers that is neither printed nor ignored, with a count and an example, and a **show** / **ignore** button per row.
- Two list entries are special-cased inside the template: `city` prints the combined "Written from" row (`city`, `state`, `location`), and `coverurl` prints the cover image.
- Field names: lowercase letters, digits, hyphens, underscores. Dots work (`are.na`).
- Empty fields never print. The "New Source" button creates a dozen empty ones on purpose.

### Links in fields

TiddlyWiki's `links[]` and `backlinks[]` only read a tiddler's body text. A tag is tracked separately (`tagging[]`), and `[[Name]]` in a field is not a link to it at all. Moving an author from the body into the `author` field therefore removes the link.

`LinkExplorer` compensates:

- **Inbound** = `backlinks[]` plus every tiddler that has `[[This Title]]` in any field listed in `MetaInfoFields`.
- **Outbound** = `links[]` plus every `[[Title]]` in this tiddler's listed fields.
- Only double-bracketed names count, so `[[Ellen Lupton]] and Jennifer Cole Phillips` links to Ellen Lupton only.
- A field only takes part once it is on the `MetaInfoFields` list. `source` holds bracketed links in several tiddlers and is not on the list yet.
- Inbound leaves out tiddlers tagged `private` or `hide`. Outbound is not filtered.
- Tags are deliberately not folded in; the pills and `TagExplorer` already cover them.

Core features that depend on real links (the info panel's References tab, relink, the missing-tiddlers list) still do not see field links.

### Conventions for quote and source tiddlers

- A quote tiddler is titled with the quote (or a short form of it), tagged `Quote`, with the author in the `author` field as `[[Name]]`, any link in `url`, and a `year` when known. The body is the quote in a `<<<` block, with the source work after the closing `<<<`.
- Notes pasted from old text files are full of CamelCase names (SubRosa, YouTube) that TiddlyWiki turns into links. Start such a tiddler's text with `\rules except wikilink`. Explicit `[[links]]` still work.

### Toolbar/button customization
- `$:/tags/PageControls` — reordered stock buttons, inserted two custom quick-create shortcuts: "New 02021 EAD" and "New Source".
- `$:/tags/EditorToolbar` — includes overridden `linkify`/`transcludify` buttons.

### Palette
- The active palette is **`$:/palettes/Wjerk`** (`sad2021tw/tiddlers/$__palettes_Wjerk`): the kit colors, with warm White ground, brown-black ink, cornflower links and a pink accent. `$:/palette` points to it. This closes the July open question about the stock ContrastLight palette being active.
- The older `$:/palettes/ContrastLight-BjornMeansTweaks` is still in the repo, unused.
- The palette holds literal hex values because TiddlyWiki does colour math on them. `Wjerk Tokens` (below) re-exposes them as CSS variables.
- **A palette entry can land on more than one background.** `tiddler-controls-foreground-selected` colours the selected toolbar icon on the page ground *and* the editor-toolbar icons on dark buttons. Check every place an entry is used before changing it; changing this one to suit the light ground made the editor toolbar unreadable (2026-10-06). The pairings that fail on one ground are corrected in `OOKB Styles.css`, not in the palette.
- 2026-10-06/08: `sidebar-controls-foreground-hover` had been set to the background colour, so page-control icons vanished on hover. It and `tiddler-controls-foreground-hover` are now `wjerk-accent`. The selected green was snapped to the kit's `green-4` (`#89A271`).

### Custom CSS
- `OOKB Styles.css` (`sad2021tw/tiddlers/OOKB Styles.css`, meta at `OOKB Styles.css.meta`) — stylesheet tiddler of about 380 lines, tagged `$:/tags/Stylesheet hide`. This is the right home for future pure-CSS tweaks. It ends with a commented "Toolbar icon states" block that records each icon/background pairing and its contrast ratio.
- `Wjerk Tokens.tid` — tagged `$:/tags/Stylesheet hide`. Reads the active palette and writes the kit's semantic tokens (`--color-bg`, `--color-text`, `--color-accent`…) so `OOKB Styles.css` can use `var(--color-*)`. It starts with `\rules except dash`, because wikitext otherwise turns `--` into an en dash and breaks every custom-property name.
- Stylesheet tiddlers load in title order, and `$:/…` sorts before `OOKB Styles`, so this file's rules come after the theme's and win at equal specificity. Its overrides rely on that.
- **Leftover:** `$/plugins/danielo515/context/css` (143 bytes, tagged `$:/tags/Stylesheet`) is still present from the ContextPlugin removed in July. Harmless; can be deleted.

### Plugins (extend the system, not templates per se)
- `OokTech/WordCount` — word count display + editor hook, wired into `$:/tags/ViewTemplate`.
- `flibbles/relink` and `flibbles/relink-titles` — keep links updated when tiddler titles change.
- `snowgoon88/edit-comptext` — custom plugin, source in `sad2021tw/plugins/edit-comptext`.

**Removed:** `danielo515/ContextPlugin` (search-result context highlighting) was removed on 2026-07-01 — its `<$context>` widget calls `dots.cloneNode()`, which TiddlyWiki's server-side/Node rendering environment doesn't implement. This crashed every static build after ~69 of ~1516 tiddlers and prevented `static/static.css` from ever being generated. See the Publishing section in `CLAUDE.md`.

## How TiddlyWiki templating works (for future tweaks)

1. **Full override** — give a tiddler the exact same title as a core/theme shadow tiddler (e.g. `$:/core/templates/static.tiddler.html`). Completely replaces the shadow. Powerful, but you own all future drift from upstream. Good practice: keep a backup copy of the original (as done with the `~ orig` tiddler) so you can diff against it later.
2. **List-injection (preferred for additions)** — most page regions are built from a *list* of component tiddlers tagged to a marker tiddler (`$:/tags/ViewTemplate`, `$:/tags/PageTemplate`, `$:/tags/PageControls`, `$:/tags/EditorToolbar`, `$:/tags/SideBarSegment`, etc.). Create a new tiddler, tag it appropriately, then edit the tag tiddler's `list:` field to position it. This is how MetaInfoTemplate/LinkExplorer/etc. were added — non-destructive and composable.
3. **Palette/theme swap** — `$:/palette` and `$:/theme` are pointer tiddlers referencing a `$:/palettes/<name>` or `$:/themes/<name>` tiddler. Create your own palette tiddler, then repoint `$:/palette` to it.
4. **CSS-only** — for pure visual tweaks, prefer adding to `OOKB Styles.css` (tagged `$:/tags/Stylesheet`) over touching template markup — smaller blast radius, easier to revert.
5. **One list, one loop** — when a template would repeat the same block for each of several fields or items, keep the items in a data tiddler's `list` field and loop over it (`<$list filter="[list[MetaInfoFields]]" variable="field">`). Adding an item becomes a one-word edit, and other templates can read the same list. `MetaInfoTemplate`, `LinkExplorer` and `Field Audit` all read `MetaInfoFields`.
6. **Finding the stock version to diff against** — the installed core/theme source lives in `node_modules/tiddlywiki/core/` and `node_modules/tiddlywiki/themes/` (wherever the `tiddlywiki` package is installed, e.g. via `npm ls -g tiddlywiki` or checking `which tiddlywiki`). Useful for confirming whether a shadow tiddler override actually diverges from default, and for seeing what a theme's stylesheet applies before deciding to disable or override it.

## Tools outside this repo that read the tiddlers

- `~/Code/lectureScripts/scripts/tiddlers-to-md.py` renders chosen tiddlers into one Markdown file for a lecture folder (`compiled-from-tiddlers.md`). The tiddlers stay canonical; the Markdown is regenerated, never edited. Used by `lecture-pure-content/`, `lecture-everything-is-a-motion-graphic/` and `lecture-time-speed-motion/`.
- `~/Code/lectureScripts/scripts/md-to-tiddlers.py` goes the other way.
