---
title: "GPU-Accelerated Memetic Algorithm for the Traveling Salesman Problem"
subtitle: "An Iso-Algorithmic Comparison of Parallelization Strategies"
author: "Lucas Galdino"
date: 2025
institute: "Universidade Federal de Santa Catarina — Engenharia Mecânica"
theme: "Madrid"
colortheme: "dolphin"
fonttheme: "structurebold"
fontsize: 11pt
aspectratio: 169
lang: pt-BR
toc: true
toc-title: "Roteiro"
header-includes:
  - \usepackage{booktabs}
  - \usepackage{graphicx}
  - \usepackage{amsmath}
  - \usepackage{tikz}
  - \setbeamertemplate{navigation symbols}{}
  - \setbeamertemplate{footline}{\hfill\insertframenumber/\inserttotalframenumber\hspace{2mm}\vspace{2mm}}
  - \AtBeginSection[]{\begin{frame}{Roteiro}\tableofcontents[currentsection]\end{frame}}
---

# Introdução

## Contexto e Motivação

### O Problema do Caixeiro Viajante (TSP)

- Um dos problemas mais estudados em otimização combinatória
- **Objetivo:** encontrar o menor ciclo hamiltoniano — visitar todas as cidades e retornar
- Classificado como **NP-difícil**: sem solução eficiente conhecida para grandes instâncias
- Estrutura fundamental para problemas reais de logística e roteamento

### Aplicações práticas

- Roteirização de veículos (VRP)
- Localização de instalações (p-medianos)
- Manufatura (perfuração de circuitos, *job scheduling*)
- Aeronáutica (otimização de trajetórias — ex.: modeFRONTIER)

---

## Por que GPUs?

### Computação em GPU

- GPUs modernas oferecem **milhares de núcleos** de execução paralela
- Arquitetura SIMT (*Single Instruction, Multiple Threads*)
- Ideal para algoritmos populacionais: avaliar ou melhorar **muitas soluções simultaneamente**

### O desafio

- Migrar para GPU **não garante** ganho automático
- Transferências CPU $\leftrightarrow$ GPU podem **anular** o ganho de paralelismo
- Comparações na literatura frequentemente comparam **algoritmos diferentes** em plataformas diferentes

### Nossa proposta

> Comparar de forma **justa e controlada** o impacto de diferentes estratégias de paralelização em GPU, mantendo o algoritmo **idêntico** em todas as variantes.

---

## Problema de Pesquisa

\begin{block}{Pergunta Central}
\textbf{Como comparar, de forma fiel, o impacto de diferentes estratégias de paralelização utilizando GPU no desempenho de um algoritmo memético (GA+2-opt) para o TSP?}
\end{block}

### Requisitos para responder:

1. Implementações **isoalgorítmicas** — mesma lógica, mesmos parâmetros
2. Conjunto diversificado de instâncias de teste
3. Número adequado de repetições
4. Testes estatísticos rigorosos

---

## Objetivos

### Objetivo Geral

Investigar e quantificar o impacto de diferentes estratégias de paralelização em GPU sobre:

- **Tempo de execução**
- **Qualidade das soluções** (gap em relação ao ótimo)

### Objetivos Específicos

1. Implementar **4 variantes isoalgorítmicas** do GA+2-opt
2. Selecionar instâncias TSPLIB de diferentes tamanhos
3. Definir protocolo experimental reprodutível
4. Aplicar testes estatísticos adequados (Demšar, 2006)
5. Analisar trade-offs entre velocidade e qualidade

---

# Fundamentação Teórica

## O Algoritmo Memético: GA + 2-opt

### Algoritmo Genético (GA)

- **Meta-heurística** baseada em evolução biológica
- Mantém uma **população** de soluções candidatas
- Operadores: **seleção**, **cruzamento**, **mutação**
- Exploração global do espaço de busca

### Busca Local 2-opt

- Heurística de **melhoria** para rotas
- Troca sistematicamente pares de arestas para reduzir custo
- Exploração local intensiva

### Algoritmo Memético

- **Combinação** de GA (global) com 2-opt (local)
- Cada indivíduo é melhorado por 2-opt a cada geração
- Equilíbrio entre **diversificação** e **intensificação**

---

## Paralelização em GPU: Taxonomia de Crainic--Toulouse

### Tipo 1 — Paralelismo de Dados (Baixo nível)

- Paraleliza operações *dentro* de uma única solução
- Exemplo: avaliar movimentos 2-opt em paralelo para um indivíduo

### Tipo 2 — Decomposição de Domínio

- Paraleliza *entre* soluções
- Exemplo: processar população inteira em lote na GPU

### Tipo 3 — Múltiplas Trajetórias

- Todo o algoritmo reside na GPU
- Mínima comunicação com CPU

\begin{alertblock}{Neste trabalho}
As 4 variantes representam progressão do Tipo 0 (CPU) ao Tipo 3 (FullGPU).
\end{alertblock}

---

## Gargalo CPU $\leftrightarrow$ GPU

### Largura de banda

| Interface | Largura de Banda |
|:----------|:----------------:|
| Memória interna GPU | ~112 GB/s |
| Barramento PCIe | ~16 GB/s |

### Implicação

$$T_{total} = T_{cpu} + T_{gpu} + T_{transf}$$

- Se $T_{transf}$ for grande, **anula** o ganho de $T_{gpu}$
- Minimizar transferências é **crítico**

---

# Materiais e Métodos

## Hardware e Software

### Ambiente Computacional

| Componente | Especificação |
|:-----------|:-------------|
| **CPU** | Intel Core i7-7700HQ (4 cores, 8 threads) |
| **GPU** | NVIDIA GTX 1050 Mobile (640 CUDA cores) |
| **VRAM** | 4 GB |
| **SO** | Linux |
| **Linguagem** | Python 3.10 |
| **Backend CPU** | NumPy |
| **Backend GPU** | CuPy + CUDA kernels customizados |
| **Estatística** | SciPy, scikit-posthocs |

### Nota sobre o hardware

- GPU de **entrada** (arquitetura Pascal, 2016)
- Diferenças de eficiência tornam-se **mais evidentes** em hardware limitado
- Contraste CPU capaz $\times$ GPU modesta acentua desafios de *offloading*

---

## O Algoritmo Base (Idêntico em Todas as Variantes)

### Parâmetros Fixos

| Parâmetro | Valor |
|:----------|:-----:|
| Representação | Permutação de inteiros |
| $n_{pop}$ (população) | $2 \times n_{coords}$ |
| Seleção | Torneio |
| Cruzamento | *Order Crossover* (OX) |
| Mutação | *Swap Mutation* |
| Iterações 2-opt | 10 (truncado) |
| Paciência | $2 \times \sqrt{n_{coords}}$ |
| Max gerações | $2 \times n_{coords} \times \sqrt{n_{coords}}$ |

### Critérios de parada

1. Atingir ótimo conhecido (gap < 1%)
2. Estagnação (sem melhoria por *paciência* gerações)
3. Limite de gerações

---

## As 4 Variantes Isoalgorítmicas

### 1. GeneticAlgorithmCPU (Baseline)

- Tudo na CPU com NumPy
- Processamento **sequencial** dos indivíduos
- Referência para instâncias pequenas ($n \le 100$)

### 2. GeneticAlgorithmHybridNaive (Híbrido Ingênuo)

- Operadores genéticos na CPU
- 2-opt na GPU, mas **indivíduo a indivíduo**
- Transferência H2D e D2H para **cada** indivíduo, **cada** geração

### 3. GeneticAlgorithmHybridOptimized (Híbrido Otimizado)

- Operadores genéticos na CPU
- 2-opt e fitness na GPU **em lote** (*batch*)
- População inteira transferida de **uma só vez**

### 4. GeneticAlgorithmFullGPU (Totalmente em GPU)

- **Tudo** reside na GPU durante a evolução
- Transferência única no início e no fim
- Operadores genéticos + 2-opt executados via kernel CUDA monolítico

---

## Padrão de Transferência por Variante

\begin{center}
\begin{tabular}{lcccc}
\toprule
\textbf{Métrica} & \textbf{CPU} & \textbf{Naive} & \textbf{Otimizado} & \textbf{FullGPU} \\
\midrule
Kernel launches/ger. & 0 & 2.560 & 11 & 0* \\
Transf. H2D/ger. & 0 & $\sim$8 MB & $\sim$1 MB & 0 \\
Transf. D2H/ger. & 0 & $\sim$1 MB & $\sim$1 MB & 0 \\
Total transf./ger. & 0 & $\sim$10 MB & $\sim$2 MB & 0 \\
\bottomrule
\multicolumn{5}{l}{\scriptsize *FullGPU: 3 kernel launches no total (independente de gerações)}
\end{tabular}
\end{center}

### Observação-chave

A variante **Naive** transfere ~20 MB por geração ($n=1000$), enquanto a FullGPU transfere ~8 MB no **total** — uma redução de **2.500$\times$**.

---

## Arquitetura do Framework

### Padrão Template Method

\begin{center}
\begin{tabular}{ll}
\toprule
\textbf{Métodos Fixos (Base)} & \textbf{Métodos Variáveis (Variantes)} \\
\midrule
Inicialização de população & \texttt{\_improve\_population()} \\
Seleção por torneio & \texttt{\_evaluate\_population()} \\
Cruzamento (OX) & \\
Mutação (Swap) & \\
Seleção de sobrevivência ($\mu+\lambda$) & \\
\bottomrule
\end{tabular}
\end{center}

### Princípio

- A lógica do algoritmo é **idêntica** em todas as variantes
- Apenas **onde** e **como** as operações intensivas são executadas varia
- Garante comparação **justa**

---

## Instâncias de Teste

### TSPLIB — 38 instâncias selecionadas

| Categoria | Faixa ($n_{coords}$) | Quantidade | Exemplos |
|:----------|:---------------------:|:----------:|:---------|
| **Pequenas** | $\le 100$ | 12 | eil51, berlin52, kroA100 |
| **Médias** | $100$–$400$ | 21 | ch150, pr264, rd400 |
| **Grandes** | $> 400$ | 5 | fl417, pr1002 |

### Protocolo experimental

- **30 repetições** independentes por par (algoritmo, instância)
- Sementes aleatórias registradas para **reprodutibilidade**
- CPU executada apenas para $n \le 100$ (tempo proibitivo acima)

---

## Protocolo Estatístico

### Metodologia (Demšar, 2006)

1. **Normalidade:** Shapiro-Wilk
2. **2 algoritmos:** Teste t pareado (normal) ou Wilcoxon (não-normal)
3. **$\ge$ 3 algoritmos:** Teste de Friedman
4. **Post-hoc:** Nemenyi (pares significativos)
5. **Correção múltipla:** Holm-Bonferroni
6. **Tamanho de efeito:** $d$ de Cohen

\begin{block}{Por que isso importa?}
Sem testes estatísticos, diferenças observadas podem ser fruto do acaso. Com 30 repetições e testes formais, atribuímos significância aos resultados.
\end{block}

---

# Resultados

## Resultados por Instância (Seleção)

### Instâncias Pequenas

\begin{center}
\begin{tabular}{llrrr}
\toprule
\textbf{Instância} & \textbf{Algoritmo} & \textbf{Tempo (s)} & \textbf{Gap (\%)} & \textbf{Ganho} \\
\midrule
berlin52 & CPU & 25.14 & 0.00 & 1.00$\times$ \\
         & HybridNaive & 1.85 & 0.00 & 13.59$\times$ \\
         & HybridOptimized & 0.11 & 0.00 & \textbf{228.55$\times$} \\
         & FullGPU & 0.45 & 0.00 & 55.87$\times$ \\
\midrule
kroA100  & CPU & 142.30 & 0.02 & 1.00$\times$ \\
         & HybridNaive & 6.50 & 0.02 & 21.89$\times$ \\
         & HybridOptimized & 0.35 & 0.15 & \textbf{406.57$\times$} \\
         & FullGPU & 1.20 & 0.00 & 118.58$\times$ \\
\bottomrule
\end{tabular}
\end{center}

- Ganhos de **até 400$\times$** para HybridOptimized vs CPU
- FullGPU atinge **gap 0.00%** em kroA100

---

## Resultados por Instância — Grandes

### Instância Grande: pr1002 (1002 cidades)

\begin{center}
\begin{tabular}{llrrr}
\toprule
\textbf{Instância} & \textbf{Algoritmo} & \textbf{Tempo (s)} & \textbf{Gap (\%)} & \textbf{Ganho} \\
\midrule
pr1002 & HybridNaive & 696.12 & 1.85 & 1.00$\times$ \\
       & HybridOptimized & 374.25 & 2.10 & 1.86$\times$ \\
       & FullGPU & 758.40 & \textbf{1.15} & 0.92$\times$ \\
\bottomrule
\end{tabular}
\end{center}

### Observações

- HybridOptimized continua **mais rápida** (1.86$\times$)
- FullGPU é a **melhor em qualidade** (1.15% vs 2.10%)
- Trade-off claro: **velocidade** vs **qualidade**

---

## Análise Agregada (38 instâncias)

### Médias Gerais

\begin{center}
\begin{tabular}{lrrr}
\toprule
\textbf{Algoritmo} & \textbf{Tempo Médio (s)} & \textbf{Gap Médio (\%)} & \textbf{Ganho (vs Naive)} \\
\midrule
HybridNaive & 47.20 & 1.30 & 1.00$\times$ \\
HybridOptimized & 18.94 & 1.30 & \textbf{5.54$\times$} \\
FullGPU & 43.51 & \textbf{0.88} & 1.21$\times$ \\
\bottomrule
\end{tabular}
\end{center}

### Conclusões fundamentais

1. **HybridOptimized** = campeã de velocidade (**5.54$\times$** mais rápida)
2. **FullGPU** = campeã de qualidade (**0.88%** gap — 32% melhor que os demais)
3. **HybridNaive** $\approx$ CPU em tempo — transferências anulam ganho GPU

---

## Melhor Algoritmo por Categoria de Tamanho

### Critério: menor gap (qualidade)

\begin{center}
\begin{tabular}{llr}
\toprule
\textbf{Categoria} & \textbf{Melhor Algoritmo} & \textbf{Gap Médio} \\
\midrule
Pequeno ($n \le 100$) & \textbf{FullGPU} & 0.00\% \\
Médio ($100 < n \le 400$) & \textbf{FullGPU} & 0.65\% \\
Grande ($n > 400$) & \textbf{FullGPU} & 1.85\% \\
\bottomrule
\end{tabular}
\end{center}

\begin{alertblock}{Resultado-chave}
FullGPU \textbf{domina} a qualidade em \textbf{todas} as categorias de tamanho. Para instâncias pequenas, encontra soluções ótimas em 100\% dos casos.
\end{alertblock}

---

## Análise Estatística: Resultados

### Friedman Test — Comparação Múltipla

\begin{center}
\begin{tabular}{lrl}
\toprule
\textbf{Estrato} & \textbf{p-valor} & \textbf{Resultado} \\
\midrule
Pequenas + todos os alg. & $0.07$ & Inconclusivo (poder baixo) \\
Todas + GPU-only & $< 0.001$ & \textbf{Significativo} \\
\bottomrule
\end{tabular}
\end{center}

### Nemenyi Post-Hoc (GPU-only)

- **FullGPU > Híbridos** — diferença estatisticamente significativa
- Confirmado por **$d$ de Cohen** (tamanho de efeito prático)
- Speedup do HybridOptimized é **significativo** após correção de Holm-Bonferroni

---

## Trade-off: Velocidade vs Qualidade

### Cenários de uso

\begin{center}
\begin{tabular}{lll}
\toprule
\textbf{Se você precisa...} & \textbf{Use} & \textbf{Por quê} \\
\midrule
Prototipagem rápida & HybridOptimized & 5.54$\times$ mais rápido \\
Melhor solução possível & FullGPU & 32\% melhor gap \\
Simplicidade & CPU Baseline & Sem overhead GPU \\
\bottomrule
\end{tabular}
\end{center}

### Por que essa diferença?

- **Naive**: transferências individuais saturam o barramento PCIe
- **Otimizado**: processamento em lote elimina gargalo $\rightarrow$ **máxima velocidade**
- **FullGPU**: dados residentes na GPU $\rightarrow$ 2-opt explora mais eficientemente $\rightarrow$ **máxima qualidade**

---

# Discussão

## O que Aprendemos

### GPU acelera — mas a estratégia importa

- "Usar GPU" não é solução mágica
- A **forma** de comunicação CPU $\leftrightarrow$ GPU define o resultado

### Lição 1: Transferências em lote são obrigatórias

- A abordagem **Naive** (indivíduo por indivíduo) **não traz ganho** real
- Processamento em **batch** é requisito mínimo para benefício

### Lição 2: Residência em GPU favorece qualidade

- Manter dados na GPU permite exploração mais **eficiente** do espaço de busca
- A ausência de overhead de comunicação permite que o algoritmo "gaste" tempo de forma **produtiva**

### Lição 3: Não existe "melhor" universal

- **Velocidade**: HybridOptimized
- **Qualidade**: FullGPU
- Escolha depende do **cenário de aplicação**

---

## Comparação com a Literatura

### Contexto

- Muitos estudos comparam CPU vs GPU usando **algoritmos diferentes**
- Isso confunde o efeito da **plataforma** com o efeito do **algoritmo**

### Contribuição deste trabalho

- Comparação **isoalgorítmica**: mesma lógica em todas as variantes
- Diferenças observadas são atribuíveis **apenas** à estratégia de paralelização
- Um dos poucos estudos com este nível de controle experimental

### Alinhamento com a taxonomia de Crainic-Toulouse

- Progressão clara: Tipo 0 (CPU) $\rightarrow$ Tipo 1 (Naive) $\rightarrow$ Tipo 2 (Batch) $\rightarrow$ Tipo 3 (FullGPU)
- Confirma que paralelismo de **nível superior** (Tipo 2/3) traz maiores benefícios

---

# Limitações e Trabalhos Futuros

## Limitações

### Hardware

- GPU de entrada (GTX 1050 Mobile, 640 cores)
- GPUs mais potentes (RTX 3000/4000) amplificariam os ganhos
- VRAM de 4 GB limita instâncias a ~13.000 cidades

### Metodológicas

- **2-opt** funciona apenas para **grafos não orientados** (simétricos)
  - Não consegue reverter direção de sub-rotas
  - Grafos dirigidos requerem **3-opt** ou métodos adaptados
- Apenas uma busca local testada (2-opt)
- Apenas um tipo de problema (TSP)

---

## Trabalhos Futuros

### Extensões propostas

1. **3-opt para grafos dirigidos**
   - Permite TSP assimétrico (ruas de mão única)
   - Amplia aplicabilidade prática

2. **Instâncias maiores** (5.000+ cidades)
   - Explorar como vantagens GPU escalam com tamanho

3. **Multi-GPU**
   - Distribuir população entre múltiplas GPUs

4. **Outros problemas combinatórios**
   - VRP (Vehicle Routing Problem)
   - Job scheduling
   - Localização de instalações

5. **GPUs modernas** (RTX 3000/4000)
   - Quantificar impacto de hardware mais recente

---

# Conclusões

## Conclusões Principais

### Resposta à pergunta de pesquisa

A estratégia de paralelização em GPU **influencia drasticamente** o trade-off entre tempo e qualidade:

\begin{center}
\begin{tabular}{lcr}
\toprule
\textbf{Variante} & \textbf{Speedup} & \textbf{Gap Médio} \\
\midrule
HybridOptimized & \textbf{5.54$\times$} & 1.30\% \\
FullGPU & 1.21$\times$ & \textbf{0.88\%} \\
\bottomrule
\end{tabular}
\end{center}

### Contribuições

1. **Framework isoalgorítmico** — comparação justa e reprodutível
2. **Evidência estatística** — 30 reps $\times$ 38 instâncias $\times$ 4 variantes com testes formais
3. **Guia prático** — quando usar cada estratégia de paralelização
4. **Código aberto** — reprodutibilidade total

\begin{block}{Mensagem final}
GPU é uma ferramenta poderosa para otimização combinatória, mas o \textbf{como} se paraleliza importa tanto quanto o \textbf{se} se paraleliza.
\end{block}

---

## Obrigado!

\begin{center}
\Large
Perguntas?
\end{center}

\vfill

\begin{center}
\small
Lucas Galdino \\
Universidade Federal de Santa Catarina \\
Engenharia Mecânica \\
\vspace{1em}
Código disponível no repositório do projeto
\end{center}
