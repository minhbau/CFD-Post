#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 18:57:20 2018
    This code for DMD post processing.
@author: weibo
"""
# %% Load necessary module
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from timer import timer
from DMD import DMD
from scipy.interpolate import griddata
import os

plt.close("All")
plt.rc('text', usetex=True)
font = {
    'family': 'Times New Roman',  # 'color' : 'k',
    'weight': 'normal',
}

matplotlib.rc('font', **font)

# %% load data
InFolder = "/media/weibo/Data1/BFS_M1.7L_0505/SpanAve/5/"
SaveFolder = "/media/weibo/Data1/BFS_M1.7L_0505/SpanAve/Test"
path = "/media/weibo/Data1/BFS_M1.7L_0505/DataPost/"
dirs = sorted(os.listdir(InFolder))
DataFrame = pd.read_hdf(InFolder + dirs[0])
NewFrame = DataFrame.query("x>=-5.0 & x<=15.0 & y>=-3.0 & y<=5.0")
#NewFrame = DataFrame.query("x>=9.0 & x<=13.0 & y>=-3.0 & y<=5.0")
ind = NewFrame.index.values
xval = NewFrame['x']
yval = NewFrame['y']
x1 = -5.0
x2 = 15.0
y1 = -3.0
y2 = 5.0
with timer("Load Data"):
    Snapshots = np.vstack(
        [pd.read_hdf(InFolder + dirs[i])['u'] for i in range(np.size(dirs))])
    Snapshots = Snapshots.T
Snapshots = Snapshots[ind, :]
m, n = np.shape(Snapshots)
Snapshots1 = Snapshots[:, :-1]
# %% DMD
timepoints = np.arange(550, 659.5 + 0.5, 0.5)
predmd = DMD(Snapshots)
with timer("DMD computing"):
    eigval, phi = predmd.dmd_standard(fluc='True')

coeff = predmd.dmd_amplitude()
dynamics = predmd.dmd_dynamics(timepoints)
residual = predmd.dmd_residual
print("The residuals of DMD is ", residual)

with timer("Precompute SPDMD amplitudes"):
    predmd.spdmd_amplitude()
# %% SPDMD
gamma = np.logspace(0, 3, 20)
with timer("SPDMD computing"):
    ans = predmd.compute_spdmd(gamma=gamma)
print("The nonzero amplitudes of each gamma:", ans.Nz)
# %% decide the value of gamma to show SPDMD
sp = 15
sp_no = ans.Nz[sp]
sp_gamma = ans.gamma[sp]
sp_ind = np.arange(n-1)[ans.nonzero[:, sp]]
# %% Eigvalue Spectrum
matplotlib.rcParams['xtick.direction'] = 'in'
matplotlib.rcParams['ytick.direction'] = 'in'
matplotlib.rc('font', size=14)
fig1, ax1 = plt.subplots(figsize=(6, 5.5))
unit_circle = plt.Circle((0., 0.), 1., color='grey', linestyle='-', fill=False,
                         label='unit circle', linewidth=6.0, alpha=0.7)
ax1.add_artist(unit_circle)
ax1.scatter(eigval.real, eigval.imag, marker='o',
            facecolor='none', edgecolors='k', s=18)
sp_eigval = eigval[sp_ind]
ax1.scatter(sp_eigval.real, sp_eigval.imag, marker='o',
            facecolor='k', edgecolors='k', s=18)
limit = np.max(np.absolute(eigval))+0.1
ax1.set_xlim((-limit, limit))
ax1.set_ylim((-limit, limit))
plt.xlabel(r'$\Re(\mu_i)$')
plt.ylabel(r'$\Im(\mu_i)$')
ax1.grid(b=True, which='both', linestyle=':')
plt.gca().set_aspect('equal', adjustable='box')
plt.savefig(path + 'DMDEigSpectrum.svg', bbox_inches='tight')
plt.show()
# %% Mode frequency specturm
matplotlib.rc('font', size=14)
fig1, ax1 = plt.subplots(figsize=(6, 5.5))
phi_abs = np.linalg.norm(phi*coeff, axis=0)
phi_max = np.max(phi_abs)
phi1 = phi_abs/phi_max
freq = predmd.omega/2/np.pi
ind1 = freq > 0.0
ax1.set_xscale("log")
ax1.vlines(freq[ind1], [0], phi1[ind1], color='k', linewidth=1.0)
ind2 = ans.nonzero[:, sp] & ind1
ax1.scatter(freq[ind2], phi1[ind2], marker='o',
            facecolor='gray', edgecolors='k', s=15.0)
ax1.set_ylim(bottom=0.0)
plt.xlabel(r'$f \delta_0/u_\infty$')
plt.ylabel(r'$|\phi_i|$')
ax1.grid(b=True, which='both', linestyle=':')
plt.savefig(path + 'DMDFreqSpectrum.svg', bbox_inches='tight')
plt.show()
# %% specific mode in space
matplotlib.rcParams['xtick.direction'] = 'out'
matplotlib.rcParams['ytick.direction'] = 'out'
ind = 4
ind1 = sp_ind[ind-1]
x, y = np.meshgrid(np.unique(xval), np.unique(yval))
modeflow = phi[:, ind1].real
u = griddata((xval, yval), modeflow, (x, y))
corner = (x < 0.0) & (y < 0.0)
u[corner] = np.nan
matplotlib.rc('font', size=18)
fig, ax = plt.subplots(figsize=(12, 4))
c1 = -0.015 #-0.024
c2 = 0.024  #0.018
lev1 = np.linspace(c1, c2, 11)
lev2 = np.linspace(c1, c2, 6)
cbar = ax.contourf(x, y, u, levels=lev1, cmap='RdBu_r', extend='both') 
#cbar = ax.contourf(x, y, u,
#                   colors=('#66ccff', '#e6e6e6', '#ff4d4d'))  # blue, grey, red
ax.grid(b=True, which='both', linestyle=':')
ax.set_xlim(x1, x2)
ax.set_ylim(y1, y2)
ax.tick_params(labelsize=14)
cbar.cmap.set_under('#053061')
cbar.cmap.set_over('#67001f')
# add colorbar
rg2 = np.linspace(c1, c2, 3)
cbaxes = fig.add_axes([0.16, 0.76, 0.18, 0.07])  # x, y, width, height
cbar1 = plt.colorbar(cbar, cax=cbaxes, orientation="horizontal", ticks=rg2)
cbar1.set_label(r'$\Re(\phi)$', rotation=0, fontdict=font)
cbaxes.tick_params(labelsize=16)
ax.set_xlabel(r'$x/\delta_0$', fontdict=font)
ax.set_ylabel(r'$y/\delta_0$', fontdict=font)
plt.savefig(path+'DMDMode'+str(ind)+'.svg', bbox_inches='tight')
plt.show()
# %% Time evolution of each mode (first several modes)
"""
plt.figure(figsize=(10, 5))
matplotlib.rc('font', size=18)
plt.plot(timepoints[:-1], dynamics[0, :].real*phi[0, 0].real)
plt.plot(timepoints[:-1], dynamics[12, :].real*phi[0, 12].real)
plt.plot(timepoints[:-1], dynamics[22, :].real*phi[0, 22].real)
plt.xlabel(r'$tu_\infty/\delta_0/$')
plt.ylabel(r'$\phi$')
plt.grid(b=True, which='both', linestyle=':')
plt.savefig(path + 'DMDModeTemp' + str(ind) + '.svg', bbox_inches='tight')
plt.show()
"""
# %% Reconstruct flow field using DMD
tind = 0
N_modes = np.shape(phi)[1]
reconstruct = predmd.reconstruct(predmd.modes, predmd.amplit, predmd.Vand)
meanflow = np.mean(Snapshots, axis=1)
x, y = np.meshgrid(np.unique(xval), np.unique(yval))
newflow = phi[:, :N_modes]@dynamics[:N_modes, tind]
# newflow = reconstruct[:,tind]
u = griddata((xval, yval), meanflow+newflow.real, (x, y))
corner = (x < 0.0) & (y < 0.0)
u[corner] = np.nan
matplotlib.rc('font', size=18)
fig, ax = plt.subplots(figsize=(12, 4))
lev1 = np.linspace(-0.20, 1.15, 18)
cbar = ax.contourf(x, y, u, cmap='rainbow', levels=lev1, extend="both")
ax.set_xlim(x1, x2)
ax.set_ylim(y1, y2)
ax.tick_params(labelsize=14)
cbar.cmap.set_under('b')
cbar.cmap.set_over('r')
ax.set_xlabel(r'$x/\delta_0$', fontdict=font)
ax.set_ylabel(r'$y/\delta_0$', fontdict=font)
# add colorbar
rg2 = np.linspace(-0.20, 1.15, 4)
cbaxes = fig.add_axes([0.16, 0.76, 0.18, 0.07])  # x, y, width, height
cbar1 = plt.colorbar(cbar, cax=cbaxes, orientation="horizontal", ticks=rg2)
cbar1.set_label(r'$u/u_{\infty}$', rotation=0, fontdict=font)
cbaxes.tick_params(labelsize=14)
plt.savefig(path+'DMDReconstructFlow.svg', bbox_inches='tight')
plt.show()

err = Snapshots1 - (reconstruct.real+np.tile(meanflow.reshape(m, 1), (1, n-1)))
print("Errors of DMD: ", np.linalg.norm(err)/n)
# how about residuals???

# %% Test DMD using meaning flow
def DMDMeanflow(Snapshots):
    flow = DMD(Snapshots)
    n = np.shape(Snapshots)[1]
    with timer("DMD computing"):
        eigval, phi = flow.dmd_standard()
    
    coeff = flow.dmd_amplitude()
    dynamics = flow.dmd_dynamics(timepoints)
    residual = flow.dmd_residual
    print("The residuals of DMD is ", residual)
    # Reconstruct flow field using DMD
    # tind = 0
    x, y = np.meshgrid(np.unique(xval), np.unique(yval))
    newflow = np.reshape(phi[:, 0], (m,1))@np.reshape(dynamics[0, :], (1, n-1))
    meanflow = np.mean(newflow.real, axis=1)
    # newflow = reconstruct[:,tind]
    u = griddata((xval, yval), meanflow, (x, y))
    corner = (x < 0.0) & (y < 0.0)
    u[corner] = np.nan
    matplotlib.rc('font', size=18)
    fig, ax = plt.subplots(figsize=(12, 4))
    lev1 = np.linspace(-0.20, 1.15, 18)
    cbar = ax.contourf(x, y, u, cmap='rainbow', levels=lev1) #, extend="both")
    ax.set_xlim(x1, x2)
    ax.set_ylim(y1, y2)
    ax.tick_params(labelsize=14)
    cbar.cmap.set_under('b')
    cbar.cmap.set_over('r')
    ax.set_xlabel(r'$x/\delta_0$', fontdict=font)
    ax.set_ylabel(r'$y/\delta_0$', fontdict=font)
    # add colorbar
    rg2 = np.linspace(-0.20, 1.15, 4)
    cbaxes = fig.add_axes([0.16, 0.76, 0.18, 0.07])  # x, y, width, height
    cbar1 = plt.colorbar(cbar, cax=cbaxes, orientation="horizontal", ticks=rg2)
    cbar1.set_label(r'$u/u_{\infty}$', rotation=0, fontdict=font)
    cbaxes.tick_params(labelsize=14)
    plt.savefig(path + 'DMDMeanFlow.svg', bbox_inches='tight')
    plt.show()
    ## Original Meanflow
    origflow = np.mean(Snapshots, axis=1)
    u = griddata((xval, yval), origflow, (x, y))
    corner = (x < 0.0) & (y < 0.0)
    u[corner] = np.nan
    matplotlib.rc('font', size=18)
    fig, ax = plt.subplots(figsize=(12, 4))
    lev1 = np.linspace(-0.20, 1.15, 18)
    cbar = ax.contourf(x, y, u, cmap='rainbow', levels=lev1)  # ,extend="both")
    ax.set_xlim(x1, x2)
    ax.set_ylim(y1, y2)
    ax.tick_params(labelsize=14)
    cbar.cmap.set_under('b')
    cbar.cmap.set_over('r')
    ax.set_xlabel(r'$x/\delta_0$', fontdict=font)
    ax.set_ylabel(r'$y/\delta_0$', fontdict=font)
    # add colorbar
    rg2 = np.linspace(-0.20, 1.15, 4)
    cbaxes = fig.add_axes([0.16, 0.76, 0.18, 0.07])  # x, y, width, height
    cbar1 = plt.colorbar(cbar, cax=cbaxes, orientation="horizontal", ticks=rg2)
    cbar1.set_label(r'$u/u_{\infty}$', rotation=0, fontdict=font)
    cbaxes.tick_params(labelsize=14)
    plt.savefig(path + 'OrigMeanFlow.svg', bbox_inches='tight')
    plt.show()
    print("Errors of MeanFlow: ", np.linalg.norm(meanflow-origflow)/n)


#  DMD for mean flow
DMDMeanflow(Snapshots)
