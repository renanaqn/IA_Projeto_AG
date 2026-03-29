# Projeto 1 - Algoritmos Genéticos

**Implementação**

- O código encontra a rota mais curta (menor soma de quilômetros ) saindo de Parnamirim (Nó #3) até Apodi (Nó #13), por exemplo.
- Usamos Codificação por Valor, pois cromossomos binários não fariam sentido para navegar em um grafo real;
- A seleção é por Torneio, garantindo uma boa pressão seletiva sem a variância excessiva da Roleta.
- A substituição por geração com elitismo, garantindo que o melhor caminho nunca seja perdido;
- E a Taxa de Mutação está configurada baixa (10%), exatamente para evitar que o AG vire uma busca puramente aleatória;
- Como o mapa não é um grafo completo (nem todas as cidades se conectam diretamente), então os operadores de Crossover e Mutação  podem acabar gerando saltos impossíveis no mapa (ex: Natal direto para Caicó), então na função de Fitness aplica uma penalidade severa para conexões inexistentes;