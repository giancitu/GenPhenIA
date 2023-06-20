"""
En este script se exploraran los datos reales. Por un lado los de bitgenia y
por otro lado los de ClinVar. Se mirará por ejemplo, la cantidad de fenotipos
observados promedio, se mirará también la cantidad de missing phens y la
cantidad de incorrect phens. Y por último, yendo a un nivel más profundo, se
mirará el nivel de vaguedad de un fenotipo. Esto es, a qué distancia
está del fenotipo específico que causa el gen.
"""

## {{{ IMPORTACIONES
import numpy as np
import random
import sys
sys.path.insert(0,'/home/brainy/Desktop/1ercuatri2023/Tesis/GenPhenIA/src')
import linear_model_lab as lml
import phen_gen_weight_functions as pgw
PATH = "/home/brainy/Desktop/1ercuatri2023/Tesis/GenPhenIA/"
import ast
import json
import scienceplots
import matplotlib.pyplot as plt
import pandas as pd
import csv
# import matplotlib
# matplotlib.use('TkAgg')
## }}}

## {{{ Convertir a diccionario el set que nos dieron

def convert_to_dict(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # This will give us a list of tuples
    list_of_tuples = ast.literal_eval(content)

    # Now, we will convert it to a dictionary
    # We'll also convert the string representation of list to an actual list using ast.literal_eval
    dictionary = {t[0]: ast.literal_eval(t[1]) for t in list_of_tuples}

    return dictionary

file_path = f"{PATH}data/real/bitgenia_IDs_tov3.sets"
dictionary_bitgenia = convert_to_dict(file_path)
dictionary_clinvar = convert_to_dict(f"{PATH}data/real/clinvar_IDs_tov3.sets")

# print(dictionary)

def save_to_json(dictionary, json_file_path):
    with open(json_file_path, 'w') as json_file:
        json.dump(dictionary, json_file, indent=4, sort_keys=True)
save_to_json(dictionary_bitgenia,f'{PATH}data/real/bitgenia.json')
save_to_json(dictionary_clinvar,f'{PATH}data/real/clinvar.json')
## }}}


## {{{

#TODO empezar a hacer funciones que me digan cuántos mph e iph tienen cada
# uno de los sets

with open(f'{PATH}data/real/bitgenia.json','r') as f:
    bitgenia = json.load(f)

with open(f'{PATH}data/real/clinvar.json','r') as f:
    clinvar = json.load(f)

bitgenia_total_phenotypes = [len(phen_set) for phen_set in bitgenia.values()]
clinvar_total_phenotypes = [len(phen_set) for phen_set in clinvar.values()]

with plt.style.context(['science','ieee','nature']):
    fig, (ax1,ax2) = plt.subplots(1,2)

    ax1.hist(bitgenia_total_phenotypes,bins=20,alpha=.7)
    ax1.set_title("Bitgenia")
    ax1.set_xlabel("Fenotipos observados totales (N)",size=4)
    ax1.set_ylabel("Frecuencia",size=4)
    ax1.axvline(x=np.mean(bitgenia_total_phenotypes),linestyle="--",
            label=f"media $={np.round(np.mean(bitgenia_total_phenotypes),2)}$")
    ax1.tick_params(axis='both',which='major',labelsize=3)
    ax1.legend(fontsize=5)
    ax1.text(20,60,f"std $= {np.round(np.std(bitgenia_total_phenotypes),2)}$",fontsize=4)

    ax2.hist(clinvar_total_phenotypes,bins=20,alpha=.7)
    ax2.set_title("Clinvar")
    ax2.set_xlabel("Fenotipos observados totales (N)",size=4)
    ax2.axvline(x=np.mean(clinvar_total_phenotypes),linestyle="--",
            label=f"media $={np.round(np.mean(clinvar_total_phenotypes),2)}$")
    ax2.tick_params(axis='both',which='major',labelsize=3)
    ax2.legend(fontsize=5)
    ax2.text(25,360,f"std $= {np.round(np.std(clinvar_total_phenotypes),2)}$",fontsize=4)
## }}}


## {{{ Ahora es hora de empezar a ver las distribuciones de mph e iph

"""
En esta parte vamos a utilizar el diccionario phenotype_gene_dict.json y para
cada gen, vamos a hacer la resta entre FO de bitgenia o clinvar, y F
registrados para ese gen.
"""
with open (f"{PATH}data/simulated/phenotype_gene_dict.json",'r') as f:
    phenotype_gene_dict = json.load(f)
    for phen in phenotype_gene_dict:
        phenotype_gene_dict[phen] = [int(gene.split(':')[-1])
                for gene in phenotype_gene_dict[phen]]

def ruidos_reales(db_curada,db_real):
    """
    Esta función calcula la cantidad de mph que hay en una base de datos real
    """
    mph = []
    iph = []
    for gene in db_real:
        phens_curados = list(db_curada[db_curada[2] == gene][0].values)
        phens_curados = [int(phen.split(':')[-1]) for phen in phens_curados]
        phens_reales = db_real[gene]
        mph.append((len(phens_curados) -
                len(set(phens_curados).intersection(set(phens_reales))))/
                len(set(phens_reales).union(set(phens_curados))))
        iph.append(((len(phens_reales)) -
                len(set(phens_curados).intersection(set(phens_reales))))/
                len(set(phens_reales).union(set(phens_curados))))

    return mph , iph


with open(f'{PATH}data/phenotype_to_genes.txt','r') as file:
    reader = csv.reader(file,delimiter='\t')
    df = pd.DataFrame(reader)


mph,iph = ruidos_reales(df,bitgenia)

## }}}


## {{{ plotting

with plt.style.context(['science','ieee','nature']):
    fig, ax1 = plt.subplots()
    ax1.boxplot([mph,iph],flierprops=dict(markerfacecolor='r', markersize=0.4))
    ax1.set_xticklabels(['mph', 'iph'])
    ax1.set_ylabel("$\%$")
    ax1.set_xlabel("Tipos de ruido",fontsize=5)
    ax1.set_title(f"Ruidos reales de Bitgenia",fontsize=6)
    ax1.text(1.5,0.95,f"mph $= {np.round(np.mean(mph),3)}\pm {np.round(np.std(mph),3)}$",fontsize=4)
    ax1.text(1.5,0.84,f"iph $= {np.round(np.mean(iph),3)}\pm {np.round(np.std(iph),3)}$",fontsize=4)

## }}}


## {{{ Explorando especificidad de los fenotipos reales
with open(f'{PATH}data/real/clinvar.json','r') as f:
    clinvar = json.load(f)

with open(f'{PATH}data/real/bitgenia.json','r') as f:
    bitgenia = json.load(f)

with open(f'{PATH}/config/phen_properties.csv','r') as file:
    phen_prop = pd.read_csv(file,comment='#',sep='\t')
    phen_childrens = phen_prop.set_index('Unnamed: 0')['num_children'].to_dict()
    phen_ancestors = phen_prop.set_index('Unnamed: 0')['num_ancestors'].to_dict()
    phen_weights = phen_prop.set_index('Unnamed: 0')['a/(a+c)'].to_dict()
    phen_freqs = phen_prop.set_index('Unnamed: 0')['frecuencia relativa'].to_dict()

with open(f'{PATH}data/simulated/gene_phenotype_dict.json','r') as file:
    gold_standard = json.load(file)
# bitgenia_childrens = [children for children in phen_childrens.values()]

bitgenia_childrens = []
for phens in bitgenia.values():
    for phen in phens:
        try:
            bitgenia_childrens.append(phen_childrens[phen])
        except:
            continue
bitgenia_ancestors = []
for phens in bitgenia.values():
    for phen in phens:
        try:
            bitgenia_ancestors.append(phen_ancestors[phen])
        except:
            continue
bitgenia_weights = []
for phens in bitgenia.values():
    for phen in phens:
        try:
            bitgenia_weights.append(phen_weights[phen])
        except:
            continue
bitgenia_freqs = []
for phens in bitgenia.values():
    for phen in phens:
        try:
            bitgenia_freqs.append(phen_freqs[phen])
        except:
            continue



clinvar_childrens = []
for phens in clinvar.values():
    for phen in phens:
        try:
            clinvar_childrens.append(phen_childrens[phen])
        except:
            continue

clinvar_ancestors = []
for phens in clinvar.values():
    for phen in phens:
        try:
            clinvar_ancestors.append(phen_ancestors[phen])
        except:
            continue

clinvar_weights = []
for phens in clinvar.values():
    for phen in phens:
        try:
            clinvar_weights.append(phen_weights[phen])
        except:
            continue

clinvar_freqs = []
for phens in clinvar.values():
    for phen in phens:
        try:
            clinvar_freqs.append(phen_freqs[phen])
        except:
            continue



gold_standard_childrens = []
for phens in gold_standard.values():
    for phen in phens:
        try:
            gold_standard_childrens.append(phen_childrens[phen])
        except:
            continue

gold_standard_ancestors = []
for phens in gold_standard.values():
    for phen in phens:
        try:
            gold_standard_ancestors.append(phen_ancestors[phen])
        except:
            continue

gold_standard_weights = []
for phens in gold_standard.values():
    for phen in phens:
        try:
            gold_standard_weights.append(phen_weights[phen])
        except:
            continue
gold_standard_freqs = []
for phens in gold_standard.values():
    for phen in phens:
        try:
            gold_standard_freqs.append(phen_freqs[phen])
        except:
            continue

## }}}

## {{{





# Pre-calculated means
bitgenia = [np.mean(bitgenia_childrens),np.mean(bitgenia_ancestors),np.nanmean(bitgenia_weights),np.nanmean(bitgenia_freqs)]
clinvar = [np.mean(clinvar_childrens),np.mean(clinvar_ancestors),np.nanmean(clinvar_weights),np.nanmean(clinvar_freqs)]
gold_standard = [np.nanmean(gold_standard_childrens), np.nanmean(gold_standard_ancestors), np.nanmean(gold_standard_weights),np.nanmean(gold_standard_freqs)]


bitgenia_std = [np.std(bitgenia_childrens), np.std(bitgenia_ancestors)]
clinvar_std = [np.std(clinvar_childrens), np.std(clinvar_ancestors)]



# Setting the bar widths
bar_width = 0.3

# Setting the positions of the bars on x axis
r = np.arange(len(bitgenia))

# with plt.style.context(['science','ieee','nature']):
    # fig,ax = plt.subplots()
    # ax.bar(0, bitgenia[0],  width=bar_width,
            # label='Media hijos',alpha=.7)
    # ax.bar(0.3, bitgenia[1], width=bar_width,
            # label='Media ancestros',alpha=.7)
    # ax.bar(1, clinvar[0], width=bar_width,
            # alpha=.7,color='black')
    # ax.bar(1.3, clinvar[1], width=bar_width,
            # alpha=.7,color='r')
    # ax.bar(2, gold_standard[0], width=bar_width,
            # alpha=.7,color='black')
    # ax.bar(2.3, gold_standard[1], width=bar_width,
            # alpha=.7,color='r')

    # # Adding xticks
    # # ax.set_xlabel('Groups', fontweight='bold')
    # ax.set_xticks([0.15,1.15,2.15], ['Bitgenia', 'Clinvar','Gold standard'])

    # ax.legend(fontsize=4.5)

    # # ax.show()
# with plt.style.context(['science','ieee','nature']):
    # fig,ax = plt.subplots()
    # ax.bar('Bitgenia', bitgenia[2],  width=bar_width,alpha=.7,
            # yerr=np.nanstd(bitgenia_weights))
    # ax.bar('Clinvar', clinvar[2], width=bar_width,
            # alpha=.7,color='black',
            # yerr=np.nanstd(clinvar_weights))
    # ax.bar('Gold\nStandard', gold_standard[2], width=bar_width,
            # alpha=.7,color='black',
            # yerr=np.nanstd(gold_standard_weights))
    # ax.set_title('Media de $a/(a+c)$ para cada base de datos',fontsize=6)

with plt.style.context(['science','ieee','nature']):
    fig,ax = plt.subplots()
    ax.bar('Bitgenia', bitgenia[3],  width=bar_width,alpha=.7)
    ax.bar('Clinvar', clinvar[3], width=bar_width,alpha=.7,color='black')
    ax.bar('Gold\nStandard', gold_standard[3], width=bar_width,alpha=.7,color='black')
    ax.set_title('Media de la frecuencia de aparición \nde los fenotipos registrados',fontsize=5)
## }}}
