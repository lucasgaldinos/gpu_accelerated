Completed: *Design full TCC chapter skeleton* (5/7)

Here’s a concrete, UFSC-compliant skeleton for your thesis, aligned with the *real* scope (TSP + GA+2-opt, 4 iso-algorithmic variants, chapter4_validation benchmark).

I’ll also point out, for each chapter, what should be *moved / reused / rewritten* from first_draft.md and the technical_decisions docs.

---

## 1. Front matter (pré-textuais)

You already have most of this; main change is updating the **Resumo/Abstract** to the GA+2-opt/TSP scope.

- Capa, folha de rosto, ficha catalográfica, folha de aprovação, dedicatória, agradecimentos (as required by UFSC).
- **Resumo** (PT-BR, máx. 250–300 palavras)
  - Foco: TSP, GA+2-opt, comparação CPU vs 3 variantes GPU (HybridNaive, HybridOptimized, FullGPU), 38 instâncias TSPLIB, metodologia estatística (30 repetições, Friedman + Nemenyi, etc.).
  - Remove VRP and SA do escopo principal (podem aparecer só em 1 frase de contexto ou trabalhos futuros).
- **Abstract** (EN, espelho do resumo).
- **Lista de Figuras, Tabelas, Abreviaturas, Símbolos**  
  - Reaproveitar listas do first_draft.md, mas:
    - Podar símbolos/abreviaturas só de VRP e algoritmos não implementados (Tabu, ACO, etc.) ou movê-los para *Apêndice* se forem citados apenas em trabalhos futuros.
- **Sumário**  
  - Atualizar ao final, quando a estrutura abaixo estiver fixa.

---

## 2. Capítulo 1 – Introdução

**Objetivo**: responder às perguntas de problema/justificativa/objetivos do `roteiro_analise_critica.md`.

### 1.1 Contexto e motivação

- TSP como benchmark clássico de otimização combinatória.
- Crescimento do tamanho das instâncias e custo de metaheurísticas.
- GPUs como plataforma massivamente paralela para acelerar heurísticas de roteamento.
- Reaproveitar a abertura do Cap. 1 do first_draft.md, mas:
  - Cortar ênfase em VRP como escopo principal.
  - Manter VRP apenas como motivação e *trabalhos futuros*.

### 1.2 Problema de pesquisa

- Formulação clara, em português simples, algo como:
  - “Como comparar, de forma isoalgorítmica e estatisticamente rigorosa, o impacto de diferentes estratégias de paralelização em GPU para um Algoritmo Genético híbrido com 2-opt aplicado ao TSP?”
- Aqui você já “vende” que o código força algoritmos isoalgorítmicos: mesma lógica, só mudam os pontos de execução (CPU vs GPU).

### 1.3 Objetivo geral

- Ex.: “Investigar e quantificar o ganho de desempenho e o impacto na qualidade das soluções ao acelerar um Algoritmo Genético híbrido com 2-opt para TSP em GPU, usando variantes isoalgorítmicas e metodologia estatística padronizada.”

### 1.4 Objetivos específicos

Sugeridos (ajuste a gosto):

1. Implementar quatro **variações isoalgorítmicas** de GA+2-opt (CPU, HybridNaive, HybridOptimized, FullGPU).
2. Definir um conjunto representativo de instâncias TSPLIB (pequenas, médias, grandes).
3. Elaborar um protocolo experimental com $\approx 30$ repetições por instância/algoritmo.
4. Aplicar testes estatísticos (Shapiro–Wilk, t pareado/Wilcoxon, Friedman + Nemenyi, Holm–Bonferroni, Cohen’s *d*) para comparar algoritmos.
5. Discutir limites práticos (VRAM, overhead de kernel, thresholds de tamanho) e implicações para projetos reais.

### 1.5 Justificativa

- Conectar com:
  - Lacuna de estudos **reprodutíveis** comparando variantes isoalgorítmicas em GPU.
  - Falta de benchmarks que isolam ganho de paralelização vs ganho de “engenharia de algoritmo”.
  - Relevância prática (rotações em logística, mas mantendo escopo de implementação em TSP).

### 1.6 Organização do trabalho

- Breve parágrafo descrevendo o conteúdo dos Capítulos 2–6.

> **De onde vem o texto?**  
>
> - Cap. 1 do first_draft.md é a base, mas você simplifica o escopo para TSP+GA+2-opt e remove promessas de VRP/SA como resultados finais.

---

## 3. Capítulo 2 – Fundamentação Teórica / Revisão Bibliográfica

**Objetivo**: cumprir a *revisão bibliográfica* do roteiro, sem misturar demais com metodologia do seu framework.

### 2.1 Otimização combinatória e o Problema do Caixeiro Viajante

- Definição formal do TSP.
- NP-dificuldade.
- TSPLIB como conjunto padrão de instâncias.
- Referências: Cook, Reinelt etc.

### 2.2 Heurísticas para o TSP

- **Heurísticas de construção**: vizinho mais próximo, inserção, etc. (curto, pois não são o foco).
- **Heurísticas de melhoria**:
  - k-opt, com destaque para 2-opt (Croes), 3-opt, Lin–Kernighan.
  - Papel de 2-opt em metaheurísticas modernas e em memetic algorithms (GLS+FLS, etc.).

### 2.3 Algoritmos genéticos e heurísticas híbridas

- Visão geral de GA:
  - Representação, população, fitness, seleção, cruzamento, mutação.
- GA para TSP (Larrañaga, Goldberg, etc.).
- **Algoritmos meméticos / GA+LS**:
  - GA+2-opt, GA+3-opt, GA+Lin–Kernighan.
  - Citar Fujimoto & Tsutsui (GPU GA para TSP) e outros trabalhos relevantes.

### 2.4 Computação em GPU e paralelização de metaheurísticas

- Conceitos básicos de CUDA / GPU:
  - Hierarquia grid–block–thread, SIMT, memória global/compartilhada.
- Taxonomias:
  - Flynn (SISD/SIMD/MIMD).
  - Crainic & Toulouse (P-Data, S-Task, P-Task) para metaheurísticas paralelas.
- Exemplos de TSP em GPU:
  - GA, SA, ACO, 2-opt paralela, GLS, etc.

> [!important]Importante:  
>
> - Aqui você fala **dos trabalhos dos outros**, não do seu código.  
> - Parte do que hoje está em 2.4 do first_draft.md pode ficar aqui (definição de CUDA, taxonomias), mas:
>   - Os detalhes do *seu* kernel 2-opt e do *seu* framework vão para o Cap. 3.

### 2.5 Comparação estatística de algoritmos de otimização

- Por que precisamos de:
  - Múltiplas instâncias.
  - Múltiplas repetições.
- Visão geral (sem fórmulas pesadas):
  - Demšar (2006): Friedman + Nemenyi para múltiplos algoritmos.
  - Testes pareados (t, Wilcoxon) para comparações por instância.
  - Conceito de tamanho de efeito (Cohen’s *d*).

> **De onde vem o texto?**  
>
> - Adaptar e condensar trechos da `statistical_tests_comprehensive_guide.md` (parte conceitual).  
> - Detalhes matemáticos (PDFs, funções gama) podem ir para apêndice.

---

## 4. Capítulo 3 – Materiais e Métodos

Este é o coração metodológico, e deve usar:

- `GA_HYPERPARAMETER_TUNING_AND_PERFORMANCE_BENCHMARKS.md`
- `GPU_2OPT_INTEGRATION_ANALYSIS.md`
- `statistical_tests_comprehensive_guide.md`
- `insights.md`
- `missing_decisions.md`

### 3.1 Ambiente computacional

- **Hardware**:
  - CPU: Intel Core i7-7700HQ
    >[!caution]
    >add proper specs.
  - RAM: 16 GB DDR4.
  - GPU: NVIDIA GeForce GTX 1050 Mobile (4 GB GDDR5 VRAM).
- **Software**:
  - Sistema Operacional: Linux (debian 13).
  - Linguagem: Python 3.10.16.
  - Bibliotecas Principais:
    - NumPy 2.26 (CPU)
    - cupy-cuda12x 13.6.0 (GPU),
    - CUDA Toolkit
      ```out
      nvcc: NVIDIA (R) Cuda compiler driver
      Built on Fri_Jun_14_16:34:21_PDT_2024
      Cuda compilation tools, release 12.6, V12.6.20
      Build cuda_12.6.r12.6/compiler.34431801_0
      ```
- **Restrições de Hardware**:
  - Limite de VRAM: Configurado para 65% da capacidade total (aprox. 2.6 GB) para evitar contenção com o sistema operacional e garantir estabilidade.
    >[!caution]
    >informação inventada e não checada. Acredito ser 80%. Você estão com presguiça de rodar comandos?

### 3.2 Arquitetura do framework

#### 3.2.1 Organização do código

- Descreve a arquitetura modular final (`benchmarks_v2` e `src/benchmarking_v2`):
  - `code/src/algorithms/{improvement, metaheuristics}`: Implementações dos algoritmos de busca local e metaheurísticas.
  - `code/src/protocols`: Definição das interfaces e do padrão `xp` para abstração de backend (NumPy/CuPy), permitindo a execução agnóstica de hardware.
  - `code/benchmarks_v2/configs`: Arquivos JSON (`algorithms.json`, `benchmark.json`, `problems.json`) que definem a matriz experimental, desacoplando a configuração da lógica.
  - `code/src/benchmarking_v2`: Lógica desacoplada para orquestração (`orchestration.py`), execução (`algorithm_runner.py`) e coleta de dados (`checkpoint_io.py`).

>[!caution]
> deve ser descritivo. Adicionar códigos, a não ser que pseudocódigos em casos pontuai, é expressamente proibido. ccaso seja necessário adicionar códigos, devem estar no apêndice.

#### 3.2.2 Representação do problema e estrutura de dados

- **Carregamento**: Instâncias TSPLIB são carregadas de um banco de dados DuckDB (`datasets/routing.duckdb`) através dos `loaders`.
- **Estrutura**: A matriz de distâncias é pré-calculada em `float64` (precisão dupla) para garantir precisão numérica.
- **Limite de VRAM**: A capacidade máxima teórica de cidades ($n$) é calculada pela fórmula $n = \sqrt{\frac{VRAM_{disponivel\_bytes}}{8}}$, resultando em $n \approx 18.000$ cidades para 2.6 GB de VRAM.
- **Padrão `ProblemContext`**: Objeto que encapsula a matriz de distâncias e a transfere para a GPU (`cp.asarray`) uma única vez por problema, evitando transferências repetidas da matriz de distância.
  >[!caution]
  >versões nào otimizadas do algoritmos devem transferir a matriz a cada geração (HybridNaive). O total de transferências de memória também será mostrado.
  >
  > é extremamente necessário que você explore os resultados em [results.duckdb](./../results/benchmark_results/results.duckdb/results.duckdb).

#### 3.2.3 Heurística de melhoria 2-opt

- **Versão CPU (NumPy)**: Avaliação vetorizada de todos os movimentos de uma vizinhança para acelerar a busca sequencial, explorando as instruções SIMD da CPU.
- **Versão GPU (CuPy + RawKernel)**:
  - Avaliação de todos os $O(n^2)$ movimentos 2-opt em paralelo.
  - **Redução**: Devido a limitações de integração do CuPy com a biblioteca CUB (CUDA Unbound), foi implementada uma redução manual eficiente em nível de bloco e warp utilizando memória compartilhada (`__shared__`) para encontrar o melhor movimento (Best Improvement).
  - *Diagrama*: Incluir diagrama de sequência ilustrando o paralelismo massivo na avaliação dos movimentos e a etapa de redução.

>[!caution]
>tá ruim demais. Isso foi propriamente documentado, já. Tem que colocar também a referência de onde veio a implementaçào disso (nvidicuda2024? mesma implementação que o CUB? quem propôs? quais kernals usam isso?)

#### 3.2.4 Algoritmo Genético base

- **Estrutura**: Representação de permutação de cidades.
  Por que eu escolhi este algoritmo OX? porque fujimoto já havia implementado e mostrado. o objetivo era a implementação e comparação entre CPU, GPU e variações dos mesmo algoritmos, focando em variações nas taxonomias propostas por Crainic & Toulouse. Outras variações podem ser implementadas. Isso pode ser citado no capítulo 6.
- **Operadores**:
  - Seleção: Torneio (Tournament Selection). Explicar certinho como funciona.
  - Cruzamento: Order Crossover (OX), preservando a ordem relativa das cidades. Explicar certinho como funciona.
  - Mutação: Swap Mutation (troca de duas cidades). Explicar certinho como funciona.

#### 3.2.5 Algoritmo Memético

- **Integração**: O algoritmo combina a exploração global do Algoritmo Genético com a exploração local intensiva do 2-opt.
- **Funcionamento**: Após a geração da nova população (cruzamento e mutação), a heurística 2-opt é aplicada a cada indivíduo (ou a uma subpopulação) para refinar a solução, levando-a a um ótimo local antes da próxima geração.
- *Diagrama*: Incluir diagrama mostrando o ciclo do Algoritmo Memético, destacando onde o 2-opt se insere no fluxo do AG.
- **Ciclo e Elitismo**: Ciclo geracional padrão com elitismo, preservando os 2 melhores indivíduos para garantir monotonicidade na convergência.
- **Critérios de Parada**:
  - **Ótimo Atingido**: A execução para se a solução atinge um valor dentro de 1% do ótimo conhecido (`cost <= best_known * 1.01`). Este relaxamento (vs. $10^{-6}$) foi adotado para acelerar a bateria de testes em problemas difíceis sem comprometer a análise de convergência.
  - **Estagnação (`patience`)**: Parâmetro adaptativo definido como `patience` = $\max(20, \lfloor 2\sqrt{n} \rfloor)$.
    - *Justificativa*: Análises empíricas mostraram que um valor fixo (e.g., 50) era excessivo para problemas pequenos (desperdício de tempo) e insuficiente para problemas grandes (parada prematura). A função da raiz quadrada escala a paciência com a complexidade do espaço de busca, mitigando a bimodalidade nos tempos de execução.
  - **Geração Máxima**: Limite superior adaptativo: $max\_gens = 14.3 \cdot n - 46$.
- *Diagrama*: Incluir fluxograma detalhado do AG Base, com notas explicativas para cada etapa (Seleção, Crossover, Mutação, Avaliação).

>[!caution]Muito simples. Este arquivo deve ser um guia.
>
> - Deve-se justificar os porquês dessas escolhas. Deve-se referenciar corretamente baseando-se nas [referências](./refs.bib). Pode-se dizer que estarão sendo melhores explicados a frente, no [subcapítulo 3.4](#34-parâmetros-experimentais)
> - Problemas encontrados e tudo o mais. Linkando com o subcapítulo onde os problemas encontrados são explicados.
> - O funcionamento de um algoritmo genético deve ser explicitada através de diagramas. O algoritmos base pode ter um flowchart com notas explicativas adicionais de cada um dos processos.
> - Umas subsessão para cada etapa do algoritmo deve ser feita.

>[!caution]
>
> - Explicacão clara sobre como o AG e o 2-opt agem dentro do algoritmo memético.
> - Como o 2-opt age na melhoria, para além do algoritmo genético.
> - diagramas do funcionamento base do algoritmo memético devem estar presentes.

#### 3.2.6 Variações isoalgorítmicas do GA

- **Conceito**: O termo "isoalgorítmico" é usado para descrever quatro variações que compartilham a mesma estrutura lógica de alto nível (definida por `GeneticAlgorithmBase`), diferindo apenas na plataforma de execução (CPU/GPU) de seus componentes (AG e 2-opt). O termo "isoalgorítmico será substituído, usando nomes como algoritmos funcionalmente equivalente, como expressado no capítulo 1.
- **Variantes**:
  1. **CPU**: AG e 2-opt executados puramente em CPU com NumPy.
  2. **HybridNaive**: AG em CPU, 2-opt em GPU. Lança um kernel CUDA separado para cada indivíduo da população. Serve para demonstrar o alto overhead de lançamento de kernels e transferência de dados.
  3. **HybridOptimized**: AG em CPU, 2-opt em GPU. Utiliza processamento em lote (Batch Processing), lançando um único kernel para processar toda a população simultaneamente, maximizando a ocupação da GPU.
  4. **FullGPU**: AG e 2-opt totalmente residentes na GPU. Minimiza drasticamente as transferências de dados entre Host e Device, mantendo a população na VRAM durante todo o processo.
- *Diagramas*: Incluir fluxogramas simples no texto principal para cada variante. Diagramas técnicos detalhados devem constar no Apêndice A.
- As variantes devem ser propriamente descritas. [Diagramas](../documentation/diagrams) simples como flowcharts devem estar no arquivo principal. Diagramas mais complexos devem estar no Apêndice A e propriamente linkados utilizando o formato pandoc.

### 3.3 Conjunto de instâncias de teste

- **Seleção**: 38 instâncias da TSPLIB, agrupadas por tamanho (Pequeno, Médio, Grande) conforme `CHAPTER4_BENCHMARK_GUIDE.md`.
- **Justificativa**: A seleção abrange uma ampla gama de tamanhos (de 51 a 4461 cidades) e inclui instâncias clássicas da literatura para garantir a comparabilidade com outros trabalhos.
- **Tabela**: Apresentar tabela com nome da instância, dimensão ($n$) e valor da melhor solução conhecida (BSF).
- Informações adicionais sobre a escolha devem ser justificadas e referenciadas.

### 3.4 Parâmetros experimentais

A escolha dos parâmetros foi guiada por recomendações clássicas (e.g., @goldberg1989genetic) e ajustada via análises empíricas (`GA_HYPERPARAMETER_TUNING...`) para o contexto específico de GPU.

- **Parâmetros Estáticos do GA**:
  - `population_size = 256`: Escolhido para garantir diversidade genética suficiente e alinhar com a arquitetura da GPU (múltiplo de 32/warp).
  - `mutation_rate = 0.02`: Taxa conservadora para manter a diversidade sem destruir esquemas promissores.
  - `tournament_size = 5`: Pressão seletiva moderada.
  >[!caution]
  >As escolhas devem estar propriamente referenciadas, acredito ser através de Goldberg nas referências.
- **Parâmetros da Busca Local**:
  - `two_opt_iterations = 100`: Aumentado de 10 para 100 após tuning.
    - *Justificativa*: 10 iterações eram insuficientes para convergência local significativa. 100 iterações oferecem um melhor compromisso entre tempo de execução e qualidade da solução refinada.
  > [!caution]
  > Explicar o que isso significa para o algoritmo e para os resultados. Por que não são utilizadas mais iterações e verificar a veracidade desta informação através da literatura.
- **Parâmetros de Execução**:
  - `seed = 42`: Para garantir a reprodutibilidade das execuções estocásticas.
    >[!caution]
    >investigue a ceracidade destas informações, as `seeds` são realmente iguais? Acredito que houve uma troca.
  - `repetitions = 30`: Número de execuções independentes por par (algoritmo, instância) para permitir análise estatística robusta, conforme recomendado por @demvsar2006statistical.

### 3.5 Metodologia estatística

- **Pipeline por Instância**:
  1. **Normalidade**: Teste de Shapiro-Wilk para verificar a distribuição dos dados (custos e tempos).
  2. **Comparação Pareada**:
      - Se normal: Teste t de Student pareado.
      - Se não-normal: Teste de Wilcoxon Signed-Rank (não-paramétrico).
  3. **Tamanho de Efeito**: Cálculo do Cohen's *d* para quantificar a magnitude da diferença, não apenas sua significância.
  4. **Correção**: Aplicação de Holm-Bonferroni para controlar a taxa de erro familiar (FWER) em múltiplas comparações.
- **Pipeline Global**:
  - Teste de Friedman para detectar diferenças entre algoritmos através de múltiplos datasets.
  - Teste Nemenyi post-hoc para identificar quais pares de algoritmos diferem significativamente no ranking global.
- **Significância**: $\alpha = 0.05$ adotado como padrão.
- *Ameaças*: Discussão sobre violações de premissas estatísticas e como foram tratadas (e.g., uso de testes robustos/não-paramétricos).

>[!caution]
>
>- linkar com [subcapitulo 3.7](#37-ameaças-à-validade-e-evolução-metodológica) onde ameaças à validade são discutidas.
>- adicionar diagrama de decisão para testes a partir de [statistical_tests_comprehensive_guide.md](../documentation/technical_decisions/statistical_tests_comprehensive_guide.md#L6420)

### 3.6 Procedimento experimental

Descreve o fluxo de trabalho do framework `benchmarks_v2`, orquestrado pelo script `code/benchmarks_v2/run_chapter4_benchmark.py`:

1. **Configuração**: Carrega as configurações dos arquivos `benchmark.json`, `algorithms.json` e `problems.json`, definindo a matriz de experimentos.
2. **Execução**: Para cada problema e cada algoritmo, o `AlgorithmRunner` executa 30 repetições independentes. A variante CPU é executada apenas para instâncias com $n < 100$ por questões de viabilidade temporal.
3. **Coleta de Dados**: O `CheckpointIO` salva os resultados de cada execução em arquivos JSON. Os dados incluem tempo de execução, custo final, gap para o ótimo, **número de gerações completadas e o motivo da parada** (e.g., `hit_optimal`, `no_improvements`).
4. **Análise e Geração de Relatórios**: Scripts auxiliares (`aggregate_statistics.py`, `report_generator.py`) processam os checkpoints para realizar a análise estatística e gerar as tabelas e gráficos para o Capítulo 4.

> [!caution]
> Temos dois tipos de benchmarks. O mais completo está na [`v2`](../code/benchmarks_v2). Mas nossos primeiros resultados foram analisados na [`v1`](../code/benchmarks)

### 3.7 Ameaças à validade e evolução metodológica

- **Evolução do Framework (v1 vs v2)**: O projeto iniciou com um framework monolítico (`benchmarks/chapter4_validation.py`). Resultados preliminares (v1) revelaram falhas na captura de metadados e rigidez nos parâmetros. O framework atual (v2) foi desenvolvido para corrigir isso, introduzindo modularidade e parâmetros adaptativos.
- **Parâmetros Empíricos**: O ajuste de `patience` e `two_opt_iterations` foi baseado em observações empíricas do comportamento do algoritmo. Embora melhore a robustez média, pode não ser ótimo para casos extremos (outliers).
- **Dureza da Instância**: Observou-se que o tamanho $n$ não é o único preditor de tempo de execução; a estrutura topológica da instância influencia a convergência. Isso introduz uma variabilidade intrínseca que modelos simples baseados em $n$ não capturam totalmente.
- **Correções**: Adoção de critérios de parada mais granulares e aumento das iterações de busca local foram correções diretas para problemas de convergência prematura observados nas fases iniciais.

>[!caution]
> Será melhor descrito no apêndice.

---

## 5. Capítulo 4 – Resultados

Este capítulo “consome” diretamente o que `chapter4_validation.py` produz, conforme CHAPTER4_BENCHMARK_GUIDE.md.

### 4.1 Validação do protocolo

- Relatar um “test run” com poucas repetições (2) apenas para mostrar que:
  - Pipeline estatístico funciona.
  - Tabelas são geradas corretamente.
- Depois, focar nos resultados com 30 repetições.

### 4.2 Estatísticas por instância

- Basear-se na **Tabela 1** (summary por problema):
  - Gap médio, desvio padrão, tempo médio, speedup.
- Apresentar:
  - Alguns casos ilustrativos (por ex. uma instância pequena, uma média, uma grande).
  - Mostrar gráficos simples: boxplots de custo, tempos, speedup por instância ou por faixa de tamanho.

### 4.3 Comparação agregada entre algoritmos

- Basear-se na **Tabela 2** (estatísticas agregadas) e **Tabela 3** (melhor algoritmo por faixa).
- Discutir:
  - Qual algoritmo domina em gap e em tempo.
  - Situações em que HybridOptimized vs FullGPU se destacam.
  - Comparação com CPU onde é aplicável.

### 4.4 Escalabilidade e speedup

- Gráficos:
  - Speedup vs número de cidades.
  - Tempo absoluto vs tamanho, separando por algoritmo.
- Relacionar:
  - Overhead de kernel → porque HybridNaive sofre.
  - Benefícios de batch 2-opt e FullGPU à medida que n cresce.

### 4.5 Qualidade das soluções e significância estatística

- Mostrar exemplos de:
  - Comparações pareadas com significância (p-valor baixo, *d* grande).
  - Casos em que diferenças são pequenas / não significativas.
- Discutir:
  - Quando GPU traz apenas ganho de tempo, sem perda de qualidade.
  - Se há trade-offs entre gap e tempo.

---

## 6. Capítulo 5 – Discussão

- Conectar os resultados com:
  - Questão de pesquisa (Cap. 1).
  - Literatura (Cap. 2).
- Tópicos sugeridos:
  - Isoalgorítmico como ferramenta para isolar impacto da plataforma.
  - Interpretação dos ganhos de speedup vs custo de implementação.
  - Comparação qualitativa com trabalhos de Fujimoto & Tsutsui e outros (sem prometer melhor/igual, mas contextualizando).
  - Limitações:
    - Só TSP, nada de VRP.
    - Uma GPU específica (GTX 1050).
    - Um conjunto limitado de parâmetros de GA.

---

## 7. Capítulo 6 – Conclusões e Trabalhos Futuros

### 6.1 Síntese das contribuições

- Reforçar:
  - Implementação das quatro variantes isoalgorítmicas.
  - Protocolo estatístico completo e reprodutível.
  - Resultados de speedup e qualidade.

### 6.2 Respostas às questões de pesquisa e objetivos

- Ponto a ponto:
  - Como cada objetivo específico foi cumprido.
  - Quais hipóteses foram apoiadas/contrariadas.

### 6.3 Trabalhos futuros

- Extensões óbvias:
  - VRP (usando mesma arquitetura).
  - Outras metaheurísticas (SA, Tabu, GLS, ILS).
  - GPUs mais modernas e multi-GPU.
  - Persistent kernels, mais otimizações de kernel.

---

## 8. Pós-textuais

- **Referências** (a partir de refs.bib).
- **Glossário** (termos como “isoalgorítmico”, “2-opt”, “warp”, etc.).
- **Apêndices**:
  - Pseudocódigos dos algoritmos (GA+2-opt, variantes).
  - Detalhes matemáticos dos testes estatísticos (PDFs, derivação de t e $\chi^2$ se você quiser).
  - Trechos de configuração de benchmark (`chapter4_validation.py`).
- **Anexos**:
  - Tabelas completas de resultados (se forem muito grandes para o corpo principal).

---

## Terminologia para “iso-algoritmos”

Sugestão consistente para o texto:

- Use “**variações isoalgorítmicas** de Algoritmos Genéticos” ou “**algoritmos isoalgorítmicos**” e defina explicitamente uma vez:
  - “Chamamos de algoritmos **isoalgorítmicos** aqueles que mantêm a mesma estrutura algorítmica (mesmos operadores, parâmetros e fluxo de controle), diferindo apenas na forma de implementação e na plataforma de execução (CPU vs GPU).”
- Depois, referir-se às quatro variantes como:
  - “GA-CPU”, “GA-HybridNaive”, “GA-HybridOptimized”, “GA-FullGPU”.

---

## Checklist atual

Com base no que já foi feito e neste esqueleto:

1. Review core thesis and analysis docs – **concluído**  
2. Inspect core algorithm and benchmark code – não iniciado  
3. Survey benchmark results and data structure – não iniciado  
4. Analyze bibliography and select key references – **concluído (base inicial)**  
5. Design full TCC chapter skeleton – **concluído (neste texto)**  
6. Plan diagrams and methodological details – ainda por fazer  
7. Produce consolidated analysis and task list document – ainda por fazer  

Se você quiser, o próximo passo é escolher um capítulo (normalmente Cap. 1 ou 3) e começar a reescrita guiada com base neste esqueleto.
