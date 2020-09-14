#!/usr/bin/env python3
import argparse
import sys as os
import datetime
import numpy as np
import convolution as conv
import extract_s_w as sw
'''
Commandline tool to use new convolution codes.

Do it like this:
>>> python3 convsw.py inputfile outputfile -fwhm1 [-fwhm2] [-S] [-Wmin] [-Wmax] 

Input details:
>>> python3 convsw.py -h

Examples:
1) Convolution with single resolution.
>>>./convsw.py al-acar1d_100.dat al.dat -fwhm1=0.9 
2) Convolution with two resolutions.
>>>./convsw.py al-acar1d_100.dat al.dat -fwhm1=0.9 -fwhm2=2.4
3) Convolution and sw-parameters with single resolution.
>>>./convsw.py al-acar1d_100.dat al.dat -fwhm1=0.9  -S=0.41 -Wmin=1.37 -Wmax=3.699
4) Convolution and sw-parameters with two resolutions.
>>>./convsw.py al-acar1d_100.dat al.dat -fwhm1=0.9 -fwhm2=1.3  -S=0.41 -Wmin=1.37 -Wmax=3.699
'''

def parse_arguments():
	'''Read arguments from a command line.'''
	parser = argparse.ArgumentParser()
	parser.add_argument('infile',  help='input_filename')
	parser.add_argument('outfile', help='output filename')
	parser.add_argument('-fwhm1', type=float, required=True, help='FWHM in keV, Energy resolution detector 1, required')
	parser.add_argument('-fwhm2', type=float, required=False, help='FWHM in keV, Energy resolution detector 2, optional')
	parser.add_argument('-S', type=float,  required=False, help='S cut in a.u., optional')
	parser.add_argument('-Wmin', type=float, required=False, help='W min cut in a.u., optional')
	parser.add_argument('-Wmax', type=float, required=False, help='W max cut in a.u., optional')

	args = parser.parse_args()
	return args

def read_infile():
	'''Read input file'''
	indata = np.empty([0, 2])
	with open(args.infile, 'r') as infile:								
		for line in infile.readlines()[2:]: #start the reading from line 2 to skip general info
			inline= [float(i) for i in line.split(' ') if i.strip()]	
			if inline[0] <= 5.5: indata= np.vstack((indata, inline)) #momentum cutoff at 5.5 a.u or at max
		infile.close()
	return indata
	
def write_output(convdata1, convdata2=None):
	'''Write convoluted data into output file'''			
	with open(args.outfile, 'w+') as outfile:
		outfile.write("Input file: %s \nDate: %s\n" % (args.infile, datetime.date.today().strftime("%d-%m-%Y"))) 
		if args.fwhm2 == None: #if only fwhm1 is given
			outfile.write('{0:<30}{1:<30}\n'.format(str(''), "FWHM1=%0.3f" %(args.fwhm1)))
			outfile.write('{0:<30}{1:<30}\n'.format('Momentum (a.u.)', 'Annihilation rate (a.u.^{-1})'))
			for i in convdata1:
				outfile.write('{0:<30.9E}{1:<30.9E}\n'.format(i[0], i[1]))
		else: #if fwhm1 and fwhm2 are given							
			outfile.write('{0:<30}{1:<30}{2:<30}\n'.format(
				str(''), "FWHM1=%0.3f" %(args.fwhm1), "FWHM2=%0.3f" %(args.fwhm2)))
			outfile.write('{0:<30}{1:<30}{2:<30}\n'.format(
				'Momentum (a.u.)', 'Annihilation rate (a.u.^{-1})', 'Annihilation rate (a.u.^{-1})'))
			for n, i in enumerate(convdata1):
				outfile.write('{0:<30.9E}{1:<30.9E}{2:<30.9E}\n'.format(i[0], i[1], convdata2[n, 1]))
	outfile.close()		

def write_output_sw(sw1, sw2=None):
	'''Add SW parameters and SW window inputs to the end of output file'''
	with open(args.outfile, 'a') as outfile:
		outfile.write("\nSW parameters with inputs S=%f, Wmin=%f, Wmax=%f\n" 
			% (args.S, args.Wmin, args.Wmax)) 
		if args.fwhm2 == None: #if only fwhm1 is given write sw1 under its column
			outfile.write('{0:<30}{1:<30}\n{2:<30}{3:<30}\n'.format(
				str(''), "S1=%0.9f" %(sw1[0]), 
				str(''), "W1=%0.9f" %(sw1[1])))
		else: #if fwhm1 and fwhm2 are given	write sw params for both under respective columns
			outfile.write('{0:<30}{1:<30}{2:<30}\n{3:<30}{4:<30}{5:<30}\n'.format(
				str(''), "S1=%0.9E" %(sw1[0]), "S2=%0.9E" %(sw2[0]), 
				str(''), "W1=%0.9E" %(sw1[1]), "W2=%0.9E" %(sw2[1])))
	outfile.close()	
		
def main():
	if args.infile==args.outfile: os.exit('Input and output files have the same name.')		
	indata = read_infile()
	qspacing = indata[1, 0] #first step
	gaussian_range = indata[-1, 0] #last momentum
	kev_to_mc= 3.91	#<--- voisi olla useamman numeron tarkkuudella
	
	#convolution
	convdata1 = conv.conv_mirror(indata, args.fwhm1*kev_to_mc, gaussian_range, qspacing)	#uses convolution.py and fwhm1
	if args.fwhm2 != None:
		convdata2 = conv.conv_mirror(indata, args.fwhm2*kev_to_mc, gaussian_range, qspacing)	#uses convolution.py and fwhm2 of given
		write_output(convdata1, convdata2)	#in a.u
	else:
		write_output(convdata1)	#in a.u

	#sw-params
	if args.S != args.Wmin != args.Wmax != None: #all three have inputs
		sw1  = sw.calc_s_w(args.S, args.Wmin, args.Wmax, convdata1)	#uses extract_s_w.py for convoluted data with fwhm1
		if args.fwhm2 != None:
			sw2 = sw.calc_s_w(args.S, args.Wmin, args.Wmax, convdata2)	#uses extract_s_w.py for convoluted data with fwhm2, if given
			write_output_sw(sw1, sw2)
		else:
			write_output_sw(sw1)
	elif args.S == args.Wmin == args.Wmax == None: #all three empty
		os.exit()
	else: #some but not all input values given
		os.exit('Give all three: -S, -Wmin, -Wmax')
	
if __name__ == '__main__':
	args = parse_arguments()
	main()

