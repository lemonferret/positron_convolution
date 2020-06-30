import pandas as pd
import numpy as np
import math as math
import matplotlib.pyplot as plt
import scipy.special as ss
import convolution as conv

def read_acar1d(directory):
	name111 = directory + '/acar1d_111_ave'
	name110 = directory + '/acar1d_110_ave'
	name100 = directory + '/acar1d_100_ave'

	dat111 = pd.read_csv(name111, skipinitialspace=True, delim_whitespace = True, header = None, skiprows = 2)
	dat110 = pd.read_csv(name110, skipinitialspace=True, delim_whitespace = True, header = None, skiprows = 2)
	dat100 = pd.read_csv(name100, skipinitialspace=True, delim_whitespace = True, header = None, skiprows = 2)

	return dat111, dat110, dat100

def read_acar1d_conv(directory):
	name111 = directory + '/acar1d_111_ave'
	name110 = directory + '/acar1d_110_ave'
	name100 = directory + '/acar1d_100_ave'	

	dat111 = np.loadtxt(name111, skiprows=2, usecols=(0,1))[:1200]
	dat110 = np.loadtxt(name110, skiprows=2, usecols=(0,1))[:1200]
	dat100 = np.loadtxt(name110, skiprows=2, usecols=(0,1))[:1200]
	
	dat111 =conv.conv_mirror(dat111, 4.3, 5, 0.01)
	dat110 =conv.conv_mirror(dat110, 4.3, 5, 0.01)
	dat100 =conv.conv_mirror(dat100, 4.3, 5, 0.01)

	return dat111, dat110, dat100


def plotter(ax, dat, colors, labels, direction):
	for i, n in enumerate(dat):
		ax.plot( n[0],  n[1], color=colors[i],  linestyle='solid', label=labels[i])
		print(max(n[1]/2))
	ax.legend()
	ax.set_ylabel('Annihilation rate (ps^{-1} a.u.^{-1})')
	ax.set_xlabel('Momentum (a.u.)')
	ax.set_title('Ennen: '+direction)
	#ax.set_xlim([-0.1, 2.5])
	ax.set_xlim([-0.1, 12])
	ax.set_ylim([5e-8, 2])	
	return ax
	
def plotter_conv(ax, dat, colors, labels, direction):
	for i, n in enumerate(dat):
		ax.plot(n[:,0],n[:,1], color=colors[i],  linestyle='solid', label=labels[i])
	ax.legend()
	ax.set_ylabel('probability')
	ax.set_xlabel('Momentum(a.u.)')
	ax.set_title('Jälkeen:   '+direction)
	ax.set_xlim([-0.1, 12])
	ax.set_ylim([5e-8, 2])	
	return ax

def main():
	(none_111, none_110, none_100) = read_acar1d("3x3x3_none")
	(mono_111, mono_110, mono_100) = read_acar1d("3x3x3_mono")
	(div1_111, div1_110, div1_100) = read_acar1d("3x3x3_div1")
	(triv1_111, triv1_110, triv1_100) = read_acar1d("3x3x3_triv1")
	(tetrav4_111, tetrav4_110, tetrav4_100) = read_acar1d("3x3x3_tetrav4")
	
	fig, ((ax1, ax2, ax3), (ax4, ax5, ax6))= plt.subplots(2, 3, sharey=False, figsize=(15, 8))
	colors = ['lightgreen', 'violet', 'teal', 'blue', 'thistle']
	labels = ['none', 'mono',  'div1', 'triv1', 'tetrav4']
	
	ax1 = plotter(ax1, [none_111, mono_111, div1_111, triv1_111, tetrav4_111], colors, labels, '111')
	ax2 = plotter(ax2, [none_110, mono_110, div1_110, triv1_110, tetrav4_110], colors, labels, '110')
	ax3 = plotter(ax3, [none_100, mono_100, div1_100, triv1_100, tetrav4_100], colors, labels, '100')


	#convolution 
	(none_111, none_110, none_100) = read_acar1d_conv("3x3x3_none")
	(mono_111, mono_110, mono_100) = read_acar1d_conv("3x3x3_mono")
	(div1_111, div1_110, div1_100) = read_acar1d_conv("3x3x3_div1")
	(triv1_111, triv1_110, triv1_100) = read_acar1d_conv("3x3x3_triv1")
	(tetrav4_111, tetrav4_110, tetrav4_100) = read_acar1d_conv("3x3x3_tetrav4")


	colors = ['lightgreen', 'violet', 'teal', 'blue', 'thistle']
	labels = ['none', 'mono',  'div1', 'triv1', 'tetrav4']
	ax4 = plotter_conv(ax4, [none_111, mono_111, div1_111, triv1_111, tetrav4_111], colors, labels, '111')
	ax5 = plotter_conv(ax5, [none_110, mono_110, div1_110, triv1_110, tetrav4_110], colors, labels, '110')
	ax6 = plotter_conv(ax6, [none_100, mono_100, div1_100, triv1_100, tetrav4_100], colors, labels, '100')

	ax1.set_yscale("log")
	ax2.set_yscale("log")
	ax3.set_yscale("log")
	ax4.set_yscale("log")
	ax5.set_yscale("log")
	ax6.set_yscale("log")

	plt.show()
	
	
	
if __name__ == '__main__':
	main()

