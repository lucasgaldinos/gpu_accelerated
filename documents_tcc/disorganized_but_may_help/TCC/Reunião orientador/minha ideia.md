Utilizar as capacidades de GPU para obter melhores resultados quando calculando rotas em um VRP.

A princípio, desenvolveria um banco de dados geográfico utilizando ferramentas de mapa open source para coleta dos pontos. Além disso, o banco de dados deve ter outros tipos de informação, como tipos de carros, tamanho da frota, pontos de entrega, etc, que seriam criados utilizando mock data (dados falsos com o obetivo de simular possíveis situações reais).  
Criar as restrições, baseado na literatura, e além disso, criar novas restrições conforme o projeto se faz necessário (Essa parte seria mais complexa, principalmente a parte do pickup and delivery, então simplificações seriam feitas para deixar o problema ser expandido no futuro).

Nova proposta: Utilizar o trabalho já desenvolvido pelo professor, com as restrições do modelo, talvez inserir novas possíveis restrições como tamanho da carga, mas com o foco principal em utilizar de métodos de paralelismo, tanto por CPU quanto por GPU quando possível. Isso permitiria oferecer esse tipo de serviço através de:

1. Aplicativo para o motorista que calcularia server-side, utilizando um cluster com GPU.
2. Aplicativo local para o motorista, que poderia rodar na própria central multimídia, localmente, que tem plataforma semelhante a celulares android e onde o linux é muito utilizado. Talvez o que mais atrapalhe é o tamanho de um banco de dados local com essas informações, que pode tornar inviável esse tipo de aplicação.

Comparar os resultados

Falar sobre minha experiência com o problema. Dizer que estou meio enferrujado, mas que o tópico me é de bastante interesse.
