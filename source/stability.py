#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 15:22:31 2018
    This code for plotting line/curve figures

@author: weibo
"""
# %% Load necessary module
import numpy as np
import pandas as pd
import plt2pandas as p2p
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.ticker as ticker
from scipy.interpolate import interp1d, splev, splrep
from scipy import signal
from data_post import DataPost
import variable_analysis as fv
from timer import timer
import sys
import os
from planar_field import PlanarField as pf
from triaxial_field import TriField as tf

plt.close("All")
plt.rc("text", usetex=True)
font = {
    "family": "Times New Roman",  # 'color' : 'k',
    "weight": "normal",
    "size": "large",
}

path = "/media/weibo/VID2/BFS_M1.7L/"
pathP = path + "probes/"
pathF = path + "Figures/"
pathM = path + "MeanFlow/"
pathS = path + "SpanAve/"
pathT = path + "TimeAve/"
pathI = path + "Instant/"

matplotlib.rcParams["xtick.direction"] = "in"
matplotlib.rcParams["ytick.direction"] = "in"
textsize = 15
numsize = 12
matplotlib.rc("font", size=textsize)

VarName = [
    "x",
    "y",
    "z",
    "u",
    "v",
    "w",
    "rho",
    "p",
    "T",
    "Q-criterion",
    "L2-criterion",
]

StepHeight = 3.0
MeanFlow = pf()
MeanFlow.load_meanflow(path)
MeanFlow.add_walldist(StepHeight)
stat = MeanFlow.PlanarData

# %% save dividing line coordinates
dividing = np.loadtxt(pathM + "BubbleLine.dat", skiprows=1)[:-2, :]
x2 = np.arange(dividing[-1, 0], 50.0+0.125, 0.125)
y2 = np.ones(np.size(x2))*(-2.99342)
x3 = np.concatenate((dividing[:,0], x2), axis=0)
y3 = np.concatenate((dividing[:,1], y2), axis=0) # streamline
xx = np.zeros(np.size(x3))
yy = np.zeros(np.size(y3))
frame1 = stat.loc[stat['z'] == 0, ['x', 'y']]
frame2 = frame1.query("x>=0.0 & y<=3.0")
xmesh = frame2['x'].values
ymesh = frame2['y'].values
for i in range(np.size(x3)):
    variance = np.sqrt(np.square(xmesh - x3[i]) + np.square(ymesh - y3[i]))
    idx = np.where(variance == np.min(variance))[0][0]
    xx[i] = xmesh[idx]
    yy[i] = ymesh[idx]
xy = np.vstack((xx, yy))
strmln = pd.DataFrame(xy.T, columns=['x', 'y'])
strmln = strmln.drop_duplicates(keep='last')
strmln.to_csv(pathM + "BubbleGrid.dat", sep=' ',
              float_format='%1.8e', index=False)

# draw dividing line
fig, ax = plt.subplots(figsize=(6.4, 3.0))
matplotlib.rc('font', size=14)
ax.set_xlabel(r"$x/\delta_0$", fontsize=textsize)
ax.set_ylabel(r"$y/\delta_0$", fontsize=textsize)
ax.plot(xx, yy, 'k')
ax.ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
ax.grid(b=True, which="both", linestyle=":")
plt.show()
plt.savefig(
    pathF + "BubbleGrid.svg", bbox_inches="tight", pad_inches=0.1
)

# %% compute coordinates where the BL profile has Max RMS along streamwise direction
varn = '<u`u`>'
xnew = np.arange(0.0, 40.0+0.125, 0.125)
znew = np.zeros(np.size(xnew))
varv = np.zeros(np.size(xnew))
ynew = np.zeros(np.size(xnew))
for i in range(np.size(xnew)):
    df = fv.max_pert_along_y(stat, '<u`u`>', [xnew[i], znew[i]])
    varv[i] = df[varn]
    ynew[i] = df['y']
data = np.vstack((xnew, ynew, varv))
df = pd.DataFrame(data.T, columns=['x', 'y', varn])
# df = df.drop_duplicates(keep='last')
df.to_csv(pathM + "MaxRMS.dat", sep=' ',
          float_format='%1.8e', index=False)

# draw maximum value curve
fig, ax = plt.subplots(figsize=(6.4, 3.0))
matplotlib.rc('font', size=14)
ax.set_xlabel(r"$x/\delta_0$", fontsize=textsize)
ax.set_ylabel(r"$y/\delta_0$", fontsize=textsize)
ax.plot(xnew, ynew, 'k')
ax.ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
ax.grid(b=True, which="both", linestyle=":")
plt.show()
plt.savefig(
    pathF + "MaxPertLoc.svg", bbox_inches="tight", pad_inches=0.1
)

# %% Plot RMS of velocity on the wall along streamwise direction
loc = ['z', 'y']
val = [0.0, -2.99704]
varnm = '<u`u`>'
pert = fv.pert_at_loc(stat, varnm, loc, val)
fig, ax = plt.subplots(figsize=(6.4, 2.2))
matplotlib.rc('font', size=14)
ax.set_ylabel(r"$\sqrt{u^{\prime 2}}/u_{\infty}$", fontsize=textsize)
ax.set_xlabel(r"$x/\delta_0$", fontsize=textsize)
ax.plot(pert['x'], np.sqrt(pert[varnm]), 'k')
ax.set_xlim([0.0, 30])
ax.ticklabel_format(axis="y", style="sci", scilimits=(-1, 1))
ax.grid(b=True, which="both", linestyle=":")
plt.show()
plt.savefig(
    pathF + "PerturProfileX.svg", bbox_inches="tight", pad_inches=0.1
)

# %% Plot RMS of velocity along wall-normal direction
loc = ['x', 'z']
val = [10.0, 0.0]
pert = fv.pert_at_loc(stat, varnm, loc, val)
fig, ax = plt.subplots(figsize=(6.4, 2.2))
matplotlib.rc('font', size=14)
ax.set_xlabel(r"$u^{\prime}/u_{\infty}$", fontsize=textsize)
ax.set_ylabel(r"$y/\delta_0$", fontsize=textsize)
ax.plot(pert[varnm], pert['y'])
ax.ticklabel_format(axis="x", style="sci", scilimits=(-2, 2))
ax.grid(b=True, which="both", linestyle=":")
plt.show()
plt.savefig(
    pathF + "PerturProfileY.svg", bbox_inches="tight", pad_inches=0.1
)

# %% Plot RMS of velocity along spanwise on the dividing line
# load data method1
#TimeAve = tf()
#TimeAve.load_3data(pathT, FileList=pathT + 'TimeAve.h5', NameList='h5')
#stat3d = TimeAve.TriData
# load data method2
df0 = pd.read_hdf(pathT + 'MeanFlow0.h5')
df1 = pd.read_hdf(pathT + 'MeanFlow1.h5')
df2 = pd.read_hdf(pathT + 'MeanFlow2.h5')
df3 = pd.read_hdf(pathT + 'MeanFlow3.h5')
stat3d = pd.concat([df0, df1, df2, df3], ignore_index=True)
# %% plot
loc = ['x', 'y']
valarr = [[0.0078125, -0.00781],
          [2.5625, -0.43750],
          [5.5625, -1.1875],
          [7.625, -1.4375],
          [11.3125, -1.6875]]
#          [15.0, -1.6875]]

fig, ax = plt.subplots(1, 5, figsize=(6.4, 3.2))
fig.subplots_adjust(top=0.92, bottom=0.08, left=0.1, right=0.9, wspace=0.2)
matplotlib.rc('font', size=14)
title = [r'$(a)$', r'$(b)$', r'$(c)$', r'$(d)$', r'$(e)$']
# a
val = valarr[0]
pert = fv.pert_at_loc(stat3d, varnm, loc, val)
ax[0].plot(np.sqrt(pert[varnm]), pert['z'], 'k-')
ax[0].set_xlim([0.0, 1e-3])
ax[0].ticklabel_format(axis="x", style="sci", scilimits=(-1, 1))
ax[0].set_yticks([-8.0, -4.0, 0.0, 4.0, 8.0])
ax[0].set_ylabel(r"$z/\delta_0$", fontsize=textsize)
ax[0].tick_params(axis='both', labelsize=numsize)
ax[0].set_title(title[0], fontsize=numsize)
ax[0].grid(b=True, which="both", linestyle=":")
ax[0].xaxis.offsetText.set_fontsize(numsize)
# b
val = valarr[1]
pert = fv.pert_at_loc(stat3d, varnm, loc, val)
ax[1].plot(np.sqrt(pert[varnm]), pert['z'], 'k-')
ax[1].set_xlim([1e-2, 3e-2])
ax[1].ticklabel_format(axis="x", style="sci", scilimits=(-2, 2))
ax[1].set_yticklabels('')
ax[1].tick_params(axis='both', labelsize=numsize)
ax[1].set_title(title[1], fontsize=numsize)
ax[1].grid(b=True, which="both", linestyle=":")
ax[1].xaxis.offsetText.set_fontsize(numsize)
# c
val = valarr[2]
pert = fv.pert_at_loc(stat3d, varnm, loc, val)
ax[2].plot(np.sqrt(pert[varnm]), pert['z'], 'k-')
ax[2].set_xlim([0.05, 0.20])
ax[2].set_xlabel(r"$\sqrt{u^{\prime 2}}/u_{\infty}$",
                 fontsize=textsize, labelpad=18.0)
ax[2].ticklabel_format(axis="x", style="sci", scilimits=(-2, 2))
ax[2].set_yticklabels('')
ax[2].tick_params(labelsize=numsize)
ax[2].set_title(title[2], fontsize=numsize)
ax[2].grid(b=True, which="both", linestyle=":")
# d
val = valarr[3]
pert = fv.pert_at_loc(stat3d, varnm, loc, val)
ax[3].plot(np.sqrt(pert[varnm]), pert['z'], 'k-')
ax[3].set_xlim([0.05, 0.20])
ax[3].ticklabel_format(axis="x", style="sci", scilimits=(-2, 2))
ax[3].set_yticklabels('')
ax[3].tick_params(labelsize=numsize)
ax[3].set_title(title[3], fontsize=numsize)
ax[3].grid(b=True, which="both", linestyle=":")
# e
val = valarr[4]
pert = fv.pert_at_loc(stat3d, varnm, loc, val)
ax[4].plot(np.sqrt(pert[varnm]), pert['z'], 'k-')
ax[4].set_xlim([0.05, 0.20])
ax[4].ticklabel_format(axis="x", style="sci", scilimits=(-2, 2))
ax[4].set_yticklabels('')
ax[4].tick_params(labelsize=numsize)
ax[4].set_title(title[4], fontsize=numsize)
ax[4].grid(b=True, which="both", linestyle=":")
plt.show()
plt.savefig(
    pathF + "PerturProfileZ.svg", bbox_inches="tight"
)

# %%############################################################################
"""
    distribution of amplitude & amplication factor along a line
"""
# %% load time sequential snapshots
InFolder = path + 'Slice/TP_2D_Z_03/'
dirs = sorted(os.listdir(InFolder))
DataFrame = pd.read_hdf(InFolder + dirs[0])
grouped = DataFrame.groupby(['x', 'y', 'z'])
DataFrame = grouped.mean().reset_index()
var = 'p' # 'u'
Snapshots = DataFrame[['x', 'y', 'z', 'u', 'p']]

fa = 1.7*1.7*1.4
skip = 2
timepoints = np.arange(700, 999.75 + 0.25, 0.25)
with timer("Load Data"):
    for i in range(np.size(dirs)-1):
        if i % skip == 1:
            TempFrame = pd.read_hdf(InFolder + dirs[i+1])
            grouped = TempFrame.groupby(['x', 'y', 'z'])
            Frame1 = grouped.mean().reset_index()
            Frame2 = Frame1[['x', 'y', 'z', 'u', 'p']]
            if np.shape(Frame1)[0] != np.shape(DataFrame)[0]:
                sys.exit('The input snapshots does not match!!!')
            Snapshots = pd.concat([Snapshots, Frame2])

Snapshots[var] = Snapshots[var] * fa
m, n = np.shape(Snapshots)
dt = 0.5
freq_samp = 2.0


# %% compute amplitude of variable along a line
xynew = np.loadtxt(pathM + "BubbleGrid.dat", skiprows=1)
# xynew = np.loadtxt(pathM + "MaxRMS.dat", skiprows=1)
xval = xynew[:, 0]
yval = xynew[:, 1]
amplit = np.zeros(np.size(xval))
for i in range(np.size(xval)):
    xyz = [xval[i], yval[i], 0.0]
    amplit[i] = fv.amplit(Snapshots, xyz, var)

# %% plot amplitude of variable along a line
fig, ax = plt.subplots(figsize=(6.4, 3))
matplotlib.rc('font', size=14)
ax.set_xlabel(r"$x/\delta_0$", fontsize=textsize)
ax.set_ylabel(r"$A_{u^{\prime}}$", fontsize=textsize)
ax.plot(xval, amplit)
b, a = signal.butter(3, 0.15, btype='lowpass', analog=False)
amplit1 = signal.filtfilt(b, a, amplit)
ax.plot(xval, amplit1, 'r--')
ax.ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
ax.grid(b=True, which="both", linestyle=":")
plt.show()
plt.savefig(
    pathF + var + "_AmplitX.svg", bbox_inches="tight", pad_inches=0.1
)

# %% compute RMS along a line
varnm = '<u`u`>'
loc = ['x', 'y']
uu = np.zeros(np.size(xval))
for i in range(np.size(xval)):
    xyz = [xval[i], yval[i]]
    uu[i] = fv.pert_at_loc(stat, varnm, loc, xyz)[varnm]

# %% draw RMS & amplication factor along streamwise
fig, ax = plt.subplots(figsize=(6.4, 3.0))
matplotlib.rc('font', size=14)
ax.set_xlabel(r"$x/\delta_0$", fontsize=textsize)
ax.set_ylabel(r"$\sqrt{u^{\prime 2}}/u_{\infty}$", fontsize=textsize)
ax.plot(xval, uu, 'k')
ax.set_xlim([-0.5, 20.5])
ax.ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))

ax2 = ax.twinx()
ax2.set_xlabel(r"$x/\delta_0$", fontsize=textsize)
ax2.set_ylabel(r"$A/A_0$", fontsize=textsize)
ax2.set_yscale('log')
ax2.plot(xval[1:], amplit1[1:]/amplit1[0], 'k--')
ax2.set_xlim([-0.5, 20.5])
# ax2.set_ylim([0.8, 100])
ax2.axvline(x=0.6, linewidth=1.0, linestyle='--', color='gray')
ax2.axvline(x=3.2, linewidth=1.0, linestyle='--', color='gray')
ax2.axvline(x=6.5, linewidth=1.0, linestyle='--', color='gray')
ax2.axvline(x=9.7, linewidth=1.0, linestyle='--', color='gray')
ax2.axvline(x=12., linewidth=1.0, linestyle='--', color='gray')
# ax.ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
# ax2.grid(b=True, which="both", linestyle=":")
plt.show()
plt.savefig(
    pathF + var + "GrowRateX.svg", bbox_inches="tight", pad_inches=0.1
)

# %%############################################################################
"""
    RMS distribution along a line, computed from temporal snapshots
"""
# %% Plot RMS map along a line
# compute RMS by temporal sequential data
varnm = 'p'
rms = np.zeros(np.size(xval))
for i in range(np.size(xval)):
    xyz = [xval[i], yval[i], 0.0]
    rms[i] = fv.rms_map(Snapshots, xyz, varnm)

# plot
matplotlib.rcParams['xtick.direction'] = 'in'
matplotlib.rcParams['ytick.direction'] = 'in'
fig, ax = plt.subplots(figsize=(6.4, 3.0))
# ax.yaxis.major.formatter.set_powerlimits((-2, 3))
ax.plot(xval, rms, 'k-')
ax.set_xlim([0.0, 30.0])
ax.set_xlabel(r"$x/\delta_0$", fontsize=textsize)
ax.set_ylabel(r"$\mathrm{RMS}(p^{\prime}/p_{\infty})$", fontsize=textsize)
ax.grid(b=True, which="both", linestyle=":")
ax.axvline(x=10.9, linewidth=1.0, linestyle='--', color='k')
plt.savefig(pathF + var + "_RMSMap.svg", bbox_inches="tight", pad_inches=0.1)
plt.show()

# %%############################################################################
"""
    frequency-weighted PSD along a line
"""
# %% compute
samples = int(np.size(timepoints) / skip / 2 + 1)
FPSD = np.zeros((samples, np.size(xval)))
for i in range(np.size(xval)):
    xyz = [xval[i], yval[i], 0.0]
    freq, FPSD[:, i] = fv.fw_psd_map(Snapshots, xyz, var, dt, freq_samp, opt=1)
freq = freq[1:]
FPSD = FPSD[1:, :]
# %% Plot frequency-weighted PSD map along a line
SumFPSD = np.sum(FPSD, axis=0)
FPSD1 = np.log(FPSD/SumFPSD)
matplotlib.rcParams['xtick.direction'] = 'out'
matplotlib.rcParams['ytick.direction'] = 'out'
fig, ax = plt.subplots(figsize=(8, 3.5))
# ax.yaxis.major.formatter.set_powerlimits((-2, 3))
ax.set_xlabel(r"$x/\delta_0$", fontsize=textsize)
ax.set_ylabel(r"$f\delta_0/u_\infty$", fontsize=textsize)
print(np.max(FPSD1))
print(np.min(FPSD1))
lev = np.linspace(-10, -2, 41)
cbar = ax.contourf(xval, freq, FPSD1, cmap='gray_r', levels=lev)
# every stage of the transition
ax.axvline(x=0.6, linewidth=1.0, linestyle='--', color='k')
ax.axvline(x=3.2, linewidth=1.0, linestyle='--', color='k')
ax.axvline(x=6.5, linewidth=1.0, linestyle='--', color='k')
ax.axvline(x=9.7, linewidth=1.0, linestyle='--', color='k')
ax.axvline(x=12., linewidth=1.0, linestyle='--', color='k')
ax.set_yscale('log')
ax.set_xlim([0.0, 30.0])
rg = np.linspace(-10, -2, 5)
cbar = plt.colorbar(cbar, ticks=rg)
cbar.ax.xaxis.offsetText.set_fontsize(numsize)
cbar.ax.tick_params(labelsize=numsize)
cbar.update_ticks()
barlabel = r'$\log_{10} [f\cdot\mathcal{P}(f)/\int \mathcal{P}(f) \mathrm{d}f]$'
cbar.set_label(barlabel, rotation=90, fontsize=numsize)
plt.tick_params(labelsize=numsize)
plt.tight_layout(pad=0.5, w_pad=0.8, h_pad=1)
plt.savefig(pathF + var + "_FWPSDMap.svg", bbox_inches="tight", pad_inches=0.1)
plt.show()

# %%############################################################################
"""
    boundary layer profile of RMS
"""
# %% plot BL fluctuations profile
varnm = '<u`u`>'
fig, ax = plt.subplots(1, 7, figsize=(6.4, 2.5))
fig.subplots_adjust(top=0.92, bottom=0.08, left=0.1, right=0.9, wspace=0.2)
matplotlib.rc('font', size=14)
title = [r'$(a)$', r'$(b)$', r'$(c)$', r'$(d)$', r'$(e)$']
matplotlib.rcParams['xtick.direction'] = 'in'
matplotlib.rcParams['ytick.direction'] = 'in'
xcoord = np.array([-40, 0, 5, 10, 15, 20, 30])
loc = ['z', 'x']
for i in range(np.size(xcoord)):
    pert = fv.pert_at_loc(stat, varnm, loc, [0.0, xcoord[i]])
    if xcoord[i] > 0.0:
        ax[i].plot(np.sqrt(pert[varnm]), pert['y']+3.0, 'k-')
    else:
        ax[i].plot(np.sqrt(pert[varnm]), pert['y'], 'k-')
    ax[i].set_ylim([0, 4])
    if i != 0:
        ax[i].set_yticklabels('')
    # ax[i].set_xticks([0, 0.5, 1], minor=True)
    ax[i].tick_params(axis='both', which='major', labelsize=numsize-1)
    ax[i].ticklabel_format(axis="x", style="sci", scilimits=(-2, 2))
    ax[i].set_title(r'$x/\delta_0={}$'.format(xcoord[i]),
                    fontsize=numsize-2, y=0.96)
    ax[i].grid(b=True, which="both", linestyle=":")
ax[0].set_ylabel(r"$\Delta y/\delta_0$", fontsize=textsize)
ax[3].set_xlabel(r'$u^{\prime}/u_\infty$', fontsize=textsize)
plt.tick_params(labelsize=numsize)
plt.show()
plt.savefig(
    pathF + "BLProfileRMS.pdf", bbox_inches="tight", pad_inches=0.1
)