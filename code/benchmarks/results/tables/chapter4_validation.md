# Chapter 4 Validation Results

Generated: 2025-11-20 21:57:59

## Table 1: Summary Statistics by Problem

| Problem | Algorithm | Mean Cost | Std Dev | Gap (%) | Mean Time (s) | Speedup |
|:--------|:----------|----------:|--------:|--------:|--------------:|--------:|
| berlin52 | CPU | 7542.00 | 0.00 | 0.00 | 24.71 | — |
| berlin52 | FullGPU | 7542.00 | 0.00 | 0.00 | 0.30 | 83.17× |
| berlin52 | HybridNaive | 7542.00 | 0.00 | 0.00 | 0.61 | 40.35× |
| berlin52 | HybridOptimized | 7542.00 | 0.00 | 0.00 | 0.12 | 209.51× |
| eil51 | CPU | 427.00 | 0.00 | 0.23 | 125.57 | — |
| eil51 | FullGPU | 426.00 | 0.00 | 0.00 | 0.31 | 411.21× |
| eil51 | HybridNaive | 426.00 | 0.00 | 0.00 | 0.83 | 150.82× |
| eil51 | HybridOptimized | 426.00 | 0.00 | 0.00 | 0.20 | 618.75× |

*Note: Speedup calculated relative to CPU (—\ indicates baseline algorithm).*

## Table 2: Algorithm Performance Comparison (All Problems)

| Algorithm | Mean Gap (%) | Std Gap | Mean Time (s) | Std Time | Avg Speedup |
|:----------|-------------:|--------:|--------------:|---------:|------------:|
| CPU | 0.12 | 0.12 | 75.14 | 50.43 | — |
| FullGPU | 0.00 | 0.00 | 0.30 | 0.00 | 249.45× |
| HybridNaive | 0.00 | 0.00 | 0.72 | 0.11 | 104.01× |
| HybridOptimized | 0.00 | 0.00 | 0.16 | 0.04 | 468.34× |

## Table 3: Best Algorithm by Problem Size

| Size Category | Problems | Best Algorithm | Mean Gap (%) | Mean Time (s) |
|---------------|----------|----------------|--------------|---------------|
| Small (n<100) | berlin52, eil51 | FullGPU | 0.00 | 0.30 |