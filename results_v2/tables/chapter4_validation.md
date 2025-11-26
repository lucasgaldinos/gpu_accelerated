# Chapter 4 Validation Results

Generated: 2025-11-26 02:20:34

## Table 1: Summary Statistics by Problem

| Problem | Algorithm | Mean Cost | Std Dev | Gap (%) | Mean Time (s) | Speedup |
|:--------|:----------|----------:|--------:|--------:|--------------:|--------:|
| berlin52 | CPU | 7558.88 | 24.74 | 0.22 | 25.94 | 0.02× |
| berlin52 | FullGPU | 7542.00 | 0.00 | 0.00 | 0.30 | 1.92× |
| berlin52 | HybridNaive | 7546.00 | 10.95 | 0.05 | 0.58 | — |
| berlin52 | HybridOptimized | 7558.38 | 23.27 | 0.22 | 0.12 | 5.02× |
| bier127 | FullGPU | 118795.94 | 164.31 | 0.43 | 3.65 | 0.83× |
| bier127 | HybridNaive | 119102.38 | 242.70 | 0.69 | 3.02 | — |
| bier127 | HybridOptimized | 119135.31 | 195.51 | 0.72 | 0.52 | 5.85× |
| ch130 | FullGPU | 6158.19 | 19.57 | 0.79 | 5.24 | 0.64× |
| ch130 | HybridNaive | 6154.44 | 12.35 | 0.73 | 3.35 | — |
| ch130 | HybridOptimized | 6148.94 | 12.53 | 0.64 | 0.60 | 5.54× |
| ch150 | FullGPU | 6547.69 | 16.77 | 0.30 | 5.83 | 0.79× |
| ch150 | HybridNaive | 6582.56 | 12.89 | 0.84 | 4.63 | — |
| ch150 | HybridOptimized | 6575.44 | 12.23 | 0.73 | 0.76 | 6.12× |
| d198 | FullGPU | 15913.19 | 22.84 | 0.84 | 13.62 | 0.57× |
| d198 | HybridNaive | 15907.31 | 17.88 | 0.81 | 7.82 | — |
| d198 | HybridOptimized | 15918.56 | 25.04 | 0.88 | 1.48 | 5.28× |
| eil101 | FullGPU | 633.75 | 2.14 | 0.76 | 1.90 | 1.21× |
| eil101 | HybridNaive | 633.25 | 1.68 | 0.68 | 2.29 | — |
| eil101 | HybridOptimized | 633.56 | 1.41 | 0.73 | 0.35 | 6.50× |
| eil51 | CPU | 428.38 | 1.11 | 0.56 | 21.12 | 0.03× |
| eil51 | FullGPU | 427.75 | 0.66 | 0.41 | 0.50 | 1.18× |
| eil51 | HybridNaive | 428.81 | 1.13 | 0.66 | 0.60 | — |
| eil51 | HybridOptimized | 428.75 | 0.90 | 0.65 | 0.11 | 5.41× |
| eil76 | CPU | 541.75 | 1.52 | 0.70 | 82.70 | 0.02× |
| eil76 | FullGPU | 542.25 | 1.98 | 0.79 | 1.00 | 1.32× |
| eil76 | HybridNaive | 541.81 | 1.81 | 0.71 | 1.32 | — |
| eil76 | HybridOptimized | 541.12 | 1.69 | 0.58 | 0.19 | 6.86× |
| fl417 | FullGPU | 11988.19 | 13.38 | 1.07 | 86.20 | 1.12× |
| fl417 | HybridNaive | 12072.62 | 73.04 | 1.78 | 96.26 | — |
| fl417 | HybridOptimized | 12090.25 | 144.66 | 1.93 | 18.33 | 5.25× |
| kroA100 | CPU | 21396.31 | 63.28 | 0.54 | 176.05 | 0.01× |
| kroA100 | FullGPU | 21284.75 | 4.84 | 0.01 | 1.56 | 1.13× |
| kroA100 | HybridNaive | 21376.62 | 68.88 | 0.44 | 1.77 | — |
| kroA100 | HybridOptimized | 21363.94 | 58.44 | 0.39 | 0.29 | 6.15× |
| kroA150 | FullGPU | 26674.75 | 85.58 | 0.57 | 6.54 | 0.71× |
| kroA150 | HybridNaive | 26714.75 | 50.54 | 0.72 | 4.63 | — |
| kroA150 | HybridOptimized | 26712.69 | 55.74 | 0.71 | 0.72 | 6.43× |
| kroA200 | FullGPU | 29664.38 | 88.13 | 1.01 | 12.50 | 1.02× |
| kroA200 | HybridNaive | 29637.69 | 60.08 | 0.92 | 12.71 | — |
| kroA200 | HybridOptimized | 29626.12 | 114.66 | 0.88 | 2.11 | 6.03× |
| kroB100 | CPU | 22279.81 | 55.94 | 0.63 | 182.31 | 0.01× |
| kroB100 | FullGPU | 22193.44 | 46.73 | 0.24 | 2.04 | 0.89× |
| kroB100 | HybridNaive | 22278.12 | 65.08 | 0.62 | 1.82 | — |
| kroB100 | HybridOptimized | 22256.56 | 61.70 | 0.52 | 0.32 | 5.68× |
| kroB150 | FullGPU | 26282.25 | 55.66 | 0.58 | 7.54 | 0.58× |
| kroB150 | HybridNaive | 26321.50 | 45.68 | 0.73 | 4.35 | — |
| kroB150 | HybridOptimized | 26332.38 | 39.90 | 0.77 | 0.71 | 6.08× |
| kroC100 | CPU | 20828.06 | 56.81 | 0.38 | 175.80 | 0.01× |
| kroC100 | FullGPU | 20759.44 | 18.14 | 0.05 | 1.53 | 1.19× |
| kroC100 | HybridNaive | 20840.62 | 54.72 | 0.44 | 1.82 | — |
| kroC100 | HybridOptimized | 20825.88 | 62.61 | 0.37 | 0.29 | 6.34× |
| kroD100 | CPU | 21429.81 | 42.84 | 0.64 | 183.36 | 0.01× |
| kroD100 | FullGPU | 21373.19 | 47.54 | 0.37 | 2.07 | 0.87× |
| kroD100 | HybridNaive | 21439.69 | 54.18 | 0.68 | 1.81 | — |
| kroD100 | HybridOptimized | 21411.81 | 37.70 | 0.55 | 0.32 | 5.63× |
| kroE100 | CPU | 22206.69 | 53.22 | 0.63 | 195.27 | 0.01× |
| kroE100 | FullGPU | 22157.69 | 22.79 | 0.41 | 2.10 | 0.88× |
| kroE100 | HybridNaive | 22199.31 | 41.13 | 0.60 | 1.84 | — |
| kroE100 | HybridOptimized | 22184.50 | 67.54 | 0.53 | 0.30 | 6.08× |
| lin105 | FullGPU | 14381.31 | 8.96 | 0.02 | 1.70 | 1.11× |
| lin105 | HybridNaive | 14448.81 | 38.56 | 0.49 | 1.88 | — |
| lin105 | HybridOptimized | 14436.69 | 39.95 | 0.40 | 0.31 | 5.99× |
| lin318 | FullGPU | 42919.06 | 130.76 | 2.12 | 39.71 | 1.40× |
| lin318 | HybridNaive | 42831.38 | 419.46 | 1.91 | 55.43 | — |
| lin318 | HybridOptimized | 42852.31 | 388.09 | 1.96 | 9.67 | 5.73× |
| pcb442 | FullGPU | 52401.06 | 208.06 | 3.20 | 78.83 | 1.61× |
| pcb442 | HybridNaive | 52363.56 | 838.59 | 3.12 | 127.04 | — |
| pcb442 | HybridOptimized | 51999.06 | 669.39 | 2.40 | 31.99 | 3.97× |
| pr1002 | FullGPU | 269686.38 | 741.50 | 4.11 | 757.20 | 0.91× |
| pr1002 | HybridNaive | 280109.94 | 3702.25 | 8.13 | 692.64 | — |
| pr1002 | HybridOptimized | 278657.00 | 2967.31 | 7.57 | 383.07 | 1.81× |
| pr107 | FullGPU | 44470.19 | 93.23 | 0.38 | 2.68 | 0.74× |
| pr107 | HybridNaive | 44570.00 | 109.71 | 0.60 | 2.00 | — |
| pr107 | HybridOptimized | 44558.69 | 106.03 | 0.58 | 0.35 | 5.64× |
| pr124 | FullGPU | 59030.00 | 0.00 | 0.00 | 2.11 | 1.56× |
| pr124 | HybridNaive | 59278.06 | 255.00 | 0.42 | 3.30 | — |
| pr124 | HybridOptimized | 59250.44 | 189.53 | 0.37 | 0.47 | 6.96× |
| pr136 | FullGPU | 97276.69 | 140.39 | 0.52 | 4.64 | 0.76× |
| pr136 | HybridNaive | 97544.81 | 127.16 | 0.80 | 3.55 | — |
| pr136 | HybridOptimized | 97478.38 | 208.30 | 0.73 | 0.62 | 5.76× |
| pr144 | FullGPU | 58537.00 | 0.00 | 0.00 | 3.23 | 1.14× |
| pr144 | HybridNaive | 58818.62 | 167.52 | 0.48 | 3.68 | — |
| pr144 | HybridOptimized | 58762.25 | 138.55 | 0.38 | 0.64 | 5.74× |
| pr152 | FullGPU | 73935.69 | 138.48 | 0.34 | 4.89 | 0.89× |
| pr152 | HybridNaive | 74151.81 | 148.59 | 0.64 | 4.35 | — |
| pr152 | HybridOptimized | 74166.19 | 181.82 | 0.66 | 0.75 | 5.83× |
| pr264 | FullGPU | 49327.19 | 102.03 | 0.39 | 21.55 | 1.00× |
| pr264 | HybridNaive | 49638.44 | 477.12 | 1.02 | 21.64 | — |
| pr264 | HybridOptimized | 49618.69 | 169.11 | 0.98 | 3.54 | 6.12× |
| pr299 | FullGPU | 49115.69 | 103.89 | 1.92 | 31.47 | 1.25× |
| pr299 | HybridNaive | 48963.44 | 447.84 | 1.60 | 39.49 | — |
| pr299 | HybridOptimized | 48804.69 | 284.62 | 1.27 | 6.65 | 5.94× |
| pr439 | FullGPU | 108467.00 | 149.59 | 1.17 | 83.30 | 1.39× |
| pr439 | HybridNaive | 110152.31 | 1661.37 | 2.74 | 115.73 | — |
| pr439 | HybridOptimized | 110210.00 | 1534.98 | 2.79 | 23.06 | 5.02× |
| pr76 | CPU | 108746.69 | 293.49 | 0.54 | 71.00 | 0.01× |
| pr76 | FullGPU | 108206.94 | 53.12 | 0.04 | 0.81 | 1.30× |
| pr76 | HybridNaive | 108572.81 | 309.08 | 0.38 | 1.06 | — |
| pr76 | HybridOptimized | 108752.56 | 325.92 | 0.55 | 0.19 | 5.54× |
| rat195 | FullGPU | 2372.75 | 8.42 | 2.14 | 13.36 | 1.04× |
| rat195 | HybridNaive | 2344.69 | 3.85 | 0.93 | 13.86 | — |
| rat195 | HybridOptimized | 2347.56 | 9.02 | 1.06 | 2.83 | 4.91× |
| rat783 | FullGPU | 9208.25 | 17.81 | 4.57 | 361.53 | 1.16× |
| rat783 | HybridNaive | 9476.75 | 221.28 | 7.62 | 419.34 | — |
| rat783 | HybridOptimized | 9596.50 | 183.51 | 8.98 | 206.96 | 2.03× |
| rat99 | CPU | 1219.19 | 3.07 | 0.68 | 186.25 | 0.01× |
| rat99 | FullGPU | 1214.75 | 2.86 | 0.31 | 1.86 | 1.01× |
| rat99 | HybridNaive | 1218.56 | 3.02 | 0.62 | 1.87 | — |
| rat99 | HybridOptimized | 1217.00 | 3.41 | 0.50 | 0.35 | 5.39× |
| rd100 | CPU | 7962.94 | 22.80 | 0.67 | 181.68 | 0.01× |
| rd100 | FullGPU | 7916.62 | 9.77 | 0.08 | 1.77 | 0.98× |
| rd100 | HybridNaive | 7953.25 | 20.63 | 0.55 | 1.74 | — |
| rd100 | HybridOptimized | 7964.31 | 14.19 | 0.69 | 0.26 | 6.59× |
| rd400 | FullGPU | 15737.12 | 50.52 | 2.98 | 73.05 | 1.38× |
| rd400 | HybridNaive | 15799.56 | 190.55 | 3.39 | 101.01 | — |
| rd400 | HybridOptimized | 15785.62 | 261.51 | 3.30 | 24.88 | 4.06× |
| st70 | CPU | 677.88 | 2.12 | 0.43 | 55.13 | 0.02× |
| st70 | FullGPU | 675.00 | 0.00 | 0.00 | 0.64 | 1.47× |
| st70 | HybridNaive | 676.69 | 2.02 | 0.25 | 0.93 | — |
| st70 | HybridOptimized | 676.94 | 1.60 | 0.29 | 0.18 | 5.30× |
| ts225 | FullGPU | 126643.00 | 0.00 | 0.00 | 12.66 | 0.77× |
| ts225 | HybridNaive | 127608.88 | 178.67 | 0.76 | 9.77 | — |
| ts225 | HybridOptimized | 127516.00 | 177.60 | 0.69 | 1.87 | 5.22× |
| u159 | FullGPU | 42084.62 | 17.91 | 0.01 | 4.41 | 1.16× |
| u159 | HybridNaive | 42377.31 | 140.27 | 0.71 | 5.09 | — |
| u159 | HybridOptimized | 42381.81 | 124.79 | 0.72 | 0.87 | 5.83× |

*Note: Speedup calculated relative to HybridNaive (— indicates baseline algorithm).*

## Table 2: Algorithm Performance Comparison (All Problems)

| Algorithm | Mean Gap (%) | Std Gap | Mean Time (s) | Std Time | Avg Speedup |
|:----------|-------------:|--------:|--------------:|---------:|------------:|
| CPU | 0.55 | 0.14 | 128.05 | 66.99 | — |
| FullGPU | 0.87 | 1.14 | 43.57 | 131.97 | — |
| HybridNaive | 1.30 | 1.71 | 46.74 | 128.49 | — |
| HybridOptimized | 1.28 | 1.79 | 19.13 | 68.51 | 2.44× |

## Table 3: Best Algorithm by Problem Size

| Size Category | Problems | Best Algorithm | Mean Gap (%) | Mean Time (s) |
|:--------------|:---------|:---------------|-------------:|--------------:|
| Small (n<100) | eil51, berlin52, st70, eil76, pr76, rat99 | FullGPU | 0.26 | 0.85 |
| Medium (100≤n<300) | kroA100, kroB100, kroC100, kroD100, kroE100, rd100, eil101, lin105, pr107, pr124, bier127, ch130, pr136, pr144, ch150, kroA150, kroB150, pr152, u159, rat195, d198, kroA200, ts225, pr264, pr299 | FullGPU | 0.49 | 6.82 |
| Large (n≥300) | lin318, rd400, fl417, pr439, pcb442, rat783, pr1002 | FullGPU | 2.74 | 211.40 |

*Note: Best algorithm determined by lowest mean gap to known optimum.*
