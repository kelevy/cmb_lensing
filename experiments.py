# importing relevant modules
import numpy as np
import tools


#################################################################################################################################


def specs(experiment): 
    
    if experiment == 's4wide':
        specs_dic = {
            #freq: [beam_arcmins, white_noise, red_noise, elknee, alphaknee]              
            27: [7.4, 21.5, 21.5, 415, -3.5],
            39: [5.1, 11.9, 11.9, 391, -3.5], 
            93: [2.2, 1.9, 1.9, 1932, -3.5],
            145: [1.4, 2.1, 2.1, 3917, -3.5],
            225: [0.9, 6.9, 6.9, 6740, -3.5],
            278: [0.7, 16.8, 16.8, 6792, -3.5],
            }   
        corr_noise_bands = {27:[39], 39:[27], 93:[145], 145:[93], 225: [278], 278: [225]}
        rho = 0.9
        
    if experiment == 'so':
        specs_dic = {
            #freq: [beam_arcmins, white_noise, red_noise, elknee, alphaknee] 
            27:  [7.4, 52.1, 6.1,  1000, -3.5],
            39:  [5.1, 27.1, 3.8,  1000, -3.5], 
            93:  [2.2, 5.8,  9.3,  1000, -3.5],
            145: [1.4, 6.5,  23.8, 1000, -3.5],
            225: [1.0, 15.0, 80.0, 1000, -3.5],
            280: [0.9, 37.0, 108.0, 1000, -3.5],
            }
        corr_noise_bands = {27:[39], 39:[27], 93:[145], 145:[93], 225: [280], 280: [225]}
        rho = 0.9
            
    if experiment == 'ccatp':
        specs_dic = {
            #freq: [beam_arcmins, white_noise, red_noise, elknee, alphaknee] 
            27:  [7.4, 52.1, 6.1,  1000, -3.5],
            39:  [5.1, 27.1, 3.8,  1000, -3.5], 
            93:  [2.2, 5.8,  9.3,  1000, -3.5],
            145: [1.4, 6.5,  23.8, 1000, -3.5],
            225: [1.0, 15.0, 80.0, 1000, -3.5],
            280: [0.9, 37.0, 108.0, 1000, -3.5],
            220: [0.95, 14.6, 0.07, 1000, -3.5],
            280: [0.75, 27.5, 0.19, 1000, -3.5], 
            350: [0.58, 104.8, 0.94, 1000, -3.5],
            410: [0.50, 376.6, 2.4, 1000, -3.5],
            }
        corr_noise_bands = {27:[39], 39:[27], 93:[145], 145:[93], 225: [280], 280: [225], 220: [220], 280:[280], 350:[350], 
                            410:[410]}   
        rho = 0.9
    return specs_dic, corr_noise_bands, rho


def frequencies(experiment):
    specs_dic, _, _ = specs(experiment)
    freq_arr = sorted( specs_dic.keys() )
    return freq_arr


def beam_power_spectrum(beam_fwhm):
    l = np.arange(10000)
    fwhm_radians = np.radians(beam_fwhm/60)
    sigma = fwhm_radians / np.sqrt(8. * np.log(2.))
    bl = np.exp(-1 * l * (l+1) * sigma ** 2)  
    return l, bl


def beam_power_spectrum_dict(experiment, opbeam = None):
    specs_dic, _, _ = specs(experiment)
    freq_arr = sorted( specs_dic.keys() )
    bl_dic = {}
    for freq in freq_arr:
        beam_fwhm, noiseval_white, noiseval_red, elknee, alphaknee = specs_dic[freq]
        l, bl_dic[freq] = beam_power_spectrum(beam_fwhm)
    if opbeam is not None:
        l, bl_dic['effective'] = beam_power_spectrum(opbeam)
    return l, bl_dic


def rebeam(bl_dic, threshold = 1000.):
    freq_arr = []
    for nu in list(bl_dic.keys()): 
        if isinstance(nu, int):
            freq_arr.append(nu)
    freq_arr = sorted(freq_arr)

    bl_eff = bl_dic['effective']
    rebeam_arr = []
    for freq in freq_arr:
        if freq is 'effective': continue
        bad_inds = np.where(bl_dic[freq]<0)
        bl_dic[freq][bad_inds] = 0.
        currinvbeamval = 1/bl_dic[freq]
        currinvbeamval[currinvbeamval>threshold] = threshold
        rebeamval = bl_eff * currinvbeamval
        rebeam_arr.append( rebeamval )
    return np.asarray( rebeam_arr )



def white_noise_power_spectrum(noiseval_white):
    l = np.arange(10000)
    delta_white_radians = np.radians(noiseval_white/60)
    nl_white = np.tile(delta_white_radians**2, int(max(l)) + 1 )
    nl_white = np.asarray( [nl_white[int(i)] for i in l] )
    return l, nl_white

    
def red_noise_power_spectrum(noiseval_red, elknee, alphaknee):
    l = np.arange(10000)
    n_red = np.radians(noiseval_red/60)**2 
    nl_red = n_red*(l/elknee)**alphaknee
    return l, nl_red

    

def noise_power_spectrum(noiseval_white, noiseval_red = None, elknee = -1, alphaknee = 0, beam_fwhm = None, noiseval_red2 = None, elknee2 = -1, alphaknee2 = 0, rho = None):
    
    l = np.arange(10000)
    cross_band_noise = 0
    if noiseval_red2 is not None:
        assert rho is not None
        cross_band_noise = 1
    
    # computing white noise power spectrum
    delta_white_radians = np.radians(noiseval_white/60)
    nl = np.tile(delta_white_radians**2, int(max(l)) + 1 )
    nl = np.asarray( [nl[int(i)] for i in l] )
       
    # adding atmospheric noise power spectrum
    if elknee != -1:
        n_red = np.radians(noiseval_red/60)**2 
        nl_red = n_red*(l/elknee)**alphaknee
        nl += nl_red
        nl[np.isinf(nl)] = 0
        if cross_band_noise:
            n_red2 =  np.radians(noiseval_red2/60)**2
            nl_red2= n_red2*(l/elknee2)**alphaknee2
            nl_red2[np.isinf(nl_red2)] = 0 
    
    # deconvolving noise power spectrum
    if beam_fwhm is not None:
        l, bl = beam_power_spectrum(beam_fwhm)
        nl *= bl**(-1)
    
    # computing cross band noise power spectrum
    if cross_band_noise:
        nl = rho * (nl_red * nl_red2)**(0.5)
        
    return l, nl


def noise_power_spectra_dict(experiment, deconvolve = False, use_cross_noise = False):
    
    # reading in experiment specs
    specs_dic, corr_noise_bands, rho = specs(experiment)
    freq_arr = sorted( specs_dic.keys() )
    beam_arr, whitenoise_arr, rednoise_arr, elknee_arr, alphaknee_arr = [], [], [], [], []
    for freq in freq_arr:
        beam_fwhm, noiseval_white, noiseval_red, elknee, alphaknee = specs_dic[freq]
        beam_arr.append(beam_fwhm)
        whitenoise_arr.append(noiseval_white)
        rednoise_arr.append(noiseval_red)
        elknee_arr.append(elknee)
        alphaknee_arr.append(alphaknee) 
      
    # creating noise power spectra dictionary
    nl_dic = {}
    for i in range(len(freq_arr)):
        beam_fwhm1, noiseval_white1, noiseval_red1, elknee1, alphaknee1  = beam_arr[i], whitenoise_arr[i], rednoise_arr[i], elknee_arr[i],  alphaknee_arr[i]
        for j in range(len(freq_arr)):        
            beam_fwhm2, noiseval_white2, noiseval_red2, elknee2, alphaknee2  = beam_arr[j], whitenoise_arr[j], rednoise_arr[j], elknee_arr[j], alphaknee_arr[j]
            if freq_arr[i] == freq_arr[j]: 
                if deconvolve is False:
                    l, nl =  noise_power_spectrum(noiseval_white1, noiseval_red1, elknee1, alphaknee1)
                else:
                    l, nl =  noise_power_spectrum(noiseval_white1, noiseval_red1, elknee1, alphaknee1, beam_fwhm1)
            else:
                if freq_arr[j] in corr_noise_bands[freq_arr[i]]: 
                    l, nl = noise_power_spectrum(noiseval_white1, noiseval_red1, elknee1, alphaknee1, beam_fwhm1, noiseval_red2, 
                                                 elknee2, alphaknee2, rho)
                else:
                    l = np.arange(10000)
                    nl = np.zeros( len(l) )
            nl[l<=10] = 0.
            nl_dic[(freq_arr[i], freq_arr[j])] = nl
    
    if use_cross_noise is False:
        nl_arr = [nl_dic[freq, freq]  for freq in freq_arr]  
        nl_dic = {}
        for i, freq in enumerate(freq_arr):
            nl_dic[freq] = nl_arr[i]
  
    return l, nl_dic