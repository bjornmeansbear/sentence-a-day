# tiddlywiki sad2021tw --rendertiddlers '[!is[system]]' $:/core/templates/static.tiddler.html static text/plain
# tiddlywiki sad2021tw --rendertiddler $:/core/templates/static.template.html static.html text/plain
# tiddlywiki sad2021tw --rendertiddler $:/core/templates/static.template.css static/static.css text/plain

# https://www.didaxy.com/exporting-static-sites-from-tiddlywiki-part-1
# tiddlywiki sad2021tw --rendertiddlers [!is[system]] $:/core/templates/static.tiddler.html static text/plain --rendertiddler $:/core/templates/static.template.css static/static.css text/plain

# tiddlywiki sad2021tw --rendertiddlers '[!is[system]]' $:/core/templates/static.tiddler.html static text/plain --rendertiddler $:/core/templates/static.template.html static.html text/plain --rendertiddler $:/core/templates/static.template.css static/static.css text/plain --rendertiddler $:/core/templates/alltiddlers.template.html alltiddlers.html text/plain

tiddlywiki sad2021tw --render '[!is[system]]' $:/core/templates/static.tiddler.html static text/plain --render $:/core/templates/static.template.html static.html text/plain --render $:/core/templates/static.template.css static/static.css text/plain --render $:/core/templates/alltiddlers.template.html alltiddlers.html text/plain --build index
