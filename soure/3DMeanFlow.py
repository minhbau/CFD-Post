#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 17:39:31 2018
    Plot for time-averaged flow (3D meanflow)
@author: Weibo Hu
"""
# %%
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev
import matplotlib
import pandas as pd
import plt2pandas as p2p
import variable_analysis as fv
from planar_field import PlanarField as pf
from data_post import DataPost
from glob import glob
from scipy.interpolate import griddata
from numpy import NaN, Inf, arange, isscalar, asarray, array
from timer import timer
import matplotlib.patches as patches
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
import os

plt.close("All")
plt.rc("text", usetex=True)
font = {"family": "Times New Roman", "color": "k", "weight": "normal"}

path = "/media/weibo/VID2/BFS_M1.7TS/"
pathP = path + "probes/"
pathF = path + "Figures/"
pathM = path + "MeanFlow/"
pathS = path + "SpanAve/"
pathT = path + "TimeAve/"
pathI = path + "Instant/"
matplotlib.rcParams["xtick.direction"] = "out"
matplotlib.rcParams["ytick.direction"] = "out"
textsize = 15
numsize = 12
matplotlib.rc("font", size=textsize)

# %% Load Data for time- spanwise-averaged results
# filter files
FileId = pd.read_csv(path + "StatList.dat", sep='\t')
filelist = FileId['name'].to_list()
pltlist = [os.path.join(path + 'TP_stat/', name) for name in filelist]
MeanFlow = pf()
MeanFlow.load_meanflow(path, FileList=pltlist)

# %% convert every single mean flow block
MeanFlow = pf()
MeanFlow.merge_meanflow(path)
    
# %% Load Data for time- spanwise-averaged results
MeanFlow = pf()
MeanFlow.load_meanflow(path)

# %% check mesh 
temp = MeanFlow.PlanarData[['x', 'y']]
df = temp.query("x>=-5.0 & x<=5.0 & y>=-3.0 & y<=1.0")
ux = np.unique(df.x)
uy = np.unique(df.y)
fig, ax = plt.subplots(figsize=(6.4, 3.0))
matplotlib.rc("font", size=textsize)
for i in range(np.size(ux)):
    if i % 2 == 0:
        df_x = df.loc[df['x']==ux[i]]
        ax.plot(df_x['x'], df_x['y'], 'k-', linewidth=0.4)
for j in range(np.size(uy)):
    if j % 4 == 0:
        df_y = df.loc[df['y']==uy[j]]
        ax.plot(df_y['x'], df_y['y'], 'k-', linewidth=0.4)
plt.gca().set_aspect("equal", adjustable="box")
ax.set_xlim(-5.0, 5.0)
ax.set_ylim(-3.0, 1.0)
ax.set_xticks(np.linspace(-5.0, 5.0, 5))
ax.tick_params(labelsize=numsize)
ax.set_xlabel(r"$x/\delta_0$", fontsize=textsize)
ax.set_ylabel(r"$y/\delta_0$", fontsize=textsize)
plt.savefig(pathF + "Grid.pdf", bbox_inches="tight")
plt.show()
    

# %%
x, y = np.meshgrid(np.unique(MeanFlow.x), np.unique(MeanFlow.y))
corner = (x < 0.0) & (y < 0.0)

# %% Mean flow isolines
fv.DividingLine(MeanFlow.PlanarData, pathM)
# %% Save sonic line
fv.SonicLine(MeanFlow.PlanarData, pathM, option='velocity', Ma_inf=1.7)
# %% Save boundary layer
fv.BoundaryEdge(MeanFlow.PlanarData, pathM)
# %% Save shock line
fv.ShockLine(MeanFlow.PlanarData, pathM)
# %% 
plt.close("All")
# %% Plot rho contour of the mean flow field
# MeanFlow.AddVariable('rho', 1.7**2*1.4*MeanFlow.p/MeanFlow.T)
MeanFlow.copy_meanval()
var = 'rho'
rho = griddata((MeanFlow.x, MeanFlow.y), MeanFlow.rho, (x, y))
print("rho_max=", np.max(MeanFlow.rho_m))
print("rho_min=", np.min(MeanFlow.rho_m))
rho[corner] = np.nan
fig, ax = plt.subplots(figsize=(6.4, 2.2))
matplotlib.rc("font", size=textsize)
rg1 = np.linspace(0.33, 1.03, 41)
cbar = ax.contourf(x, y, rho, cmap="rainbow", levels=rg1)  # rainbow_r
ax.set_xlim(-10.0, 30.0)
ax.set_ylim(-3.0, 10.0)
ax.tick_params(labelsize=numsize)
ax.set_xlabel(r"$x/\delta_0$", fontsize=textsize)
ax.set_ylabel(r"$y/\delta_0$", fontsize=textsize)
plt.gca().set_aspect("equal", adjustable="box")
# Add colorbar
rg2 = np.linspace(0.33, 1.03, 3)
cbaxes = fig.add_axes([0.17, 0.75, 0.18, 0.07])  # x, y, width, height
cbaxes.tick_params(labelsize=numsize)
cbar = plt.colorbar(cbar, cax=cbaxes, orientation="horizontal", ticks=rg2)
cbar.set_label(
    r"$\langle \rho \rangle/\rho_{\infty}$", rotation=0, fontdict=font
)
# Add shock wave
shock = np.loadtxt(pathM + "ShockLineFit.dat", skiprows=1)
ax.plot(shock[:, 0], shock[:, 1], "w", linewidth=1.5)
# shock1 = np.loadtxt(pathM + "ShockLine1.dat", skiprows=1)
# ax.plot(shock1[:, 0], shock1[:, 1], "w", linewidth=1.5)
# shock2 = np.loadtxt(pathM + "ShockLine2.dat", skiprows=1)
# ax.plot(shock2[:, 0], shock2[:, 1], "w", linewidth=1.5)
# Add sonic line
sonic = np.loadtxt(pathM + "SonicLine.dat", skiprows=1)
ax.plot(sonic[:, 0], sonic[:, 1], "w--", linewidth=1.5)
# Add boundary layer
boundary = np.loadtxt(pathM + "BoundaryEdge.dat", skiprows=1)
ax.plot(boundary[:, 0], boundary[:, 1], "k", linewidth=1.5)
# Add dividing line(separation line)
dividing = np.loadtxt(pathM + "BubbleLine.dat", skiprows=1)
ax.plot(dividing[:, 0], dividing[:, 1], "k--", linewidth=1.5)
# streamlines
x1 = np.linspace(0.0, 12.0, 120)
y1 = np.linspace(-3.0, -0.0, 100)
seeds = np.array(
    [
        [6.83, 5.93, 5.35, 3.85, 2.50, 1.42, 0.76],
        [-2.1, -1.8, -1.6, -1.14, -0.8, -0.54, -0.35],
    ]
)
xbox, ybox = np.meshgrid(x1, y1)
u = griddata((MeanFlow.x, MeanFlow.y), MeanFlow.u, (xbox, ybox))
v = griddata((MeanFlow.x, MeanFlow.y), MeanFlow.v, (xbox, ybox))
ax.streamplot(
    xbox,
    ybox,
    u,
    v,
    color="w",
    density=[3.0, 2.0],
    arrowsize=0.7,
    start_points=seeds.T,
    maxlength=30.0,
    linewidth=1.0,
)

plt.savefig(pathF + "MeanFlow.svg", bbox_inches="tight")
plt.show()

# %% Plot rms contour of the mean flow field
MeanFlow = DataPost()
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
    "uu",
    "uv",
    "uw",
    "vv",
    "vw",
    "ww",
    "Q-criterion",
    "L2-criterion",
    "gradp",
]
# MeanFlow.UserData(VarName, pathM + "MeanFlow.dat", 1, Sep="\t")
TimeAve = pd.read_hdf(pathM + "TP_stat.h5")
grouped = TimeAve.groupby(['x', 'y'])
MeanFlow = grouped.mean().reset_index()
x, y = np.meshgrid(np.unique(MeanFlow.x), np.unique(MeanFlow.y))
corner = (x < 0.0) & (y < 0.0)
var = "<v`v`>"
uu = griddata((MeanFlow.x, MeanFlow.y), getattr(MeanFlow, var), (x, y))
print("uu_max=", np.max(np.sqrt(np.abs(getattr(MeanFlow, var)))))
print("uu_min=", np.min(np.sqrt(np.abs(getattr(MeanFlow, var)))))
corner = (x < 0.0) & (y < 0.0)
uu[corner] = np.nan
fig, ax = plt.subplots(figsize=(10, 4))
matplotlib.rc("font", size=textsize)
rg1 = np.linspace(0.0, 0.20, 21)
cbar = ax.contourf(
    x, y, np.sqrt(np.abs(uu)), cmap="Spectral_r", levels=rg1
)  # rainbow_r
ax.set_xlim(-10.0, 30.0)
ax.set_ylim(-3.0, 10.0)
ax.tick_params(labelsize=numsize)
ax.set_xlabel(r"$x/\delta_0$", fontdict=font)
ax.set_ylabel(r"$y/\delta_0$", fontdict=font)
plt.gca().set_aspect("equal", adjustable="box")
# Add colorbar box
rg2 = np.linspace(0.0, 0.20, 3)
cbbox = fig.add_axes([0.14, 0.53, 0.24, 0.27], alpha=0.9)
[cbbox.spines[k].set_visible(False) for k in cbbox.spines]
cbbox.tick_params(
    axis="both",
    left=False,
    right=False,
    top=False,
    bottom=False,
    labelleft=False,
    labeltop=False,
    labelright=False,
    labelbottom=False,
)
cbbox.set_facecolor([1, 1, 1, 0.7])
# Add colorbar
cbaxes = fig.add_axes(
    [0.17, 0.70, 0.18, 0.07], frameon=True
)  # x, y, width, height
cbaxes.tick_params(labelsize=numsize)
cbar = plt.colorbar(cbar, cax=cbaxes, orientation="horizontal", ticks=rg2)
cbar.set_label(
    r"$\sqrt{|\langle v^\prime v^\prime \rangle|}$",
    rotation=0,
    fontsize=textsize,
)
# Add shock wave
shock = np.loadtxt(pathM + "ShockLineFit.dat", skiprows=1)
ax.plot(shock[:, 0], shock[:, 1], "w", linewidth=1.5)
# Add sonic line
sonic = np.loadtxt(pathM + "SonicLine.dat", skiprows=1)
ax.plot(sonic[:, 0], sonic[:, 1], "w--", linewidth=1.5)
# Add boundary layer
boundary = np.loadtxt(pathM + "BoundaryEdge.dat", skiprows=1)
ax.plot(boundary[:, 0], boundary[:, 1], "k", linewidth=1.5)
# Add dividing line(separation line)
dividing = np.loadtxt(pathM + "BubbleLine.dat", skiprows=1)
ax.plot(dividing[:, 0], dividing[:, 1], "k--", linewidth=1.5)

plt.savefig(pathF + "MeanFlowRMSVV.svg", bbox_inches="tight")
plt.show()

# %% Load Data for time-averaged results
path4 = "/media/weibo/Data1/BFS_M1.7L_0505/SpanAve/"
MeanFlow = DataPost()
MeanFlow.UserDataBin(pathF + "SolTime995.00.h5")
# %% Preprocess the data in the xy plane (z=0.0)
MeanFlowZ0 = MeanFlow.DataTab.loc[MeanFlow.DataTab["z"] == 0.0]
MeanFlowZ1 = MeanFlow.DataTab.loc[MeanFlow.DataTab["z"] == 0.5]
MeanFlowZ2 = MeanFlow.DataTab.loc[MeanFlow.DataTab["z"] == -0.5]
MeanFlowZ3 = pd.concat((MeanFlowZ1, MeanFlowZ2))
MeanFlowZ4 = MeanFlowZ3.groupby(["x", "y"]).mean().reset_index()
MeanFlowZ5 = MeanFlowZ4.loc[MeanFlowZ4["y"] > 3.0]
MeanFlowZ0 = pd.concat((MeanFlowZ0, MeanFlowZ5), sort=False)
MeanFlowZ0.to_hdf(pathF + "MeanFlowZ0.h5", "w", format="fixed")

#%% Plot contour of the mean flow field in the xy plane
# MeanFlowZ0 = DataPost()
# MeanFlowZ0.UserDataBin(path+'MeanFlowZ0.h5')
x, y = np.meshgrid(np.unique(MeanFlowZ0.x), np.unique(MeanFlowZ0.y))
omegaz = griddata((MeanFlowZ0.x, MeanFlowZ0.y), MeanFlowZ0.vorticity_3, (x, y))
corner = (x < 0.0) & (y < 0.0)
omegaz[corner] = np.nan
textsize = 18
numsize = 15
fig, ax = plt.subplots(figsize=(10, 4))
matplotlib.rc("font", size=textsize)
plt.tick_params(labelsize=numsize)
lev1 = np.linspace(-5.0, 1.0, 30)
cbar = ax.contourf(x, y, omegaz, cmap="rainbow", levels=lev1, extend="both")
ax.set_xlim(-10.0, 30.0)
ax.set_ylim(-3.0, 10.0)
cbar.cmap.set_under("b")
cbar.cmap.set_over("r")
ax.set_xlabel(r"$x/\delta_0$", fontdict=font)
ax.set_ylabel(r"$y/\delta_0$", fontdict=font)
plt.gca().set_aspect("equal", adjustable="box")
# Add colorbar
rg2 = np.linspace(-5.0, 1.0, 4)
cbaxes = fig.add_axes([0.17, 0.70, 0.18, 0.07])  # x, y, width, height
cbar = plt.colorbar(cbar, cax=cbaxes, orientation="horizontal", ticks=rg2)
cbar.set_label(r"$\omega_z$", rotation=0, fontdict=font)

box = patches.Rectangle(
    (1.0, -1.5),
    4.0,
    1.3,
    linewidth=1,
    linestyle="--",
    edgecolor="k",
    facecolor="none",
)
ax.add_patch(box)
plt.tick_params(labelsize=numsize)
plt.savefig(pathF + "Vorticity3.svg", bbox_inches="tight")
plt.show()

# %% Zoom box for streamline
fig, ax = plt.subplots(figsize=(7, 3))
cbar = ax.contourf(x, y, omegaz, cmap="rainbow", levels=lev1, extend="both")
ax.set_xlim(1.0, 5.0)
ax.set_ylim(-1.5, -0.2)
ax.set_xticks([])
ax.set_yticks([])
x1 = np.linspace(1.0, 5.0, 50)
y1 = np.linspace(-1.5, -0.2, 50)
xbox, ybox = np.meshgrid(x1, y1)
u = griddata((MeanFlowZ0.x, MeanFlowZ0.y), MeanFlowZ0.u, (xbox, ybox))
v = griddata((MeanFlowZ0.x, MeanFlowZ0.y), MeanFlowZ0.v, (xbox, ybox))
ax.streamplot(
    xbox,
    ybox,
    u,
    v,
    density=[2.0, 1.5],
    color="w",
    linewidth=1.0,
    integration_direction="both",
)
plt.tight_layout(pad=0.5, w_pad=0.5, h_pad=0.3)
plt.savefig(pathF + "V3ZoomBox.svg", bbox_inches="tight", pad_inches=0.0)
plt.show()

# %% Preprocess the data in the xz plane (y=-0.5)
MeanFlowY = MeanFlow.DataTab.loc[MeanFlow.DataTab["y"] == -1.5].reset_index(
    drop=True
)
MeanFlowY.to_hdf(path + "MeanFlowYN3.h5", "w", format="fixed")
MeanFlowY = DataPost()
MeanFlowY.UserDataBin(path + "MeanFlowYN3.h5")
# %% Plot contour of the mean flow field in the xz plane
x, z = np.meshgrid(np.unique(MeanFlowY.x), np.unique(MeanFlowY.z))
omegaz = griddata((MeanFlowY.x, MeanFlowY.z), MeanFlowY.vorticity_1, (x, z))
fig, ax = plt.subplots(figsize=(5, 3))
matplotlib.rc("font", size=textsize)
plt.tick_params(labelsize=numsize)
lev1 = np.linspace(-0.1, 0.1, 2)
lev1 = [-0.1, 0.1]
# lev1 = [-0.1, 0.0, 0.1]
cbar1 = ax.contourf(
    x, z, omegaz, cmap="RdBu_r", levels=lev1, extend="both"
)  # rainbow_r
ax.set_xlim(2.0, 10.0)
ax.set_ylim(-2.5, 2.5)
cbar.cmap.set_over("#ff5c33")  # ('#053061') #Red
cbar.cmap.set_under("#33adff")  # ('#67001f') #Blue
ax.set_xlabel(r"$x/\delta_0$")
ax.set_ylabel(r"$z/\delta_0$")
plt.gca().set_aspect("equal", adjustable="box")
# Add colorbar
# rg2 = np.linspace(-0.1, -0.1, 3)
# ax1_divider = make_axes_locatable(ax)
# cax1 = ax1_divider.append_axes("top", size="7%", pad="12%")
# cbar = plt.colorbar(cbar1, cax=cax1, orientation="horizontal", ticks=rg2)
# plt.tick_params(labelsize=numsize)
# cax1.xaxis.set_ticks_position("top")
# cbar.ax.tick_params(labelsize=numsize)
# ax.set_aspect('auto')
# cbar.set_label(r'$\omega_x$', rotation=0, fontdict=font)
# Add isolines of Lambda2 criterion
# L2 = griddata((MeanFlowY.x, MeanFlowY.z), MeanFlowY.L2crit, (x, z))
# ax.contour(x, z, L2, levels=-0.001, \
#           linewidths=1.2, colors='k',linestyles='solid')
plt.show()
plt.savefig(path2 + "Vorticity1XZ.svg", bbox_inches="tight")

# %% Preprocess the data in the xz plane (y=-0.5)
# MeanFlow = DataPost()
# MeanFlow.UserDataBin(path+'MeanFlow2.h5')
# MeanFlowX3 = MeanFlow.DataTab.loc[MeanFlow.DataTab['x'] == 3.0].reset_index(
#   drop=True
# )
# MeanFlowX3.to_hdf(path2 + "MeanFlowX3.h5", 'w', format='fixed')

# %% Plot contour of the mean flow field in the zy plane
MeanFlowX = MeanFlow.DataTab.loc[MeanFlow.DataTab["x"] == 3.25].reset_index(
    drop=True
)
MeanFlowX.to_hdf(path + "MeanFlowX3.h5", "w", format="fixed")
MeanFlowX3 = DataPost()
MeanFlowX3.UserDataBin(path + "MeanFlowX3.h5")

# %% Plot contour of the mean flow field in the zy plane
z, y = np.meshgrid(np.unique(MeanFlowX3.z), np.unique(MeanFlowX3.y))
omegax = griddata((MeanFlowX3.z, MeanFlowX3.y), MeanFlowX3.vorticity_1, (z, y))
textsize = 18
numsize = 15
fig, ax = plt.subplots(figsize=(5, 3))
matplotlib.rc("font", size=textsize)
plt.tick_params(labelsize=numsize)
lev1 = np.linspace(-0.1, 0.1, 30)
cbar1 = ax.contourf(
    z, y, omegax, cmap="rainbow", levels=lev1, extend="both"
)  # rainbow_r
ax.set_xlim(-2.5, 2.5)
ax.set_ylim(-3.0, 0.0)
cbar1.cmap.set_under("b")
cbar1.cmap.set_over("r")
ax.set_xlabel(r"$z/\delta_0$", fontdict=font)
ax.set_ylabel(r"$y/\delta_0$", fontdict=font)
plt.gca().set_aspect("equal", adjustable="box")
# Add colorbar
rg2 = np.linspace(-0.1, 0.1, 5)
# cbaxes = fig.add_axes([0.16, 0.76, 0.18, 0.07])  # x, y, width, height
ax1_divider = make_axes_locatable(ax)
cax1 = ax1_divider.append_axes("top", size="7%", pad="13%")
cbar = plt.colorbar(cbar1, cax=cax1, orientation="horizontal", ticks=rg2)
plt.tick_params(labelsize=numsize)
cax1.xaxis.set_ticks_position("top")
cbar.set_label(r"$\omega_x$", rotation=0, fontsize=textsize)
# Add streamlines
zz = np.linspace(-2.5, 2.5, 50)
yy = np.linspace(-3.0, 0.0, 30)
zbox, ybox = np.meshgrid(zz, yy)
v = griddata((MeanFlowX3.z, MeanFlowX3.y), MeanFlowX3.v, (zbox, ybox))
w = griddata((MeanFlowX3.z, MeanFlowX3.y), MeanFlowX3.w, (zbox, ybox))
ax.set_xlim(-2.5, 2.5)
ax.set_ylim(-3.0, 0.0)
ax.streamplot(
    zbox,
    ybox,
    w,
    v,
    density=[2.5, 1.5],
    color="w",
    linewidth=1.0,
    integration_direction="both",
)
plt.show()
plt.savefig(pathF + "vorticity1.svg", bbox_inches="tight", pad_inches=0.1)

# %% Plot contour and streamline of spanwise-averaged flow (Zoom in)
path = "/media/weibo/Data1/BFS_M1.7L_0505/SpanAve/7/"
path1 = "/media/weibo/Data1/BFS_M1.7L_0505/probes/"
path2 = "/media/weibo/Data1/BFS_M1.7L_0505/DataPost/"
# MeanFlowZ = DataPost()
# MeanFlowZ.UserDataBin(path+'SolTime772.50.h5')
time = "790.50"
MeanFlowZ = pd.read_hdf(path + "SolTime" + time + ".h5")
xval = np.linspace(0.0, 10, 100)
yval = np.linspace(-3.0, 0.0, 30)
x, y = np.meshgrid(xval, yval)
u = griddata((MeanFlowZ.x, MeanFlowZ.y), MeanFlowZ.u, (x, y))
# Contour
fig, ax = plt.subplots(figsize=(5, 3))
matplotlib.rc("font", size=textsize)
plt.tick_params(labelsize=numsize)
lev1 = np.linspace(-0.4, 1.2, 30)
cbar = ax.contourf(x, y, u, cmap="rainbow", levels=lev1)  # rainbow_r
ax.set_xlim(2.0, 10.0)
ax.set_ylim(-3.0, 0.0)
# cbar.cmap.set_under('b')
# cbar.cmap.set_over('r')
ax.set_xlabel(r"$x/\delta_0$", fontdict=font)
ax.set_ylabel(r"$y/\delta_0$", fontdict=font)
plt.gca().set_aspect("equal", adjustable="box")
# Add colorbar box
rg2 = np.linspace(0.0, 0.20, 3)
cbbox = fig.add_axes([0.46, 0.54, 0.435, 0.19], alpha=0.2)
[cbbox.spines[k].set_visible(False) for k in cbbox.spines]
cbbox.tick_params(
    axis="both",
    left=False,
    right=False,
    top=False,
    bottom=False,
    labelleft=False,
    labeltop=False,
    labelright=False,
    labelbottom=False,
)
cbbox.set_facecolor([1, 1, 1, 0.7])
# Add colorbar
rg2 = np.linspace(-0.4, 1.2, 3)
cax = fig.add_axes([0.6, 0.65, 0.25, 0.05])  # x, y, width, height
cbar = plt.colorbar(cbar, cax=cax, orientation="horizontal", ticks=rg2)
# cbar.ax.set_title(r'$u/u_\infty$', fontsize=textsize)
cbar.set_label(
    r"$u/u_\infty$", rotation=0, x=-0.28, labelpad=-28, fontsize=textsize
)
plt.tick_params(labelsize=numsize)
# Streamline
v = griddata((MeanFlowZ.x, MeanFlowZ.y), MeanFlowZ.v, (x, y))
# x, y must be equal spaced
ax.streamplot(
    x,
    y,
    u,
    v,
    density=[4, 2.5],
    color="w",
    arrowsize=0.5,
    linewidth=0.6,
    integration_direction="both",
)
plt.savefig(
    pathF + "StreamVortex" + time + ".svg", bbox_inches="tight", pad_inches=0.1
)
plt.show()



