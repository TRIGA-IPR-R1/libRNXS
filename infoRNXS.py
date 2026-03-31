import libRNXS as rn

# Imprime na tela informações da estrutura do dicionário
rn.infoRNXS()

# Importa o dicionário
nodalXS = rn.getRNXS("exemplosRNXS/26_to_6grps/FE_UZrH10_B_6grps_latXS2Nodal.rnxs")
rn.infoRNXS(nodalXS)


nodalXS = rn.getRNXS("exemplosRNXS/26_to_12grps/CR_C_Wat_B4C_12grps_latXS2Nodal.rnxs")
rn.infoRNXS(nodalXS)


nodalXS = rn.getRNXS("exemplosRNXS/26_to_26grps/CT_Wat_A_26grps_latXS2Nodal.rnxs")
rn.infoRNXS(nodalXS)
