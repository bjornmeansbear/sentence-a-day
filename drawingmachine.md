# Pi-Top + Axidraw = Libre Drawing Machine

```
Notes:
line numbers: shift + alt + 3
line wrap: esc + $
```

As a graphic designer and college educator (I am a Graphic Designer by trade, and am a Graphic Design Professor at the [Maryland Institute College of Art](http://www.mica.edu) ), I am always looking for more ways to produce visual design, as well as more ways to show students alternatives to the status quo. I have been exploring lower cost and less fussy tools for my own design practice as well as more flexible and customizable tools for my classrooms. Basically: how do I show students and my clients good alternatives to the Apple/Adobe monoverse that the visual design profession typically uses. I've also been hoping to find ways of extending the life of our studio equipment. So, these goals have led me to F/LOSS, the GNU/Linux world generally, and computers like Raspberry Pis and specifically the Pi-Top.

The Pi-Top was an especially alluring option: a minimal, expandable, inexpensive, portable, all-in-one computer that was built upon raspberry pis I was already comfortable playing with (I had been working on my own LCD + pi + battery kit that was going no where), and gave me a real computer that looked different -- it says "I am not the computer you are used to" -- all while using my F/LOSS design stack! I had to give it a try.

Bring it from classroom to classroom easily.

Okay, so there is a novel computer platform to use for creating digital design -- Pi-Top + raspbian + F/LOS design tools... what about output?

I am always trying to make designs with actual physical tools where possible -- how can I return to more pens and pencils and paper and whatever despite this trend towards everything on a screen; everything just printed. And I had been playing around with using our vinyl cutter as a drawing plotter by justtaping a sharpie into the holder that would normally hold the cutting blade. I ended up finding the Axidraw. This seemed like a cool option to pair with the Pi-Top -- they both are non-status-quo tools for designing and design output for sure! they are also both from this Free/Libre community...

The MICA Graphic Design department had gotten three axidraws, and I decided to adopt one an start using it where possible in my work. The axidraw is setup to easily "print" from inkscape (link to inkscape? inkscape is a libre vector drawing program). So, I had a Pi-Top, I had an axidraw. I needed to put them together with inkscape!

I wanted to use the Pi-Top as a design laptop. That meant that I decided not to use the regular polaris system; I decided to build my own more minimal raspbian distro. I wanted the Pi-Top just to have the few design programs I wanted and to be mainly a moveable control station for the axidraw for various workshops I was doing around the department.

I decided to do as minimal an install as possible.

Instead of the default polaris distro, I started with just raspbian lite. I added the few required Pi-Top packages. I then decided to exp[eriment with as little GUI as possible as well -- I only installed openbox, which is just a window manager (basically it lets you have enough graphical interface to open programs and files and such in windows, but isn't really a graphic interface. So, the Pi-Top boots to the GNU Bash Terminal; and then you have to manually start openbox to get to the design stuff. I run `startx` from the terminal once I'm logged in and then poof! I'm suddenly on a totally blank desktop where I can then launch a terminal window again to run the programs I need like inkscape... (I need to Find the link to the instructions I followed to get this far... I had found someone elses tutorial for doing a basic raspbian lite + openbox setupminimal ui setup)

So great, I had the Pi-Top working, I could get all the battery charging, monitor and keyboard stuff to power my pi w/ minimal OS. I could get openbox to run... but I still had nothing else installed. I need to get inkscape installed and running and then I needed to get inkscape to talk to the axidraw.

I made sure to run apt-get update and then just installed inkscape and all its dependencies from apt-get: `sudo apt-get inkscape`

Easy. There were a few other things that needed to get installed; and I still run into a few complications where something is thought to be missing or a python version doesn't match, but for the most part this stuff is all pretty painless. So, once inkscape was working, I then just needed to follow the instructions from axidraw and get the axidraw plugins in the right spots for inkscape to find. A `sudo reboot` later and whir spin buzz I had a pen on a 2d robot arm ready to draw whatever I could vectorize with inkscape.

Lastly, I cloned my git repo of my favorite open source and libre fonts to make sure I had everything typography wise I might want to play with avaiable on my Pi-Top.

Having never worked with such a minimal install before, I do occasionally still run into issues of packages missing or some dependency being wrong; but for the most part this was painless and easy and the resources I needed were just waiting for me a duck duck go search away.

Since getting the axidraw working, I've also been getting some other plugins and programs onto my Pi-Top. I found [name of program], a libre 2d plotter controller, which allows me to use the aging Roland vinyl cutter in our department -- despite the fact that we can't get a new driver for it for our macOS or Windows machines without paying an exorbidant fee. So while being a cool way to test out libre designing and interesting "drawn" output, the Pi-Top and the F/LOSS ecosystem it is a part of continue to offer opportunities ...

Some sort of better conclusion???
