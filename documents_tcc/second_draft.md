---
title: "GPU-Accelerated Isoalgorítmico GA+2-opt para TSP"
author: "Lucas Galdino"
date: 2025-11-22
lang: pt-BR
bibliography:
   - ./refs.bib
reference-section-title: "Referências"
link-citations: true
---

- [Capítulo 1 – Introdução](#capítulo-1--introdução)
  - [1.1 Contexto e motivação](#11-contexto-e-motivação)
  - [1.2 Problema de pesquisa](#12-problema-de-pesquisa)
  - [1.3 Objetivo geral](#13-objetivo-geral)
  - [1.4 Objetivos específicos](#14-objetivos-específicos)
  - [1.5 Justificativa](#15-justificativa)
- [Capítulo 2 - Revisão bibliográfica](#capítulo-2---revisão-bibliográfica)
  - [2. Fundamentação teórica e revisão bibliográfica](#2-fundamentação-teórica-e-revisão-bibliográfica)
    - [2.1 Otimização combinatória e o Problema do Caixeiro Viajante](#21-otimização-combinatória-e-o-problema-do-caixeiro-viajante)
    - [2.2 Heurísticas para o TSP](#22-heurísticas-para-o-tsp)
    - [2.3 Algoritmos genéticos e heurísticas híbridas](#23-algoritmos-genéticos-e-heurísticas-híbridas)
    - [2.4 Computação em GPU e paralelização de meta-heurísticas](#24-computação-em-gpu-e-paralelização-de-meta-heurísticas)
    - [2.5 Comparação estatística de algoritmos de otimização](#25-comparação-estatística-de-algoritmos-de-otimização)

## Capítulo 1 – Introdução

### 1.1 Contexto e motivação

O Problema do Caixeiro Viajante (Traveling Salesman Problem – TSP) é um dos problemas mais estudados em otimização combinatória [@cook2012pursuit]. Tem esse nome devida a sua história clássica: um vendedor precisa visitar um conjunto de cidades, passando por cada uma exatamente uma vez, e deseja minimizar a distância total percorrida.

O objetivo é encontrar um ciclo hamiltoniano (ciclo onde deve-se passar por todos os vértices uma vez e retornar ao vértice original). Apesar de sua formulação simples, o TSP é NP-difícil (que é um problema sem solução em tempo polinomial) e, na sua formulação de decisão: "existe um tour com custo menor ou igual a $B$?", é NP-completo: não se conhece algoritmo em tempo polinomial que o resolva em geral, embora seja fácil verificar o custo de uma solução candidata. Cook [@cook2012pursuit] argumenta que essa combinação de simplicidade, dificuldade teórica e rica estrutura geométrica faz do TSP um estudo de caso central tanto para a teoria da complexidade quanto para desenvolvimento de métodos exatos e heurísticos.

Na prática, variantes do TSP aparecem em domínios como roteirização de veículos, planejamento de inspeções, manufatura e testes de circuitos, genômica e astronomia, entre outros [@cook2012pursuit]. Exemplos clássicos incluem o posicionamento e ordenamento de furos em placas de circuito impresso, kogística e problemas de mapeamento genético. Mesmo quando modelos reais são mais complexos (com janelas de tempo, múltiplos veículos ou restrições de capacidade), é comum validar ideias de projeto e análise de algoritmos primeiro em instâncias clássicas do TSP, justamente pela ampla disponibilidade de referências, testes padronizados e de soluções ótimas conhecidas.

Paralelamente, a evolução do hardware trouxe processadores gráficos (GPUs) como plataforma acessível para computação de alto desempenho (HPC) [@nvidia2024cuda] e com a popularização e acessibilidade, pesquisas nestas áreas cresceram rapidamente. As IAs generativas são totalmente dependentes desse tipo de hardware, por exemplo.

GPUs oferecem milhares de núcleos relativamente simples, organizados em um modelo de execução massivamente paralelo, mais próximo do paradigma SIMD/SIMT descrito por Flynn e extensões modernas [@flynn1972taxonomy; @almasi2002high]. Em troca de um controle mais restrito nos fluxos de processo e memória, essas arquiteturas entregam uma grande largura de banda de memória (comunicação entre CPUs e GPUs) e uma grande taxa de operações aritméticas por segundo (FLOPs), desde que o problema ofereça operações semelhantes que possam ser executadas em paralelo, sejam elas utilizando paralelismos funcionais (mais complexos) e paralelismos de dados (mais simples). Isso torna GPUs particularmente atrativas para tarefas como o cálculo de matrizes (ganho exponencial, como demonstrado nesse trabalho), a avaliação de grandes populações de soluções e a aplicação de movimentos de vizinhança independentes em heurísticas de melhoria.

Do ponto de vista das meta-heurísticas, Crainic e Toulouse propõem uma taxonomia de paralelização que distingue, em linhas gerais, paralelismo em dados, paralelismo funcional e esquemas com múltiplas trajetórias cooperativas [@crainic2003parallel; @crainic2010parallel]. De forma simplificada, pode-se falar em três tipos:

1. paralelismo *dados* (por exemplo, várias soluções de uma população sendo avaliadas em paralelo);
2. paralelismo em *tarefas* dentro de uma mesma trajetória de busca (por exemplo, vizinhanças sendo exploradas em paralelo para uma solução corrente);  
3. paralelismo que mantêm várias trajetórias completas de busca (estratégias de início simultâneo, modelos em ilhas, busca cooperativa).

O projeto desta monografia explora principalmente  algoritmos do tipo 1, ao explorar paralelismo em dados em vizinhanças de 2-opt e na avaliação de populações em algoritmos genéticos, em linha com estudos recentes sobre heurísticas para TSP em GPU [@schulz2013gpu; @tsp_gpu; @fujimoto2011highly].

Ainda assim, nem todo algoritmo se beneficia automaticamente de uma migração para GPU. Inicializações de kernels, movimentação de dados entre CPU e GPU podem anular ganhos de paralelismo, especialmente em problemas de porte pequeno ou em implementações que realizam pouco trabalho por inicializações de kernel [@van2013gpu; @luong2013gpu]. Limitações de memória (VRAM) devem ser cuidadosamente calculadas para que a memória total ocupada não passe do limite do hardware. Nesses cenários, uma comparação direta entre versões em CPU e GPU exige cuidado extra: deve-se isolar o impacto da plataforma de execução sem confundir o efeito com mudanças na lógica do algoritmo. Ao longo deste trabalho, esses desafios são documentados explicitamente em estudos de caso, onde kernels são chamados de forma não cautelosa e versões otimizadas (Capítulos 3 e 4), bem como em notas técnicas específicas sobre *overhead* de lançamentos de kernel e padrões de redução em GPU.

Este trabalho insere-se nesse contexto, investigando como acelerar, utilizando GPU, um Algoritmo Genético (Genetic Algorithm – GA) híbrido com 2-opt para o TSP, de forma controlada e estatisticamente rigorosa,
>[!caution]
>
> - que métodos? ainda não analisamos os dados, nem sabemos se realmente iremos utilizar todos.
> - deixar esta nota aqui até resolução.
usando instâncias clássicas da biblioteca TSPLIB [@reinelt1991tsplib]. A combinação entre GA e busca local é um exemplo de algoritmo memético amplamente estudado na literatura [@larranaga1999genetic; @goldberg1989genetic], em que operadores evolutivos globais são complementados por heurísticas de melhoria como 2-opt [@croes1958method] ou Lin–Kernighan [@lin1973efficient]. Neste Trabalho de Conclusão de Curso, usarei a nomenclatura em inglês para alguns termos técnicos como "2-opt", "TSPLIB", "GPU", "CPU" e "GA".

### 1.2 Problema de pesquisa

Muitos estudos em computação de alto desempenho comparam algoritmos em CPU e GPU utilizando implementações que diferem não apenas na plataforma de execução, mas também em detalhes relevantes da lógica do algoritmo (por exemplo, operadores distintos, parâmetros diferentes ou vizinhanças não equivalentes) [@schulz2013gpu; @van2013gpu; @benaini2018genetic]. Isso torna difícil atribuir ganhos de desempenho exclusivamente ao uso da GPU, uma vez que alterações no desenho algorítmico ou na parametrização podem, por si só, explicar diferenças observadas. Parâmteros escolhidos serão discutidos no capítulo 3 `>[!caution] fazer o link para pula para o capítulo 3, de forma que seja renderizada em pandoc como um link em pdf no latex`

Neste trabalho, busquei implementar os algoritmos sob as mesmas condições. A estrutura dos algoritmos busca ser idêntica e otimizada tanto para CPU, quanto para GPU, de forma justa, para todos os Algoritmos Genéticos, assim como para o algoritmo de busca local 2-opt, variando apenas a forma como cada "módulo" estrutural do algoritmo é inserido durante o processo de execução e como ele será exectudao: Através de paralelismo ou não. A pergunta central pode ser formulada da seguinte forma:

> **Como comparar, de forma fiel, o impacto de diferentes estratégias de paralelização utilizando GPU no desempenho de um Algoritmo Memético (GA+2-opt) `>[!caution] Introduzir o conceito de algoritmo memético mais acime e referenciar` para o Problema do Caixeiro Viajante?**

Responder a essa pergunta exige, ao mesmo tempo, um desenho experimental cuidadoso de hiperparâmetros e validade estatística (número significativo de instâncias, número adequado de repetições, métricas de qualidade e tempo). Os parâmetros básicos dos GAs (tamanho de população $n_{pop}$, taxa de mutação $\dot{m}$ `>[!caution] adicionar os símbolos matemáticos próprios ao katex, usar o símbolo conforme literatura para taxa de mutação`, torneio $k$, iterações de 2-opt) $n_{rep}$ são escolhidos com base em recomendações da literatura de algoritmos evolutivos [@eiben2015introduction; @goldberg1989genetic] e em análises específicas documentadas nos relatórios técnicos do projeto (Capítulo 3). `>[!caution] fazer o link para pula para o capítulo 3, de forma que seja renderizada em pandoc como um link em pdf no latex`

### 1.3 Objetivo geral

O objetivo geral deste trabalho é:

> **Investigar e quantificar, o impacto de diferentes estratégias de paralelização em GPU, seguindo a taxonomia de [@Crainic2003] -> tipos 1,2,3 sobre o tempo de execução e a qualidade das soluções de um Algoritmo Genético híbrido com 2-opt aplicado ao Problema do Caixeiro Viajante.**

> [!caution]
> mais detalhado. Objetivo muito fora do padrão, traduzido ao pé da letra. Objetivo não

> [!ULTRACAUTION]
> a citação de autores deve ser feita corretamente, com o sobrenome e o ano, conforme as normas ABNT. Deve assegurar que as fontes  realmente dize isso. Também, senti falta dos documentos principais e mais densos. #read-pdf [crainic2003parallel](../documentation/pdfs/Parallel_Strategies_for_Meta-Heuristics.pdf), #websearch and #fetch [article{crainic2010parallel](../documentation/refs.bib#L696-L706) [designing_parallel_metaheuristics](../documentation/pdfs/designin-parallel-heuristics.pdf). Não há paenas paralelismo funcional e

### 1.4 Objetivos específicos

Para viabilizar o objetivo geral, definem-se os seguintes objetivos específicos:

1. **Implementar quatro variações isoalgorítmicas** de um Algoritmo Genético híbrido com 2-opt para o TSP, que diferem apenas na forma e no local de execução (CPU ou GPU):
   - uma versão executada puramente no CPU (**GA-CPU**), em que todas as operações (seleção, cruzamento, mutação, 2-opt e cálculo de custo) são executadas com NumPy, servindo como referência sequencial; linkar com o capítulo 3 `>[!caution] fazer o link para pula para o capítulo 3, de forma que seja renderizada em pandoc como um link em pdf no latex; Tem certeza que são are ferência sequencial? leia [full_benchmark results](./code/benchmarks/results/full_benchmark.log)`;
   - uma versão híbrida com 2-opt executada na GPU e avaliação em CPU (**GA-Híbrido-TransferênciaCompleta**), que inicia kernels **individualmente** para cada rota e transfere as soluções (ou tours) completos entre CPU e GPU a cada iteração;
   - uma versão híbrida otimizada (**GA-Híbrido-Batch**), em que 2-opt e o cálculo de custos são executados em GPU em lote (*batch*), reduzindo o número de lançamentos de kernel e o volume de dados transferidos;
   - uma versão totalmente em GPU (**GA-FullGPU**), na qual população, operadores genéticos, busca local e avaliação permanecem residentes na GPU durante toda a evolução.

   >[!caution]
   > - id: chap3
   > - description: Fazer o link para o capítulo 3, onde a arquitetura do framework. Não gostei dos nomes. Deve ter diagrama
   > - mantenha essa nota aqui até resolução.
2. **Selecionar um conjunto de instâncias da TSPLIB** com diferentes faixas de tamanho (pequenas $n_{coords} \leq 100$, médias $100 < n_{coords} \leq 500$ e grandes $n_{coords} > 500$), de forma a demonstrar os imensos ganhos de peroformance que podem ser atingidos e tendo  diversidade suficiente para análise de ganhos em escala, tendo apenas um leve ajuste na prática de agrupamento utilizada em estudos prévios com TSPLIB [@reinelt1991tsplib].
3. **Definir um protocolo experimental reprodutível**, incluindo número de repetições por instância e algoritmo, critérios de parada, parâmetros do GA e limites práticos impostos pela capacidade de memória da GPU. O desenho desse protocolo segue recomendações da literatura de comparação de algoritmos e de testes estatísticos [@demsar2006statistical] e é detalhado no Capítulo 3 `[!caution] Link with chapter 3`.
4. **Aplicar um conjunto de testes estatísticos apropriados** para comparação de algoritmos, incluindo testes de normalidade (Shapiro–Wilk), testes pareados paramétricos (teste *t* pareado) e não paramétricos (Wilcoxon), análise de rankings em múltiplas instâncias (teste de Friedman com pós-teste de Nemenyi) e medidas de tamanho de efeito (Cohen *d*), conforme recomendações em @demsar2006statistical e literatura correlata de teste de hipóteses.
   >[!caution]
   > - essa nota fica aqui até resolução final sobre o algoritmo utilizado. Algoritmo base é, depois de 100 iterações, o `GAnaive + 2-opt.`
   > - Adicionar ao capiúlo 3 a seção de metodologia estatística utilizada.
5. **Analisar os resultados obtidos**, discutindo as possíveis condições (tamanho da instância $n_{coords}$, relação entre custo de comunicação e custo de computação padrões de acesso à memória)
   >[!caution]
   >add proper latex and prper reference for nvidiacuda D2H, H2D. Appendix could have code/pseudocode.`

   cada variação isoalgorítmica é vantajosa, os limites práticos do uso de GPU neste contexto e as implicações para o projeto de algoritmos de roteamento em cenários reais, à luz das diretrizes para paralelização de meta-heurísticas [@crainic2003parallel; @alba2005parallel] e de estudos de caso em roteamento em GPU [@schulz2013gpu; @tsp_gpu; @fujimoto2011highly].

### 1.5 Justificativa

Do ponto de vista científico, o TSP continua sendo um problema de referência para avaliar novas ideias em heurísticas e meta-heurísticas [@cook2012pursuit]. A vasta disponibilidade de estudos, instâncias utilizadas em larga escala e muitas soluções ótimas conhecidas, em particular as fornecidas pela TSPLIB [@reinelt1991tsplib], na qual o projeto se baseia, permite medir o desempenho de diferentes algoritmos tanto em termos de qualidade quanto em tempo de execução.
>[!caution]
>
>- adicionar variáveis katex em inglês com subindices. Pode introduzir depois, mas algumas já  podem ir sendo pré-definidas. Usar n_{coords} para número de coordenadas, n_{pop} para tamanho de população. variáveis para transferEncia de dados, tempo de execução, etc.
>- id: chap3
>- description: adicionar cálculos e explicação para controle de memória de cada algoritmo no capítulo 3

No campo da computação de alto desempenho, diferentes trabalhos relatam ganhos relevantes ao portar heurísticas de melhoria e algoritmos evolutivos para GPU, inclusive em variantes do TSP [@schulz2013gpu; @tsp_gpu; @fujimoto2011highly]. Esses resultados indicam que GPUs são um hardware promissor para esse tipo de algoritmo, mas também evidenciam um problema recorrente: em muitas comparações, as versões em CPU e GPU diferem não apenas na plataforma de execução, mas também em detalhes de implementação e parametrização, o que dificulta isolar o efeito específico da paralelização.

Além disso, para que conclusões sobre desempenho sejam confiáveis, não basta observar poucos experimentos isolados. É necessário adotar um desenho experimental com múltiplas repetições, tanto para instâncias quanto para, medidas de dispersão e testes de hipótese adequados, como discutido na literatura de comparação de algoritmos [@demsar2006statistical]. Neste trabalho, esses cuidados são incorporados ao experimento, de modo que as diferenças observadas entre variantes em CPU e GPU possam ser atribuídas, com maior segurança, às estratégias de paralelização avaliadas.

Este trabalho justifica-se, portanto, por combinar três elementos que, em conjunto, fortalecem a contribuição científica:

1. **Implementação de heurísticas clássicas em GPU** (particularmente 2-opt e operadores do AG), explorando o paralelismo de forma explícita.
2. **Comparação entre variantes funcionalmente equivalentes do algoritmo em CPU e GPU**, mantendo fixos operadores, parâmetros e critérios de parada, de modo a isolar o efeito da plataforma de execução.
3. **Aplicação de metodologia estatística rigorosa**, com múltiplas repetições por instância, testes de hipótese adequados e medidas de tamanho de efeito.

Os capítulos seguintes discutem, à luz desses três eixos, em que condições cada variante é vantajosa, quais são os limites práticos do uso de GPU neste contexto e como os resultados dialogam com estudos prévios de heurísticas em GPU.

> [!note] ainda verei se usarei ou não essa nota
>
> ## 1.6 Organização do traba
>
> Este texto está organizado da seguinte forma:
>
> - **Capítulo 2 – Fundamentação Teórica / Revisão Bibliográfica**: apresenta os conceitos básicos de otimização combinatória e do TSP, revisa heurísticas de construção e melhoria (com ênfase em 2-opt), discute algoritmos genéticos e meta-heurísticas híbridas, introduz princípios de computação em GPU e paralelização de meta-heurísticas, e resume abordagens estatísticas para comparação de algoritmos.
> - **Capítulo 3 – Materiais e Métodos**: descreve o ambiente computacional, a arquitetura do framework desenvolvido (incluindo abstrações de backend e estratégias isoalgorítmicas), os detalhes do Algoritmo Genético híbrido com 2-opt nas quatro variantes consideradas, o conjunto de instâncias TSPLIB utilizado, os parâmetros experimentais e o protocolo estatístico adotado.
> - **Capítulo 4 – Resultados**: apresenta os resultados numéricos dos experimentos, incluindo estatísticas por instância, análises agregadas por faixa de tamanho, medidas de speedup e qualidade das soluções, além da interpretação dos testes estatísticos aplicados.
> - **Capítulo 5 – Discussão**: interpreta criticamente os resultados à luz da literatura, discute as implicações dos achados para o projeto de algoritmos de roteamento em GPU e analisa limitações do estudo.
> - **Capítulo 6 – Conclusões e Trabalhos Futuros**: sintetiza as principais contribuições do trabalho, responde explicitamente aos objetivos propostos e indica possíveis extensões, como a aplicação do framework a problemas de roteirização mais complexos.
> - Elementos pós-textuais, como referências, glossário, apêndices técnicos e anexos com tabelas completas de resultados, são apresentados ao final do documento, conforme normas da instituição.

## Capítulo 2 - Revisão bibliográfica

### 2. Fundamentação teórica e revisão bibliográfica

Este capítulo apresenta conceitos teóricos e a bibliografia utilizada para contextualizar o problema estudado e as escolhas metodológicas adotadas. São discutidos o Problema do Caixeiro Viajante (TSP) no contexto da otimização combinatória[@properref], sua importância geral e exemplos de utilização. Também serão discutidas generalizações do problema[@properref], heurísticas e metaheurísticas clássicas para o TSP[@roperrefs], aprofundando-se então no tópico de algoritmos genéticos e algoritmos meméticos[@properrefs], princípios de computação em GPU[@properref] e taxonomias de paralelização de meta-heurísticas[@properrefs], além de noções básicas de comparação estatística de algoritmos de otimização[@properrefs].
>[!caution]
>por favor, adicionar as referências aqui, para cada situação

#### 2.1 Otimização combinatória e o Problema do Caixeiro Viajante

O TSP pode ser formulado, na versão simétrica[^1], como um problema de encontrar um ciclo hamiltoniano de custo mínimo — podendo este ser a distância percorrida, combustível gasto, ou mesmo uma combinação de fatores. Para fins deste trabalho, o custo será também chamado de distância — em um grafo completo não direcionado $G = (V, E)$, no qual cada vértice em $V$ representa uma cidade e cada aresta $(i, j) \in E$ possui um custo $c_{ij} \geq 0$ entre as cidades $i$ e $j$ [@cook2012pursuit]. O objetivo é determinar uma combinação das cidades que minimize a soma total dos custos, retornando à cidade de origem. Geralmente em aplicações práticas assume-se que a matriz de custos é métrica e euclidiana, isto é, os custos derivam de distâncias euclidianas entre coordenadas no plano.

[^1]: Na versão assimétrica do TSP, os custos de viagem entre pares de cidades podem diferir dependendo da direção (ou seja, $c_{ij} \neq c_{ji}$). Em TSPs simétricos, o custo do cálculo de distâncias pode ser representadas por uma matriz triangular, diminuindo os cálculos de $n^2$ para $(n)(n+1)/2$.
      >[!caution]
      >Eu não tenho certeza da fórmula, por favor, checar.

Do ponto de vista da complexidade, o TSP é um problema NP-difícil em sua forma de otimização e NP-completo em sua forma de decisão [@cook2012pursuit]. Isso significa que, em geral, não se conhece um algoritmo em tempo polinomial que resolva instâncias arbitrárias em grande escala. Mesmo que seja relativamente fácil verificar o custo de uma ou várias soluções candidatas, não podemos afirmar que esta é solução a exata em tempo polinomial. Algoritmos modernos como `Held-Karp` [@held1962dynamic] com uma complexidade $O(n^2 2^n)$ e o algoritmo `Concorde` [@cook2012pursuit] com uma complexidade indefinida, conseguem resolver instâncias com milhares de cidades [^2], mas seu tempo de execução cresce exponencialmente (ainda melhor que a força bruta (n-1)) com o tamanho do problema, tornando-os impraticáveis para instâncias muito grandes.

[^2]: O algoritmo Held-Karp "troca" a complexidade temporal da força bruta $O(n!)$ por uma complexidade espacial $O(n 2^n)$, tornando sua viabilidade limitada a $\sim{40}$ problemas. Já o algoritmo Concorde, baseado em técnicas de ramificação e corte, é capaz de resolver instâncias com até 85.900 cidades, mas seu desempenho depende fortemente da estrutura específica da instância [@cook2012pursuit].

Ao longo das últimas décadas, o TSP consolidou-se também como um padrão de avaliação empírica de algoritmos, graças à disponibilidade de coleções de instâncias padronizadas, como a TSPLIB [@reinelt1991tsplib]. Essas coleções incluem instâncias com diferentes tamanhos, estruturas e origens (geográficas, sintéticas, industriais), A maioria delas com soluções ótimas conhecidas e obtidas por métodos exatos. No presente trabalho, são utilizadas algumas dessas instâncias como base para avaliar e comparar heurísticas e variantes paralelas de um Algoritmo Memético (algoritmos evolucionários a técnicas de busca locais) [@properrefs].

#### 2.2 Heurísticas para o TSP

Devido à dificuldade de resolver instâncias grandes do TSP exatamente, uma vasta literatura de heurísticas tem sido desenvolvida para produzir boas soluções em tempos de computação aceitáveis [@cook2012pursuit,@otherrefs]. De forma geral, heurísticas podem ser agrupadas em dois grandes tipos: heurísticas de construção e heurísticas de melhoria.

Heurísticas de construção produzem uma solução viável “do zero”, frequentemente seguindo regras simples, também algoritmos gulosos, como escolher iterativamente o vizinho mais próximo ou inserir cidades em posições que causem o menor aumento de custo. Exemplos incluem a heurística do vizinho mais próximo (nearest neighbor — NN), heurísticas de inserção (insertion heuristics) e variantes baseadas em árvores de extensão mínimas (Minimum Spanning Trees — MSTs), como o Algoritmo de Christofides. Embora rápidas e fáceis de implementar, essas estratégias tendem a gerar soluções de qualidade moderada, servindo sobretudo como ponto de partida para métodos mais sofisticados. Simchi et al. [@simchi2005logic] demonstra que algumas dessas soluções garantem uma solução $H^*$ não maior que $1.5\times$ o custo ótimo $B^*$, em casos específicos.
>[!caution] Citações necessárias
>citar ainda [@simchi2005logic] e os cálculos de upper bounds e lower bounds relacionados -> capítulos 4 e 5 do livro. #read-pdf [simchi-levi](../documentation/pdfs/simchi2005logic.pdf)

Heurísticas de melhoria partem de uma solução inicial e aplicam sucessivos movimentos locais que procuram reduzir seu custo. Entre essas, as chamadas $k$-opt são particularmente influentes: um movimento $2$-opt consiste em remover duas arestas de um tour e reconectar os segmentos resultantes de modo a eliminar cruzamentos e reduzir o comprimento total [@croes1958method];
>[!caution]
>2-opt movements really only affect crossings? As long as I know, it does not affect only crosses. Please, better explain this.

movimentos $3$-opt e extensões mais complexas, como o algoritmo de Lin–Kernighan, generalizam essa ideia [@lin1973efficient]. Estas e outras heurísticas de melhoria desempenham papel central em muitos algoritmos modernos para TSP, tanto como procedimentos isolados quanto como componentes de meta-heurísticas, sendo utiliados como procedimentos de busca local.

Neste trabalho, a heurística 2-opt é utilizada como busca local básica acoplada ao Algoritmo Genético, em linha com diversos estudos que combinam heurísticas de construção simples com procedimentos de melhoria mais intensivos para obter soluções de alta qualidade em tempo razoável [@addproperrefs].

#### 2.3 Algoritmos genéticos e heurísticas híbridas

Algoritmos Genéticos (Genetic Algorithms – GAs) são meta-heurísticas inspiradas em princípios de evolução biológica, nas quais uma população de soluções candidatas é iterativamente modificada por operadores análogos à seleção natural, recombinação e mutação [@goldberg1989genetic; @eiben2015introduction]. Na sua forma mais simples, um AG mantém uma população de indivíduos representando soluções para o problema; em cada geração, indivíduos são selecionados com base em uma função de aptidão (fitness), recombinados por operadores de cruzamento e perturbados por operadores de mutação. A nova população resultante substitui total ou parcialmente a anterior, e o processo se repete até que um critério de parada seja satisfeito.

No contexto do TSP, é comum representar cada solução como uma permutação das cidades, utilizar operadores de cruzamento especializados para rotas — como Order Crossover (OX), Partially Matched Crossover (PMX), entre outros — e empregar mutações que preservem a viabilidade da permutação, como trocas de posição entre duas cidades [@larranaga1999genetic]. Estudos clássicos mostram que GAs podem produzir soluções competitivas para o TSP quando combinados com operadores e parâmetros adequados [@goldberg1989genetic].

Uma extensão importante dessa ideia é o conceito de algoritmos meméticos, nos quais operadores evolutivos (seleção, cruzamento, mutação) são combinados com heurísticas de busca local aplicadas a indivíduos da população [@larranaga1999genetic]. Em problemas de roteamento, isso resulta em esquemas GA+LS, nos quais um GA guia a exploração global do espaço de soluções e um procedimento de melhoria, como 2-opt ou Lin–Kernighan, refina soluções promissoras. Trabalhos como o de Fujimoto e Tsutsui [@fujimoto2011highly] tiveram uma grande influência na decisão do tema e exploram justamente essa combinação para o TSP em ambientes de computação paralela, motivando a adoção de uma abordagem semelhante neste estudo.

#### 2.4 Computação em GPU e paralelização de meta-heurísticas

Processadores gráficos (GPUs) evoluíram, nas últimas décadas, de dispositivos voltados principalmente para renderização gráfica para plataformas de computação de uso geral (GPGPU), amplamente utilizadas em aplicações científicas e de inteligência artificial [@nvidia2024cuda]. O modelo de programação CUDA, por exemplo, organiza o trabalho em grades (*grids*) de blocos de threads, seguindo um paradigma de execução massivamente paralelo próximo ao SIMT (Single Instruction, Multiple Threads), relacionado às classificações de arquiteturas de Flynn [@flynn1972taxonomy; @almasi2002high]. Nessa configuração, milhares de threads executam o mesmo kernel sobre dados distintos, o que é adequado a tarefas com alto grau de paralelismo em dados.
>[!caution]
>revisar amanhã

Crainic e Toulouse propuseram uma taxonomia para paralelização de meta-heurísticas que as distingue em três grandes tipos: abordagens que exploram paralelismo em dados (neste trabalho, usadas intercaladamente como *P-Data*), paralelismo em tarefas (neste trabalho, usadas intercaladamente como *P-Tasks*) e esquemas com trajetórias de busca cooperativas [@crainic2003parallel; @crainic2010parallel]. No **tipo 1**, avaliações de soluções, cálculos de custo e procedimentos de busca local, principalmente quando cálculos de matrizes estão envolvidas, são distribuídos entre vários processadores (paralelismo em CPU, por exemplo usando os vários núcleos do processador) ou threads (GPUs, modelo SIMT). No **tipo 2**, diferentes partes ou fases de um mesmo algoritmo são executadas em paralelo; no **tipo 3**, múltiplas execuções (trajetórias) de uma meta-heurística interagem por meio de mecanismos de cooperação, como modelos em ilhas ou memórias compartilhadas.
>[!caution]
>preciso revisar essa part amanha, sobre os tipos 1,2,3.
>Parece ir contra o que eu tinha entendido antes.

Aplicações de GPU a meta-heurísticas para o TSP exploram principalmente paralelismo em dados, seja na avaliação em massa de rotas em algoritmos genéticos (através de cálculos de redução), seja aplicando paralelismo a movimentos de vizinhança em heurísticas de melhoria [@schulz2013gpu; @tsp_gpu; @fujimoto2011highly]. Outros trabalhos investigam paralelização de Simulated Annealing, Colônias de Formigas (ACO) e outras meta-heurísticas em GPU, geralmente aproveitando o grande número de threads para explorar múltiplas soluções ou vizinhanças em cada passo da busca [@addproperrefs]. Esses estudos motivam o uso de GPUs como plataforma para acelerar algoritmos meméticos,

```markdown
mas também evidenciam desafios relacionados a movimentação de dados entre CPU e GPU,  
escolha de granularidade adequada de kernels e limitações de memória.
```

>[!caution]
> adicionar mais informações sobre esses desafios, linkar com o próximo capítulo.

#### 2.5 Comparação estatística de algoritmos de otimização

Meta-heurísticas estocásticas, como GAs e algoritmos meméticos, produzem resultados que variam de execução para execução devido ao uso de aleatoriedade em diversos pontos (inicialização, seleção, mutação, entre outros). Por esse motivo, a comparação de algoritmos de otimização não pode se basear em uma única execução por instância, tampouco apenas em médias simples sem qualquer análise de variabilidade. A literatura de comparação de algoritmos enfatiza a importância de utilizar múltiplas instâncias de teste, múltiplas repetições por combinação algoritmo–instância e métricas que considerem tanto qualidade da solução quanto tempo de execução [@demsar2006statistical].

Demšar [@demsar2006statistical] discute procedimentos estatísticos apropriados para comparar algoritmos em vários problemas, recomendando o uso de testes de hipótese pareados (como o teste *t* pareado ou o teste de Wilcoxon) quando se deseja comparar dois algoritmos em uma coleção de instâncias, e testes baseados em rankings, como o teste de Friedman seguido de pós-testes de Nemenyi, quando mais de dois algoritmos são avaliados simultaneamente. Medidas de tamanho de efeito, como o *d* de Cohen, complementam a análise ao quantificar a magnitude prática das diferenças observadas.

Neste trabalho, esses princípios gerais orientam o desenho experimental e a análise dos resultados apresentados nos capítulos seguintes, garantindo que as comparações entre variantes em CPU e GPU sejam realizadas de forma estatisticamente fundamentada.
