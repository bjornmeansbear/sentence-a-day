# PiTop + Axidraw = Libre Drawing Machine

Nano Notes:
line numbers: shift + alt + 3
line wrap: esc + $

As a graphic designer and college educator (I am a Graphic Designer by trade, and am a Graphic Design Professor at the [Maryland Institute College of Art](http://www.mica.edu) ), I am alway$

The pitop was an especially alluring option: a minimal, expandable, inexpensive, portable, all-in-one computer that was built upon raspberry pis I was already comfortable playing with (I ha$

Bring it from classroom to classroom easily.

Okay, so there is a novel computer platform to use for creating digital design -- pitop + raspbian + F/LOS design tools... what about output?

I am always trying to make designs with actual physical tools where possible -- how can I return to more pens and pencils and paper and whatever despite this trend towards everything on a s$

The MICA Graphic Design department had gotten three axidraws, and I decided to adopt one an start using it where possible in my work. The axidraw is setup to easily "print" from inkscape (l$

I wanted to use the pitop as a design laptop. That meant that I decided not to use the regular polaris system; I decided to build my own more minimal raspbain distro. I wanted the pitop jus$

I decided to do as minimal an install as possible.

Instead of the default polaris distro, I started with just raspbian lite. I added the few required pitop packages. I then decided to exp[eriment with as little GUI as possible as well -- I $

(I need to Find the link to the instructions I followed to get this far... I had found someone elses tutorial for doing a basic raspbian lite + openbox setupminimal ui setup)

So great, I had the pitop working, I could get all the battery charging, monitor and keyboard stuff to power my pi w/ minimal OS. I could get openbox to run... but I still had nothing else $

I made sure to run apt-get update and then just installed inkscape and all its dependencies from apt-get: `sudo apt-get inkscape`

Easy. There were a few other things that needed to get installed; and I still run into a few complications where something is thought to be missing or a python version doesn't match, but fo$

Lastly, I cloned my git repo of my favorite open source and libre fonts to make sure I had everything typography wise I might want to play with avaiable on my pitop.

Having never worked with such a minimal install before, I do occasionally still run into issues of packages missing or some dependency being wrong; but for the most part this was painless a$

Since getting the axidraw working, I've also been getting some other plugins and programs onto my pitop. I found [name of program], a libre 2d plotter controller, which allows me to use the$

Some sort of better conclusion???
