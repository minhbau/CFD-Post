# -*- coding: utf-8 -*-
"""
Created on Tue May 1 10:24:50 2018
    This code for reading data from specific file to post-processing data
    1. FileName (infile, VarName, (row1), (row2), (unique) ): sort data and 
    delete duplicates, SPACE is NOT allowed in VarName
    2. MergeFile (NameStr, FinalFile): NameStr-input file name to be merged
    3. GetMu (T): calculate Mu if not get from file
    4. unique_rows (infile, outfile):
@author: Weibo Hu
"""

import numpy as np
import scipy as sp
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib
import warnings
import pandas as pd
from DataPost import DataPost
from scipy.interpolate import interp1d
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from scipy.interpolate import griddata
import scipy.optimize
from numpy import NaN, Inf, arange, isscalar, asarray, array
import sys
from timer import timer
import os


# Obtain intermittency factor from an undisturbed and specific wall pressure
def Intermittency(sigma, Pressure0, WallPre, TimeZone):
    # AvePre    = np.mean(WallPre)
    AvePre = np.mean(Pressure0)
    # wall pressure standard deviation of undisturbed BL
    threshold = AvePre+3*sigma
    # Alternative approximate method
    # DynamicP = 0.5*0.371304*469.852**2, ratio = 0.006/(1+0.13*1.7**2)**0.64
    # sigma1 = DynamicP*ratio
    # threshold value for turbulence
    sign = np.zeros(np.size(WallPre))
    ind = np.where(WallPre > threshold)[0]
    sign[ind] = 1.0
    # sign = (WallPre-threshold)/abs(WallPre-threshold)
    # sign      = np.maximum(0, sign[:])
    gamma = np.trapz(sign, TimeZone)/(TimeZone[-1]-TimeZone[0])
    return gamma


# Obtain skewness coefficient corresponding to intermittency factor
def Alpha3(WallPre):
    AvePre = np.mean(WallPre)
    sigma = np.std(WallPre)
    n = np.size(WallPre)
    temp1 = np.power(WallPre-AvePre, 3)
    alpha = np.sum(temp1)/n/np.power(sigma, 3)
    return alpha


# Obtain nondimensinal dynamic viscosity
def Viscosity(Re_delta, T):
    # nondimensional T
    mu = 1.0/Re_delta*np.power(T, 0.75)
    return mu


# Obtain skin friction coefficency
def SkinFriction(mu, du, dy): 
    # all variables are nondimensional
    Cf = 2*mu*du/dy
    return Cf


# obtain Power Spectral Density
def PSD(VarZone, dt, Freq_samp, opt=2):
    TotalNo = np.size(VarZone)
    if (Freq_samp > 1/dt):
        warnings.warn("PSD results are not accurate due to too few snapshots",
                      UserWarning)
    elif (Freq_samp == 1/dt):
        Var = VarZone
    else:                 
        TimeSpan = np.arange(0, np.size(VarZone) * dt, dt)
        TotalNo = int((TimeSpan[-1]-TimeSpan[0]) * Freq_samp) + 1
        TimeZone = np.linspace(TimeSpan[0], TimeSpan[-1], TotalNo)
        VarZone  = VarZone - np.mean(VarZone )
        # interpolate data to make sure time-equaled distribution
        Var = np.interp(TimeZone, TimeSpan, VarZone) # time space must be equal   
    # POD, fast fourier transform and remove the half
    if opt == 2:
        Var_fft = np.fft.rfft(Var)[1:] # remove value at 0 frequency
        Var_psd = np.abs(Var_fft)**2/(Freq_samp*TotalNo)
        num = np.size(Var_fft)
        Freq = np.linspace(Freq_samp/TotalNo, Freq_samp/2, num)
    if opt == 1:
        Freq, Var_psd = signal.welch(Var, fs=Freq_samp, nperseg=int(TotalNo/2),
                                     nfft=TotalNo)
        Freq = Freq[1:]
        Var_psd = Var_psd[1:]
    return (Freq, Var_psd)


# Obtain Frequency-Weighted Power Spectral Density
def FW_PSD(VarZone, dt, Freq_samp, opt=2):
    Freq, Var_PSD = PSD(VarZone, dt, Freq_samp, opt=opt)
    FPSD = Var_PSD * Freq
    return (Freq, FPSD)


# Obtain cross-power sepectral density
def Cro_PSD(Var1, Var2, dt, Freq_samp, opt=1):
    TotalNo = np.size(Var1)
    if (np.size(Var1) != np.size(Var2)):
        warnings.warn("Check the size of input varable 1 & 2", UserWarning)
    if (Freq_samp > 1/dt):
        warnings.warn("PSD results are not accurate due to too few snapshots",
                      UserWarning)
    elif (Freq_samp == 1/dt):
        NVar1 = Var1
        NVar2 = Var2
    else:
        TimeSpan = np.arange(0, np.size(Var1)*dt, dt)
        TotalNo = int((TimeSpan[-1]-TimeSpan[0]) * Freq_samp) + 1
        TimeZone = np.linspace(TimeSpan[0], TimeSpan[-1], TotalNo)
        VarZone1 = Var1 - np.mean(Var1)
        VarZone2 = Var2 - np.mean(Var2)
        NVar1 = np.interp(TimeZone, TimeSpan, VarZone1) # time space must be equal
        NVar2 = np.interp(TimeZone, TimeSpan, VarZone2) # time space must be equal
    if opt == 1:
        Freq, Cpsd = signal.csd(NVar1, NVar2, Freq_samp, nperseg=int(TotalNo/2), 
                                nfft=TotalNo)
        Freq = Freq[1:]
        Cpsd = Cpsd[1:]
    if opt == 2:
        Var1_fft = np.fft.rfft(NVar1)[1:]
        Var2_fft = np.fft.rfft(NVar2)[1:]
        Cpsd = Var1_fft*Var2_fft
        num = np.size(Var1_fft)
        Freq = np.linspace(Freq_samp / TotalNo, Freq_samp / 2, num)
    return (Freq, Cpsd)


def Coherence(Var1, Var2, dt, Freq_samp, opt=1):
    TotalNo = np.size(Var1)
    if (np.size(Var1) != np.size(Var2)):
        warnings.warn("Check the size of input varable 1 & 2", UserWarning)
    if (Freq_samp > 1/dt):
        warnings.warn("PSD results are not accurate due to too few snapshots",
                      UserWarning)
    elif (Freq_samp == 1/dt):
        NVar1 = Var1
        NVar2 = Var2
    else:                 
        TimeSpan = np.arange(0, np.size(Var1) * dt, dt)
        TotalNo = int((TimeSpan[-1]-TimeSpan[0]) * Freq_samp) + 1
        TimeZone = np.linspace(TimeSpan[0], TimeSpan[-1], TotalNo)
        VarZone1 = Var1 - np.mean(Var1)
        VarZone2 = Var2 - np.mean(Var2)
        NVar1 = np.interp(TimeZone, TimeSpan, VarZone1) # time space must be equal
        NVar2 = np.interp(TimeZone, TimeSpan, VarZone2) # time space must be equal
    if opt == 1:
        Freq, gamma = signal.coherence(NVar1, NVar2, fs=Freq_samp, 
                                       nperseg=int(TotalNo/2), nfft=TotalNo)
        Freq = Freq[1:]
        gamma = gamma[1:]
    if opt == 2:
        Freq, cor = Cro_PSD(NVar1, NVar2, dt, Freq_samp)
        psd1 = PSD(NVar1, dt, Freq_samp)[1]
        psd2 = PSD(NVar2, dt, Freq_samp)[1]
        gamma = abs(cor)**2 / psd1 / psd2
    return (Freq, gamma)


# Obtain the standard law of wall (turbulence)
def StdWallLaw():
    ConstK = 0.41
    ConstC = 5.2
    yplus1 = np.arange(1, 15, 0.1) # viscous sublayer velocity profile
    uplus1 = yplus1
    yplus2 = np.arange(3, 1000, 0.1) # logarithm layer velocity profile
    uplus2 = 1.0/ConstK*np.log(yplus2)+ConstC
    UPlus1 = np.column_stack((yplus1, uplus1))
    UPlus2 = np.column_stack((yplus2, uplus2))
    return(UPlus1, UPlus2)


# Draw reference experimental data of turbulence
# 0y/\delta_{99}, 1y+, 2U+, 3urms+, 4vrms+, 5wrms+, 6uv+, 7prms+, 8pu+,
# 9pv+, 10S(u), 11F(u), 12dU+/dy+, 13V+, 14omxrms^+, 15omyrms^+, 16omzrms^+
def ExpWallLaw(Re_theta):
    if isinstance(Re_theta, str):
        ExpData = np.loadtxt ("vel_"+Re_theta+"_dns.prof", skiprows = 14)
    else:
        sys.exit('Re_theta must be a string!!!')
    m, n = ExpData.shape
    y_delta = ExpData[:, 0]
    y_plus = ExpData[:, 1]
    u_plus = ExpData[:, 2]
    urms_plus = ExpData[:, 3]
    vrms_plus = ExpData[:, 4]
    wrms_plus = ExpData[:, 5]
    uv_plus = ExpData[:, 6]
    UPlus = np.column_stack((y_plus, u_plus))
    UVPlus = np.column_stack((y_plus, uv_plus))
    UrmsPlus = np.column_stack((y_plus, urms_plus))
    VrmsPlus = np.column_stack((y_plus, vrms_plus))
    WrmsPlus = np.column_stack((y_plus, wrms_plus))
    return(UPlus, UVPlus, UrmsPlus, VrmsPlus, WrmsPlus)


def UTau(walldist, u, rho, mu):
    rho_wall= rho[1]
    mu_wall = mu[1]
    tau_wall = mu_wall*u[1]/walldist[1]
    u_tau = np.sqrt(np.abs(tau_wall/rho_wall))
    return u_tau


# This code validate boundary layer profile by
# incompressible, Van Direst transformed
# boundary profile from mean reults
def DirestWallLaw(walldist, u, rho, mu):
    if((np.diff(walldist) < 0.0).any()):
        sys.exit("the WallDist must be in ascending order!!!")
    m = np.size(u)
    rho_wall= rho[1]
    mu_wall = mu[1]
    u_tau = UTau(walldist, u, rho, mu)
    u_van = np.zeros(m)
    for i in range(m):
        u_van[i] = np.trapz(rho[:i+1]/rho_wall, u[:i+1])
    u_plus_van = u_van/u_tau
    y_plus = u_tau*walldist*rho_wall/mu_wall
    # return(y_plus, u_plus_van)
    UPlusVan = np.column_stack((y_plus, u_plus_van))
    return(UPlusVan)


# Obtain reattachment location with time
def ReattachLoc(InFolder, OutFolder, timezone):
    dirs = sorted(os.listdir(InFolder))
    data = pd.read_hdf(InFolder + dirs[0])
    NewFrame = data.query("x>=9.0 & x<=13.0 & y==-2.99703717231750488")
    ind = NewFrame.index.values
    # timezone = np.arange(600, 999.5 + 0.5, 0.5)
    xarr = np.zeros(np.size(timezone))
    # xzone = np.linspace(-40.0, 70.0, 111)
    with timer("Computing reattaching point"):
        for i in range(np.size(dirs)):
            frame = pd.read_hdf(InFolder + dirs[i])
            frame = frame.iloc[ind]
            xarr[i] = frame.loc[frame['u'] >= 0.0, 'x'].head(1)
    reatt = np.vstack((timezone, xarr)).T
    np.savetxt(
        OutFolder + "Reattach.dat",
        reatt,
        fmt='%.8e',
        delimiter='  ',
        header="t, x")


# Obtain shock location inside the boudary layer with time
def ShockFoot(InFolder, OutFoler, timepoints, yval, var):
    dirs = sorted(os.listdir(InFolder))
    data = pd.read_hdf(InFolder + dirs[0])
    xarr = np.zeros(np.size(timezone))
    if (np.size(timepoints) != np.size(dirs)):
        sys.exit('The input snapshots does not match!!!')
    with timer("Computing shock foot location"):
        for i in range(np.size(dirs)):
            frame = pd.read_hdf(InFolder + dirs[i])
            NewFrame = frame.loc[frame['y']==yval]
            temp = NewFrame.loc[NewFrame['u'] >= var, 'x']
            xarr[i] = temp.head(1)
    foot = np.vstack((timezone, xarr)).T
    np.savetxt(
        OutFolder + "ShockFoot.dat",
        foot,
        fmt='%.8e',
        delimiter='  ',
        header="t, x")


# Obtain shock location outside boundary layer with time
def ShockLoc(InFolder, OutFolder, timepoints):
    dirs = sorted(os.listdir(InFolder))
    # fig1, ax1 = plt.subplots(figsize=(10, 4))
    # ax1.set_xlim([0.0, 30.0])
    # ax1.set_ylim([-3.0, 10.0])
    # matplotlib.rc('font', size=textsize)
    data = pd.read_hdf(InFolder + dirs[0])
    x0 = np.unique(data['x'])
    x1 = x0[x0 > 10.0]
    x1 = x1[x1 <= 30.0]
    y0 = np.unique(data['y'])
    y1 = y0[y0 > -2.5]
    xini, yini = np.meshgrid(x1, y1)
    corner = (xini < 0.0) & (yini < 0.0)
    shock1 = np.empty(shape=[0, 3])
    shock2 = np.empty(shape=[0, 3])
    ys1 = 0.0
    ys2 = 5.0
    if np.size(timepoints) != np.size(dirs):
        sys.exit('The input snapshots does not match!!!')
    for i in range(np.size(dirs)):
        with timer('Shock position at ' + dirs[i]):
            frame = pd.read_hdf(InFolder + dirs[i])
            gradp = griddata((frame['x'], frame['y']), frame['|gradp|'],
                             (xini, yini))
            gradp[corner] = np.nan
            cs = ax1.contour(
                xini, yini, gradp, levels=0.06, linewidths=1.2, colors='gray')
            xycor = np.empty(shape=[0, 2])
            for isoline in cs.collections[0].get_paths():
                xy = isoline.vertices
                xycor = np.append(xycor, xy, axis=0)
                ax1.plot(xy[:, 0], xy[:, 1], 'r:')
            ind1 = np.where(np.around(xycor[:, 1], 8) == ys1)[0]
            x1 = np.mean(xycor[ind1, 0])
            shock1 = np.append(shock1, [[timepoints[i], x1, ys1]], axis=0)
            ind2 = np.where(np.around(xycor[:, 1], 8) == ys2)[0]
            x2 = np.mean(xycor[ind2, 0])
            shock2 = np.append(shock2, [[timepoints[i], x2, ys2]], axis=0)
            ax1.plot(x1, ys1, 'g*')
            ax1.axhline(y=ys1)
            ax1.plot(x2, ys2, 'b^')
            ax1.axhline(y=ys2)
    np.savetxt(
        OutFolder + "ShockA.dat",
        shock1,
        fmt='%.8e',
        delimiter='  ',
        header="t, x, y")
    np.savetxt(
        OutFolder + "ShockB.dat",
        shock2,
        fmt='%.8e',
        delimiter='  ',
        header="t, x, y")


def Correlate(x, y, method='Sample'):
    if method == 'Population':
        sigma1 = np.std(x, ddof=0)
        sigma2 = np.std(y, ddof=0) # default population standard deviation
        sigma12 = np.cov(x, y, ddof=0)[0][1] # default sample standard deviation
        correlation = sigma12/sigma1/sigma2
    else:
        sigma1 = np.std(x, ddof=1)
        sigma2 = np.std(y, ddof=1) # default population standard deviation
        sigma12 = np.cov(x, y, ddof=1)[0][1] # default sample standard deviation
        correlation = sigma12/sigma1/sigma2
    return correlation


# Vorticity: omega=delta*v
# omega1 = dw/dy-dv/dz; omega2 = du/dz-dw/dx, omega3 = dv/dx-du/dy
def Vorticity():
    return 0

if __name__ == "__main__":
    InFolder = "/media/weibo/Data1/BFS_M1.7L_0505/Snapshots/Snapshots1/"
    OutFolder = "/media/weibo/Data1/BFS_M1.7L_0505/DataPost/Data/"
    timezone = np.arange(600, 999.5 + 0.5, 0.5)
    ShockFoot(InFolder, OutFolder, timezone, -1.875, 0.8)
"""
    InFolder = "/media/weibo/Data1/BFS_M1.7L_0505/Snapshots/Snapshots1/"
    OutFolder = "/media/weibo/Data1/BFS_M1.7L_0505/DataPost/Data/"
    path2 = "/media/weibo/Data1/BFS_M1.7L_0505/"
    numsize = 14
    textsize = 18
    #%%  Plot reattachment point with time
    #spl = splrep(timezone, xarr, s=0.35)
    #xarr1 = splev(timezone[0::5], spl)
    reatt = np.loadtxt(OutFolder+"Reattach.dat", skiprows=1)
    timezone = reatt[:, 0]
    Xr = reatt[:, 1]

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
    ax.set_xlabel(r'$f\delta_0/u_\infty$', fontsize=textsize)
    ax.set_ylabel('Weighted PSD, unitless', fontsize=textsize)
    ax.grid(b=True, which='both', linestyle=':')
    Fre, FPSD = FW_PSD(Xr, 0.5, 2.0)
    Fre1, psd1 = PSD(Xr, 0.5, 2.0, opt=2)
    ax.semilogx(Fre, FPSD, 'k', linewidth=1.0)
    ax.yaxis.offsetText.set_fontsize(numsize)
    plt.tick_params(labelsize=numsize)
    plt.tight_layout(pad=0.5, w_pad=0.8, h_pad=1)
    plt.savefig(path2+'XrFWPSD.svg', bbox_inches='tight', pad_inches=0.1)
    plt.show()

    shock1 = np.loadtxt(OutFolder+"Shock1.dat", skiprows=1)
    shock2 = np.loadtxt(OutFolder+"Shock2.dat", skiprows=1)
    angle = np.arctan(5/(shock2[:, 1]-shock1[:, 1]))
    foot = shock2[:, 1] - 8.0/np.tan(angle)
    Xs = foot
    #Xs = angle*180/np.pi #shock2[:, 1]

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
    ax.yaxis.major.formatter.set_powerlimits((0, 3))
    ax.set_xlabel(r'$f\delta_0/u_\infty$', fontsize=textsize)
    ax.set_ylabel ('Weighted PSD, unitless', fontsize=textsize)
    ax.grid(b=True, which='both', linestyle=':')
    Fre1, FPSD1 = FW_PSD(Xs, 0.5, 2.0)
    Fre2, psd2 = PSD(Xs, 0.5, 2.0, opt=2)
    ax.semilogx(Fre, FPSD1, 'k', linewidth=1.0)
    ax.yaxis.offsetText.set_fontsize(numsize)
    plt.tick_params(labelsize=numsize)
    plt.tight_layout(pad=0.5, w_pad=0.8, h_pad=1)
    plt.savefig(path2+'ShockangleFWPSD.svg', bbox_inches='tight', pad_inches=0.1)
    plt.show()

    fre, cor = Cro_PSD(Xr, Xs, 0.5, 2.0)
    phase = np.arctan(cor.imag, cor.real)
    fre, gam = Coherence(Xr, Xs, 0.5, 2.0)
    fre1, gam1 = Coherence(Xr, Xs, 0.5, 2.0, opt=2)

    fre1 = fre1[1:]
    gam1 = gam1[1:]

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
    ax.yaxis.major.formatter.set_powerlimits((0, 3))
    ax.set_xlabel(r'$f\delta_0/u_\infty$', fontsize=textsize)
    ax.set_ylabel ('Weighted PSD, unitless', fontsize=textsize)
    ax.grid(b=True, which='both', linestyle=':')
    # Fre3, PSD3 = signal.welch(Xs, fs=2.0, nperseg=800, scaling='density')
    Fre3, PSD3 = PSD(Xr, 0.5, 2.0, opt=1)
    FPSD3 = Fre3*PSD3
    ax.semilogx(Fre3, FPSD3, 'k', linewidth=1.0)
    ax.yaxis.offsetText.set_fontsize(numsize)
    plt.tick_params(labelsize=numsize)
    plt.tight_layout(pad=0.5, w_pad=0.8, h_pad=1)
    plt.savefig(path2+'test.svg', bbox_inches='tight', pad_inches=0.1)
    plt.show()
"""

# Fs = 1000
# t = np.arange(0.0, 1-1.0/Fs, 1/Fs)
# var = np.cos(2*3.14159265*100*t)+np.random.uniform(-1, 1, np.size(t))
# Var_fft = np.fft.fft(var)
# Var_fftr = np.fft.rfft(var)
# Var_psd = abs(Var_fft)**2
# Var_psd1 = Var_psd[:int(np.size(t)/2)]
# Var_psd2 = abs(Var_fftr)**2
# fre1, Var_psd3 = PSD(var, t, Fs)
# num = np.size(Var_psd1)
# freq = np.linspace(Fs/2/num, Fs/2, num)
# f, fpsd = FW_PSD(var, t, Fs)
# #fre, psd = PSD(var, t, Fs)
# #plt.plot(fre1, 10*np.log10(Var_psd3))
# fig2, ax2 = plt.subplots()
# ax2.plot(f, fpsd)
# plt.show()

# fig, ax = plt.subplots()
# ax.psd(var, 500, Fs)
# plt.show()
