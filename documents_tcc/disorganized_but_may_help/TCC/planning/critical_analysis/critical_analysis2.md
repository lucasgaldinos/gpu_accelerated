---
bibliography:
- refs.bib
---

::: resumoumacoluna
O documento realizará uma análise crítica do Trabalho de Conclusão de
Curso (TCC) intitulado [@tcc_vitorhp]. O objetivo é avaliar a qualidade
do trabalho, identificar suas contribuições, limitações e oportunidades
para futuros estudos. A análise será conduzida com base em critérios de
avaliação acadêmica, considerando a clareza, coerência, relevância e
originalidade do trabalho. O documento apresentará uma visão geral do
TCC, uma análise detalhada das partes constituintes, como introdução,
objetivos, metodologia, resultados e discussão, e uma conclusão com as
principais contribuições e sugestões para trabalhos futuros.

**Palavras-chave**: latex. abntex. editoração de texto.
:::

# Introdução

O TCC foi escolhido devido ao meu interesse e familiaridade em relação
ao tema otimização de rotas. Também tenho interesse em desenvolver algo
parecido, mas abordando outro problema relacionado ao famoso Problema do
Caixeiro Viajante.

# Análise das Partes Constituintes

Serão analisados aqui diversos aspectos da abordagem do estudante Victor
Hammann Pereira.

## Partes Constituintes

Ao iniciar o trabalho o autor apresenta

1.  **Resumo**: O trabalho possui um resumo, explicitando o que será
    discutido dentro do trabalho. O resumo é claro e objetivo,
    apresentando uma visão geral do problema, da metodologia utilizada e
    dos resultados obtidos.

2.  **Abstract**: O texto possui também um abstract, que é uma versão
    resumida do trabalho em inglês. O abstract é claro e objetivo,
    apresentando uma visão geral do problema, da metodologia utilizada e
    dos resultados obtidos.

3.  **Lista de siglas**: As siglas utilizadas no trabalho.

4.  **Lista de figuras**: Uma lista com todas as figuras utilizadas no
    trabalho, com seus respectivos títulos e páginas.

5.  **Lista de tabelas**: Uma lista com todas as tabelas utilizadas no
    trabalho, com suas legendas e páginas.

6.  **Sumário**: Contendo as informações sobre os capítulos do trabalho.

Em seguida, no primeiro capítulo, são apresentados

1.  **Justificativa**: Logo na introdução, o autor apresenta a
    justificativa do trabalho, explicando a importância do problema e a
    necessidade de uma solução computacional para a definição de rotas
    baseadas no uso do sistema de transporte coletivo.

2.  **Objetivos**: O autor define os objetivos gerais e os objetivos
    específicos do trabalho.

3.  **Considerações iniciais**: O autor apresenta as considerações
    iniciais, explicando as limitações da metodologia adotada.

No segundo capítulo, são apresentados

1.  **Revisão bibliográfica**: São analisados trabalhos similares ou
    dentro do proposto pelo autor

2.  **Materiais**: São apresentados os materiais utilizados para o
    desenvolvimento do trabalho, como linguagem de programação
    utilizada, serviço de bancos de dados, bibliotecas e ferramentas GIS
    (Geographic Information System).

No terceiro capítulo, o autor descreve a **metodologia** utilizada para
o desenvolvimento do trabalho, iniciando através da descrição de
informações necessárias, preparação dos dados e desenvolvimento do
modelo.

O quarto capítulo, são apresentados os **resultados** obtidos pelo autor
através da metodologia proposta.

No quinto capítulo, são apresentadas **conclusões** do trabalho,
resumindo os principais aprendizados, resultadoes e implicações. São
desenvolvidas também recomendações para futuros trabalhos.

Finalmente o autor apresenta

1.  **Referências bibliográficas**: O trabalho possui uma lista das
    referências bibliográficas citadas ao longo do texto.

2.  **Apêndices**: Nos apêndices são apresentados os códigos
    desenvolvidos pelo autor.

# Análise Elaborada das Partes

## Análise da Justificativa

O autor inicia a justificativa explicando como o transporte permite às
pessoas se deslocarem sem a necessidade de possuir um automóvel. Em
seguida a presenta os problemas enfrentados para a adoção do mesmo,
sendo a apresentação do mesmo um dos principais problemas a ser
resolvido. Uma solução para este problema aumentaria a adoção e a
qualidade dos serviços ofertados. Ainda cita problemas relacionados ao
uso excessivo de carros.

A justificativa expõe alguns problemas relacionados ao serviços de
transporte coletivo. O autor, no entanto poderia trazer outros problemas
em que a solução proposta pode ser aplicada, como por exemplo, a
otimização do tempo de viagem dos usuários, a redução de emissões de
gases de efeito estufa, a melhoria da segurança dos usuários, entre
outros.

## Análise dos Objetivos

Os objetivos gerais, sintetizam o propósito do trabalho quanto a
utilização de softwares abertos para o roteamento de ônibus utilizando
softwares abertos, porém peca ao desconsiderar o objeto de estudo como a
cidade de Florianópolis ao generalizar para a determinação em outros
locais. No entanto, cita tais problemas ao falar das limitações do
modelo. Tal solução só seria possível levando em consideração as
diversas características e particularidades de cada local.

Alguns dos objetivos específicos são bem definidos e claros. O autor
objetiva identificar as ferramentas disponíveis para fornecimento de
informações relativos a rotas, tais como softwares GIS e aplicar
funcionalidades destes para processamento de dados espaciais relativos a
infraestrutura do transporte. Aplicar também técnicas de criação e
modelagem de bancos de dados, coleta e limpeza de dados para o suporte
do serviço e analisar os resultados obtidos.

O autor ainda cita as limitações do seu modelo, como a área de estudo
sendo limitada a Florianópolis, a desconsideração de fatores externos ao
sistema de transporte coletivo, como não haver o acesso em tempo real
aos ônibus, a desconsideração de trânsito e curvas --- o cálculo é
utilizado calculando pontos absolutos de distância ---, o cálculo do
tempo ser baseado em estimativas fornecidas pela própria prestadora de
serviços (estas últimas, ao meu ver, as que mais prejudicam a
aplicação), a desconsideração de fatores de custos de passagens aos
usuários do sistema de transporte.

Os objetivos não explicitam que tipo de método ou qual problema dentro
do VRP busca ser resolvido, quais técnicas pretende implementar, e
difere da justificativa do problema. O objetivo está contextualizado com
ênfase em ferramentas e não no problema em si.

## Análise da Conclusão

O trabalho desenvolvido satisfez o objetivo do autor em identificar as
ferramentas disponíveis para fornecimento de informações relativos a
rotas, utilizando diferentes softwares abertos de GIS, bancos de dados e
para cálculos computacionais. Os principais softwares abertos utilizados
foram o:

1.  OSM (OpenStreetMap) para a coleta de dados de infraestrutura de
    transporte;

2.  QGIS e GRASS como softwares de GIS para a visualização e análise de
    dados espaciais;

3.  PostgreSQL e PostGIS com a extensão pgRouting para a criação e
    modelagem de bancos de dados espaciais;

4.  Python para o desenvolvimento do algoritmo de cálculo de rotas.

O autor realiza o objetivo de utilizar softwares abertos para o
desenvolvimento, destacando os principais problemas encontrados durante
o processo e ressaltando que diversas simplificações tiveram que ser
realizadas, principalmente quando se tratando do cálculo de rotas.
Destaca também que não foram levadas em consideração o sentido das
linhas de ônibus, piorando os resultados obtidos, e que, melhores
resultados poderiam ser obtidos, mas a eliminação de resultados ruins
seriam uma tarefa mais complexa. Apesar destes problemas, a saída
através da linha de comando é bem informativa, mesmo não permitindo a
visualização através do mapa.

No geral, o objetivo principal proposto pelo trabalho foi atingida,
mesmo que o discente não tenha obtido um produto realmente funcional.

## Análise do Corpo do Trabalho

O problema a ser resolvido é uma variação do famoso Problema do Caixeiro
Viajante (TSP - Traveling Salesman Problem), que consiste em encontrar o
caminho mais curto possível que visita um conjunto de cidades e retorna
à cidade de origem. O nome da variação, apesar de não citado, é
denominada Problema de Roteamento de Veículos Capacitado com Coleta,
Entrega e Janelas de Tempo (CVRPPDTW - Capacitated Vehicle Routing
Problem with Pickup, Delivery and Time Windows), que adiciona restrições
de capacidade dos veículos e janelas de tempo de atendimento aos
clientes. Este problema é um problema NP-difícil, o que significa que
não existe uma solução eficiente conhecida para resolvê-lo em tempo
polinomial. Portanto, é necessário utilizar técnicas de otimização, como
algoritmos de busca local, algoritmos genéticos ou métodos heurísticos
para encontrar soluções aproximadas. É largamente estudado,
principalmente na área de pesquisa operacional, otimização e IA. Tem
aplicações em diversas áreas, como logística, transporte, engenharias,
eletrônica e ciência da computação. Estas observações não são
trabalhados no texto, mas seriam importantes para contextualizar o
problema e mostrar a relevância da solução proposta.

A justificativa do trabalho apresenta a importância do problema, mas não
entra nos detalhes sobre necessidade de uma solução computacional para a
definição de rotas baseadas no uso do sistema de transporte coletivo
para o usuário do sistema.

O autor poderia ter citado a relevância do problema na justificativa,
explicando como o uso do sistema de transporte coletivo pode contribuir
para a redução de emissões de gases de efeito estufa e reduzir o tempo
de deslocamento.

A busca por uma solução computacional para lidar com a complexidade dos
dados envolvidos, como a grande quantidade de informações sobre os
sistemas de transporte coletivo, a demanda de passageiros e as
restrições de capacidade dos veículos. Tal solução, se bem aplicada,
também diminuiria o tempo de planejamento, necessidade de recursos
humanos para a definição de rotas (consequentemente diminuindo erros
humanos), melhoraria a satisfação dos passageiros, diminuiria o uso de
recursos na mesma linha, teoricamente diminuiria gastos públicos com
empresas terceirizadas e manutenção de vias e ainda contribuiria para a
redução de congestionamentos nas cidades. Essas são apenas algumas das
possíveis aplicações do trabalho, que podem ser ainda mais impactantes e
que falhei em observar.

O trabalho realizado possui todas as partes constituintes necessárias,
onde o que não consta, não era aplicável. A metodologia utilizada é bem
explicada, a ênfase dada ao uso de softwares abertos é positiva, e o
discente demonstra um bom conhecimento adquirido através do processo
apesar das simplificações feitas. Julgo tais simplificações normais,
pois tal desenvolvimento iria além do escopo proposto por um trabalho de
conclusão de curso, necessitando de ferramentas mais robustas, métodos
não tão acessíveis, parcerias com empresas privadas para a obtenção de
dados precisos, financiamento e tempo. A revisão bibliográfica também é
bem trabalhada, trazendo diversas referências e resultados de trabalhos
já desenvolvidos.

## Análise dos resultados

Devido às simplificações e complexidade do tema proposto, muitas
simplificações são realizadas, gerando resultados que apesar de
realizarem o proposto, não são tão satisfatórios.

# Análise da Língua Portuguesa

A partir do que foi lido, não identifiquei nenhum erro ortográfico
crasso ou não conformação às normas da língua. O texto é bem escrito e o
discente demonstra um bom conhecimento da língua.

# Comentários Finais

O trabalho apresenta limitações, mas estas são normais para um trabalho
de conclusão de curso e não prejudicam o objetivo principal proposto. Ao
meu ver, trata-se de um ótimo trabalho, com boa revisão bibliográfica. O
discente demonstra ter adquirido bastante conhecimento dos softwares
utilizados. Além disso, o uso de softwares abertos democratiza a
acessibilidade a quem possa se interessar pelo tema.

O autor também disponibiliza o código fonte do trabalho, o que é um
ponto positivo, pois permite que outros possam replicar o resultado, e
até mesmo melhorá-lo. Seria interessante se o banco de dados utilizado
estivesse disponibilizado em anexo, mas é factível que isso não seja
possível devido ao seu tamanho, tendo o discente que arcar com os custos
da disponibilidade, tendo o mesmo provido as informações necessárias
para que a replicação do trabalho seja possível.
