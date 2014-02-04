tamadumper
==========

Tamagotchi P's Deco Pierce (SPI flash) dumper /programmer

The Tamagotchi P's has accesories called Deco Pierces. These pierces contain a GD25Q20 serial (SPI) flash chip from Giga Device which can also be reprogrammed.
This project allowes you to dump and reprogram the pierces.

The basic hardware that is needed for the dumer is a 10 pin 0.1 Inch spaced card edge connector and a 3.3V level converter that is connected to
an interface. This project will support several interfaces. The following are currently available:

arduino	-	cointains python script and arduino sketch to use a Arduino (Leonardo) as tamadumper using a self made shield.
			A shield can be made using the schematic from the lpt version.
			
lpt -		Contains schematic and tools to make a parallel port version of the tamadumper.

