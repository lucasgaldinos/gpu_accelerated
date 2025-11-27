UNIVERSIDADE FEDERAL DE SANTA CATARINA
CENTRO TECNOL ´OGICO
DEPARTAMENTO DE ENGENHARIA CIVIL
VICTOR HAMANN PEREIRA
DESENVOLVIMENTO DE M ´ETODO COMPUTACIONAL PARA DEFINIC ¸˜AO DE ROTAS BASEADAS
NO USO DO SISTEMA DE TRANSPORTE COLETIVO
6 de dezembro de 2017VICTOR HAMANN PEREIRA
DESENVOLVIMENTO DE M ´ETODO COMPUTACIONAL PARA DEFINIC ¸˜AO DE ROTAS BASEADAS
NO USO DO SISTEMA DE TRANSPORTE COLETIVO
Trabalho de Conclus ˜ao de Curso apresentado pelo acad ˆemico
Victor Hamann Pereira `a banca examinadora do Curso de
Graduac ¸ ˜ao de Engenharia Civil da Universidade Federal
de Santa Catarina como requisito parcial para obtenc ¸ ˜ao do
t´ıtulo de Engenheiro Civil.
Professor orientador: Alexandre Hering Coelho, Dr.
6 de dezembro de 2017Ficha de identificação da obra elaborada pelo autor,
 através do Programa de Geração Automática da Biblioteca Universitária da UFSC.
Pereira, Victor Hamann Pereira
   Desenvolvimento de método computacional para definição
de rotas baseadas no uso do sistema de transporte coletivo
/ Victor Hamann Pereira Pereira ; orientador, Alexandre
Hering Coelho Coelho, 2017.
   60 p.
   Trabalho de Conclusão de Curso (graduação) -
Universidade Federal de Santa Catarina, Centro Tecnológico,
Graduação em Engenharia Civil, Florianópolis, 2017.
   Inclui referências.

   1. Engenharia Civil. 2. Área de transportes. 3.
Transporte coletivo. 4. Sistemas de informações
geográficas. 5. Roteamento. I. Coelho, Alexandre Hering
Coelho. II. Universidade Federal de Santa Catarina.
Graduação em Engenharia Civil. III. Título.「 必 死 に 生 きてこそ、その 生 涯 は 光 を 放 つ」
織 田 信 長
iAGRADECIMENTOS
Agradeço aos meus pais pelo apoio e incentivo que me deram, e pelas lições que me ensinaram.
Ao professor e orientador Alexandre Hering Coelho pela dedicação tanto na sala de aula quanto
na orientação deste trabalho, e sobretudo pela paciência.
Aos amigos e colegas do curso pela jornada compartilhada ao longo da graduação.
A todos que de alguma forma contribuíram para a realização deste trabalho.
iiRESUMO
O planejamento de rotas é um passo importante do uso do sistema de transporte coletivo, e uma apre-
sentação adequada das informações de itinerários de ônibus e o uso de trip planners automatizados
podem facilitar o uso do sistema pelos usuários. O presente trabalho busca o desenvolvimento e a
implementação computacional de um método que, a partir de coordenadas geográﬁcas de partida e
chegada, e data e horário de partida, deﬁne rotas baseadas no sistema de transporte coletivo. Para
isso foram coletados dados da região central de Florianópolis, consistindo da malha viária, pontos e
itinerários das linhas de ônibus. Os dados coletados foram então processados de forma a possibilitar
a análise de rotas. O método é implementado através do uso de sistemas de informações geográﬁcas
e banco de dados espacial, com o auxílio de programação de scripts . As rotas são deﬁnidas com base
na rota de menor distância entre os pontos de partida e chegada. Como resultado são retornados rotas
de ônibus ordenadas pela estimativa de tempo de percurso, acompanhadas de instruções detalhadas
de como segui-las. Apesar de serem produzidos resultados em parte positivos, as limitações presentes
no método o distanciam de uma aplicação funcional.
Palavras-chave: ônibus urbano, roteamento, sistemas de informações geográﬁcas, banco de dados
espacial.
iiiABSTRACT
Trip planning is an important step in the usage of the public transportation system, and an adequate
presentation of itinerary information, as well as the usage of automated trip planners can help users
in the use of the system. This paper seeks to develop and implement a computational method which,
based on coordinates of origin and destination points, along with the departure date and time, deﬁnes
transit routes. For this purpose, data from the central region of Florianópolis were collected, consis-
ting of street network, bus stops and bus transit itineraries. The data were then processed in order to
enable route analysis. The method is implemented through the use of geographic information sys-
tems and spatial database, with the aid of scripting. The routes are deﬁned based on the shortest path
between origin and destination. The results are bus routes sorted by estimated time taken, accompa-
nied by detailed instructions on how to follow them. Despite partially positive results, the limitations
of the method distance it from having practical use.
Keywords: urban bus, routing, geographic information systems, spatial database.
ivLista de Siglas
ArcIMS Arc Internet Map Server
DARP Dial-a-Ride Problem
ESRI Environmental Systems Research Institute
GIS Geographic Information System
GRASS Geographic Resources Analysis Support System
MTC Montreal Transit Commission
OSM OpenStreetMap
PSQL PostgreSQL
SGBD Sistema Gerenciador de Banco de Dados
SIG Sistema de Informações Geográﬁcas
SQL Structured Query Language
vLista de Figuras
1 Relação topológica entre polígonos . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
2 Função snap . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12
3 Função break . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12
4 Método . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15
5 Preparação dos dados . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16
6 Interface do OpenStreetMap (OSM) . . . . . . . . . . . . . . . . . . . . . . . . . . 17
7 Tabela de atributos da camada de linhas do OSM, extraída do QGIS . . . . . . . . . 19
8 Tabela de atributos da camada de multilinhas . . . . . . . . . . . . . . . . . . . . . 19
9 Tabela de atributos da camada de pontos . . . . . . . . . . . . . . . . . . . . . . . . 19
10 Horários de saída de ônibus retirados do sitedo Consórcio Fênix . . . . . . . . . . . 20
11 Resultado da ﬁltragem . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21
12 Interseção entre links da malha . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22
13 Procedimento para deﬁnição de rotas . . . . . . . . . . . . . . . . . . . . . . . . . . 25
14 Deﬁnição de uma rota . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 29
15 Divergência entre rotas . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30
16 Estimativa do tempo levado . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 31
17 Exemplo de saída do método . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 34
18 Rota mostrada no mapa . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 35
19 Exemplo de saída com duas linhas de ônibus . . . . . . . . . . . . . . . . . . . . . . 35
viLista de Tabelas
1 Filtragem dos dados geométricos . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18
2 Listas de pontos de ônibus por link . . . . . . . . . . . . . . . . . . . . . . . . . . . 27
3 Trechos da rota . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33
4 Trechos da rota agrupados . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33
viiSumário
1 Introdução 1
1.1 Justiﬁcativa . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
1.2 Objetivos . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
1.2.1 Objetivo geral . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
1.2.2 Objetivos especíﬁcos . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
1.3 Limitações do trabalho . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
2 Revisão bibliográﬁca 4
2.1 Trabalhos relacionados . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4
2.2 Sistemas de informações geográﬁcas . . . . . . . . . . . . . . . . . . . . . . . . . . 5
2.2.1 Topologia . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
2.3 Banco de dados . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
2.3.1 Sistema gerenciador de banco de dados . . . . . . . . . . . . . . . . . . . . 9
2.3.2 SQL . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9
2.3.3 Banco de dados espacial . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
2.4 PostgreSQL . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
2.4.1 PostGIS . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
2.4.2 pgRouting . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
2.5 QGIS e GRASS GIS . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
2.6 Python . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13
3 Método 14
3.1 Preparação dos dados . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14
3.1.1 Criação do banco de dados espacial . . . . . . . . . . . . . . . . . . . . . . 14
3.1.2 Estudo de fontes de dados . . . . . . . . . . . . . . . . . . . . . . . . . . . 17
3.1.3 Coleta e ﬁltragem dos dados geométricos . . . . . . . . . . . . . . . . . . . 18
3.1.4 Tratamento topológico da malha viária . . . . . . . . . . . . . . . . . . . . 21
3.1.5 Coleta dos horários de saída dos ônibus . . . . . . . . . . . . . . . . . . . . 23
3.2 Desenvolvimento do procedimento para deﬁnição das rotas . . . . . . . . . . . . . . 23
3.2.1 Dados de entrada . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24
3.2.2 Rota de menor distância . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24
3.2.3 Deﬁnição das rotas de ônibus . . . . . . . . . . . . . . . . . . . . . . . . . 26
3.2.4 Estimativa de tempo levado para cada rota . . . . . . . . . . . . . . . . . . . 30
3.2.5 Dados de saída . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33
viii4 Resultados 34
5 Conclusões 36
5.1 Recomendações para trabalhos futuros . . . . . . . . . . . . . . . . . . . . . . . . . 36
Referências 38
APÊNDICE A - Comandos SQL 40
APÊNDICE B -Script de inserção dos horários de ônibus 41
APÊNDICE C -Script de roteamento 42
ix1 Introdução
Mobilidade urbana é um tema que afeta a todos. Filas e congestionamentos levam ao aumento do
tempo que as pessoas passam se locomovendo, resultando em uma queda da produtividade e da qua-
lidade de vida da população. Através do estudo de melhores formas de planejamento e operação dos
sistemas de transporte, seja na melhoria da infraestrutura viária ou do sistema de transporte coletivo,
a área de transportes pode oferecer soluções para os problemas relacionados à mobilidade urbana.
Segundo CNT (2017), no Brasil, o principal meio utilizado para o transporte de passageiros é o
rodoviário, principalmente devido à carência de oferta de outras infraestruturas de transporte.
Um modo muito comum no Brasil para o transporte coletivo é o ônibus. Uma parte importante
do serviço de ônibus é a disponibilização de informações aos usuários, de forma que estas possam
planejar suas viagens previamente.
O uso de sistemas de informações geográﬁcas (SIG) pode ser muito útil para o desenvolvimento
de sistemas que auxiliem no planejamento das viagens. Estes podem ser chamados de trip planners .
Trépanier et al. (2005) deﬁnem trip planner como ferramentas web que criam itinerários baseados em
transporte coletivo a partir de um par origem-destino informado pelo usuário.
Segundo Cherry et al. (2006), nos Estados Unidos, agências de transporte coletivo têm disponibi-
lizado informações na internet, usando mapas, itinerários e trip planners automatizados. No Brasil,
porém, é comum que estas informações sejam disponibilizadas de maneira limitada, mostrando os
horários de saída dos ônibus e suas rotas, porém sem indicar, por exemplo, os horários em que os
ônibus devem chegar em cada ponto de ônibus, e muitas vezes sequer quais linhas de ônibus passam
pelos pontos, diﬁcultando o uso do transporte coletivo.
Recentemente foi lançado o aplicativo ﬂoripanoponto1, um trip planner que deﬁne rotas de ôni-
bus baseado nas linhas de ônibus de Florianópolis, inclusive linhas que acessam o continente. Este
aplicativo possui uma interface gráﬁca de fácil utilização e, além de deﬁnir rotas de um ponto a ou-
tro da cidade, disponibiliza os itinerários das linhas de ônibus e previsão de chegada nos pontos de
ônibus. Este aplicativo é um bom exemplo de como disponibilizar as informações ao usuário, e seria
interessante que este tipo de serviço fosse prestado também em outras cidades brasileiras.
Além de facilitar o uso do sistema de transporte coletivo pela população, trip planners podem
ajudar os próprios provedores do serviço de ônibus a planejar e adaptar o sistema atual. Trépanier
et al. (2005) realizaram um estudo baseado em dados do histórico de uso de um trip planner do
sitedaMontreal Transit Commission (MTC) para determinar se estes dados seriam úteis ao planeja-
mento do transporte coletivo. A conclusão do estudo foi que os dados podem ajudar na identiﬁcação
de novos locais a serem acessados pelo sistema de transporte coletivo, no melhor entendimento do
comportamento dos usuários e na atualização do SIG e do trip planner em si.
1<https://www.floripanoponto.com.br/>
11.1 Justiﬁcativa
O sistema de transporte coletivo permite o deslocamento de pessoas sem a necessidade de possuir um
automóvel próprio. Cherry et al. (2006) comentam que um dos maiores problemas associados ao uso
de transporte coletivo é a apresentação da informação.
Uma melhor apresentação da informação relacionada ao transporte coletivo poderia incentivar seu
uso. Segundo Silva (2000), sistemas de informações aos usuários garantem um aumento na qualidade
do serviço ofertado aos passageiros.
Segundo International Energy Agency (2002) apud Lacerda (2006), veículos de passeio com ca-
pacidade para cinco passageiros correspondem a 62% do espaço ocupado por um ônibus urbano com
capacidade para quarenta passageiros. Considerando isso, um maior uso do sistema de transporte co-
letivo poderia reduzir os problemas de congestionamento da malha viária. Além de reduzir o tráfego,
os ônibus proporcionam grande mobilidade para a população:
"Os ônibus têm papel fundamental na mobilidade urbana, visto que são responsáveis
por alimentar esses sistemas, pois são meios de transporte com maior capilaridade e que
podem chegar a áreas mais distantes – e até mesmo mais isoladas – dos municípios,
permitindo, assim, maior acessibilidade para a população." (CNT, 2017, p. 12)
Um método capaz de determinar as melhores linhas de ônibus a serem utilizadas para se locomo-
ver de um ponto a outro facilitaria o uso deste sistema, sendo muito útil para a sociedade.
1.2 Objetivos
1.2.1 Objetivo geral
Desenvolver e implementar, com recursos computacionais, um método que determine rotas de ônibus
urbano com base em dados e recursos de software abertos.
1.2.2 Objetivos especíﬁcos
Identiﬁcar e estudar ferramentas disponíveis para fornecimento de informações relativas a rotas
de ônibus urbano;
Estudar e aplicar técnicas de modelagem de banco de dados espacial;
Coletar dados necessários para constituir um banco de dados capaz de dar suporte a um sistema
de informações sobre rotas de ônibus urbano;
Aplicar funcionalidades de sistemas de informações geográﬁcas para processamento de dados
espaciais relativos a infraestrutura de transporte;
Analisar os resultados obtidos pelo método.
21.3 Limitações do trabalho
Este trabalho possui limitações que distanciam o funcionamento do método da realidade.
A malha viária é modelada como uma rede seguindo uma estrutura de grafo. Desta forma, a
velocidade do percurso de cada linkda malha é considerada como constante, e não são considerados
os efeitos de curvas.
Em relação aos dados coletados, foi estudada somente a região central de Florianópolis, e só foram
coletadas informações relacionadas a parte das linhas de ônibus que compõe o sistema de transporte
coletivo da cidade.
O método desenvolvido neste trabalho opera de maneira estática, sem considerar dados de posici-
onamento de ônibus ou da operação do sistema de transporte em tempo real. Não são considerados,
por exemplo, congestionamentos que poderiam reduzir a velocidade do percurso nas rotas de ônibus.
Além disso, as velocidades dos ônibus são consideradas como constantes, baseadas em informa-
ções disponibilizadas pelo provedor do serviço de ônibus, não levando em consideração informações
sobre horários de pico.
A avaliação das rotas deﬁnidas é feita somente em relação à estimativa de tempo levado, sem
considerar a distância total percorrida a pé ou custos de passagens.
32 Revisão bibliográﬁca
Nesta seção são explorados conceitos necessários à realização do trabalho. Primeiramente são apre-
sentados trabalhos que tratam de desenvolvimento de trip planners e de roteamento. A análise destes
trabalhos remete a conceitos intimamente relacionados: sistema de informações geográﬁcas, uso de
banco de dados com funções de relacionamento espacial e linguagem de programação. Então, a
revisão aborda também estes conceitos na sua sequência.
2.1 Trabalhos relacionados
Hickman (2002) desenvolveu um método para deﬁnir rotas de ônibus para a rede de ônibus Sun
Tran em Tucson, Arizona, que utiliza dados históricos da operação do sistema de ônibus para, além
de determinar as rotas mais rápidas, calcular a probabilidade da rota levar o tempo estimado. Este
método elimina rotas de maior tempo conforme é aplicado, de forma a reduzir a sua demanda por
processamento computacional.
Cherry et al. (2006) desenvolveram um protótipo de trip planner que deﬁne rotas para a Sun
Tran baseado em SIG. Este sistema permite ao usuário deﬁnir o local de partida e pontos os quais
queira visitar clicando no mapa. O desenvolvimento foi feito com o software Arc Internet Map Ser-
ver(ArcIMS) da Environmental Systems Research Institute (ESRI), capaz de apresentar informações
geográﬁcas através da Internet, e consistiu de três etapas:
desenvolvimento de um mapa SIG, baseado em arquivos shapeﬁle ;
criação de um serviço de mapas, que gera os mapas apresentados ao usuário a partir do original;
design da interface utilizada pelo usuário.
O roteamento foi feito com base no algoritmo de Hickman (2002). Os dados de entrada do pro-
tótipo são os locais de partida e chegada, os time points em que o usuário gostaria de subir no ônibus
(time points sendo pontos que têm horários de passagem do ônibus conhecidos) e o horário em que
o usuário gostaria de chegar no local. A rota é então informada ao usuário através de um conjunto
de instruções textuais de como segui-la. A principal limitação está relacionada à performance do
sistema, que precisa gerar milhares de objetos para mostrar o mapa ao usuário.
Nienkotter (2017) desenvolveu um algoritmo de roteirização baseado no algoritmo de Clark &
Wright para a análise de rotas de empilhadeiras em armazéns de grande porte. Este algoritmo leva
em consideração as operações de picking , ou coleta, e de armazenamento de forma conjunta, ou seja,
com as empilhadeiras fazendo ambas as operações, em vez de se deﬁnir um grupo de empilhadeiras
para realizar cada operação.
4Foi realizado um estudo de caso em uma empresa de grande porte, comparando a deﬁnição das
rotas no momento do trabalho com as produzidas pelo modelo proposto. A partir deste estudo, porém,
não foi observada economia de mão-de-obra nas soluções geradas pelo modelo.
Haweroth (2017) realizou um estudo de roteirização no serviço Transporte Eﬁciente, em Joinville,
propondo conﬁgurações de rotas baseadas no Dial-a-Ride Problem (DARP), que consiste de otimizar
rotas para o transporte de um conjunto de pessoas com um ponto de partida e chegada, de forma a
atender às suas restrições.
Foi desenvolvido um método baseado em uma heurística de programação que leva em considera-
ção o atraso. O método foi implementado na linguagem de programação C#, e acabou apresentando
tempo de execução elevado e gerando soluções não-factíveis.
2.2 Sistemas de informações geográﬁcas
Para trabalhar com características geométricas é útil o estudo de SIG. SIG possibilitam a análise e
processamento de dados relacionados geometricamente.
SIG, do inglês geographic information system , pode ser deﬁnido como um conjunto de ferramen-
tas para coletar, armazenar, transformar e visualizar dados espaciais do mundo real para um conjunto
particular de propósitos (BURROUGH, 1986).
Mais do que um conjunto de ferramentas, é importante deﬁnir SIG como sistemas computacionais,
que permitem a automatização de tarefas de alta complexidade. Um aspecto de SIG a ser analisado é
a maneira como os dados são representados.
Segundo Burrough (1986), todo SIG é uma representação computacional de aspectos do mundo
real, e que, como seria impossível representar todos os elementos nos quais se tem interesse, SIG
apresentam uma visão simpliﬁcada do mundo, frequentemente chamada de modelo. Para entender a
maneira como SIG representam a realidade, é necessário entender o modelo de dados que utilizam.
Hagget e Chorley (1967) apud Burrough (1986) deﬁnem modelo como uma síntese de dados,
usada para lidar com um sistema cuja escala ou complexidade seja demasiado elevada.
O modelo utilizado por SIG é baseado em elementos, ou tipos de dado, básicos, que quando
agrupados e relacionados, representam o espaço, objetos contidos no espaço e as relações entre estes
objetos.
Os elementos básicos utilizados por SIG são três: (MONMONIER, 1991):
pontos;
linhas;
áreas.
5Como representações da realidade, sob uma ótica geográﬁca, SIG estão intimamente relacionados
com mapas, que em grande parte utilizam os mesmos elementos para a representar o mundo. Mapas
rodoviários, por exemplo, utilizam uma combinação dos três elementos básicos: pontos para indicar
a localização de marcos e pequenas cidades, linhas para indicar o comprimento e formato de rios e
rodovias, e áreas para representar o tamanho e formato de cidades grandes.
Cada elemento representa objetos com foco em características diferentes destes. Segundo Güting
(1994), um ponto representa um objeto cuja localização é importante, mas sua dimensão não. Linhas
representam estruturas que permitam o deslocamento no espaço, ou conexões entre objetos no espaço.
A área, em contraste ao ponto, representa objetos em que suas dimensão e formato são relevantes,
como países.
O elemento utilizado para representar elementos do mundo real depende, entre outros fatores, da
escala em que se pretende trabalhar. Segundo Monmonier (1991), a maioria dos mapas são menores
do que a realidade que representam, e a escala indica o quão menor o mapa é.
Os mapas rodoviários do exemplo anterior trabalham com escalas relativamente grandes. Um
mapa de uma cidade, por exemplo, teria uma escala menor. Neste contexto, o elemento representado
por cada tipo de dado muda. A cidade em si passa a ser uma área, pois nesta escala sua dimensão
é relevante, enquanto as linhas podem representar a malha viária e pontos a localização de pontos
turísticos, entre outros.
A partir do agrupamento e relacionamento de elementos básicos, é possível deﬁnir elementos mais
complexos para acomodar diferentes fenômenos do mundo real. Segundo Heywood et al. (2006),
além dos três tipos básicos (ponto, linha e área), existem outros dois tipos de dado: redes e super-
fícies. Uma rede é um conjunto de linhas conectadas, podendo representar a malha viária e redes
hidrográﬁcas, por exemplo. A superfície é uma área tridimensional. Uma superfície pode ser usada
para representar topograﬁa ou variáveis não-topográﬁcas como densidade demográﬁca e nível de po-
luição.
Com estes cinco tipos de dado, é possível representar a realidade a um alto nível de complexidade
sem sobrecarregar o sistema com detalhes. É importante, porém, entender como exatamente esta
representação é feita por um computador.
O olho humano é capaz de identiﬁcar formas eﬁcientemente, mas um computador necessita de ins-
truções exatas sobre como padrões espaciais devem ser manipulados e apresentados (BURROUGH,
1986 apud HEYWOOD et al., 2006).
A maneira como isto é feito afeta SIG em vários níveis, desde o armazenamento ao processamento
e análise dos dados, sendo de suma importância entender as implicações de se utilizar cada aborda-
gem. Heywood et al. (2006) aﬁrma que existem duas principais formas de representação de entidades
espaciais por computadores. São as abordagens vetorial e raster .
Os mesmos autores explicam que o modelo de dados raster utiliza células individuais como blo-
6cos para construção de imagens que representam pontos, linhas, áreas, redes e superfícies. Neste
modelo, o formato e tamanho das entidades espaciais é deﬁnido a partir do agrupamento das células.
O tamanho da célula é importante, pois inﬂuencia como as entidades serão mostradas.
Imagens obtidas por satélite, por exemplo, podem ser vistas como um modelo raster da realidade,
em que cada pixel da imagem corresponde a uma área, representada pela cor captada pelo satélite. A
partir da análise destes pixels é possível mapear objetos do mundo real.
A abordagem vetorial trabalha os tipos de dado de maneira diferente. Segundo Heywood et al.
(2006), o modelo vetorial de dados utiliza coordenadas cartesianas (x,y) para armazenar a forma de
uma entidade espacial. Neste modelo, em contrapartida ao raster , o ponto é o bloco de construção
mais básico a partir do qual os outros tipos de dado são deﬁnidos. Linhas e áreas são construídas
conectando-se séries de pontos. Uma linha é um polígono aberto, enquanto uma área é um polígono
fechado. Quanto mais complexo o formato de uma entidade, mais pontos são necessários à sua
representação.
2.2.1 Topologia
A relação entre elementos representados espacialmente pode ser descrita com o uso da topologia. A
partir das relações topológicas entre objetos é possível realizar diversas análises dos sistemas que estes
compõem. A topologia é também uma ótima ferramenta para a manutenção e garantia da integridade
de dados geométricos.
Segundo Obe e Hsu (2015), a topologia deﬁne as regras de inter-relação entre geometrias. Por
exemplo, considerando polígonos que representem áreas vizinhas, a topologia descreve quais vértices
destes polígonos são compartilhados. Se as áreas reais por algum motivo forem modiﬁcadas, o modelo
deve ser modiﬁcado da mesma maneira. A relação topológica entre os polígonos garante a integridade
dos dados quando as alterações forem feitas, sem sobreposição ou espaços vazios entre os elementos.
Na Figura 1 estão representadas três áreas vizinhas que sofreram modiﬁcações, mostrando as
mudanças correspondentes nas suas representações. Após a alteração, os polígonos que representam
as áreas continuam adjacentes uns aos outros, e as linhas que os delimitam continuam conectadas
corretamente.
A topologia é particularmente útil para representar redes. Neste caso, a relação topológica entre
as linhas e nós deﬁne quais linhas estão conectadas a quais nós. Neste sentido, a estrutura de uma
rede de links conectados por nós pode ser descrita utilizando um grafo:
"Grafo é um modelo matemático que representa relações entre objetos. Um grafo é um
conjunto dado por G= (V;E ), onde Vé um conjunto ﬁnito de pontos, normalmente
denominados de nós ou vértices e Eé uma relação entre vértices, ou seja, um conjunto
de pares em VV." (LINDEN, 2009)
Assim, cada nó é um vértice do grafo, enquanto cada linké um par ordenado de vértices, ou seja,
7Figura 1: Relação topológica entre polígonos
uma aresta do grafo. A partir da estrutura de grafo, é possível fazer análises ligadas a roteamento, ou
seja, como uma rede pode ser percorrida.
Para se representar o ﬂuxo de uma rede, é fundamental que seja possível representar o sentido
do ﬂuxo. Segundo Linden (2009), um grafo pode ser direcionado ou não. No caso direcionado, as
arestas somente podem ser percorridas no sentido início-ﬁm, enquanto no caso não-direcionado isso
não é necessário.
Em determinada malha viária, por exemplo, podem existir na mesma rede ruas de um sentido e
de dois. Portanto, para que o sentido das ruas seja considerado, pode-se utilizar um grafo direcionado
em que haja duas arestas para as ruas de dois sentidos, e somente uma para as de um sentido.
2.3 Banco de dados
Foram abordados até aqui assuntos relacionados à representação de dados geométricos. É importante
entender também como estes dados são armazenados e gerenciados pelo computador.
Uma ferramenta importante a ser estudada é o banco de dados. Segundo Ramez e Navathe (2005),
um banco de dados é uma coleção de dados com as seguintes propriedades:
os dados armazenados representam aspectos do mundo real;
o banco de dados é uma coleção lógica e coerente de dados;
o banco de dados é projetado, construído e povoado por dados de forma a atender a um propósito
especíﬁco.
8O banco de dados é muito útil para o gerenciamento de dados. Um modelo de banco de dados
muito utilizado é o modelo relacional. Um banco de dados relacional é um banco de dados no qual
os dados armazenados são visualizados por meio de relações, ou seja, confuntos de informações
associadas (DATE, 2003).
Um banco de dados relacional, segundo Sumathi e Esakkirajan (2007), utiliza uma coleção de
tabelas para representar tanto dados quanto a relação entre estes dados. Cada linha da tabela repre-
senta um elemento ou relação entre elementos, enquanto as colunas contêm características destes
elementos.
Codd (1990) ressalta que os dados contidos no banco de dados devem ser identiﬁcados, de forma a
garantir a integridade dos dados. Geralmente é reservada uma coluna para a identiﬁcação do elemento,
para que seja possível rastreá-lo ao se realizar consultas.
Por exemplo, as arestas de um grafo podem ser representado minimamente pelos seus nós de
início e ﬁm. Logo a tabela que contiver estas arestas possuirá, no mínimo, as três seguintes colunas:
identiﬁcação;
nó de início;
nó de ﬁm.
Cada linha da tabela representa uma aresta com as características correspondentes aos valores em
cada coluna.
2.3.1 Sistema gerenciador de banco de dados
O banco de dados armazena dados, mas para acessar estes dados e processá-los, ou realizar consul-
tas mais complexas aos dados, relacionando várias tabelas, são utilizados sistemas gerenciadores de
banco de dados (SGBD).
Ramez e Navathe (2005) deﬁnem um SGBD como um software que facilita a deﬁnição, constru-
ção, manipulação e compartilhamento de banco de dados. Segundo Sumathi e Esakkirajan (2007),
um SGBD é capaz de manipular e retirar dados armazenados em um banco de dados relacional.
2.3.2 SQL
A comunicação com um SGBD é feita através de uma linguagem de consulta, com a qual são dadas
ao SGBD as instruções de como trabalhar com os dados armazenados.
Segundo Codd (1990), uma linguagem de consulta deve possuir quatro comandos básicos:
retrieve (coletar);
insert (inserir);
9update (atualizar);
delete (deletar).
Estas operações são a base para se manipular os dados armazenados em um banco de dados.
A linguagem padrão utilizada na comunicação com um SGBD é o Structured Query Language
(SQL) (SUMATHI; ESAKKIRAJAN, 2007).
O SQL implementa estas operações através dos comandos " select ", "insert ", "update " e "delete ".
2.3.3 Banco de dados espacial
Para que possam ser armazenados dados geométricos em bancos de dados, é necessária a implemen-
tação de dispositivos especíﬁcos para este propósito. Um banco de dados capaz de armazenar estes
dados é denominado de banco de dados espacial.
Segundo Obe e Hsu (2015), um banco de dados espacial possui tipos de dado especiﬁcamente
desenhados para armazenar objetos no espaço. Considerando isso, um banco de dados espacial pode
ser parte de um SIG, especiﬁcamente a parte de armazenagem das camadas de dados.
Uma característica importante de bancos de dados espaciais é a capacidade de se indexar os dados
espaciais. Güting (1994) explica que o principal propósito da indexação espacial é permitir a seleção
de dados com base em relações geométricas. A indexação organiza o espaço e os objetos de forma que
somente parte do espaço e um subconjunto dos objetos precisem ser considerados para realizar esta
seleção. Isto acelera a manipulação e processamento de dados geométricos, viabilizando a realização
de tarefas complexas que envolvam séries de consultas ao banco de dados espacial.
As próximas seções da revisão são dedicadas a abordar algumas ferramentas capazes de imple-
mentar os conceitos de SIG e banco de dados espacial vistos até agora.
2.4 PostgreSQL
PostgreSQL (PSQL) é uma ferramenta capaz de gerenciar bancos de dados:
"O PostgreSQL é um SGBD relacional, utilizado para armazenar informações de solu-
ções de informática em todas as áreas de negócios existentes, bem como administrar o
acesso a essas informações." (MILANI, 2008, página 25)
O PSQL é open source , sendo uma ferramenta muito acessível para o desenvolvimento de sistemas
baseados em banco de dados.
Existem diversas extensões que podem ser instaladas em bancos de dados PSQL.
102.4.1 PostGIS
Para permitir o armazenamento de dados geométricos em bancos de dados PSQL, é utilizada e exten-
são PostGIS.
A extensão PostGIS deﬁne uma série de funções para o processamento de dados geométricos. O
PostGIS permite a realização de análises de caráter geométrico de dados, como cálculo de distância
entre elementos, se estes se interceptam ou estão contidos uns nos outros.
2.4.2 pgRouting
Para adicionar ao PSQL funções de roteamento e de análise topológica de redes, é instalada a exten-
são pgRouting (PGROUTING TEAM, 2017). Para que seja instalado o pgRouting, é necessário a
instalação prévia do PostGIS.
Entre as funções implementadas pelo pgRouting, destaca-se a função pgr_dijkstra. Esta função
encontra a rota de menor custo entre dois nós de um grafo (PGROUTING TEAM, 2017), podendo
este ser direcionado ou não. O custo é um valor associado às arestas, normalmente links de uma malha
viária, do grafo e pode ser arbitrado ou calculado a partir de características de cada link, podendo ser
usado, por exemplo, o comprimento do linkcomo custo. Neste caso o caminho encontrado é o de
menor distância.
Os dados de entrada para esta função são uma rede de links conectadas por nós, o valor do custo
para se percorrer o link, e os nós de início e ﬁm. No caso não-direcionado, é considerado o mesmo
custo em ambos os sentidos, enquanto no caso direcionado deve ser informado o custo para cada
sentido. Valores negativos indicam que não é possível percorrer o linkneste sentido.
2.5 QGIS e GRASS GIS
Duas ferramentas muito úteis capazes de implementar funcionalidades SIG são o QGIS e o Geo-
graphic Resources Analysis Support System (GRASS). Estas têm um alto nível de integração, sendo
possível utilizar funções do GRASS em dados carregados no QGIS.
Segundo Obe e Hsu (2015), QGIS é uma ferramenta para visualização, edição e análise de SIG.
O QGIS possui um alto nível de integração com o PostGIS, permitindo a conexão direta entre as
camadas de dados armazenadas no banco de dados espacial.
Segundo Neteler e Mitasova (2007), GRASS é um SIG que trabalha com camadas de dados raster
e vetoriais, com processamento integrado de imagem e visualização de subsistemas de dados.
O GRASS possui uma série de funções para o processamento computacional de dados, que são
agrupadas em módulos. Em especial pode-se citar as funções para o tratamento topológico de ca-
madas de dados vetoriais. Para isso é usado o módulo v.clean (GRASS DEVELOPMENT TEAM,
2017). As funções deste módulo realizam pequenas correções para garantir a integridade do modelo.
11A função snap está ilustrada na Figura 2. Esta função conecta vértices a outro vértice que esteja
mais próximo do que um valor de tolerância dado como entrada (GRASS DEVELOPMENT TEAM,
2017). Desta forma, links que tenham seu nó de início ou ﬁm muito próximo a outro nó têm seu
tamanho e formato ajustados. Isto garante que uma rota gerada possa passar por esses links . Esta
função nem sempre deve ser aplicada. Se a conexão não existir nas ruas reais sendo representadas
pelos links , estes não devem ser conectados um ao outro, pois isso seria uma representação incorreta
da malha.
Figura 2: Função snap
A função break , ilustrada na Figura 3, quebra linhas nas interseções com outras linhas (GRASS
DEVELOPMENT TEAM, 2017). No caso mostrado na Figura 3 os dois links interceptantes são
quebrados na sua interseção, resultando em quatro links , todos conectados pelo nó central. Assim
como a função snap , esta nem sempre deve ser aplicada. Em alguns casos, como viadutos e túneis,
não existe uma conexão real entre as ruas representadas pelos links . Nestes casos não se deve utilizar
esta função.
Figura 3: Função break
122.6 Python
A partir da programação de scripts integrados às ferramentas abordadas anteriormente, é possível
utilizar várias funções de diferentes software de forma sequencial, utilizando os resultados de uma
função como parâmetro de outra. Isto aumenta o nível de complexidade das tarefas que podem ser
realizadas, e permite a automatização de processos.
Uma linguagem de programação capaz de aplicar este conceito muito bem é o Python, por pos-
suir várias bibliotecas capazes de integrar programação a sistemas de banco de dados. Segundo Lutz
(2011), há interfaces que permitem a comunicação entre scripts em Python e bancos de dados re-
lacionais como MySQL, PostgreSQL e Oracle. Programando em Python, é possível desenvolver
aplicações complexas rapidamente, utilizando as bibliotecas já disponíveis.
133 Método
Para se deﬁnir as rotas de ônibus, são necessárias informações sobre a infraestrutura de transporte
coletivo, consistindo de quatro elementos:
malha viária;
itinerários das linhas de ônibus;
localização dos pontos de ônibus;
horários de saída dos ônibus.
A partir destes dados, é possível o desenvolvimento de um procedimento que deﬁna as rotas. Este
procedimento deve acessar os dados coletados e extrair informações geométricas e não-geométricas,
e então retornar os itinerários de cada rota, distâncias percorridas e tempo levado.
Neste sentido é útil o estudo de formas de coleta, armazenamento e processamento destes dados,
e de análise de redes de transporte. Tendo isso em mente, o método é dividido em duas partes, a
primeira sendo a preparação dos dados (Seção 3.1), e a segunda o desenvolvimento do procedimento
para deﬁnição das rotas (Seção 3.2). O método do trabalho está ilustrado de forma geral no ﬂuxograma
da ﬁgura 4.
3.1 Preparação dos dados
A preparação dos dados envolve a coleta, armazenamento e processamento de dados de forma a
possibilitar a análise de rotas. O processo de preparação dos dados está ilustrado no ﬂuxograma da
Figura 5, e seus passos serão descritos em maior detalhe nas seções 3.1.1 a 3.1.5.
3.1.1 Criação do banco de dados espacial
Com o intuito de armazenar os dados, foi criado o banco de dados. Este foi criado a partir do Post-
greSQL. Para torná-lo um banco de dados espacial, foi instalada a extensão PostGIS. O pgRouting foi
instalado para possibilitar a análise de roteamento, importante para os passos descritos mais adiante,
na seção 3.2. Isto foi feito através de linha de comando, com os comandos2"create database" e "create
extension":
CREATE DATABASE mydb ;
CREATE EXTENSION p o s t g i s ;
CREATE EXTENSION p g r o u t i n g ;
2A lista com os comandos SQL utilizados neste trabalho encontra-se no Apêndice A.
14Figura 4: Método
15Figura 5: Preparação dos dados
16Desta forma é possível armazenar os dados geométricos no banco de dados conforme estes são cole-
tados.
3.1.2 Estudo de fontes de dados
O passo seguinte à criação do banco de dados foi estudar fontes para os dados necessários ao traba-
lho. Para dados geométricos, a fonte escolhida foi o OpenStreetMap (OSM)3, por conter informações
geométricas, georreferenciadas, da infraestrutura de transporte suﬁcientes para o desenvolvimento do
método. Segundo Haklay e Weber (2008), o projeto OSM é uma coleção de dados que providencia
mapas viários gerados por seus usuários. Os mesmos autores explicam que a função de exportação
do OSM permite o download de dados do OSM em diferentes formatos vetoriais e raster para pro-
cessamento. A Figura 6 mostra a interface do OSM acessado via web. É possível delimitar a área a
ser exportada através da própria interface gráﬁca.
Figura 6: Interface do OSM
Foram importados dados do OSM em formato vetorial, guardadas em um arquivo no formato
osm. Este arquivo foi então aberto no QGIS e suas camadas de dados foram carregadas. A partir
das tabelas de atributos das camadas de dados, estes foram examinados para descobrir exatamente
quanta informação estava disponível. A Figura 7 mostra a tabela de atributos da camada de linhas
importada. Cada coluna da tabela representa alguma característica das linhas. As colunas relevantes
para este trabalho são as colunas name ehighway , que indicam, no caso de linhas que representem
3<https://www.openstreetmap.org/>
17ruas, o nome da rua e o tipo de rua que a linha representa.
Além de linhas foram importadas camadas de multilinhas e pontos. Suas tabelas de atributos estão
mostradas nas Figuras 8 e 9. No caso das multilinhas, na coluna other_tags é possível descobrir quais
multilinhas representam linhas de ônibus ("route"=>"bus"), e a coluna name indica o nome da linha.
Para os pontos, a coluna highway indica quais pontos são pontos de ônibus ( bus_stop ).
Ositedo Consórcio Fênix4disponibiliza horários de sáida e tempos estimados para o percurso
total das linhas de ônibus. Na Figura 10 é mostrado um exemplo das informações encontradas.
3.1.3 Coleta e ﬁltragem dos dados geométricos
Foram coletados, a partir do OSM, dados da região central de Florianópolis vista a familiaridade do
autor com a malha viária e linhas de ônibus presentes nesta região, possibilitando a inspeção dos dados
coletados. A inspeção dos dados vetoriais foi feita visualmente e a partir das tabelas de atributos no
QGIS, de forma semelhante ao mostrado na seção 3.1.2.
As camadas de dados coletadas tiveram de ser ﬁltradas por conterem mais dados do que o neces-
sário, o que causaria interferência no procedimento para a deﬁnição das rotas. Além das rodovias,
as linhas representam outros elementos como hidrovias e divisas administrativas. Se esses não fos-
sem removidos, a representação da malha viária estaria incorreta, e rotas passando por linhas que
não representam ruas poderiam ser geradas. Algumas das multilinhas coletadas representam rodovias
estaduais, e algumas das linhas de ônibus tinham parte de seu traçado fora da área coletada. A mai-
oria dos pontos coletados não representam pontos de ônibus mas sim outros objetos e localizações.
Portanto foi utilizado o QGIS para ﬁltrar estes dados de forma a se obter somente os dados desejados,
conforme a tabela 1.
Tabela 1: Filtragem dos dados geométricos
Tipo de dado Dado obtido
Linha Malha viária
Multilinha Traçado das linhas de ônibus
Ponto Pontos de ônibus
A ﬁltragem foi feita a partir das informações nas tabelas de atributos das camadas de dados (Figu-
ras 7, 8 e 9). Foram utilizados os seguintes comandos SQL a na janela de ﬁltragem do QGIS. Foram
selecionadas linhas em que a coluna highway não estivesse vazia:
highway IS NOT NULL
Foram selecionados pontos em que a coluna highway estivesse deﬁnida como "bus_stop":
highway = ’ b u s _s t o p ’
4<http://www.consorciofenix.com.br/horarios/>
18Figura 7: Tabela de atributos da camada de linhas do OSM, extraída do QGIS
Figura 8: Tabela de atributos da camada de multilinhas
Figura 9: Tabela de atributos da camada de pontos
19Figura 10: Horários de saída de ônibus retirados do sitedo Consórcio Fênix
E por ﬁm, multilinhas com a tag"’route’=>’bus_stop’":
o t h e r _t a g s LIKE ’%" r o u t e "= >" bus"% ’
No caso das linhas de ônibus, foram removidas as linhas que estivessem visivelmente incompletas,
por estarem parcialmente fora da área coletada. Além disso, foram deixadas somente onze linhas, o
que já é suﬁciente para o desenvolvimento do método.
Na Figura 11 está ilustrada parte dos dados antes e depois do processo de ﬁltragem. É possível
observar que a maioria dos pontos, que representam árvores, lojas e outras localidades, são removidos,
deixando somente os pontos de ônibus. Além disso, linhas que não representam a malha viária foram
20removidas.
Figura 11: Resultado da ﬁltragem
Após a ﬁltragem das camadas de dados geométricas, os pontos e linhas de ônibus foram inseridas
no banco de dados através do QGIS. Ao se fazer isso, foram criadas automaticamente as tabelas
no banco de dados contendo as mesmas informações que as tabelas de atributos, com adição de
uma coluna de identiﬁcação dentro do banco de dados e uma contendo a geometria dos elementos
inseridos.
3.1.4 Tratamento topológico da malha viária
Quando são coletados dados de uma malha viária, é possível que haja problemas na modelagem e que
a representação geométrica das vias não esteja conectada corretamente. Nestes casos, para que seja
possível gerar um grafo a partir da malha, é necessário o tratamento topológico desta malha.
Nos dados da malha viária coletados para este trabalho, foram encontrados alguns problemas
desta natureza. A Figura 12 é um screenshot do QGIS onde é mostrado um caso de interseção entre
links da malha. A linha mais grossa representa um único linkque está atravessando outros nos pontos
circulados.
O tratamento topológico foi feito com o módulo v.clean do GRASS. Para isso a camada de dados
contendo a malha viária foi exportada do QGIS para um arquivo shapeﬁle , que foi então importado
pelo GRASS. Então foram utilizadas as funções break esnap . A função break quebrou os links da
malha nas interseções detectadas. A função snap foi então utilizada para para garantir a conexão entre
oslinks da malha.
É importante notar que estas funções foram aplicadas em todos os links da malha. Não foi feita
uma análise para se determinar quais links deveriam ser ignorados, como links que representem via-
dutos ou túneis.
21Figura 12: Interseção entre links da malha
Com a malha corrigida, esta foi inserida no banco de dados, gerando a tabela de links . Então
foram criadas duas colunas nesta tabela para conter os nós de início ( source ) e ﬁm ( target ), com os
seguintes comandos:
ALTER TABLE b u s_ l i n e s ADD C O L U M N s o u r c e i n t e g e r ;
ALTER TABLE b u s _l i n e s ADD C O L U M N t a r g e t i n t e g e r ;
Na sequência utilizada a função pgr_create_topology dopgrouting a partir da geometria dos links
para gerar a tabela de nós e preencher as colunas de nós de início e ﬁm, dando como parâmetros o
nome da tabela de links (edges ) e a tolerância (distância mínima entre nós a serem gerados):
SELECT p g r_ c r e a t e _t o p o l o g y ( ’ edges ’ , 0 . 0 0 0 1 ) ;
Desta forma os links são representados em forma de grafo, possibilitando o uso da função de rotea-
mento.
223.1.5 Coleta dos horários de saída dos ônibus
Com os dados geométricos todos inseridos no banco de dados, foram coletados os horários de saída e
tempos de percurso total para cada linha de ônibus. Os tempos de percurso das linhas são utilizadas
para se estimar a velocidade média dos ônibus. Os horários indicam a disponibilidade do serviço.
Estes dados foram obtidos no sitedo Consórcio Fênix, em formato de texto. Os horários são
diferentes dependendo do dia da semana. Em Florianópolis, os horários de saída dos ônibus são mais
frequentes em dias úteis e menos em sábados, domingos e feriados. Algumas linhas operam somente
em dias úteis.
Para armazenar os horários de saída foi criada no banco de dados uma tabela com quatro colunas:
identiﬁcação;
linha de ônibus;
dia da semana (útil, sábado ou domingo);
horário de saída.
Isto foi feito executando o seguinte comando:
CREATE TABLE b u s_ d e p t _t i m e s (
i dPRIMARY KEY ,
b u s_ l i n e _i d i n t e g e r REFERENCES b u s_ l i n e s ,
day_group varchar ( 4 ) ,
time time ) ;
A identiﬁcação da linha de ônibus está relacionada à tabela de linhas de ônibus. Desta forma, com o
dia da semana e linha utilizada, é possível consultar os horários de saída da linha.
Para cada uma das linhas de ônibus coletadas, os seus horários foram copiados e inseridos no
banco de dados através de um script em Python, encontrado no Apêndice B deste trabalho. Um
exemplo do comando SQL utilizado pelo script para inserir cada horário está mostrado a seguir:
INSERT INTO b u s_ d e p t _t i m e s ( b u s_ l i n e _i d , day_group , time )
VALUES ( 5 , ’ u t i l ’ , 1 6 : 2 0 : 0 0 ) ;
Desta forma foi possível preencher a tabela de maneira rápida e eﬁciente.
3.2 Desenvolvimento do procedimento para deﬁnição das rotas
O procedimento para deﬁnição das rotas de ônibus foi desenvolvido a partir de programação de um
script na linguagem Python, que se encontra no Apêndice C. Este script realiza consultas ao banco
de dados baseadas nos dados de entrada. A partir das informações obtidas nas consultas é deﬁnida a
23rota de menor distância, e a partir desta são deﬁnidas as rotas de ônibus. Então é feito o cálculo do
tempo para cada rota. As rotas são então apresentadas em ordem crescente de tempo levado. Este
procedimento está ilustrado no ﬂuxograma da Figura 13 e será descrito em maior detalhe nas seções
3.2.1 a 3.2.5.
3.2.1 Dados de entrada
Os dados de entrada do método são os seguintes:
ponto de partida;
ponto de chegada;
data e horário de partida.
Estes são deﬁnidos no próprio script . Desta forma o script precisa ser alterado sempre que os
dados de entrada forem alterados.
Neste trabalho, pontos de partida e chegada são deﬁnidos por suas coordenadas x e y, e são utili-
zados na determinação da rota de menor distância.
O dia da semana, extraído da data, e o horário de partida determinam a disponibilidade do serviço
de transporte coletivo com base nos horários de saída armazenados no banco de dados.
3.2.2 Rota de menor distância
Primeiramente é utilizada a função ST_Distance do PostGIS para se determinar os nós da malha mais
próximos aos pontos de partida e chegada. Esta função recebe como parâmetros duas geometrias, e
retorna a sua distância. A função é aplicada para se determinar a distância de todos os nós aos pontos
de partida e chegada, e são encontrados os nós com os menores valores retornados. Isto é feito com o
seguinte comando:
SELECT id , ST_Distance ( the_geom : : geography , ST_GeomFromText ( ’POINT
( 48.552658  27.599111) ’ , 4 3 2 6 ) ) AS d i s t F R O M nodes ORDER BY d i s t LIMIT
1 ;
Há dois pontos a serem observados no comando:
a função ST_GeomFromText é usada para gerar uma geometria de ponto a partir de coordena-
das;
como as geometrias estão deﬁnidas em graus decimais, é utilizado o termo "::geography" para
que a distância seja retornada em metros.
24Figura 13: Procedimento para deﬁnição de rotas
25É então utilizada a função pgr_dijkstra do pgRouting para se determinar a rota de menor distância
entre estes nós. Como entrada da função são informados os links da malha, mais especiﬁcamente seu
nó de início, nó de ﬁm e comprimento (para o cálculo da distância percorrida), e os nós encontrados
pela função ST_Distance. O comprimento dos links é calculado através da função ST_Length do
PostGIS. O roteamento é feito no modo não-direcionado, pois a rota pode ser percorrida a pé. É
retornada a sequência de links da rota de menor distância. O comando SQL utilizado é o seguinte:
SELECT node , edge , c o s t , seq F R O M p g r _d i j k s t r a (
’SELECT id , source , t a r g e t , ST_Length ( the_geom : : geography ) AS c o s t
FROM edges ’ , {1} , {2} , f a l s e ) ;
o comprimento de cada link, em metros, é deﬁnido como o custo, de forma que a rota resultante
é a de menor distância;
{1} e {2} são substituídos pelos ids dos nós de início e ﬁm da rota;
o termo " false " nesta posição indica que o grafo não é direcionado. Se este fosse direcionado,
seria necessário informar o parâmetro " reverse_cost ".
3.2.3 Deﬁnição das rotas de ônibus
Para acelerar o procedimento de deﬁnição das rotas de ônibus, foi criada uma coluna na tabela de
pontos de ônibus relacionando estes aos links da malha, de forma a se determinar quais links possuem
pontos de ônibus:
ALTER TABLE b u s _s t o p s ADD C O L U M N c l o s e s t_ e d g e i n t e g e r ;
Foi utilizada a função ST_Intersects entre os links e as linhas de ônibus, e a partir dos resultados
positivos ( links interceptados pelas linhas) foi utilizada a função ST_Distance entre os links e pontos
de ônibus para se determinar os links mais próximos a cada ponto. A coluna closest_edge de cada
ponto foi então deﬁnida com o id do linkcorrespondente. Foi utilizado o seguinte comando para
realizar esta operação:
UPDATE b u s_ s t o p s SET c l o s e s t _e d g e = i d e F R O M (
SELECT DISTINCT idb , f i r s t_ v a l u e ( i d e ) OVER ( PARTITION BY i d b ORDER BY
d i s t ) AS i d e F R O M (
SELECT b . i d asidb , e . i d aside , ST_Distance ( e . the_geom , b . the_geom ) AS d i s t
F R O M edges e , b u s_ s t o p s b , b u s _l i n e s l
W H E R E S T_ I n t e r s e c t s ( e . the_geom , l . the_geom ) ) AS foo
)AS b a r W H E R E i d = i d b ;
26Para se deﬁnir as rotas de ônibus a partir da rota de menor distância, é inicialmente consultada a
tabela do banco de dados que deﬁne quais links têm pontos de ônibus:
SELECT c l o s e s t _e d g e F R O M b u s_ s t o p s ;
A partir dos valores retornados são determinados quais links da rota de menor distância têm pontos
de ônibus. Então é utilizada a função ST_Intersects entre estes links e as linhas de ônibus para se
determinar quais destas passam pelos links selecionados:
SELECT l . i d F R O M b u s_ l i n e s l , edges e
W H E R E e . i d = {1} AND S T _I n t e r s e c t s ( e . the_geom , l . the_geom ) ;
{1} é substituído pelo id do link.
Não é considerado o sentido das linhas de ônibus, ou seja, o método supõe que todas as linhas vão
e voltam pelo mesmo caminho. É comum que isso ocorra, mas em alguns casos há diferenças entre o
caminho de ida e volta. Além disso, pode haver diferenças nos horários de saída para cada sentido da
linha.
Com isso são formadas listas de quais links da rota de menor distância têm acesso a quais linhas
de ônibus. A partir destas listas é possível combinar linhas de ônibus para formar rotas com mais de
uma linha.
Para combinações de mais de uma linha de ônibus, de forma a simpliﬁcar o procedimento, somente
são considerados válidos os casos onde o último ponto de ônibus de cada linha precede ou coincide
com o primeiro ponto da próxima. A tabela 2 mostra um exemplo de uma rota pela qual passam três
linhas de ônibus. O "x" representa pontos de ônibus na rota por onde passa a linha de ônibus da coluna
respectiva. Neste caso seriam consideradas as linhas individualmente e a combinação da Linha 1 com
a Linha 3. O primeiro ponto da Linha 2 precede o último da Linha 1, enquanto o último ponto da
Linha 2 sucede o primeiro da Linha 3. Com essa simpliﬁcação, combinações entre a Linha 2 e uma
das outras não são consideradas.
Link Linha 1 Linha 2 Linha 3
1
2 x x
3
4 x x x
5
6 x x
7
8
Tabela 2: Listas de pontos de ônibus por link
27Com as combinações deﬁnidas as rotas são deﬁnidas. Baseado nos pontos de embarque e desem-
barque de cada rota, é atribuído o modo de transporte para cada link. Para os links entre um ponto de
embarque e desembarque da mesma linha de ônibus, o modo de transporte é o ônibus, para os outros,
a pé.
A Figura 14 ilustra o procedimento de deﬁnição de uma rota. A Figura 14a ilustra um exemplo
de malha viária com linhas e pontos de ônibus. Na Figura 14b é deﬁnida a rota de menor distância,
e são mostrados então somente pontos de ônibus nesta rota, e linhas que passam por estes pontos. A
Figura 14c mostra um exemplo de rota combinando as duas linhas de ônibus que passam pela rota de
menor distância.
É possível que haja divergências entre a rota de menor distância e as rotas deﬁnidas. Isto ocorre
pois a condição para que uma linha de ônibus seja considerada pelo método é que haja pontos de
ônibus na rota de menor distância pelos quais a linha passe. Neste sentido, se a linha de ônibus
possuir um traçado diferente do da rota de menor distância, porém interceptá-la em pelo menos dois
pontos de ônibus (embarque e desembarque), esta será levada em consideração na deﬁnição das rotas.
Na Figura 15 é possível observar um exemplo disso: os traçados são distintos no trecho mostrado,
mas se interceptam no ponto de ônibus indicado, possibilitando o embarque.
A diferença na distância não é considerada pelo método. O caminho percorrido é considerado
como igual ao da rota de menor distância. Isto causa pequenas discrepâncias nas distâncias medidas
para a parte da rota percorrida pelo ônibus, porém a parte percorrida a pé e os pontos de embarque e
desembarque não são afetados.
28(a) Malha viária com linhas e pontos de ônibus
(b) Rota de menor distância
(c) Rota deﬁnida
Figura 14: Deﬁnição de uma rota
29Figura 15: Divergência entre rotas
3.2.4 Estimativa de tempo levado para cada rota
Para cada rota deﬁnida na seção 3.2.3 é estimado o tempo levado para que se determine as rotas mais
rápidas. O procedimento para a estimativa do tempo levado está ilustrado na Figura 16.
Os tempos estimados são divididos em três grupos:
tempo de percurso do usuário a pé;
tempo de percurso do usuário utilizando o ônibus;
tempos de espera para o usuário subir no ônibus.
Para cada rota as distâncias percorridas a pé e de ônibus são calculadas a partir dos pontos de
embarque e desembarque e dos links da rota inicial. É então aplicada uma velocidade, diferente para
cada modo de transporte, para se estimar o tempo levado em cada trecho da rota, conforme a Equação
   1.

t=d
v(1)
Onde:
té o tempo levado;
30Sim
NãoHorário de partida
do usuário
Horário de chegada do usuário
no ponto de ônibus
Horário de embarqueCálculo do
tempo de
espera
Horário de desembarque
Outra linha será utilizada?
Horário de chegada
do usuárioFigura 16: Estimativa do tempo levado
Nota: As linhas contínuas representam o
tempo levado ao longo do percurso da rota.
dé a distância percorrida;
vé a velocidade de locomoção.
A velocidade a pé foi considerada como 0,91 m=s (KNOBLAUCH et al., 1996). A velocidade
do ônibus vonibus (Equação 2) foi calculada dividindo a distância total da linha de ônibus dlinha pelo
tempo estimado de percurso da linha tlinha, obtido do sitedo Consórcio Fênix.
vonibus =dlinha
tlinha(2)
31O tempo total levado ttotalé a soma do tempo levado em cada trecho e dos tempos de espera, como
mostrado na Equação 3:
ttotal =nX
i=1(tpei+tei+tpdi) +tpc (3)
Onde:
né o número de linhas de ônibus utilizadas;
tpeé o tempo levado para o usuário chegar no ponto de embarque, a partir do ponto de partida
ou do último ponto de desembarque;
teé o tempo de espera até o ônibus chegar no ponto de embarque, a partir do momento em que
o usuário chega;
tpdé o tempo levado para o usuário, no ônibus, chegar ao ponto de deesembarque;
tpcé o tempo levado para o usuário chegar ao ponto de chegada.
O tempo de espera tedepende do horário em que o usuário chega no ponto de ônibus hup(Equação
4):
te=f(hup) (4)
A estimativa do tempo total levado ttotal, portanto, é feita trecho a trecho, de maneira sequencial. O
horário hupé a soma do horário de partida do usuário hpcom os tempos calculados até o usuário
chegar no ponto de embarque (Equação 5).
hupi=hp+iX
j=1tpej+i 1X
j=1(tej+tpdj) (5)
Para se estimar o tempo de espera te, é feita uma estimativa do tempo que o ônibus levará para chegar
ao ponto de embarque top. Isto é feito utilizando a função pgr_dijkstra dando como entrada o primeiro
nó de linha de ônibus e o nó mais próximo ao ponto de ônibus, e os links por onde passam linhas de
ônibus. A distância obtida é então dividida pela velocidade. O tempo resultante é então subtraído do
horário em que o usuário chega no ponto de embarque hup, resultando no horário em que o ônibus
deveria partir para chegar ao mesmo tempo em que o usuário, como mostrado na Equação 6.
h0
os=hup top (6)
Este horário é então comparado com os horários de saída da linha de ônibus e dia da semana corres-
pondentes. Se o ônibus partir antes do horário calculado, o usuário não o alcançará a tempo. Logo
32é considerado o horário de saída hosimediatamente após o calculado ( h0
os). A diferença entre estes
horários é o tempo de espera para o respectivo ponto de embarque (Equação 7).
te=hos h0
os (7)
3.2.5 Dados de saída
Por ﬁm, as rotas são ordenadas pelo tempo levado e são mostradas as de menor tempo. Os links
percorridos por cada rota são agrupados pelo modo de transporte e pelo nome da rua correspondente,
para facilitar a leitura dos resultados.
O agrupamento está ilustrado nas tabelas 3 e 4. A tabela 3 mostra a rua, distância, modo de
transporte e tempo levado para cada linkda rota. A tabela 4, por sua vez mostra estas informações
agrupadas por modo de transporte e rua.
Tabela 3: Trechos da rota
Rua Comprimento Modo de transporte Tempo
Rua A 100 m A pé 60 s
Rua A 200 m Ônibus 40 s
Rua A 500 m Ônibus 100 s
Rua B 300 m Ônibus 60 s
Rua B 200 m Ônibus 40 s
Rua B 400 m Ônibus 80 s
Rua C 600 m Ônibus 120 s
Rua C 300 m A pé 180 s
Rua C 200 m A pé 120 s
Tabela 4: Trechos da rota agrupados
Rua Comprimento Modo de transporte Tempo
Rua A 100 m A pé 60 s
Rua A 700 m Ônibus 140 s
Rua B 900 m Ônibus 180 s
Rua C 600 m Ônibus 120 s
Rua C 500 m A pé 300 s
São informadas as distâncias percorridas a pé e de ônibus, além das estimativas de tempo levado
para cada trecho da rota.
334 Resultados
Os resultados do método são conjuntos de instruções para o uso do sistema de transporte coletivo.
Devido às limitações do método e simpliﬁcações feitas, a qualidade dos resultados varia signiﬁcati-
vamente dependendo das particularidades de cada caso.
A Figura 17 mostra um exemplo da saída do método. No caso são mostradas somente as duas
melhores rotas identiﬁcadas. Para cada rota são mostradas as distâncias a serem percorridas a pé e de
ônibus, o tempo estimado para cada trecho e o tempo de espera para o usuário subir no ônibus. Além
disso são mostradas as distâncias e tempo totais. Conforme descrito anteriormente, pode-se observar
que o método não considera o sentido da linha de ônibus: as linhas da primeira e segunda opções tem
sentidos opostos, mas ambas aparecem no resultado. Por outro lado, as distâncias são condizentes
com a realidade.
Figura 17: Exemplo de saída do método
A Figura 18 mostra uma rota correspondente ao resultado da Figura 17.
A Figura 19 mostra um exemplo da saída com mais de uma linha sendo utilizada. Neste caso a
34Figura 18: Rota mostrada no mapa
saída é semelhante, exceto que há dois pontos de embarque e dois de desembarque.
Figura 19: Exemplo de saída com duas linhas de ônibus
Rotas com mais de uma linha de ônibus raramente são os melhores resultados, principalmente
devido aos tempos de espera. Isto também ocorre pela pequena área utilizada no trabalho, pois dos
casos em que poderia ser usada uma combinação de linhas, normalmente é possível utilizar somente
uma linha.
355 Conclusões
Ao longo do trabalho foi criado um sistema que a partir dos dados de entrada do usuário retorna rotas
para uso das linhas de ônibus.
Durante o desenvolvimento do método foram aplicados diversos conceitos relacionados a SIG,
banco de dados espacial e scripting , utilizando software apropriados para a coleta, processamento e
gerenciamento dos dados.
O QGIS se mostrou muito útil para a visualização e inspeção dos dados, sendo de fácil uso. A sua
integração com o PostGIS, em particular, facilitou a inserção de dados no banco de dados espacial.
A coleta de dados a partir do OSM apresentou alguns problemas. Quando se exporta camadas de
dados em arquivos shapeﬁle do OSM, estas perdem grande parte de suas características topológicas.
Neste sentido, o GRASS se mostrou muito eﬁciente para o tratamento destas falhas, processando-as
rapidamente, sem gerar mais links do que o necessário.
O banco da dados espacial baseado no PostgreSQL se mostrou útil ao gerenciamento dos dados
coletados, facilitando o relacionamento destes dados.
A geração de rotas a pé e de ônibus se mostrou uma tarefa de alta complexidade, tanto em relação
ao processamento dos dados quanto à programação com base nestes, sendo necessárias uma série de
simpliﬁcações no método.
Devido a estas simpliﬁcações, a qualidade dos resultados é reduzida. A não-consideração do
sentido das linhas de ônibus, em particular, distancia o método de uma aplicação funcional. Com
algumas medidas relativamente simples, como alterações na maneira com que as rotas são deﬁnidas,
seria possível melhorar um pouco os resultados, mas eliminar os resultados ruins é uma tarefa mais
complexa, exigindo um estudo mais aprofundado de como trabalhar os dados geométricos coletados.
A saída do método, feita através de linha de comando, é bem informativa e detalhada, porém não
permite a visualização das rotas geradas através de um mapa, o que facilitaria a interpretação dos
resultados.
5.1 Recomendações para trabalhos futuros
Considerar rotas entre os pontos de ônibus próximos aos pontos de partida e chegada, de forma
a aumentar a probabilidade de que as linhas passantes por estes pontos sejam utilizadas. Isto
melhoraria os resultados ao se reduzir a distância percorrida a pé pelo usuário.
Considerar o caminho efetivamente percorrido pelo ônibus nas rotas deﬁnidas, de forma a re-
duzir a discrepância entre a distância percorrida apresentada no resultado e a real.
Estudar o desenvolvimento de aplicações gráﬁcas para possibilitar a deﬁnição visual, através
de um mapa, dos dados de entrada, e a representação visual das rotas resultantes.
36Estudar de forma mais aprofundada as características geométricas das linhas de ônibus e como
relacioná-las aos links da malha viária poderia ajudar a considerar o sentido das linhas, melho-
rando consideravelmente os resultados do método.
37Referências
BURROUGH, Peter A. Principles of Geographical Information Systems for Land Resources
Assessment . 1986. Pp. 5, 6.
CHERRY, Christopher; HICKMAN, Mark; GARG, Anirudh. Design of a Map-Based Transit
Itinerary Planner. Journal of Public Transportation , v. 9, n. 2, 2006. Pp. 1, 2, 4.
CNT. Pesquisa Mobilidade da População Urbana, 2017. Pp. 1, 2.
CODD, E. F. The Relational Model for Database Management . 1990. P. 9.
DATE, C. J. Instructor’s Manual for An Introduction to Database Systems . 8. ed. 2003. P. 9.
GRASS DEVELOPMENT TEAM. GRASS GIS 7.2.3 Reference Manual . 2017. Pp. 11, 12.
GÜTING, Ralf Hartmut. An Introduction to Spatial Database Systems. Praktische Informatik IV ,
FernUniversität Hagen , 1994. Pp. 6, 10.
HAGGET, P; CHORLEY, R J. Models, paradigms and the new geography. Models in Geography ,
1967. P. 5.
HAKLAY, Mordechai; WEBER, Patrick. OpenStreetMap: User-Generated Street Maps. IEEE
Computer Society , 2008. P. 17.
HAWEROTH, Flávia. Aplicação de Roteirização e Programação de Veículos no Transporte
Público de Pessoas com Deﬁciência no Município de Joinville - SC . 2017. Universidade Federal
de Santa Catarina. P. 5.
HEYWOOD, Ian; CORNELIUS, Sarah; CARVER, Steve. An Introduction to Geographical
Information Systems . 2006. Pp. 6, 7.
HICKMAN, Mark. Robust Passenger Itinerary Planning Using Transit A VL Data. Transportation
Research Board , 2002. P. 4.
INTERNATIONAL ENERGY AGENCY. Bus Systems for the Future: Achieving Sustainable
Transport Worldwide . 2002. P. 2.
KNOBLAUCH, Richard; PIETRUCHA, Martin; NITZBURG, Marsha. Field Studies of Pedestrian
Walking Speed and Start-Up Time. Transportation Research Board , 1996. P. 31.
LACERDA, Sander Magalhães. Preciﬁcação de congestionamento e transporte coletivo urbano.
BNDES Setorial , 2006. P. 2.
LINDEN, Ricardo. Técnicas de Agrupamento. Revista de Sistemas de Informação da FSMA , n. 4,
2009. Pp. 7, 8.
LUTZ, Mark. Programming Python . 2011. P. 13.
38MILANI, André. PostgreSQL : Guia do Programador. 2008. P. 10.
MONMONIER, Mark. How to Lie with Maps . 1991. Pp. 5, 6.
NETELER, Markus; MITASOV A, Helena. Open Source Gis A Grass Gis Approach . 2007. P. 11.
NIENKOTTER, Maiko Andrei. Proposta de um modelo heurístico para a roteirização de
empilhadeiras em um armazém de grande porte . 2017. Universidade Federal de Santa Catarina.
P. 4.
OBE, Regina O.; HSU, Leo S. PostGIS in Action . 2015. Pp. 7, 10, 11.
PGROUTING TEAM. pgRouting Manual . 22 jul. 2017. P. 11.
RAMEZ, Elmasri; NA V ATHE, Shamkant B. Sistemas de Banco de Dados . 2005. Pp. 8, 9.
SILV A, D. Sistemas Inteligentes no Transporte Público por Ônibus . 2000. Diss. (Mestrado) –
Universidade Federal do Rio Grande do Sul. P. 2.
SUMATHI, S.; ESAKKIRAJAN, S. Fundamentals of Relational Database Management
Systems . 2007. Pp. 9, 10.
TRÉPANIER, Martin; CHAPLEAU, Robert; ALLARD, Bruno. Can Trip Planner Log Files Analysis
Help in Transit Service Planning? Journal of Public Transportation , v. 8, n. 2, 2005. P. 1.
39APÊNDICE A - Comandos SQL
Seção 3.1.1:
CREATE DATABASE mydb ;
CREATE EXTENSION p o s t g i s ;
CREATE EXTENSION p g r o u t i n g ;
Seção 3.1.3: (somente a condição WHERE, usados na janela de ﬁltragem do QGIS)
highway IS NOT NULL
highway = ’ b u s_ s t o p ’
o t h e r _t a g s LIKE ’%" r o u t e "= >" bus"% ’
Seção 3.1.4:
ALTER TABLE b u s_ l i n e s ADD C O L U M N s o u r c e i n t e g e r ;
ALTER TABLE b u s _l i n e s ADD C O L U M N t a r g e t i n t e g e r ;
SELECT p g r_ c r e a t e _t o p o l o g y ( ’ edges ’ , 0 . 0 0 0 1 ) ;
Seção 3.1.5:
CREATE TABLE b u s_ d e p t _t i m e s (
i dPRIMARY KEY ,
b u s_ l i n e _i d i n t e g e r REFERENCES b u s_ l i n e s ,
day_group varchar ( 4 ) ,
time time ) ;
INSERT INTO b u s_ d e p t _t i m e s ( b u s_ l i n e _i d , day_group , time )
VALUES ( 5 , ’ u t i l ’ , 1 6 : 2 0 : 0 0 ) ;
Seção 3.2.2:
SELECT id , ST_Distance ( the_geom : : geography , ST_GeomFromText ( ’POINT(  48.552658 27.599111) ’ , 4 3 2 6 ) ) AS
d i s t F R O M nodes ORDER BY d i s t LIMIT 1 ;
SELECT node , edge , c o s t , seq F R O M p g r_ d i j k s t r a (
’SELECT id , source , t a r g e t , ST_Length ( the_geom : : geography ) AS c o s t
FROM edges ’ , {1} , {2} , f a l s e ) ;
Seção 3.2.3:
ALTER TABLE b u s _s t o p s ADD C O L U M N c l o s e s t_ e d g e i n t e g e r ;
UPDATE b u s _s t o p s SET c l o s e s t_ e d g e = i d e F R O M (
SELECT DISTINCT idb , f i r s t _v a l u e ( i d e ) OVER ( PARTITION BY i d b ORDER BY d i s t ) AS i d e F R O M (
SELECT b . i d asidb , e . i d aside , ST_Distance ( e . the_geom , b . the_geom ) AS d i s t F R O M edges e , b u s _s t o p s b ,
b u s_ l i n e s l
W H E R E S T _I n t e r s e c t s ( e . the_geom , l . the_geom ) ) AS foo
)AS b a r W H E R E i d = i d b ;
SELECT c l o s e s t_ e d g e F R O M b u s _s t o p s ;
SELECT l . i d F R O M b u s_ l i n e s l , edges e
W H E R E e . i d = {1} AND S T _I n t e r s e c t s ( e . the_geom , l . the_geom ) ;
40APÊNDICE B -Script de inserção dos horários de ônibus
1from d a t e t i m e import d a t e t i m e , time , t i m e d e l t a
2import psycopg2
3
4 b u s_ l i n e _i d = 39
5 db_name = "mydb"
6 password = " pg "
7
8 c l a s s b u s _d e p t :
9 pass
10
11 h o r a r i o s = open ( " h o r a r i o s . t x t " )
12 c u r r e n t_ g r o u p = " "
13 b u s _d e p t s = [ ]
14 f o r tinh o r a r i o s . r e a d ( ) . r e p l a c e ( " \ n " , " " ) . s p l i t ( " " ) :
15 i ftin[ " u t i l " , " sab " , "dom" ] :
16 c u r r e n t_ g r o u p = t
17 c o n t i n u e
18 b = b u s _d e p t ( )
19 b . group = c u r r e n t_ g r o u p
20 b . tim e = d a t e t i m e . s t r p t i m e ( t [ 0 : 5 ] , "% H:%M" ) . ti me ( )
21 b u s _d e p t s . append ( b )
22
23 h o r a r i o s . c l o s e ( )
24
25 v a l u e s = [ ]
26 f o r binb u s_ d e p t s :
27 v a l u e s . append ( " ( { 0 } , ’ { 1 } ’ , ’ { 2 } ’ ) " . format ( b u s _l i n e_ i d , b . group , b . ti me ) )
28 p r i n t ( b . group , b . ti me )
29
30 con = psycopg2 . c o n n e c t ( " h o s t = l o c a l h o s t dbname ={0} u s e r = p o s t g r e s
password ={1} " . format ( db_name , password ) )
31 con . s e t_ i s o l a t i o n _l e v e l ( psycopg2 . e x t e n s i o n s . ISOLATION_LEVEL_AUTOCOMMIT)
32 w it h con :
33 c u r = con . c u r s o r ( )
34 c u r . e x e c u t e ( "INSERT INTO b u s_ d e p t _t i m e s ( i d_ l i n e , day_group , ti me ) VALUES
{0} " . format ( " , " . j o i n ( v a l u e s ) ) )
41APÊNDICE C -Script de roteamento
1#   c o d i n g : u t f 8  
2import psycopg2
3from d a t e t i m e import d a t e t i m e , time , t i m e d e l t a
4
5# ==============================================
6 c l a s s o u t e r_ n o d e ( o b j e c t ) :# r e p r e s e n t a o p r i m e i r o e u l t i m o nos da r o t a
7 def __ i n i t __ ( s e l f , id, d i s t a n c e ) :
8 s e l f . id=id
9 s e l f . d i s t a n c e = d i s t a n c e
10 c l a s s r o u t e _s e g m e n t ( o b j e c t ) :# r e p r e s e n t a os l i n k s da r o t a
11 def_ _i n i t_ _( s e l f , seq , l e n g t h , edge =  1, node = 1, h a s_ b u s _s t o p = F a l s e , s t r e e t = " " ) :
12 s e l f . edge = edge
13 s e l f . node = node
14 s e l f . h a s_ b u s _s t o p = h a s_ b u s _s t o p
15 s e l f . b u s_ l i n e s = [ ]
16 s e l f . seq = seq
17 s e l f . l e n g t h = l e n g t h
18 s e l f . s t r e e t = s t r e e t
19 c l a s s b u s _l i n e ( o b j e c t ) :# r e p r e s e n t a l i n h a s de o n i b u s
20 def_ _i n i t_ _( s e l f , id, speed , name=" " ) :
21 s e l f . id=id
22 s e l f . name = name
23 s e l f . speed = speed
24 c l a s s c o m b i n a t i o n ( o b j e c t ) :# r e p r e s e n t a uma combinação de l i n h a s de o n i b u s
25 def_ _i n i t_ _( s e l f , b u s_ l i n e s = [ ] , tim e = t i m e d e l t a ( ) ) :
26 s e l f . b u s _l i n e s = b u s_ l i n e s
27 s e l f . tim e = tim e
28 c l a s s r o u t e _g r o u p ( o b j e c t ) :# r e p r e s e n t a um agrupamento de l i n k s d e n t r o da r o t a
29 def_ _i n i t_ _( s e l f ) :
30 s e l f . l e n g t h = 0 . 0
31 s e l f . r i d i n g_ b u s = F a l s e
32 s e l f . h a s _e m b a r k_ p o i n t = F a l s e
33 s e l f . h a s _d i s e m b a r k_ p o i n t = F a l s e
34 def t i m e _t a k e n ( s e l f ) :
35 i fs e l f . r i d i n g_ b u s :
36 # m e t r o s / m e t r o s por segundo
37 return t i m e d e l t a ( s e c o n d s = s e l f . l e n g t h / ( s e l f . b u s _l i n e . speed ) )
38 return t i m e d e l t a ( s e c o n d s = s e l f . l e n g t h / ( 0 . 9 7 ) )
39 # ==============================================
40 def g e n e r a t e_ o u t e r _e d g e s ( x , y , node_id , r o u t e _t a b l e ) :
41 c u r . e x e c u t e ( " " "
42 INSERT INTO { 2 } ( the_geom )
43 SELECT ST_MakeLine ( ST_GeomFromText ( ’ POINT ( { 0 } { 1 } ) ’ , 4 3 2 6 ) , the_geom ) FROM { 4 } WHERE i d =
{ 3 } " " " .format ( x , y , r o u t e_ t a b l e , node_id , n o d e_ t a b l e ) )
44 def g e t _c l o s e s t_ n o d e ( x , y ) :
45 c u r . e x e c u t e ( "SELECT id , ST_Distance ( the_geom : : geography , ST_GeomFromText ( ’ POINT ( { }
{ } ) ’ , 4 3 2 6 ) ) AS d i s t FROM {} ORDER BY d i s t LIMIT 1 " . format ( x , y , n o d e_ t a b l e ) )
46 node = c u r . f e t c h o n e ( )
47 return o u t e r _n o d e ( id= node [ 0 ] , d i s t a n c e = node [ 1 ] )
48 def g r o u p_ r o u t e ( e m b a r k _l i s t , d i s e m b a r k_ l i s t , b u s _l i n e s ) : # agrupa os l i n k s por modal e por rua
49 g r o u p s = [ ]
50 c u r r e n t_ g r o u p = r o u t e _g r o u p ( )
4251 f o r sinr o u t e :
52 i fs . s t r e e t :
53 c u r r e n t_ g r o u p . s t r e e t = s . s t r e e t
54 break
55 f o r sinr o u t e :
56 i fs . seq ine m b a r k _l i s t + d i s e m b a r k_ l i s t or( s . s t r e e t and s . s t r e e t !=
c u r r e n t _g r o u p . s t r e e t ) :
57 g r o u p s . append ( c u r r e n t_ g r o u p )
58 c u r r e n t _g r o u p = r o u t e_ g r o u p ( )
59 i fs . seq ine m b a r k _l i s t :
60 c u r r e n t_ g r o u p . h a s _e m b a r k_ p o i n t = True
61 c u r r e n t _g r o u p . f i r s t_ n o d e = s . node
62 i fs . seq ind i s e m b a r k _l i s t :
63 c u r r e n t_ g r o u p . h a s _d i s e m b a r k_ p o i n t = True
64 c u r r e n t _g r o u p . r i d i n g_ b u s = True in l i s t ( s . seq >= e m b a r k _l i s t [ i ] and s . seq <
d i s e m b a r k_ l i s t [ i ] f o r iin range (l e n( e m b a r k _l i s t ) ) )
65 f o r iin range (l e n( e m b a r k_ l i s t ) ) :
66 i fs . seq >= e m b a r k _l i s t [ i ] and s . seq < d i s e m b a r k_ l i s t [ i ] :
67 c u r r e n t _g r o u p . r i d i n g_ b u s = True
68 c u r r e n t _g r o u p . b u s_ l i n e = b u s _l i n e s [ i ]
69 c u r r e n t_ g r o u p . s t r e e t = s . s t r e e t i fs . s t r e e t e l s e g r o u p s [ 1]. s t r e e t
70 c u r r e n t _g r o u p . l e n g t h += s . l e n g t h
71 g r o u p s . append ( c u r r e n t_ g r o u p )
72 return g r o u p s
73 def c a l c u l a t e _w a i t i n g_ t i m e ( bl , node , c u r r e n t _t i m e ) : # c a l c u l a o tempo de e s p e r a
74 s t a r t_ n o d e s _t a b l e = " b u s_ l i n e _s t a r t_ n o d e s "
75 c u r . e x e c u t e ( "SELECT id_node FROM {0} WHERE i d_ l i n e = {1} " . format ( s t a r t _n o d e s_ t a b l e , b l . id) )
76 s t a r t _n o d e = c u r . f e t c h o n e ( ) [ 0 ]
77 c u r . e x e c u t e ( " " "
78 SELECT c o s t FROM p g r_ d i j k s t r a (
79 ’SELECT e . id , e . source , e . t a r g e t , ST_Length ( e . the_geom : : geography ) as c o s t FROM { 0 } e , { 1 }
b WHERE b . i d = { 2 } AND S T _I n t e r s e c t s ( e . the_geom , b . the_geom ) ’ ,
80 { 3 } , { 4 } , f a l s e )
81 " " ".format ( e d g e_ t a b l e , b u s _l i n e_ t a b l e , b l . id, s t a r t _n o d e , node ) )
82 t i m e_ t o _b u s_ s t o p = t i m e d e l t a ( s e c o n d s = ( ( sum ( l i n e [ 0 ] f o r l i n e inc u r . f e t c h a l l ( ) ) ) / 2 0 ) )
83
84 weekday = d e p a r t u r e _t i m e . weekday ( )
85 u t i l , sab , dom = [ 0 , 1 , 2 , 3 , 4 ] , [ 5 ] , [ 6 ]
86 i fweekday in u t i l :
87 day_group = " u t i l "
88 e l i f weekday insab :
89 day_group = " sab "
90 e l i f weekday indom :
91 day_group = "dom"
92
93
94 c u r . e x e c u t e ( "SELECT tim e FROM b u s _d e p t_ t i m e s WHERE i d _l i n e = {0} AND day_group =
’{1} ’ " . format ( b l . id, day_group ) )
95 t i m e_ l i s t = l i s t ( l i n e [ 0 ] f o r l i n e inc u r . f e t c h a l l ( ) )
96 w a i t i n g _t i m e = min ( t . s e c o n d s f o r tin( ( c u r r e n t_ t i m e  t i m e _t o_ b u s _s t o p  
d a t e t i m e . combine ( c u r r e n t_ t i m e . d a t e ( ) , ti me ) ) f o r ti me int i m e _l i s t ) i ft > t i m e d e l t a ( ) )
97 return t i m e d e l t a ( s e c o n d s = w a i t i n g_ t i m e )
98 def c a l c u l a t e _c o s t ( comb ) : # c a l c u l a o tempo em segundos com base nas combinacoes s e l e c i o n a d a s
99 e m b a r k_ l i s t = s o r t e d ( b l . f i r s t _i n s t a n c e f o r b lincomb . b u s_ l i n e s )
43100 d i s e m b a r k _l i s t = s o r t e d ( b l . l a s t_ i n s t a n c e f o r b lincomb . b u s _l i n e s )
101 comb . i n s t r u c t i o n s = [ " H o r á r i o de p a r t i d a : {0:%H:%M} . " . format ( d e p a r t u r e _ t i m e . ti me ( ) ) ]
102 c u r r e n t_ t i m e = d e p a r t u r e _t i m e
103 g r o u p s = g r o u p_ r o u t e ( e m b a r k _l i s t , d i s e m b a r k_ l i s t , comb . b u s _l i n e s )
104 f o r ging r o u p s :
105 i fg . h a s_ e m b a r k _p o i n t :
106 w a i t i n g_ t i m e = c a l c u l a t e _w a i t i n g_ t i m e ( g . b u s _l i n e , g . f i r s t_ n o d e , c u r r e n t _t i m e )
107 comb . i n s t r u c t i o n s . append ( " E s p e r a r {0} minutos p a r a s u b i r na l i n h a
{ 1 } . " . format ( w a i t i n g_ t i m e . s e c o n d s / / 6 0 , g . b u s _l i n e . name ) )
108 c u r r e n t_ t i m e += w a i t i n g _t i m e
109 i fg . h a s_ d i s e m b a r k _p o i n t :
110 comb . i n s t r u c t i o n s . append ( " Descer do ô n i b u s . " )
111 comb . i n s t r u c t i o n s . append ( " P e r c o r r e r { 0 : 0 . 0 f } m e t r o s na
{ 1 } . " . format ( g . l e n g t h , g . s t r e e t ) + ( " ( { }
minutos ) " . format ( g . t i m e_ t a k e n ( ) . s e c o n d s / / 6 0 ) i fg . t i m e _t a k e n ( ) . s e c o n d s >= 60
e l s e " ( menos de 1 minuto ) " ) )
112 c u r r e n t_ t i m e += g . t i m e _t a k e n ( )
113 comb . i n s t r u c t i o n s . append ( " H o r á r i o de chegada : {0:%H:%M} " . format ( c u r r e n t_ t i m e . ti me ( ) ) )
114 comb . i n s t r u c t i o n s . append ( " D i s t â n c i a t o t a l a pé : { 0 : 0 . 0 f } m e t r o s " . format (sum ( g . l e n g t h f o r g
ing r o u p s i f not g . r i d i n g _b u s ) / / 1 ) )
115 comb . i n s t r u c t i o n s . append ( " D i s t â n c i a t o t a l de ô n i b u s : { 0 : 0 . 0 f } m e t r o s " . format (sum ( g . l e n g t h
f o r ging r o u p s i fg . r i d i n g_ b u s ) / / 1 ) )
116 comb . i n s t r u c t i o n s . append ( "Tempo t o t a l : {0}
minutos . " . format ( ( c u r r e n t _t i m e  d e p a r t u r e_ t i m e ) . s e c o n d s / / 6 0 ) )
117
118 comb . t o t a l _t i m e = c u r r e n t_ t i m e  d e p a r t u r e _t i m e
119 # ==============================================
120 db_name = "mydb"
121 password = " pg "
122 b u s _s t o p s_ t a b l e = " b u s _s t o p s_ s a m p l e "
123 b u s _l i n e_ t a b l e = " b u s _l i n e s_ s a m p l e "
124 n o d e _t a b l e = " nodes "
125 e d g e_ t a b l e = " edges "
126 s t a r t _x , s t a r t_ y =  48.552658 , 27.599111
127 f i n i s h _x , f i n i s h_ y =  48.518273 , 27.607809
128 d e p a r t u r e _t i m e = d a t e t i m e . now ( )  t i m e d e l t a ( h o u r s =10)
129 b u s_ l i n e _c o n d = " "
130 # ==============================================
131 con = psycopg2 . c o n n e c t ( " h o s t = l o c a l h o s t dbname ={0} u s e r = p o s t g r e s
password ={1} " . format ( db_name , password ) )
132 con . s e t _i s o l a t i o n_ l e v e l ( psycopg2 . e x t e n s i o n s . ISOLATION_LEVEL_AUTOCOMMIT)
133 w it h con :
134 c u r = con . c u r s o r ( )
135 # busca i d e nome das l i n h a s de o n i b u s
136 c u r . e x e c u t e ( "SELECT id , name , ST_Length ( the_geom : : geography ) , t i m e _t a k e n FROM
{0} " . format ( b u s_ l i n e _t a b l e ) )
137 a l l_ b u s _l i n e s = l i s t ( b u s_ l i n e ( id= l i n e [ 0 ] , name= l i n e [ 1 ] , speed = l i n e [ 2 ] / l i n e [ 3 ] . s e c o n d s ) f o r
l i n e inc u r . f e t c h a l l ( ) )
138 # busca q u a i s l i n k s e s t a o proximos de ponto de o n i b u s ( t a b e l a c r i a d a para i s s o )
139 c u r . e x e c u t e ( "SELECT c l o s e s t _e d g e from {0} " . format ( b u s_ s t o p s _t a b l e ) )
140 e d g e s_ w i t h _b u s_ s t o p = l i s t ( l i n e [ 0 ] f o r l i n e inc u r . f e t c h a l l ( ) )
141 f i r s t _n o d e = g e t_ c l o s e s t _n o d e ( s t a r t_ x , s t a r t _y )
142 l a s t_ n o d e = g e t _c l o s e s t_ n o d e ( f i n i s h _x , f i n i s h_ y )
143 # e n c o n t r a uma r o t a sem c o n s i d e r a r d i r e ç ã o ou l i n h a s de onibus , e c o n s i d e r a n d o c u s t o como o
44comprimento do l i n k
144 c u r . e x e c u t e ( " " "
145 SELECT node , edge , c o s t , seq FROM p g r _d i j k s t r a (
146 ’SELECT id , source , t a r g e t , ST_Length ( the_geom : : geography ) as c o s t
147 FROM { 0 } ’ ,
148 { 1 } , { 2 } , f a l s e )
149 " " ".format ( e d g e_ t a b l e , f i r s t _n o d e . id, l a s t_ n o d e . id) )
150 r o u t e = [ ]
151 b u s _l i n e s = [ ]
152 f o r row inc u r . f e t c h a l l ( ) : # busca as i n f o r m a c o e s dos l i n k s
153 s = r o u t e_ s e g m e n t ( node = row [ 0 ] , edge = row [ 1 ] , h a s _b u s_ s t o p = row [ 1 ] in
e d g e s _w i t h_ b u s _s t o p , l e n g t h = row [ 2 ] , seq = row [ 3 ] )
154 i fs . h a s_ b u s _s t o p : # se o l i n k a t u a l p o s s u i um ponto de onibus , busca q u a i s l i n h a s
de o n i b u s passam p e l o l i n k d e f i n i n d o o p r i m e i r o e u l t i m o p o n t o s de cada l i n h a
155 c u r . e x e c u t e ( "SELECT b . i d FROM {0} b , {1} e WHERE {3} e . i d = {2} AND
S T_ I n t e r s e c t s ( e . the_geom , b . the_geom ) " . format ( b u s _l i n e_ t a b l e , e d g e _t a b l e , s . edge , b u s_ l i n e _c o n d ) )
156 i d s = l i s t ( row [ 0 ] f o r row inc u r . f e t c h a l l ( ) )
157 s . b u s_ l i n e s = l i s t ( b l f o r b lina l l _b u s_ l i n e s i fb l .id in i d s )
158 f o r b lins . b u s _l i n e s :
159 b l . l a s t_ i n s t a n c e = s . seq
160 i fb lnot in b u s _l i n e s :
161 b l . f i r s t_ i n s t a n c e = s . seq
162 b u s _l i n e s . append ( b l )
163 r o u t e . append ( s )
164 c u r . e x e c u t e ( "DELETE FROM s a m p l e_ r o u t e " )
165 f o r sinr o u t e : # i n s e r e a r o t a na t a b e l a sample
166 c u r . e x e c u t e ( " " "
167 INSERT INTO s a m p l e _r o u t e
168 SELECT the_geom FROM edges
169 WHERE i d = { 0 } " " " .format ( s . edge ) )
170 g e n e r a t e _o u t e r_ e d g e s ( s t a r t _x , s t a r t_ y , f i r s t _n o d e . id, " s a m p l e_ r o u t e " )
171 g e n e r a t e _o u t e r_ e d g e s ( f i n i s h _x , f i n i s h_ y , l a s t _n o d e . id, " s a m p l e_ r o u t e " )
172 c u r . e x e c u t e ( "SELECT id , name FROM edges WHERE name i s n o t n u l l AND i d =
ANY(ARRAY[ { 0 } ] ) " . format ( " , " . j o i n ( l i s t (s t r( s . edge ) f o r sinr o u t e ) ) ) )
173 f o r row inc u r . f e t c h a l l ( ) : # d e f i n e o nome da rua de cada l i n k
174 f o r sinr o u t e :
175 s . s t r e e t = row [ 1 ] i fs . edge == row [ 0 ] e l s e " "
176 r o u t e . i n s e r t ( 0 , r o u t e _s e g m e n t ( seq = 0 , l e n g t h = f i r s t_ n o d e . d i s t a n c e ) )
177 r o u t e . append ( r o u t e _s e g m e n t ( seq = max ( s . seq f o r sinr o u t e ) + 1 , l e n g t h =
l a s t_ n o d e . d i s t a n c e ) )
178 # remove l i n h a s de o n i b u s que apareçam somente uma v e z
179 b u s _l i n e s = l i s t ( b l f o r b linb u s_ l i n e s i fb l . f i r s t _i n s t a n c e != b l . l a s t_ i n s t a n c e )
180 combs = [ ]
181 f o r b l 1 inb u s _l i n e s : # c r i a as combinacoes de l i n h a s
182 combs . append ( c o m b i n a t i o n ( [ b l 1 ] ) )
183 f o r b l 2 inb u s_ l i n e s :
184 i fb l 2 . f i r s t _i n s t a n c e >= b l 1 . l a s t_ i n s t a n c e :
185 combs . append ( c o m b i n a t i o n ( [ bl1 , b l 2 ] ) )
186 f o r comb incombs : # c a l c u l a o tempo para cada combinação
187 c a l c u l a t e _c o s t ( comb )
188 n l = 666
189 nc = l e n( combs )
190 f o r iin range ( n l ) i fn l < nc e l s e range ( nc ) : # mostra as i n s t r u c o e s para as n m e l h o r e s
combinacoes
45191 comb = s o r t e d ( combs , key= lambda r : r . t o t a l_ t i m e ) [ i ]
192 p r i n t ( comb . b u s _l i n e s [ 0 ] . speed )
193 p r i n t ( " Opção { 0 } : \ n \ nLinhas : \ n {1} \ n " . format ( i + 1 , " , \ n " . j o i n ( l i s t ( l . name
f o r lincomb . b u s_ l i n e s ) ) ) )
194 p r i n t ( " \ n " . j o i n ( comb . i n s t r u c t i o n s ) +" \ n " )
46
