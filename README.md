# libRNXS
Biblioteca para importar arquivos RNXS para memória no python, de maneira estruturada em formato de dicionário.

#### Como usar:
Depois de estar familizado com os tipos de informações contidas no arquivo RNXS (detalhadas abaixo), execute o arquivo infoRNXS.py e leia a saída do terminal para entender como os dados são estruturados em um dicionário python.

## Descrição do tipo de arquivo `*.RNXS`

> **Nota Estrutural Geral (Branch Calculations / KEY_STATE):**
> Em todas as tabelas (Macro, Micro, Free e FDFs), os valores não são estáticos. Para cada grupo de energia, o ficheiro fornece um valor base seguido de um conjunto de variações (derivadas/branches). Estas variações ditam como a secção de choque muda em resposta a flutuações nas condições do reator (temperatura do combustível, densidade do moderador, etc.), conforme as variáveis de estado declaradas no bloco `KEY_STATE`.

---

### RNXS Não-queimáveis

**Secções de Choque Macroscópicas Homogenizadas (`! XS type:`)**
* **INV_SPD** (Inverso da Velocidade / 1/v): Usada principalmente em cálculos de cinética de reatores para determinar o tempo de geração/vida útil dos neutrões em cada grupo de energia.
* **SIG_TRP** (Transporte / Σtr​): Determina como os neutrões vazam de uma malha para outra. O inverso disto (1/3Σtr​) dá origem ao "Coeficiente de Difusão" usado nas equações do simulador nodal.
* **SIG_ABS** (Absorção Macro): A taxa total de absorção do bloco inteiro (incluindo a água e o revestimento, não apenas o combustível).
* **SIG_SP0** (Matriz de Espalhamento Isotrópico / P0​ Scattering): Trata-se de uma matriz que mostra a probabilidade de um neutrão que bate no material "abrandar" e saltar de um grupo de energia alto (ex: Grupo 1) para um mais baixo (ex: Grupo 2 ou 3).
* **SIG_KCS** (Fissão Macro Cinética): Equivale ao cálculo de potência térmica global da malha como um todo (o somatório do κΣf​ de tudo o que está lá dentro).

**Fatores de Descontinuidade de Fluxo (`! Flux DF data`)**
* **KEY_SIDEFDF** (FDF de Face): Fatores de correção matemática aplicados nas 6 faces (S1 a S6) do hexágono para garantir a conservação da corrente de nêutrons durante a homogeneização espacial.
* **KEY_CORNFDF** (FDF de Quina): Fatores aplicados aos 6 vértices (C1 a C6) do hexágono, essenciais para a reconstrução do fluxo pino a pino (pin power reconstruction) e precisão em reatores de geometria hexagonal.

---

### RNXS Não-queimáveis, mas variáveis (ex.: barra de controle dentro ou fora)

**Secções de Choque Macroscópicas Homogenizadas (`! XS type:`)**
* {...} Iguais as "RNXS Não-queimáveis", mas duplicadas:
    * `! Base tables`: barra de controle fora (tubo guia preenchido com água)
    * `! CR tables`: barra de controle dentro (tubo guia com água + barra de controle)

**Fatores de Descontinuidade de Fluxo (`! Flux DF data`)**
* {...} Iguais as "RNXS Não-queimáveis", também duplicados (pois a barra dentro altera drasticamente os fatores de descontinuidade).

---

### RNXS Combustíveis

**Fatores de Descontinuidade de Fluxo (`! Flux DF data`)**
* {...} Iguais as "RNXS Não-queimáveis", mas não variam com o burnup.

**Secções de Choque Macroscópicas Homogenizadas (`! XS type:`)**
* {...} Iguais as "RNXS Não-queimáveis", mas repetidas para múltiplos passos de queima, assim como todas abaixo.

**Secções de Choque Macroscópicas Homogenizadas "Livres"** *(Ou seja, descontando as seções de choque microscópicas abaixo - `! XS type:`)*
* **ABS_FREE** (Absorption Free): A seção de choque macroscópica de absorção (Σa​) da malha, subtraída a absorção dos isótopos rastreados (como Xe-135, Sm-149, e dependendo da modelagem, os próprios actinídeos principais). Representa a absorção "de base" da estrutura, moderador e produtos de fissão menores.
* **FIS_FREE** (Fission Free): A seção de choque macroscópica de fissão (Σf​) da mistura de base. Se o seu modelo rastreia todos os isótopos físseis (U-235, Pu-239, etc.) de forma microscópica, este valor pode ser muito próximo de zero. Ele só terá um valor significativo se o código agrupar a fissão de isótopos menores (que não estão na lista `KEY_ACTIN`) nesta variável macroscópica.
* **NFS_FREE** (Nu-Fission Free): É o termo de produção de nêutrons de base (νΣf​), livre dos isótopos rastreados. Assim como a fissão, a produção total de nêutrons no simulador será calculada somando este `NFS_FREE` com a produção calculada via densidade atômica dos actinídeos rastreados (N⋅νσf​).
* **KFS_FREE** (Kappa-Fission Free): A energia liberada por fissão (κΣf​) pela mistura de base. Usada para o cálculo de potência térmica caso haja isótopos físseis embutidos no material que não estão sendo rastreados pelo vetor isotópico dinâmico.
* **KCS_FREE** (Kinetic Cross Section Free): Similar ao `KFS_FREE`, é uma seção de choque cinética agregada livre dos venenos/rastreados. É usada muitas vezes diretamente na equação de balanço de energia do núcleo para converter o fluxo de nêutrons na malha nodal em deposição local de calor (Watts/cm³), ignorando temporariamente a parcela de energia que vem das reações dos isótopos rastreados explicitamente.
* **SP0_FREE** (Scattering P0 Free): A matriz de espalhamento isotrópico (Scattering P0​) da mistura, excluindo os isótopos rastreados. Na prática, o Xenônio e o Samário são grandes absorvedores, mas péssimos moderadores. O espalhamento é quase todo dominado pela água (Hidrogênio/Oxigênio) e pelo Grafite/Zircônio. Portanto, a matriz `SP0_FREE` conterá quase todo o comportamento de moderação (abrandamento) do nêutron, já que os isótopos responsáveis pelo espalhamento raramente precisam ser subtraídos e rastreados dinamicamente.

**Secções de Choque Microscópicas dos Actinídeos (`! Actinide XS type:`)**
* **SIG_ABS** (Absorção): A probabilidade total de o núcleo absorver o neutrão. É a soma de todas as reações de absorção (fissão + captura parasita).
* **SIG_FIS** (Fissão): A probabilidade isolada de o neutrão causar a cisão (fissão) do núcleo.
* **SIG_NFS** (Nu-Fissão / νΣf​): A secção de choque de fissão multiplicada pelo número médio de neutrões libertados por cada reação (ν). Representa a "capacidade produtiva" do isótopo.
* **SIG_KFS** (Kappa-Fissão / κΣf​): A secção de choque de fissão multiplicada pela quantidade de energia útil libertada por cada fissão (κ). Essencial para o cálculo de potência térmica distribuída.
* **SIG_CPTG** (Captura Radiativa / Capture γ): A reação (n,γ). O neutrão é "engolido" pelo núcleo, que não se fisiona, mas liberta um fotão gama para se estabilizar.
* **SIG_CPT2N** (Reação n,2n): Uma reação de limiar em que um neutrão muito rápido e energético colide com o núcleo, fazendo com que este ejete dois neutrões.

---

#### Lista de Nuclídeos

**Actinídeos (Chave: `KEY_ACTIN`) - 21 isótopos**
* **Urânio:**
    * `92234U234---` (Urânio-234)
    * `92235U235---` (Urânio-235)
    * `92236U236---` (Urânio-236)
    * `92237U237---` (Urânio-237)
    * `92238U238---` (Urânio-238)
    * `92239U239---` (Urânio-239)
* **Neptúnio:**
    * `93237NP237--` (Neptúnio-237)
    * `93238NP238--` (Neptúnio-238)
    * `93239NP239--` (Neptúnio-239)
* **Plutónio:**
    * `94238PU238--` (Plutónio-238)
    * `94239PU239--` (Plutónio-239)
    * `94240PU240--` (Plutónio-240)
    * `94241PU241--` (Plutónio-241)
    * `94242PU242--` (Plutónio-242)
* **Américo:**
    * `95241AM241--` (Américo-241)
    * `95242AM242--` (Américo-242)
    * `95342AM242M-` (Américo-242m)
    * `95243AM243--` (Américo-243)
* **Cúrio:**
    * `96242CM242--` (Cúrio-242)
    * `96243CM243--` (Cúrio-243)
    * `96244CM244--` (Cúrio-244)

**Produtos de Fissão (Chave: `KEY_FP`) - 17 isótopos**
* `44105RU105--` (Ruténio-105)
* `45105RH105--` (Ródio-105)
* `48113CD113--` (Cádmio-113)
* `53135I135---` (Iodo-135)
* `54135XE135--` (Xenónio-135)
* `56140BA140--` (Bário-140)
* `57140LA140--` (Lantânio-140)
* `60147ND147--` (Neodímio-147)
* `60148ND148--` (Neodímio-148)
* `60149ND149--` (Neodímio-149)
* `61147PM147--` (Promécio-147)
* `61148PM148--` (Promécio-148)
* `61348PM148M-` (Promécio-148m)
* `61149PM149--` (Promécio-149)
* `62147SM147--` (Samário-147)
* `62148SM148--` (Samário-148)
* `62149SM149--` (Samário-149)
