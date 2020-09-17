#!/usr/bin/env python3
import argparse
import sys as os
import datetime
import numpy as np
import fileinput
import convolution as conv
import extract_s_w as sw
'''
Commandline tool to use new convolution codes.

Do it like this:
>>>convsw.py inputfile outputfile fwhm [-swin=swin] 

Input details:
>>>convsw.py -h

Examples:
1) Convolution.
>>>convsw.py al-acar1d_100.dat al.dat fwhm
2) Convolution and sw-parameters.
>>>convsw.py al-acar1d_100.dat al.dat fwhm -swin=swin
'''

def parse_arguments():
	'''Read arguments from a command line.'''
	parser = argparse.ArgumentParser()
	parser.add_argument('infile',  help='input_filename')
	parser.add_argument('outfile', help='output filename')
	parser.add_argument('fwhm', help='FWHM in keV, Energy resolution of setup')
	parser.add_argument('-swin',  required=False, help='SW windows in a.u., optional')

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

def read_fwhmfile():
	'''Read fwhm file'''
	with open(args.fwhm, 'r') as fwhmfile:
		fwhm=[float(i) for i in fwhmfile.readline().split(' ') if i.strip()]
	fwhmfile.close()
	return fwhm
		
def read_swfile():
	'''Read sw windows file'''
	with open(args.swin, 'r') as swin:
		S=[float(i) for i in swin.readline().split(' ') if i.strip()]
		W=[float(i) for i in swin.readline().split(' ') if i.strip()]
	swin.close()
	return S, W
		
def write_output(fwhm, convdata1, convdata2=None):
	'''Write convoluted data into output file'''			
	with open(args.outfile, 'w+') as outfile:
		outfile.write("Input file: %s \nTime: %s \n" % (args.infile, datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
		if len(fwhm)==1: #if only fwhm1 is given
			outfile.write('{0:<33}{1:<33}\n'.format(str(''), "FWHM1=%0.3f" %(fwhm[0])))
			outfile.write('{0:<33}{1:<33}\n'.format('Momentum (a.u.)', 'Normalized spectrum (a.u.^{-1})'))
			for i in convdata1:
				outfile.write('{0:<33.9E}{1:<33.9E}\n'.format(i[0], i[1]))
		else: #if fwhm1 and fwhm2 are given							
			outfile.write('{0:<33}{1:<33}{2:<33}\n'.format(
				str(''), "FWHM1=%0.3f" %(fwhm[0]), "FWHM2=%0.3f" %(fwhm[1])))
			outfile.write('{0:<33}{1:<33}{2:<33}\n'.format(
				'Momentum (a.u.)', 'Normalized spectrum (a.u.^{-1})', 'Normalized spectrum (a.u.^{-1})'))
			for n, i in enumerate(convdata1):
				outfile.write('{0:<33.9E}{1:<33.9E}{2:<33.9E}\n'.format(i[0], i[1], convdata2[n, 1]))
	outfile.close()		

def write_output_sw(S, W, sw1, sw2=None):
	'''Add SW parameters and SW window inputs to the end of output file'''
	for line in fileinput.FileInput(args.outfile, inplace=1):
		if "Time:" in line:
			line = line.replace(line, line+'\nSW parameters with inputs S=[0, %f], W=[%f, %f]\n' % (S[1], W[0], W[1]))
			if sw2 == None: #if only fwhm1 is given write sw1 under its column
				line = line.replace(line, line+'{0:<33}{1:<33}\n{2:<33}{3:<33}\n'.format(
					str(''), "S1=%0.9f" %(sw1[0]), 
					str(''), "W1=%0.9f\n" %(sw1[1])))
			else: #if fwhm1 and fwhm2 are given	write sw params for both under respective columns
				line = line.replace(line, line+ '{0:<33}{1:<33}{2:<33}\n{3:<33}{4:<33}{5:<33}\n'.format(
					str(''), "S1=%0.9E" %(sw1[0]), "S2=%0.9E" %(sw2[0]), 
					str(''), "W1=%0.9E" %(sw1[1]), "W2=%0.9E\n" %(sw2[1])))
		print(line, end='')
		
def main():
	if args.infile==args.outfile: os.exit('Input and output files have the same name.')		
	indata = read_infile()
	fwhm = read_fwhmfile()
	qspacing = indata[1, 0] #first step
	gaussian_range = indata[-1, 0] #last momentum
	kev_to_mc= 3.91

	#convolution
	convdata1 = conv.conv_mirror(indata, fwhm[0]*kev_to_mc, gaussian_range, qspacing)	#uses convolution.py and fwhm1
	if len(fwhm) == 2:
		convdata2 = conv.conv_mirror(indata, fwhm[1]*kev_to_mc, gaussian_range, qspacing)	#uses convolution.py and fwhm2 of given
		write_output(fwhm, convdata1, convdata2)	#in a.u
	else:
		write_output(fwhm, convdata1)	#in a.u

	#sw-params
	if args.swin !=None:
		S, W = read_swfile()
		sw1 = sw.calc_s_w(S[1], W[0], W[1], convdata1)	#uses extract_s_w.py for convoluted data with fwhm1 
		if len(fwhm) == 2:
			sw2 = sw.calc_s_w(S[1], W[0], W[1], convdata2)	#uses extract_s_w.py for convoluted data with fwhm2, if given
			write_output_sw(S, W, sw1, sw2)
		else:
			write_output_sw(S, W, sw1)

if __name__ == '__main__':
	args = parse_arguments()
	main()

