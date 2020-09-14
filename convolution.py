#numpy is used for convenience
import numpy as np
from math import e

#matplotlib is just for visualize the figure.
import matplotlib.pyplot as plt

def Convolute_with_gaussian(fwhm,input_array,gaussian_range,qspacing):
#this function convolute the input array.
#fwhm is full width at half maximum of gaussian func, unit is 1e-3*m0*c
#input_array is the array to be convoluted (Annihilation rate of calculated momentum distribution)
#For gaussian distribution function, gaussian_range is x range of gaussian func. I usually use 5.
#the length of input array should be longer than 2n/qspacing. n is gaussian range.
#if the input array is too short, change gaussian range to a smaller value.
	momentRange = np.arange(-gaussian_range,gaussian_range,qspacing)
	gaussian = []
	for i in momentRange:
		x = e**(-(i**2)/(2*(0.05818*fwhm)**2))
		gaussian.append(x)
	gaussian = np.array(gaussian)
	out_put = np.convolve(input_array,gaussian,mode = 'same')
	return out_put

def conv_mirror(input_array, fwhm, gaussian_range,qspacing):
#the calculated momentum distribution is only half of real 
#momentum distribution. If the calculated results is directly convoluted,
#I'll get a weird curve. This won't affect ratio between 2 results, e.g. Cu/Al ratio.
#But the direct comparison of momentum distribution between calculation and
#experiments will be impossible. So here I do a mirror symmetry of calculated data first.
    symm = []
    for i in range(len(input_array)-1):
        symm.append([-input_array[-(i+1),0],input_array[-(i+1),1]])
    symm=np.array(symm)
    full_array=np.concatenate((symm,input_array), axis=0)

#Now let's convolute the full array using the convolution function.
    conv = Convolute_with_gaussian(fwhm,full_array[:,1],gaussian_range,qspacing)

#then we only want the right half of the convoluted result, and we calculate the probability density.
    ind = len(input_array)-1
    integrate = np.trapz(conv[ind:], input_array[:,0]) #a.u.
    #integrate = np.trapz(conv[ind:],input_array[:,0]*7.298202236578298)
    conv_prob_den = conv[ind:]/integrate

#finally we combine x axix (from input array) and y axis(conv_prob_den).
#the unit of x axis is converted from a.u. to 1e-3*m0*c*
#This probably can be done using only one function in one line. Anyway it works.
    final = []
    for i in range(len(input_array)):
        final.append([input_array[i,0], conv_prob_den[i]]) #a.u
        #final.append([input_array[i,0]*7.298202236578298,conv_prob_den[i]])
    final = np.array(final)
    return final

'''
Here is the example of using my function
'''

#Read bulk Al data using numpy
al = np.loadtxt("al-acar1d_100.dat", skiprows=2, usecols=(0,1))[:1200]

#convolute
al_conv = conv_mirror(al,4.3,5,0.01)
#plot figure 
plt.figure(1)
plt.subplot(111)
plt.plot(al_conv[:,0],al_conv[:,1],'b-',label = 'Al')

plt.ylim(0.0000001,0.2)
plt.xlim(0,80)
plt.yscale('log')
plt.xlabel('Momentum(1e-3 m0c)')
plt.ylabel('probability')
plt.legend(loc =1)
#plt.show()

