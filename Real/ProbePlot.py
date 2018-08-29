#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 12 18:58:21 2017
    This code for post-processing data from instantaneous/time-average plane
    data, need data file.                                                                   
@author: weibo
"""
#%%
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from scipy.interpolate import interp1d
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, ScalarFormatter
from scipy.interpolate import griddata
from scipy.interpolate import spline
from scipy import integrate
import sys
from DataPost import DataPost
import FlowVar as fv

plt.close ("all")
plt.rc('text', usetex=True)
font0 = {'family' : 'Times New Roman',
        'color' : 'k',
        'weight' : 'normal',
        'size' : 12,
        }
font1 = {'family' : 'Times New Roman',
        'color' : 'k',
        'weight' : 'normal',
        'size' : 14,}

font2 = {'family' : 'Times New Roman',
         'color' : 'k',
         'weight' : 'normal',
         'size' : 16,
        }

font3 = {'family' : 'Times New Roman',
        'color' : 'k',
        'weight' : 'normal',
        'size' : 18,
}

path = "/media/weibo/Data1/BFS_M1.7L_0505/DataPost/"
path1 = "/media/weibo/Data1/BFS_M1.7L_0505/probes/"
path2 = "/media/weibo/Data1/BFS_M1.7L_0505/DataPost/"
path3 = "/media/weibo/Data1/BFS_M1.7L_0505/DataPost/"
matplotlib.rcParams['xtick.direction'] = 'in'
matplotlib.rcParams['ytick.direction'] = 'in'

texsize = 18
labsize = 14
t0 = 499.07144
t1 = 500 #960
t2 = 920.0 #

#%% Read data for Streamwise variations of frequency of a specific variable
Probe0 = DataPost()
xloc = [-40.0, 3.481, 11.0, 60.0]
yloc = [0.0, -0.943, -3.0, -3.0]
Probe0.LoadProbeData(xloc[0], yloc[0], 0.0, path1, Uniq=True)
Probe0.ExtraSeries('time', t1, t2)
#Probe0.AveAtSameXYZ('All')
#time1 = Probe0.time
Probe10 = DataPost()
Probe10.LoadProbeData(xloc[1], yloc[1], 0.0, path1, Uniq=True)
#Probe10.unique_rows()
Probe10.ExtraSeries('time', t1, t2)
#Probe10.AveAtSameXYZ('All')
Probe20 = DataPost()
Probe20.LoadProbeData(xloc[2], yloc[2], 0.0, path1, Uniq=True)
#Probe20.unique_rows()
Probe20.ExtraSeries('time', t1, t2)
#Probe20.AveAtSameXYZ('All')
#time2 = Probe20.time
Probe30 = DataPost()
Probe30.LoadProbeData(xloc[3], yloc[3], 0.0, path1, Uniq=True)
#Probe30.unique_rows()
Probe30.ExtraSeries('time', t1, t2)
#Probe30.AveAtSameXYZ('All')


#%% Streamwise variations of time evolution of a specific variable
fa = 1.7*1.7*1.4
fig = plt.figure(figsize=(12, 6))
matplotlib.rc('font', size=14)
ax = fig.add_subplot(411)
xlabel = r'$x/\delta_0={}, \ y/\delta_0={}$'
ytitle = r'$p/p_\infty$'
var = 'p'
ax.set_title(xlabel.format(xloc[0], yloc[0]), fontdict=font1)
ax.set_xlim([t1, t2])
ax.set_ylim([0.99, 1.01])
ax.set_xticklabels('')
#ax.set_xlabel (r'$t u_\infty/\delta$', fontdict = font1)
ax.set_ylabel(ytitle, fontdict=font3)
#ax.ticklabel_format(axis='y', style='sci', useOffset=False, scilimits=(-2, 2))
ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
#ax.text (850, 6.5, 'x=0', fontdict = font2)
ax.grid(b=True, which='both', linestyle=':')
#Probe0P = Probe0.p-BProbe0P
#grow0, time0 = Probe0.GrowthRate(Probe0.time, Probe0P)
#ax.plot (time0, grow0, 'k', linewidth = 1.5)
#Probe0.AddUGrad(0.015625)
ax.plot(Probe0.time, getattr(Probe0, var)*fa, 'k', linewidth=1.0)
ax.annotate("(a)", xy=(-0.05, 1.12), xycoords='axes fraction', fontsize=labsize)
plt.tick_params(labelsize=14)
# fit curve
def func(t, A, B):
    return A / t + B
popt, pcov = Probe0.fit_func(func, Probe0.time, getattr(Probe0, var), guess=None)
A, B = popt
fitfunc = lambda t: A / t + B
#ax.plot(Probe0.time, fitfunc(Probe0.time), 'b', linewidth=1.5)


ax = fig.add_subplot(412)
ax.set_title(xlabel.format(xloc[1], yloc[1]), fontdict=font1)
ax.set_xlim([t1, t2])
ax.set_xticklabels('')
ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
ax.set_ylabel(ytitle, fontdict = font3)
ax.grid(b=True, which='both', linestyle = ':')
#Probe10P = Probe10.p-BProbe10P
#grow10, time10 = Probe10.GrowthRate(Probe10.time, Probe10P)
#ax.plot (time10, grow10, 'k', linewidth = 1.5)
#Probe10.AddUGrad(0.015625)
ax.plot(Probe10.time, getattr(Probe10, var)*fa, 'k', linewidth=1.0)
ax.annotate("(b)", xy=(-0.05, 1.10), xycoords='axes fraction', fontsize=labsize)
plt.tick_params(labelsize=14)

ax = fig.add_subplot(413)
ax.set_title(xlabel.format(xloc[2], yloc[2]), fontdict=font1)
ax.set_xlim([t1, t2])
ax.set_xticklabels('')
ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
ax.set_ylabel(ytitle, fontdict=font3)
ax.grid(b=True, which ='both', linestyle =':')
#Probe20P = Probe20.p-BProbe20P
#grow20, time20 = Probe20.GrowthRate(Probe20.time, Probe20P)
#ax.plot (time20, grow20, 'k', linewidth = 1.5)
#Probe20.AddUGrad(0.015625)
ax.plot(Probe20.time, getattr(Probe20, var)*fa, 'k', linewidth=1.0)
ax.annotate("(c)", xy=(-0.05, 1.10), xycoords='axes fraction', fontsize=labsize)
plt.tick_params(labelsize=14)

ax = fig.add_subplot(414)
ax.set_title(xlabel.format(xloc[3], yloc[3]), fontdict=font1)
ax.set_xlim([t1, t2])
#ax.set_xticklabels ('')
ax.set_xlabel(r'$t u_\infty/\delta_0$', fontdict=font3)
ax.set_ylabel(ytitle, fontdict=font3)
#ax.text (850, 6.5, 'x=0', fontdict = font2)
ax.grid(b=True, which='both', linestyle=':')
#Probe40P = Probe40.p-BProbe40P
#grow40, time40 = Probe40.GrowthRate(Probe40.time, Probe40P)
#Probe30.AddUGrad(0.015625)
ax.plot(Probe30.time, getattr(Probe30, var)*fa, 'k', linewidth=1.0)
ax.annotate("(d)", xy=(-0.05, 1.10), xycoords='axes fraction', fontsize=labsize)
#ax.plot (Probe40.time, Probe40.p, 'k', linewidth = 1.5)
plt.tick_params(labelsize=14)
plt.rc('text', usetex=True)
plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=1)
plt.savefig (path3+'StreamwiseTimeEvolution.svg', bbox_inches='tight')
plt.show()


#%% Frequency Weighted Power Spectral Density
Freq_samp = 50
fig = plt.figure(figsize=(12,10))
matplotlib.rc('font', size=14)
ax = fig.add_subplot(221)
ax.set_title(xlabel.format(xloc[0], yloc[0]), fontdict=font1)
#ax.set_xlim ([720, 960])
#ax.set_xticklabels ('')
ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
#ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
#ax = plt.gca()
#ax.yaxis.get_major_formatter().set_powerlimits((0,1))
ax.set_ylabel('WPSD, unitless', fontdict=font3)
ax.grid(b=True, which='both', linestyle=':')
#Fre0, FPSD0 = fv.FW_PSD(getattr(Probe0, var), Probe0.time, Freq_samp)
Fre0, FPSD0 = fv.FW_PSD(getattr(Probe0, var)-fitfunc(Probe0.time), Probe0.time, Freq_samp)
ax.semilogx(Fre0, FPSD0, 'k', linewidth=1.0)
ax.annotate("(a)", xy=(-0.05, 1.04), xycoords='axes fraction', fontsize=labsize)
plt.tick_params(labelsize=labsize)
#ax.psd(Probe0.p-np.mean(Probe0.p), 100, 10)
ax = fig.add_subplot(222)
ax.set_title(xlabel.format(xloc[1], yloc[1]), fontdict=font1)
#ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
#ax.set_xlabel (r'$f\delta_0/U_\infty$', fontdict = font1)
#ax.set_ylabel ('Weighted PSD, unitless', fontdict = font1)
ax.grid(b=True, which='both', linestyle=':')
Fre10, FPSD10 = fv.FW_PSD (getattr(Probe10, var), Probe10.time, Freq_samp)
ax.semilogx(Fre10, FPSD10, 'k', linewidth=1.0)
ax.annotate("(b)", xy=(-0.05, 1.04), xycoords='axes fraction', fontsize=labsize)
plt.tick_params(labelsize=labsize)

ax = fig.add_subplot(223)
ax.set_title(xlabel.format(xloc[2], yloc[2]), fontdict=font1)
#ax.set_xlim ([720, 960])
#ax.set_xticklabels ('')
ax.ticklabel_format(axis='y', style='sci', scilimits=(-1, 2))
ax.set_xlabel(r'$f\delta_0/u_\infty$', fontdict=font3)
ax.set_ylabel('WPSD, unitless', fontdict=font3)
ax.grid(b=True, which='both', linestyle=':')
Fre20, FPSD20 = fv.FW_PSD(getattr(Probe20, var), Probe20.time, Freq_samp)
ax.semilogx (Fre20, FPSD20, 'k', linewidth = 1.0)
ax.annotate("(c)", xy=(-0.05, 1.04), xycoords='axes fraction', fontsize=labsize)
plt.tick_params(labelsize=labsize)

ax = fig.add_subplot(224)
ax.set_title(xlabel.format(xloc[3], yloc[3]), fontdict=font1)
#ax.set_xlim ([720, 960])
#ax.set_xticklabels ('')
ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
#ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
ax.set_xlabel(r'$f\delta_0/u_\infty$', fontdict=font3)
#ax.set_ylabel ('Weighted PSD, unitless', fontdict = font1)
ax.grid(b=True, which='both', linestyle=':')
Fre30, FPSD30 = fv.FW_PSD(getattr(Probe30, var), Probe30.time, Freq_samp)
ax.semilogx(Fre30, FPSD30, 'k', linewidth=1.0)
ax.annotate("(d)", xy=(-0.05, 1.04), xycoords='axes fraction', fontsize=labsize)
plt.tick_params(labelsize=labsize)
plt.tight_layout(pad=0.5, w_pad=0.8, h_pad=1)
plt.savefig (path3+'StreamwiseFWPSD.svg', bbox_inches='tight')
plt.show()

#%% Compute intermittency factor
xzone = np.linspace(-40.0, 40.0, 41)
gamma = np.zeros(np.size(xzone))
alpha = np.zeros(np.size(xzone))
sigma = np.std(Probe0.p)
p0    = Probe0.p
ProbeID = DataPost()
for j in range(np.size(xzone)):
    if xzone[j] <= 0.0:
        ProbeID.LoadProbeData(xzone[j], 0.0, 0.0, path1)
    else:
        ProbeID.LoadProbeData(xzone[j], -3.0, 0.0, path1)
    ProbeID.ExtraSeries('time', t1, t2)
    gamma[j] = fv.Intermittency(sigma, p0, ProbeID.p, ProbeID.time)
    alpha[j] = fv.Alpha3(ProbeID.p)

fig3, ax3 = plt.subplots(figsize=(4, 3.5))
ax3.plot(xzone, gamma, 'ko')
ax3.set_xlabel (r'$x/\delta_0$', fontdict=font3)
ax3.set_ylabel (r'$\gamma$', fontdict=font3)
#ax3.set_ylim([0.0, 1.0])
ax3.grid(b=True, which = 'both', linestyle = ':')
ax3.axvline(x=0.0, color='k', linestyle='--', linewidth=1.0)
ax3.axvline(x=12.7, color='k', linestyle='--', linewidth=1.0)
plt.tight_layout(pad = 0.5, w_pad=0.5, h_pad =0.3)
plt.tick_params(labelsize=14)
plt.savefig (path3+'IntermittencyFactor.svg', dpi = 300)
plt.show()

#%% Skewness coefficient
fig4, ax4 = plt.subplots()
ax4.plot(gamma, alpha, 'ko')
ax4.set_xlabel (r'$\gamma$', fontdict = font3)
ax4.set_ylabel (r'$\alpha_3$', fontdict = font3)
#ax3.set_ylim([0.0, 1.0])
ax4.grid (b=True, which = 'both', linestyle = ':')
#ax4.axvline(x=0.0, color='k', linestyle='--', linewidth=1.0)
#ax4.axvline(x=12.7, color='k', linestyle='--', linewidth=1.0)
plt.tight_layout(pad = 0.5, w_pad = 0.2, h_pad = 1)
fig4.set_size_inches(6, 5, forward=True)
plt.savefig (path3+'SkewnessCoeff.svg', dpi = 300)
plt.show()
