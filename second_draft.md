---
title: "GPU-Accelerated Isoalgorítmico GA+2-opt para TSP"
author: "Lucas Galdino"
date: 2025-11-22
lang: pt-BR
bibliography:
   - documentation/refs.bib
reference-section-title: "Referências"
link-citations: true
---

# Capítulo 1 – Introdução

## 1.1 Contexto e motivação

O Problema do Caixeiro Viajante (Traveling Salesman Problem – TSP) é um dos problemas mais estudados em otimização combinatória [@cook2012pursuit]. Dado um conjunto de cidades e uma matriz de distâncias simétrica, o objetivo é encontrar um ciclo hamiltoniano de custo mínimo que visite cada cidade exatamente uma vez e retorne à origem. Apesar de sua formulação simples, o TSP é NP-difícil e, na sua formulação de decisão ("existe um tour com custo menor ou igual a $B$?"), é NP-completo: não se conhece algoritmo em tempo polinomial que o resolva em geral, embora seja fácil verificar o custo de uma solução candidata. Cook [@cook2012pursuit] argumenta que essa combinação de simplicidade, dificuldade teórica e rica estrutura geométrica faz do TSP um estudo de caso central tanto para teoria da complexidade quanto para o desenvolvimento de métodos exatos e heurísticos.

Na prática, variantes do TSP aparecem em domínios como roteirização de veículos, planejamento de inspeções, manufatura e testes de circuitos, genômica e astronomia, entre outros [@cook2012pursuit]. Exemplos clássicos incluem o ordenamento de furos em placas de circuito impresso, a minimização do tempo de reposicionamento de telescópios entre alvos e problemas de mapeamento genético. Mesmo quando modelos reais são mais complexos (com janelas de tempo, múltiplos veículos ou restrições de capacidade), é comum validar ideias de projeto e análise de algoritmos primeiro em instâncias clássicas do TSP, justamente pela ampla disponibilidade de benchmarks padronizados e de soluções ótimas conhecidas.

Paralelamente, a evolução do hardware trouxe processadores gráficos (GPUs) como plataforma acessível para computação de alto desempenho [@nvidia2024cuda]. GPUs oferecem milhares de núcleos relativamente simples, organizados em um modelo de execução massivamente paralelo, mais próximo do paradigma SIMD/SIMT descrito por Flynn e extensões modernas [@flynn1972taxonomy; @almasi2002high]. Em troca de um controle mais restrito de fluxo e memória, essas arquiteturas entregam alta largura de banda de memória e uma grande taxa de operações aritméticas por segundo, desde que o problema ofereça muitas operações semelhantes que possam ser executadas em paralelo. Isso torna GPUs particularmente atrativas para tarefas como o cálculo de matrizes de distância, a avaliação de grandes populações de soluções e a aplicação de movimentos de vizinhança independentes em heurísticas de melhoria.

Do ponto de vista das meta-heurísticas, Crainic e Toulouse propõem uma taxonomia de paralelização que distingue, em linhas gerais, paralelismo em dados, paralelismo funcional e esquemas com múltiplas trajetórias cooperativas [@crainic2003parallel; @crainic2010parallel]. De forma simplificada, pode-se falar em três famílias: (i) abordagens que paralelizam os *dados* (por exemplo, várias soluções de uma população sendo avaliadas em paralelo); (ii) abordagens que paralelizam as *tarefas* dentro de uma mesma trajetória de busca (por exemplo, vizinhanças sendo exploradas em paralelo para uma solução corrente); e (iii) abordagens que mantêm várias trajetórias completas de busca (estratégias de *multistart*, modelos em ilhas, busca cooperativa). O projeto desta monografia encaixa-se principalmente na primeira família, ao explorar paralelismo em dados em vizinhanças de 2-opt e na avaliação de populações em algoritmos genéticos, em linha com estudos recentes sobre heurísticas para TSP em GPU [@schulz2013gpu; @tsp_gpu; @fujimoto2011highly].

Ainda assim, nem todo algoritmo se beneficia automaticamente de uma migração para GPU. Lançamentos frequentes de kernels, movimentação de dados entre CPU e GPU e limitações de memória (VRAM) podem anular os ganhos teóricos de paralelismo, especialmente em problemas de porte pequeno ou em implementações que realizam pouco trabalho por chamada de kernel [@van2013gpu; @luong2013gpu]. Nesses cenários, uma comparação direta entre versões em CPU e GPU exige cuidado metodológico: é preciso isolar o impacto da plataforma de execução sem confundir o efeito com mudanças na lógica do algoritmo. Ao longo deste trabalho, esses desafios são documentados explicitamente em estudos de caso de kernels ingênuos e versões otimizadas (Capítulos 3 e 4), bem como em notas técnicas específicas sobre *overhead* de lançamentos de kernel e padrões de redução em GPU.

Este trabalho insere-se nesse contexto, investigando como acelerar, utilizando GPU, um Algoritmo Genético (Genetic Algorithm – GA) híbrido com 2-opt para o TSP, de forma controlada e estatisticamente rigorosa,
>[!caution]
>
> - que métodos? ainda não analisamos os dados, nem sabemos se realmente iremos utilizar todos.
> - deixar esta nota aqui até resolução.
usando instâncias clássicas da biblioteca TSPLIB [@reinelt1991tsplib]. A combinação entre GA e busca local é um exemplo de algoritmo memético amplamente estudado na literatura [@larranaga1999genetic; @goldberg1989genetic], em que operadores evolutivos globais são complementados por heurísticas de melhoria como 2-opt [@croes1958method] ou Lin–Kernighan [@lin1973efficient]. Neste Trabalho de Conclusão de Curso, usarei a nomenclatura em inglês para alguns termos técnicos como "2-opt", "TSPLIB", "GPU", "CPU" e "GA".

## 1.2 Problema de pesquisa

Muitos estudos em computação de alto desempenho comparam algoritmos em CPU e GPU utilizando implementações que diferem não apenas na plataforma de execução, mas também em detalhes relevantes da lógica do algoritmo (por exemplo, operadores distintos, parâmetros diferentes ou vizinhanças não equivalentes) [@schulz2013gpu; @van2013gpu; @benaini2018genetic]. Isso torna difícil atribuir ganhos de desempenho exclusivamente ao uso da GPU, uma vez que alterações no desenho algorítmico ou na parametrização podem, por si só, explicar diferenças observadas. Parâmteros escolhidos serão discutidos no capítulo 3 `>[!caution] fazer o link para pula para o capítulo 3, de forma que seja renderizada em pandoc como um link em pdf no latex`

Neste trabalho, busquei implementar os algoritmos sob as mesmas condições. A estrutura dos algoritmos busca ser idêntica e otimizada tanto para CPU, quanto para GPU, de forma justa, para todos os Algoritmos Genéticos, assim como para o algoritmo de busca local 2-opt, variando apenas a forma como cada "módulo" estrutural do algoritmo é inserido durante o processo de execução e como ele será exectudao: Através de paralelismo ou não. A pergunta central pode ser formulada da seguinte forma:

> **Como comparar, de forma fiel, o impacto de diferentes estratégias de paralelização utilizando GPU no desempenho de um Algoritmo Memético (GA+2-opt) `>[!caution] Introduzir o conceito de algoritmo memético mais acime e referenciar` para o Problema do Caixeiro Viajante?**

Responder a essa pergunta exige, ao mesmo tempo, um desenho experimental cuidadoso de hiperparâmetros e validade estatística (número significativo de instâncias, número adequado de repetições, métricas de qualidade e tempo). Os parâmetros básicos dos GAs (tamanho de população $n_{pop}$, taxa de mutação $\dot{m}$ `>[!caution] adicionar os símbolos matemáticos próprios ao katex, usar o símbolo conforme literatura para taxa de mutação`, torneio $k$, iterações de 2-opt) $n_{rep}$ são escolhidos com base em recomendações da literatura de algoritmos evolutivos [@eiben2015introduction; @goldberg1989genetic] e em análises específicas documentadas nos relatórios técnicos do projeto (Capítulo 3). `>[!caution] fazer o link para pula para o capítulo 3, de forma que seja renderizada em pandoc como um link em pdf no latex`

## 1.3 Objetivo geral

O objetivo geral deste trabalho é:

> **Investigar e quantificar, o impacto de diferentes estratégias de paralelização em GPU, seguindo a taxonomia de [@Crainic2003] -> tipos 1,2,3 sobre o tempo de execução e a qualidade das soluções de um Algoritmo Genético híbrido com 2-opt aplicado ao Problema do Caixeiro Viajante.**

> [!caution]
> mais detalhado. Objetivo muito fora do padrão, traduzido ao pé da letra. Objetivo não

> [!ULTRACAUTION]
> a citação de autores deve ser feita corretamente, com o sobrenome e o ano, conforme as normas ABNT. Deve assegurar que as fontes  realmente dize isso. Também, senti falta dos documentos principais e mais densos. #read-pdf [crainic2003parallel](documentation/pdfs/Parallel_Strategies_for_Meta-Heuristics.pdf), #websearch and #fetch [@article{crainic2010parallel,](documentation/refs.bib#L696-L706) [designing_parallel_metaheuristics](documentation/pdfs/designin-parallel-heuristics.pdf). Não há paenas paralelismo funcional e

## 1.4 Objetivos específicos

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

## 1.5 Justificativa

Do ponto de vista científico, o TSP continua sendo um problema de referência para avaliar novas ideias em heurísticas e meta-heurísticas [@cook2012pursuit]. A vasta disponibilidade de estudos, instâncias utilizadas em larga escala e muitas soluções ótimas conhecidas, em particular as fornecidas pela TSPLIB [@reinelt1991tsplib], na qual o projeto se baseia, permite medir o desempenho de diferentes algoritmos tanto em termos de qualidade quanto em tempo de execução.
>[!caution]
>
>- adicionar variáveis katex em inglês com subindices. Pode introduzir depois, mas algumas já  podem ir sendo pré-definidas. Usar n_{coords} para número de coordenadas, n_{pop} para tamanho de população. variáveis para transferEncia de dados, tempo de execução, etc.
>- id: chap3
>- description: adicionar cálculos e explicação para controle de memória de cada algoritmo no capítulo 3

No campo da computação de alto desempenho, diferentes trabalhos já demonstraram ganhos relevantes ao portar heurísticas de melhoria e algoritmos evolutivos para GPU, inclusive em variantes do TSP [@schulz2013gpu; @tsp_gpu; @fujimoto2011highly]. Ainda assim, muitos desses estudos concentram-se em evidenciar o potencial de aceleração e nem sempre controlam, de forma sistemática, o efeito de mudanças na lógica algorítmica ou na parametrização entre as versões em CPU e em GPU. Quando a comparação não é feita sob condições estritamente equivalentes, torna-se difícil atribuir os ganhos medidos exclusivamente à plataforma de execução.

Outro desafio recorrente em estudos empíricos com heurísticas é garantir que as conclusões não sejam baseadas em poucas execuções ou em análises estatísticas frágeis. A literatura de comparação de algoritmos enfatiza a importância de múltiplas repetições, testes de hipótese apropriados e medidas de tamanho de efeito para distinguir diferenças reais de variações decorrentes do acaso [@demsar2006statistical].

Este trabalho justifica-se, portanto, por combinar três elementos que, em conjunto, fortalecem a contribuição científica:

1. **Implementação de heurísticas clássicas em GPU** (particularmente 2-opt e operadores do AG), explorando o paralelismo de forma explícita.
2. **Comparação entre variantes funcionalmente equivalentes do algoritmo em CPU e GPU**, mantendo fixos operadores, parâmetros e critérios de parada, de modo a isolar o efeito da plataforma de execução.
3. **Aplicação de metodologia estatística rigorosa**, com múltiplas repetições por instância, testes de hipótese adequados e medidas de tamanho de efeito, em linha com recomendações contemporâneas para comparação de algoritmos.

Os capítulos seguintes discutem, à luz desses três eixos, em que condições cada variante é vantajosa, quais são os limites práticos do uso de GPU neste contexto e como os resultados dialogam com estudos prévios de heurísticas em GPU.

> [!note] ainda verei se usarei ou não essa nota
>
> ## 1.6 Organização do trabalho
>
> Este texto está organizado da seguinte forma:
>
> - **Capítulo 2 – Fundamentação Teórica / Revisão Bibliográfica**: apresenta os conceitos básicos de otimização combinatória e do TSP, revisa heurísticas de construção e melhoria (com ênfase em 2-opt), discute algoritmos genéticos e meta-heurísticas híbridas, introduz princípios de computação em GPU e paralelização de meta-heurísticas, e resume abordagens estatísticas para comparação de algoritmos.
> - **Capítulo 3 – Materiais e Métodos**: descreve o ambiente computacional, a arquitetura do framework desenvolvido (incluindo abstrações de backend e estratégias isoalgorítmicas), os detalhes do Algoritmo Genético híbrido com 2-opt nas quatro variantes consideradas, o conjunto de instâncias TSPLIB utilizado, os parâmetros experimentais e o protocolo estatístico adotado.
> - **Capítulo 4 – Resultados**: apresenta os resultados numéricos dos experimentos, incluindo estatísticas por instância, análises agregadas por faixa de tamanho, medidas de speedup e qualidade das soluções, além da interpretação dos testes estatísticos aplicados.
> - **Capítulo 5 – Discussão**: interpreta criticamente os resultados à luz da literatura, discute as implicações dos achados para o projeto de algoritmos de roteamento em GPU e analisa limitações do estudo.
> - **Capítulo 6 – Conclusões e Trabalhos Futuros**: sintetiza as principais contribuições do trabalho, responde explicitamente aos objetivos propostos e indica possíveis extensões, como a aplicação do framework a problemas de roteirização mais complexos.
> - Elementos pós-textuais, como referências, glossário, apêndices técnicos e anexos com tabelas completas de resultados, são apresentados ao final do documento, conforme normas da instituição.
