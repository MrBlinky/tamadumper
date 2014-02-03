################################################################
#  tamadumper v0.07                        Mr Blinky Jan 2014  #
################################################################

# written using Python 2.7.1 win32 & pyserial 2.7 win32 #

import serial #Requires pySerial to be installed
import time
import sys

global chip
global start_time

## Chip info ##
 
chipIDs		=[
			'000000',	#unknown
			'C20514',	#GPR26L080 (used in Wave 1 Tamago figures)
			'C20515',	#GPR26L160
			'C22013',	#GPR25L041 (used in Wave 2 Tamago figures)
			'C22014',	#GPR25L081
			'C22015',	#GPR25L162
			'C84012',	#GD25Q20 (used in deco pierces)
			'C84013',	#GD25Q40
			'EF4013',	#W25Q40
			'EF4014',	#W25Q80
			'EF4015',	#W25Q16
			'EF4016',	#W25Q32
			'EF4017',	#W25Q64 (used by MrBlinky's custom deco pierce)
			'EF4018'	#W25Q128
			]
			   
chipSizes	=[
			0, 			#unknown
			1	<< 20,	#GPRL26L080
			2	<< 20,	#GPRL26L160
			512	<< 10,	#GPR25L041
			1	<< 20,	#GPR25L081
			2	<< 20,	#GPR25L162
			256	<< 10,	#GD25Q20
			512	<< 10,	#GD25Q40
			512	<< 10,	#W25Q40
			1	<< 20,	#W25Q80
			2	<< 20,	#W25Q16
			4	<< 20,	#W25Q32
			8	<< 20,	#W25Q64
			16	<< 20	#W25Q128
			]

chipInfo	=[
			'',
			'GPR26L080 General Plus 8 Mbit Mask ROM',
			'GPR26L080 General Plus 16 Mbit Mask ROM',
			'GPR25L041 General Plus 4 Mbit flash',
			'GPR25L081 General Plus 8 Mbit flash',
			'GPR25L162 General Plus 16 Mbit flash',
			'GD25Q20 Giga Device 2 Mbit flash',
			'GD25Q40 Giga Device 4 Mbit flash',
			'W25Q80 Winbond 8 Mbit flash',
			'W25Q16 Winbond 16 Mbit flash',
			'W25Q32 Winbond 32 Mbit flash',
			'W25Q64 Winbond 64 Mbit flash',
			'W25Q64 Winbond 128 Mbit flash'
			]
			
##  functions ##

def usage():
	print('\nUSAGE:\n\ntamadump.py option commport [start] [length] [filename]\n')
	print('-c chip erase')
	print('-d dump flash')
	print('-i read device ID')
	print('-p program flash')
	print('-v verify flash')
	print('\n Defaults: start = 0, length = device dependent')
	print('\nExamples:')
	print ('tamadump.py /r COM3 dump.bin')
	print ('tamadump.py /r COM3 524288 dump.bin')
	print ('tamadump.py /r COM3 0 524288 dump.bin')
	return

def resetTimer():
	global start_time
	start_time = time.time()
	
def printTimer():
	elapsed_time = time.time() - start_time
	print '\nCompleted in %.2f seconds' % elapsed_time
	
def chipDetect():
	global chip
	ser.write('i')
	ID = ser.readline()[11:17]
	ser.readline() # drop status 
	if ID in chipIDs:
		chip = chipIDs.index(ID)
		print 'Found ' + chipInfo[chip] + ' (ID=%s)' % ID 
	else:
		chip = 0 
		print 'No known device found (ID=%s)' % ID 
		exit()
	print	
	return

def chipStatus():
	ser.write('i')
	ser.readline() # drop ID
	SR =ser.readline()[8:12]
	print
	s = 'Status: ' + SR + ' ('
	for i in range (15,-1,-1):
		if i == 7:
			s += '-'+str(int(SR,16) >> i & 1)
		else:
			s += str(int(SR,16) >> i & 1)
	print s + ')'
	return
	
def chipErase():
	resetTimer()
	ser.write('c')
	print (ser.readline())
	print (ser.readline())
	printTimer()
	return

def dump(start, length, filename):
	resetTimer()
	print 'Dumping ...'
	f = open(filename, 'wb')
	ser.write('a'+start)
	ser.readline()
	ser.write('l'+length)
	ser.readline()
	ser.write('d')
	b = ser.read(int(length,0))
	f.write(b)
	f.close()
	printTimer()
	return

def program(start, length, filename):
	resetTimer()
	f = open(filename, 'rb')
	b = f.read()
	print 'Flashing ...'
	ser.write('a'+start)
	ser.readline()
	ser.write('l'+length)
	ser.readline()
	ser.write('p')
	for i in range (0,int(length,0),256):
		ser.write(b[i:i+255]) #\ workaround
		ser.write(b[i+255])	  #/ using 256 causes everything to go berzerk
		ser.readline()
	f.close()
	printTimer()
	return

def verify(start, length, filename):
	resetTimer()
	print 'veryfying ...'
	f = open(filename, 'rb')
	b = f.read()
	ser.write('a'+start)
	ser.readline()
	ser.write('l'+length)
	ser.readline()
	ser.write('d')
	d = ser.read(int(length,0))
	if b == d:
		print 'Verify success'
	else:
		print "Verify failed!"
	f.close()
	printTimer()
	return
	
## main ##

#at least two parameters needed for simple commands
if len(sys.argv) < 3 : 
	usage()
	exit()
#at least 3 parameters needed for dump, program or verify
elif (len(sys.argv) < 4) and (sys.argv[1] == '-d' or sys.argv[1]== '-p' or sys.argv[1]=='-v') :
	usage()
	exit()
	
#open comm port
port = sys.argv[2]
while True:
	try:
		ser = serial.Serial(port,115200)
		break #break on connection
	except serial.SerialException:
		print 'Can\'t open ' + port + ' retrying ...'
		time.sleep(3)
print

# get chip ,start address, length and filename
chipDetect()
if len(sys.argv) == 4 :
	chipAddr = '0'
	chipLen  = str(chipSizes[chip])
	chipFile = sys.argv[3]
elif len(sys.argv) == 5 :
	chipAddr = '0'
	chipLen  = sys.argv[3]
	chipFile = sys.argv[4]
elif len(sys.argv) == 6:
	chipAddr = sys.argv[3]
	chipLen  = sys.argv[4]
	chipFile = sys.argv[5]

# execute commands
if sys.argv[1] == '-d' :
	dump(chipAddr,chipLen,chipFile)
elif sys.argv[1] == '-c' :
	chipErase()
elif sys.argv[1] == '-i' :	
	chipStatus()
elif sys.argv[1] == '-p' :
	program(chipAddr,chipLen,chipFile)
elif sys.argv[1] == '-v' :
	verify(chipAddr,chipLen,chipFile)
else:
	usage()
exit()
