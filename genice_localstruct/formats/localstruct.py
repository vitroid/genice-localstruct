# coding: utf-8

# system library
from collections import defaultdict
import itertools as it
import sys

# public library
import pairlist as pl
import numpy as np
import networkx as nx

####### Tetrahedrality Qtet
# 1.	Errington, J. R. & Debenedetti, P. G. Relationship between structural order and the anomalies of liquid water. Nature 409, 318–321 (2001).

def Qtet(lattice):
    lattice.logger.info("  Tetrahedrality.")
    cell = lattice.repcell 
    positions = lattice.reppositions
    rc = 0.35 # nm
    grid = pl.determine_grid(cell.mat, rc)
    nei = defaultdict(dict)
    for i,j,d in pl.pairs_fine(positions, rc, cell.mat, grid, distance=True):
        nei[i][j] = d
        nei[j][i] = d
    op = np.zeros(positions.shape[0])
    for i in nei:
        neis = [x for x in sorted(nei[i], key=lambda x: nei[i][x])][:4]
        vecs = np.zeros([4,3])
        for j,n in enumerate(neis):
            D = positions[n] - positions[i]
            D -= np.floor(D+0.5)
            D = cell.rel2abs(D)
            D /= np.linalg.norm(D) # unit vector
            vecs[j] = D
        x = 0.0
        for j,k in it.combinations(vecs, 2):
            cosine = np.dot(j,k)
            x += (cosine+1/3)**2
        op[i] = 1-3*x/8
    return op


####### Distance to the Fifth neighbor
# Cuthbertson, M. J.; Poole, P. H. Mixturelike Behavior Near a Liquid-Liquid Phase Transition in Simulations of Supercooled Water. Phys. Rev. Lett. 2011, 106, 115706.

def G5(lattice):
    lattice.logger.info("  Tetrahedrality.")
    cell = lattice.repcell 
    positions = lattice.reppositions
    rc = 0.6 # nm
    grid = pl.determine_grid(cell.mat, rc)
    nei = defaultdict(dict)
    for i,j,d in pl.pairs_fine(positions, rc, cell.mat, grid, distance=True):
        nei[i][j] = d
        nei[j][i] = d
    op = np.zeros(positions.shape[0])
    for i in nei:
        nei5 = [x for x in sorted(nei[i], key=lambda x: nei[i][x])]
        if len(nei5) > 4:
            op[i] = nei[i][nei5[4]]
    return op


####### Eta
# 1.	Russo, J. & Tanaka, H. Understanding water’s anomalies with locally favoured structures. Nat Commun 5, 3556 (2014).

def Eta(lattice):
    lattice.logger.info("  Gap between 1st and 2nd shells.")
    cell = lattice.repcell 
    positions = lattice.reppositions
    graph = nx.Graph(lattice.graph)
    op = np.zeros(positions.shape[0])
    for i in graph:
        nei1 = [j for j in graph[i]]
        nei2 = set()
        for j in nei1:
            nei2 |= {k for k in graph[j]}
        nei2 -= {i}
        nei2 -= set(nei1)
        if len(nei2):
            D1 = positions[i] - positions[nei1]
            D1 -= np.floor(D1+0.5)
            D1 = np.dot(D1, cell.mat)
            D1 = np.linalg.norm(D1, axis=1)
            last1 = np.max(D1)

            D2 = positions[i] - positions[list(nei2)]
            D2 -= np.floor(D2+0.5)
            D2 = np.dot(D2, cell.mat)
            D2 = np.linalg.norm(D2, axis=1)

            first2 = np.min(D2)
            op[i] = first2 - last1
    return op



        
    
def hook1(lattice):
    global qtet, g5
    lattice.logger.info("Hook1: Positional indices.")
    qtet = Qtet(lattice)
    g5   = G5(lattice)
    lattice.logger.info("Hook1: Done.")


def hook2(lattice):
    global qtet, g5
    lattice.logger.info("Hook2: Network indices.")
    eta  = Eta(lattice)
    lattice.logger.info("Hook2: Done.")

    print("# Qtet G5 eta")
    np.savetxt(sys.stdout, np.vstack([qtet,g5,eta]).T, fmt='%.5f')
    
    


def argparser(arg):
    pass
    

hooks = {1:hook1, # molecular positions
         2:hook2, # undirected graph
}

if __name__ == "__main__":
    print("Unit test")
