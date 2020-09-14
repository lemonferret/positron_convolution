import numpy as np
from math import e
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
    integrate = np.trapz(conv[ind:],input_array[:,0]*7.298202236578298)
    conv_prob_den = conv[ind:]/integrate

#finally we combine x axix (from input array) and y axis(conv_prob_den).
#the unit of x axis is converted from a.u. to 1e-3*m0*c
#This probably can be done using only one function in one line. Anyway it works.
    final = []
    for i in range(len(input_array)):
        final.append([input_array[i,0]*7.298202236578298,conv_prob_den[i]])
    final = np.array(final)
    return final

def calc_s_w(s_cut,w_cut_low,w_cut_high,input_array):
#s_cut is the momentum range of s parameter
#w_cut_low and w_cut_high are the momentum range of w parameter
#the unit of s_cut and w_cut are 1e-3*m0c
#input_array is the db spectra after convolution
    array_s,array_w=[],[]
#firstly let's get 2 arrays to calculate N_s, N_w.
    for i in range(len(input_array)):
        if input_array[i,0]<=s_cut:
            array_s.append([input_array[i,0],input_array[i,1]])
        if w_cut_low <= input_array[i,0] <= w_cut_high:
            array_w.append([input_array[i,0],input_array[i,1]])
    array_s = np.array(array_s)
    array_w = np.array(array_w)
#secondly integrate array_s array_w and input_array to get N_s, N_w and N_total
    inte_s  = np.trapz(array_s[:,1],array_s[:,0])
    inte_w  = np.trapz(array_w[:,1],array_w[:,0])
    inte_tot= np.trapz(input_array[:,1],input_array[:,0])
#thirdly calculate s and w directly
    s = inte_s/inte_tot
    w = inte_w/inte_tot
    return s,w
'''
Here is the example of using my function
'''
#Read bulk Al data using numpy
al = np.loadtxt("al-acar1d_100.dat", skiprows=2, usecols=(0,1))[:1200]

#Convolute the al data
al_conv = conv_mirror(al,4.3,5,0.01)

#calculate s and w
al_s_w  = calc_s_w(3,10,27,al_conv)
#print(al_s_w)
