```mermaid
%%{
 init: {
  'theme': 'forest',
  'themeVariables': {
   'primaryColor': '#BB2528',
   'primaryTextColor': '#fff',
   'primaryBorderColor': '#7C0000',
   'lineColor': '#F8B229',
   'secondaryColor': '#006100',
   'tertiaryColor': '#fff'
  },
  'flowchart': {
    'titleTopMargin': 10,
    'subGraphTitleMargin' : {
      'top': 10,
      'bottom': 25
    },
    'arrowMarkerAbsolute': false,
    'diagramPadding': 15,
    'curve': 'linear',
    'padding': 20,
    'wrappingWidth': 60,
    'wrappingWidth': 1
  }
 }
}%%
flowchart LR 
classDef input fill:#f9f,stroke:#333,stroke-width:4px,font-size:24px,shape:circle;
classDef process shape:rect
classDef badBadEvent fill:#f00,color:white,font-weight:bold,stroke-width:2px,stroke:yellow
subgraph "Neural network for algebraic values"
  direction LR
  init_time:::badBadEvent --> pinc:::badBadEvent
  init_cond --> pinc
  control_input --> pinc
  pinc --"y(T)"--> nn--> output:::input
  control_input --> nn
end
```

```mermaid
---
title: hi
---
%%{
 init: {
  'flowchart':{
    'nodeSpacing': 100,
    'rankSpacing': 100,
    'curve': 'basis'
  }
 }
}%%

flowchart LR

%%{ title: "My title" }%%


A-->B
A-->C
B-->D
C-->D

```

```mermaid
---
title: my graph
author: FirstName LastName
---
flowchart LR
  A[Hard] -->|Text| B(Round)
  B --> C{Decision}
```

```mermaid
stateDiagram
 title: Example state diagram
 my2ndState: My second state
 title --> my2ndState
```

```mermaid
---
title: Neural network for algebraic values
---

%%{
  init: {
    "layout": "elk",
    "theme": "base",
    "flowchart": {
      "htmlLabels": true,
      "curve": "stepAfter",
      "useWidth": 500,
      'wrappingWidth': 300
    },
    'fontFamily': 'Verdana',
    'themeVariables': {
      'lineWidth': 2,
      'lineHeight': 20,
      'lineType': 'solid',
      "useWidth": 1000
    },
    "markdownAutoWrap": false,
    'wrappingWidth': 500
  }
}%%


graph TD 
init_time@{shape: circle, label: "t", cssClasses: noLabel, 't': 500, 'w': 500, 'h': 500}
init_cond@{'shape': circle, 'label': y(0), 't': 50, 'w': 50, 'h': 50}
classDef noLabel fill:#f9f004,stroke:#333,stroke-width:2px,font-size:0px;

  init_time--> pinc[PINC]
  init_cond --> pinc
  control_input(("u(t)")) --> pinc
  pinc --"y(T)"--> nn[NN]--> output(("z(t)"))
  control_input --> nn 
```

```mermaid
%%{
  init: {
    "theme": "base",
    "flowchart": {
      "htmlLabels": true,
      "curve": "stepAfter",
      'assetWidth': 100
    },
    "themeVariables": {
      "primaryColor": "#E3E3E3",
      "edgeLabelBackground": "#FFF"
    }
  }
}%%

graph TD
  classDef bigNode fill:#A2C5E8,stroke:#2B4162,stroke-width:3,font-size:16px,width:100px,height:100px;
  init_time@{'shape': circle, 'label': "t", "r":20}
  init_cond@{'shape': rect, 'label': 'y(0)', 'rx': 250, 'ry': 250}

  init_time --> pinc[PINC]
  init_cond --> pinc
  control_input(("#emsp;u(t)")) --> pinc
  pinc -- "y(T)" --> nn[NN] --> output(("z(t)"))
  control_input --> nn
```

```plantuml
@startuml
circle "t" as init_time
circle "y(0)" as init_cond
init_time --> init_cond
@enduml
```

```plantuml
@startuml
left to right direction

skinparam defaulFontSize 16
skinparam defaultFontName Verdana
skinparam defaultFontColor #2B4162
skinparam defaultTextgather*ment center
skinparam node {
 BackgroundColor #A2C5E8
 BorderColor #2B4162
 BorderThickness 10
}
skinparam circle {
 FontSize 20
 Padding 20
}

circle "  t  " as init_time
rectangle "y(0)" as init_cond
rectangle "u(t)" as control_input
rectangle "PINC" as pinc
rectangle "NN" as nn
rectangle "z(t)" as output

init_time --> pinc
init_cond --> pinc
control_input --> pinc
pinc "y(T)" --> nn
nn --> output
control_input --> nn

@enduml
```

```mermaid
%%{
 init: {
  'theme': 'base',
  'flowchart': {
   'htmlLabels': true,
   'curve': 'stepAfter',
   'useWidth': 500,
   'wrappingWidth': 300},
  'themeVariables': {
   'primaryColor': '#BB2528',
   'primaryTextColor': '#fff',
   'primaryBorderColor': '#7C0000'
  }
 }
}%%
flowchart LR
  A[Start] --> B{Decision}
  B -->|Yes| C[Action 1]
  B -->|No| D[Action 2]
  C --> E[End]
  D --> E((E))

  classDef myClass fill:#f9f,stroke:#333,stroke-width:4px,font-size:20px;
  class A,C,E myClass;
  classDef circleClass r:30, fill:#bbf,stroke:#f66, stroke-width:2px,stroke-dasharray: 5 5,font-size:16px;
  class E,D circleClass; 
  %% r:300 is the radius of the circle defined by the css element
```

## Making nodes bigger in mermaid

1. Open a [sample flowchart](https://mermaid.live/edit)
2. Go to the element you want to see the properties and click on inspect element. There you'll see the properties of the element.
   1. Other option is directly opening the svg file and inspect the element as a whole.
3. Inspect the possible svg parameters you wanna change

Example using arrays

$$
\begin {array}{l}
\left\{
    \begin{array}{l}
        U =\quad \phi(W^1X + b^1) \\
        V =\quad \phi(W^2X + b^2)
    \end{array}
\right. \\
\left\{
    \begin{array}{l}
        Z^{(1)} = \phi(W^{z,1}X + b^{z,1})\\
        A^{(1)} = (1-Z^{(1)})\odot U + Z^{(1)}\odot V
    \end{array}
\right.\\
\left\{
    \begin{array}{l}
        Z^{(k)} = \phi(W^{z,k}A^{(k-1)} + b^{z,k}) \\
        A^{(k)} = (1-Z^{(k)})\odot U + Z^{(k)}\odot V,\quad k=2,\dots,N_L
    \end{array}
\right.\\
y= WA^{(N_L)} + b
\end {array}
$$

The secret is to use an array of arrays by beginnning an array at the start of the thing.

## all equations to the left
  
```math
\begin{align}
    &k_n =
    \left\{
        \begin{array}{l}
            k_m, if \quad p_m \in \{1,2\}, \\
            k_m +1 if \quad p_m = 3, \\
            k_m+2 if \quad p_m = 4 &
            \end{array}
    \right.
    \\
    &h^1_n=t(i_m, i_n, d_m)
    \\
    &h^2_n =
    \left\{
    \begin{array}{lrl}
    h^2_m + t(i_m, i_n, d_m), if \quad p_m \in \{1,2,3\}, \\
    t(i_m, i_n, d_m), if \quad p_m = 4
    \end{array}
    \right.
    \\
    &h^3_n =
    \left\{
    \begin{array}{lrl}
    h^3_m + t(i_m, i_n, d_m), if \quad p_m \in \{1,2,3\}, \\
    t(i_m, i_n, d_m), if \quad p_m = 4
    \end{array}
    \right.
\\
    \end{align}
```
