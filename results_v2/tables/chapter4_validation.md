# Chapter 4 Validation Results

Generated: 2025-11-25 04:19:23

## Table 1: Summary Statistics by Problem

| Problem | Algorithm | Mean Cost | Std Dev | Gap (%) | Mean Time (s) | Speedup |
|:--------|:----------|----------:|--------:|--------:|--------------:|--------:|
| berlin52 | CPU | 7557.25 | 26.41 | 0.20 | 25.88 | 0.02× |
| berlin52 | FullGPU | 7542.00 | 0.00 | 0.00 | 0.30 | 1.96× |
| berlin52 | HybridNaive | 7542.00 | 0.00 | 0.00 | 0.59 | — |
| berlin52 | HybridOptimized | 7568.75 | 24.06 | 0.35 | 0.10 | 5.81× |
| bier127 | FullGPU | 118905.00 | 98.21 | 0.53 | 4.25 | 0.71× |
| bier127 | HybridNaive | 119077.00 | 247.10 | 0.67 | 3.01 | — |
| bier127 | HybridOptimized | 119050.25 | 283.12 | 0.65 | 0.60 | 5.04× |
| ch130 | FullGPU | 6147.50 | 16.50 | 0.61 | 6.42 | 0.52× |
| ch130 | HybridNaive | 6155.50 | 9.23 | 0.74 | 3.36 | — |
| ch130 | HybridOptimized | 6153.00 | 9.00 | 0.70 | 0.56 | 5.94× |
| ch150 | FullGPU | 6538.00 | 7.07 | 0.15 | 6.15 | 0.79× |
| ch150 | HybridNaive | 6584.50 | 4.03 | 0.87 | 4.88 | — |
| ch150 | HybridOptimized | 6572.75 | 11.65 | 0.69 | 0.79 | 6.21× |
| d198 | FullGPU | 15907.75 | 19.55 | 0.81 | 16.49 | 0.51× |
| d198 | HybridNaive | 15911.50 | 22.51 | 0.83 | 8.35 | — |
| d198 | HybridOptimized | 15913.25 | 26.95 | 0.84 | 1.41 | 5.94× |
| eil101 | FullGPU | 634.25 | 1.48 | 0.83 | 2.06 | 1.08× |
| eil101 | HybridNaive | 633.25 | 1.30 | 0.68 | 2.23 | — |
| eil101 | HybridOptimized | 633.75 | 1.64 | 0.76 | 0.38 | 5.79× |
| eil51 | CPU | 428.00 | 1.41 | 0.47 | 20.82 | 0.03× |
| eil51 | FullGPU | 427.50 | 0.87 | 0.35 | 0.37 | 1.77× |
| eil51 | HybridNaive | 429.00 | 1.22 | 0.70 | 0.65 | — |
| eil51 | HybridOptimized | 429.00 | 1.22 | 0.70 | 0.11 | 6.05× |
| eil76 | CPU | 540.75 | 1.79 | 0.51 | 95.35 | 0.01× |
| eil76 | FullGPU | 540.75 | 1.79 | 0.51 | 1.14 | 1.14× |
| eil76 | HybridNaive | 541.75 | 2.17 | 0.70 | 1.30 | — |
| eil76 | HybridOptimized | 540.25 | 1.79 | 0.42 | 0.23 | 5.61× |
| fl417 | FullGPU | 11982.50 | 13.16 | 1.02 | 102.26 | 0.97× |
| fl417 | HybridNaive | 12093.75 | 79.27 | 1.96 | 99.33 | — |
| fl417 | HybridOptimized | 12018.75 | 31.67 | 1.33 | 18.15 | 5.47× |
| kroA100 | CPU | 21422.50 | 67.16 | 0.66 | 197.90 | 0.01× |
| kroA100 | FullGPU | 21284.50 | 4.33 | 0.01 | 1.58 | 1.16× |
| kroA100 | HybridNaive | 21366.50 | 82.51 | 0.40 | 1.83 | — |
| kroA100 | HybridOptimized | 21367.75 | 78.47 | 0.40 | 0.29 | 6.32× |
| kroA150 | FullGPU | 26693.75 | 96.52 | 0.64 | 6.01 | 0.76× |
| kroA150 | HybridNaive | 26682.00 | 49.58 | 0.60 | 4.54 | — |
| kroA150 | HybridOptimized | 26724.50 | 18.87 | 0.76 | 0.77 | 5.87× |
| kroA200 | FullGPU | 29667.50 | 104.46 | 1.02 | 11.73 | 0.82× |
| kroA200 | HybridNaive | 29611.50 | 32.76 | 0.83 | 9.61 | — |
| kroA200 | HybridOptimized | 29557.00 | 53.01 | 0.64 | 1.58 | 6.07× |
| kroB100 | CPU | 22261.00 | 70.83 | 0.54 | 210.05 | 0.01× |
| kroB100 | FullGPU | 22230.00 | 62.53 | 0.40 | 2.18 | 0.87× |
| kroB100 | HybridNaive | 22246.50 | 83.61 | 0.48 | 1.89 | — |
| kroB100 | HybridOptimized | 22246.25 | 67.38 | 0.48 | 0.32 | 5.81× |
| kroB150 | FullGPU | 26306.00 | 67.80 | 0.67 | 7.54 | 0.59× |
| kroB150 | HybridNaive | 26344.50 | 40.40 | 0.82 | 4.45 | — |
| kroB150 | HybridOptimized | 26299.25 | 38.13 | 0.65 | 0.72 | 6.15× |
| kroC100 | CPU | 20875.00 | 49.64 | 0.61 | 199.15 | 0.01× |
| kroC100 | FullGPU | 20751.00 | 2.00 | 0.01 | 1.52 | 1.48× |
| kroC100 | HybridNaive | 20839.75 | 51.49 | 0.44 | 2.24 | — |
| kroC100 | HybridOptimized | 20806.00 | 57.07 | 0.27 | 0.36 | 6.21× |
| kroD100 | CPU | 21407.25 | 38.15 | 0.53 | 217.53 | 0.01× |
| kroD100 | FullGPU | 21396.50 | 21.03 | 0.48 | 2.03 | 0.99× |
| kroD100 | HybridNaive | 21452.50 | 26.08 | 0.74 | 2.01 | — |
| kroD100 | HybridOptimized | 21410.50 | 32.97 | 0.55 | 0.37 | 5.47× |
| kroE100 | CPU | 22215.25 | 53.91 | 0.67 | 249.82 | 0.01× |
| kroE100 | FullGPU | 22164.25 | 14.77 | 0.44 | 1.58 | 1.34× |
| kroE100 | HybridNaive | 22216.50 | 31.70 | 0.67 | 2.12 | — |
| kroE100 | HybridOptimized | 22209.50 | 60.84 | 0.64 | 0.39 | 5.39× |
| lin105 | FullGPU | 14379.00 | 0.00 | 0.00 | 1.72 | 1.09× |
| lin105 | HybridNaive | 14447.00 | 23.55 | 0.47 | 1.88 | — |
| lin105 | HybridOptimized | 14438.75 | 41.31 | 0.42 | 0.33 | 5.72× |
| lin318 | FullGPU | 42948.50 | 102.36 | 2.19 | 33.50 | 1.67× |
| lin318 | HybridNaive | 42647.25 | 133.62 | 1.47 | 56.11 | — |
| lin318 | HybridOptimized | 42724.50 | 425.11 | 1.65 | 9.20 | 6.10× |
| pcb442 | FullGPU | 52308.75 | 187.42 | 3.01 | 82.23 | 1.54× |
| pcb442 | HybridNaive | 52296.75 | 403.44 | 2.99 | 126.37 | — |
| pcb442 | HybridOptimized | 52208.75 | 355.13 | 2.82 | 33.09 | 3.82× |
| pr1002 | FullGPU | 269484.75 | 582.57 | 4.03 | 1019.20 | 0.65× |
| pr1002 | HybridNaive | 282372.25 | 3282.91 | 9.01 | 658.93 | — |
| pr1002 | HybridOptimized | 278459.25 | 3781.66 | 7.49 | 373.18 | 1.77× |
| pr107 | FullGPU | 44482.75 | 86.61 | 0.41 | 2.50 | 0.81× |
| pr107 | HybridNaive | 44524.00 | 117.19 | 0.50 | 2.02 | — |
| pr107 | HybridOptimized | 44529.25 | 142.04 | 0.51 | 0.34 | 5.86× |
| pr124 | FullGPU | 59030.00 | 0.00 | 0.00 | 2.13 | 2.44× |
| pr124 | HybridNaive | 59258.50 | 363.61 | 0.39 | 5.21 | — |
| pr124 | HybridOptimized | 59328.00 | 222.03 | 0.50 | 0.68 | 7.61× |
| pr136 | FullGPU | 97285.75 | 82.81 | 0.53 | 4.76 | 0.79× |
| pr136 | HybridNaive | 97466.00 | 159.62 | 0.72 | 3.74 | — |
| pr136 | HybridOptimized | 97581.25 | 165.59 | 0.84 | 0.60 | 6.25× |
| pr144 | FullGPU | 58537.00 | 0.00 | 0.00 | 3.25 | 1.18× |
| pr144 | HybridNaive | 58840.75 | 110.33 | 0.52 | 3.83 | — |
| pr144 | HybridOptimized | 58700.50 | 72.99 | 0.28 | 0.63 | 6.11× |
| pr152 | FullGPU | 74030.25 | 134.49 | 0.47 | 5.07 | 0.94× |
| pr152 | HybridNaive | 74227.75 | 109.73 | 0.74 | 4.79 | — |
| pr152 | HybridOptimized | 74141.25 | 203.64 | 0.62 | 0.84 | 5.72× |
| pr264 | FullGPU | 49353.75 | 85.55 | 0.45 | 17.94 | 1.18× |
| pr264 | HybridNaive | 49867.00 | 888.15 | 1.49 | 21.19 | — |
| pr264 | HybridOptimized | 49539.50 | 39.98 | 0.82 | 2.66 | 7.98× |
| pr299 | FullGPU | 49100.25 | 105.07 | 1.89 | 30.18 | 1.08× |
| pr299 | HybridNaive | 48713.50 | 138.95 | 1.08 | 32.61 | — |
| pr299 | HybridOptimized | 48665.50 | 50.11 | 0.98 | 7.33 | 4.45× |
| pr439 | FullGPU | 108555.00 | 89.13 | 1.25 | 74.54 | 1.67× |
| pr439 | HybridNaive | 110172.75 | 1953.14 | 2.76 | 124.78 | — |
| pr439 | HybridOptimized | 109302.00 | 755.44 | 1.94 | 24.47 | 5.10× |
| pr76 | CPU | 109009.00 | 112.78 | 0.79 | 76.47 | 0.02× |
| pr76 | FullGPU | 108222.00 | 64.42 | 0.06 | 0.83 | 1.52× |
| pr76 | HybridNaive | 108668.25 | 308.33 | 0.47 | 1.26 | — |
| pr76 | HybridOptimized | 108717.75 | 356.06 | 0.52 | 0.33 | 3.81× |
| rat195 | FullGPU | 2378.00 | 9.87 | 2.37 | 11.96 | 1.90× |
| rat195 | HybridNaive | 2346.25 | 3.11 | 1.00 | 22.73 | — |
| rat195 | HybridOptimized | 2349.75 | 12.52 | 1.15 | 3.59 | 6.33× |
| rat783 | FullGPU | 9210.25 | 10.26 | 4.59 | 322.45 | 1.39× |
| rat783 | HybridNaive | 9250.00 | 140.83 | 5.04 | 448.21 | — |
| rat783 | HybridOptimized | 9589.25 | 276.92 | 8.89 | 208.13 | 2.15× |
| rat99 | CPU | 1217.75 | 3.27 | 0.56 | 219.60 | 0.01× |
| rat99 | FullGPU | 1216.75 | 3.03 | 0.47 | 1.94 | 1.02× |
| rat99 | HybridNaive | 1220.00 | 1.41 | 0.74 | 1.98 | — |
| rat99 | HybridOptimized | 1217.50 | 2.60 | 0.54 | 0.31 | 6.31× |
| rd100 | CPU | 7969.00 | 18.69 | 0.75 | 227.75 | 0.01× |
| rd100 | FullGPU | 7911.00 | 1.22 | 0.01 | 1.60 | 1.12× |
| rd100 | HybridNaive | 7938.25 | 20.05 | 0.36 | 1.80 | — |
| rd100 | HybridOptimized | 7965.75 | 20.07 | 0.70 | 0.27 | 6.54× |
| rd400 | FullGPU | 15722.00 | 47.83 | 2.89 | 70.31 | 1.46× |
| rd400 | HybridNaive | 15608.75 | 78.73 | 2.14 | 102.71 | — |
| rd400 | HybridOptimized | 15823.75 | 104.47 | 3.55 | 22.81 | 4.50× |
| st70 | CPU | 678.00 | 2.24 | 0.44 | 59.51 | 0.02× |
| st70 | FullGPU | 675.00 | 0.00 | 0.00 | 0.64 | 1.60× |
| st70 | HybridNaive | 675.75 | 0.43 | 0.11 | 1.02 | — |
| st70 | HybridOptimized | 677.00 | 1.58 | 0.30 | 0.16 | 6.28× |
| ts225 | FullGPU | 126643.00 | 0.00 | 0.00 | 12.58 | 0.82× |
| ts225 | HybridNaive | 127651.75 | 123.57 | 0.80 | 10.31 | — |
| ts225 | HybridOptimized | 127550.00 | 157.00 | 0.72 | 2.11 | 4.88× |
| u159 | FullGPU | 42080.00 | 0.00 | 0.00 | 4.41 | 1.24× |
| u159 | HybridNaive | 42293.75 | 146.04 | 0.51 | 5.49 | — |
| u159 | HybridOptimized | 42352.25 | 132.84 | 0.65 | 0.94 | 5.84× |

*Note: Speedup calculated relative to HybridNaive (— indicates baseline algorithm).*

## Table 2: Algorithm Performance Comparison (All Problems)

| Algorithm | Mean Gap (%) | Std Gap | Mean Time (s) | Std Time | Avg Speedup |
|:----------|-------------:|--------:|--------------:|---------:|------------:|
| CPU | 0.56 | 0.15 | 149.99 | 82.87 | — |
| FullGPU | 0.87 | 1.13 | 49.40 | 168.67 | — |
| HybridNaive | 1.20 | 1.58 | 47.09 | 126.54 | — |
| HybridOptimized | 1.23 | 1.77 | 18.93 | 67.22 | 2.49× |

## Table 3: Best Algorithm by Problem Size

| Size Category | Problems | Best Algorithm | Mean Gap (%) | Mean Time (s) |
|:--------------|:---------|:---------------|-------------:|--------------:|
| Small (n<100) | eil51, berlin52, st70, eil76, pr76, rat99 | FullGPU | 0.23 | 0.87 |
| Medium (100≤n<300) | kroA100, kroB100, kroC100, kroD100, kroE100, rd100, eil101, lin105, pr107, pr124, bier127, ch130, pr136, pr144, ch150, kroA150, kroB150, pr152, u159, rat195, d198, kroA200, ts225, pr264, pr299 | FullGPU | 0.51 | 6.70 |
| Large (n≥300) | lin318, rd400, fl417, pr439, pcb442, rat783, pr1002 | FullGPU | 2.71 | 243.50 |

*Note: Best algorithm determined by lowest mean gap to known optimum.*
