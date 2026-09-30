# Pi-Top + AxiDraw = Libre Drawing Machine

I'm Kristian Bjornard, a graphic designer who runs a boutique practice and teaches graphic design at the [Maryland Institute College of Art](http://www.mica.edu). Where I can, I work with Free/Libre/Open Source (F/LOSS) fonts, software, and Public Domain imagery: tools and materials anyone can use, copy, modify, and share.

I want to show students and clients that the Apple/Adobe mono-verse isn't the only way to do this work. I also want the studio equipment we already own to last longer, including a vinyl cutter the manufacturer stopped supporting. Those goals led me to F/LOSS, GNU/Linux, Raspberry Pis, and then to the Pi-Top.

The original Pi-Top is a Raspberry Pi built into a laptop-style case, a giant fluorescent green matte plastic wedge. It looks like nothing else in a classroom. It says "I am not the computer you are used to." It's inexpensive, portable, and all-in-one, so I can carry it from classroom to classroom, and it runs my F/LOSS design stack.

I already knew Pis. I had been building my own LCD, Pi, and battery kit, but it was too far, too fast for most of my colleagues to try as anything more than a toy. The Pi-Top gave me a finished version of that idea.

The Pi-Top gave me a computer to design on. I still needed a way to get the work off the screen, past "just hit print."

I'd already been doing that with our department's Roland vinyl cutter. I shoved Sharpies and ballpoint pens into the holder that normally carries the blade and drew a whole bunch of posters that way. It was an [[Adhocism|adhocist]] hack, a tool made from whatever was on hand and pointed at a job nobody designed it for. It was also the first time I could see what [[A New Design Commons|a new design commons]] might look like, one where designers build, modify, and share their own tools. I like pens and pencils and paper, and I want to keep drawing with them while everything else moves onto screens.

The MICA Graphic Design department bought three [AxiDraws](https://shop.evilmadscientist.com/846), pen plotters that hold a pen and draw a vector file on paper. I adopted one. It draws from [Inkscape](https://inkscape.org/), a libre vector drawing program, through a plugin you download and install, so it takes a little setup on more than one front, but it's doable.

The AxiDraw and the Pi-Top were a good match. Both sit outside the usual design workflow. The AxiDraw's maker was clear that its software is open source, even though not every part of the system is public, and the Pi-Top runs on a Free/Libre stack. All I had to do was connect them through Inkscape.

I mainly wanted the Pi-Top as a movable control station for the AxiDraw at workshops around the department, and as a design laptop with only the few programs I needed. So I skipped Polaris, the Pi-Top's stock operating system, and built my own minimal one on Raspbian. A small install should leave more of the machine's power for the graphics programs themselves, and it does seem to run a little better.

I kept the case. The green wedge is the point.

So, instead of the default Pi-Top Polaris distro, I started with [Raspbian Lite](https://www.raspberrypi.org/downloads/raspbian/). I added the few required Pi-Top packages. I then decided to experiment with as little GUI as possible as well: I only installed OpenBox (I am pretty sure that I used [this tutorial](https://www.raspberrypi.org/forums/viewtopic.php?p=890408), which is just a window manager (basically it lets you have enough graphical interface to open programs and files and such in windows, but isn't really a graphic interface. So, the Pi-Top boots to the GNU Bash Terminal; and then you have to manually start OpenBox to get to the design stuff. I run `startx` from the terminal once I'm logged in and then poof! I'm suddenly on a totally blank desktop where I can then launch a terminal window again to run the programs I need like inkscape... (I need to Find the link to the instructions I followed to get this far... I had found someone elses tutorial for doing a basic raspbian lite + OpenBox setupminimal ui setup)

Raspbian now comes with a just the essentials + the Pixel GUI desktop; I might try that as my base if I was doing this again to minimize pain points. But it was a good learning experience to have to install a window manager from scratch and work through the various missing package issues as I went along.

Okay! The Pi-Top was working, I could get OpenBox to run... but I still had nothing else installed. I need to get Inkscape installed and running and then I needed to get Inkscape to talk to the AxiDraw.

I made sure to run `apt-get update` and then just installed Inkscape and all its dependencies from apt-get: `apt-get inkscape` (you might need to use sudo to run these properly depending on your setup). There were still a few other things that needed to get installed; and I still run into a few complications where something is thought to be missing or a python version doesn't match, but for the most part this stuff is all pretty painless. So, once Inkscape was working, I followed the instructions from AxiDraw and get the AxiDraw plugins in the right spots for Inkscape to find. A `sudo reboot` later and whir spin buzz I had a pen on a 2d robot arm ready to draw whatever I could vectorize with the Pi-Top in Inkscape!

Lastly, I cloned my git repo of my favorite open source and libre fonts to make sure I had everything typography wise I might want to play with available on my Pi-Top.

Having never worked with such a minimal install before, I do occasionally still run into issues of packages missing or some dependency being wrong; but for the most part this was painless and easy and the resources I needed were just waiting for me a web search away.

Since getting the AxiDraw working, I've also been getting some other plugins and programs onto my Pi-Top. I found [name of program], a libre 2d plotter controller, which allows me to use the aging Roland vinyl cutter in our department -- despite the fact that we can't get a new driver for it for our macOS or Windows machines without paying an exorbitant fee. So while being a cool way to test out libre designing and interesting "drawn" output, the Pi-Top and the F/LOSS ecosystem it is a part of continue to offer opportunities ...

Some sort of better conclusion?
