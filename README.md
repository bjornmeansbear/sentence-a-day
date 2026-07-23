# A Sentence-A-Day (SAD)

_Nano Key Command Notes:_

- line numbers: `shift + alt + 3`
- line wrap: `esc + $`

Writing sentences. Day by Day. Trying to make something. Piece by Piece. It is not actually SAD. Hopefully it will be HAPPY -- or at least HOPEFUL/HELPFUL.

This project first debuted in 2019. There is a 2019 branch that saves where things were as of 202001010001. Current `master` branch is 02021. The project is (hopefully) expanding. @bjornmeansbear will continue to write sentences somewhat daily in the readme. But! the repo will start to also include essays or Q&A or back-and-forth threads from other humans. The goal: turn some of the couple good starts from 2019 into some dialog and/or discussion — or even actual projects and action.

> **License:** Where the content in this document is by Kristian Bjornard (and not otherwise owned by, quoted from, or credited to someone else), it is licensed with [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/). You can use this text for whatever you want as long as you cite where it came from, like linking back to this repo or merely stating that it came from Kristian Bjornard, and you must also license/share whatever you make in the same way -- share and share alike; let us create a freer and better and evolving culture!

## July 23, 2026

Idea for making writing easier going forward: stop treating each essay as one long tiddler. Break the good passages out into their own tiddlers — one argument or one paragraph each — and transclude them back into the essay instead of copying the text in. The Lecture: What Is Sustainable Graphic design? tiddler already does a rough version of this with its `list:` field pointing at six separate idea-tiddlers; just formalize it with actual transclusion.

The payoff: those same fragments become raw material for the next lecture or essay too. Instead of retyping an argument about substrates or open-source practice every time it's relevant, pull in the tiddler that already has it. TiddlyWiki's References panel already shows backlinks for anything `[[linked]]`, so the crosslinking mostly happens for free once the fragments exist as their own tiddlers.

Risk is chunking too small — spend more time managing fragments than writing. Keep the grain at one idea per tiddler, same as the Lecture list already does.

## July 22, 2026
Worked with Claude on tying Bjørnpaedia's static export more tightly to the other Wjerk properties. Pulled the full Wjerk header (logo + "A Climate Design Studio" blurb) into the site via `WjerkNav`, not just the nav row, so it reads as one of my sites rather than a bolted-on link — matches the condensed header already used on the a.wjerk.shop case-study pages. Un-fixed the header/nav so it scrolls away with the page instead of staying pinned (just how HTML used to work, and I like it better). Excluded internal utility tiddlers (`.hideList`, `.sourcesList`) from the static build/homepage list — they're wiki housekeeping, not content. Along the way, un-fixing the nav exposed a regression where the sidebar (site title/blurb) would float up and overlap the story river on individual tiddler pages — traced it to a stale `storytop` theme metric plus leftover fixed-position CSS from when the nav used to be pinned, and fixed the static tiddler template/CSS so the two columns sit side by side properly again, without touching the homepage grid.

## July 02026
Still working through things here. 
Have an improved workflow to publish to a static version of this up at <http://bjornpaedia.wjerk.shop> ~~<https://www.bjornpaedia.com/>~~ which gets updated when I feel like a real change has been made, useful content added, etc.

This site is what generates Bjørnpaedia: [Bjørnpaedia](http://bjornpaedia.wjerk.shop) is Kristian Bjørnard's running archive of essays, questions, notes, research, and half-formed ideas on sustainability, circular design, open-source practice (open sourcery?), and design education (and more). What it is not is a perfect portfolio of finished conclusions. The collection is full of thinking out loud, looking for intereconnection, and circling recurring questions: what does it mean to design for the welfare of all life, why climate change is inseparable from social and cultural change, what open access and transparency owe to design practice, and how to teach the next generation of designers to interrogate their own work rather than default to easy, greenwashed answers. A working design philosophy built over time.

---

## January 02020

20200113 Off to a slow start. Re-reading notes on the synthesis of form yet again. what about sustainability (restorative practice?) are the right constraints/contexts to generate forms from? is every time + space thus different? are there no universals? semiotic, architectural, or otherwise?

## January 02021

Back at this after a break for 2020.

The goal this time around is to actually generate some coherent directions for lectures, writing, essays, consulting ideas... turn them into something over my coming sabbatical hopefully.

## June 02021

020210601: Trying to get back to writing. Trying to get back to thinking. Trying to get back to clarifying. Writing down ideas and questions and clarifying statements about how sustainability, climate change, design, and life in general might fit together. The hope; well; that I generate something useful for my practice, for my family, and for these communities around me — maybe even that it can be some variety of publishable things. Here's to spaceship earth.

The rules for 020210601 and onward?

- Pick a prompt
  - like from <https://www.are.na/kristian-bjornard/sgd-01-what-is-worth-sustaining> or <https://www.are.na/kristian-bjornard/sustainability-plo> or similar...
- Write for at least 30 minutes.
- Notate the current PPM of C02. (<https://gml.noaa.gov/ccgg/trends/monthly.html>)
- ?

Notes for writing:

- How can I switch things to make sure I use typographers quotes, etc. even if in .md or .txt? and other special characters for typographic excellence...
- ???

as of 020210611 I installed tiddly wiki, use `tiddlywiki sad2021tw --listen` to make it work!

okay, going to go through this: <https://nesslabs.com/tiddlywiki-static-website-generator> -- see if I can make some export improvements, maybe somehow go right to the g h-pages branch!?

Currently have a static version of this up at <https://www.bjornpaedia.com/> > generally gets updated weekly?

need to figure out what the best way to save the tiddlywiki for web output is -- just make it a live version? save it all out to static files? both? some third way!?!?!?!?

## November 2021

This repo is filling with a lot of other kinds of things — since switching to tiddlywiki, well, there's a lot extra here now. I'm trying to figure out how to clean things up, improve things... but I'm not totally sure what to do yet. A lot of duplication not a lot of clear thinking, not a lot of long form, fleshed out stuff. But a lot of daily rantings still.

Whew.

## July 1, 2026
This repo has had a long life. still using it to build a tiddly wiki powered personal sort of encyclopedia and note site I guess? probably sort of messy and chaotic to just be sharing live to the world all the time... but hey. I've been using it less since I witched more to Notion and some other tools, but does it make sense to try and get back to this more? copy some of the notion stuff to tiddlers? try to get some interlinking going? publish this more frequently as well as link it to my new website (https://a.wjerk.shop) I have to finish.

the tiddlywiki aspects of this repo end up publishing to https://bjornpaedia.wjerk.shop/

---

Reference:

- https://nesslabs.com/tiddlywiki-beginner-tutorial
- https://www.mentalnodes.com/about
- https://nesslabs.com/tiddlywiki-static-website-generator
- https://tiddlywiki.com/static/TiddlyWiki.html
- https://nesslabs.com/digital-garden-tiddlywiki
- https://tiddlywiki.com/#Sharing%20your%20tiddlers%20with%20others
- https://tiddlywiki.com/static/Filter%2520Operators.html
- https://giffmex.org/stroll/stroll.html
- https://tiddlywiki.com/static/Philosophy%2520of%2520Tiddlers.html

