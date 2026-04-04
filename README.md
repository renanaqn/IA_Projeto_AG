# Otimização de Rotas Rodoviárias com IA
**Disciplina:** Inteligência Artificial

**Projetos:** Algoritmos Genéticos (Projeto 1) e Lógica Fuzzy (Projeto 2)

O objetivo é encontrar a melhor rota entre duas cidades, evoluindo de uma busca simples por distância física para uma busca heurística considerando o estresse da via.

## Projeto 1: Algoritmo Genético Clássico (`ag.py`)
O primeiro projeto foca em encontrar o caminho mais curto (menor quilometragem) entre uma origem e um destino utilizando evolução simulada.

### Decisões de Implementação:
* **Codificação por Valor:** Os cromossomos são representados por vetores (arrays) de tamanho variável contendo a sequência de IDs das cidades visitadas, ex: `['#1', '#3', '#10']` que significa `['Natal', 'Parnamirim', 'São José do Mipibu']`;
* **Função de Avaliação (Fitness):** O custo do indivíduo é a soma das distâncias em km das arestas reais do grafo. Rotas que tentam utilizar conexões inexistentes ou que não chegam ao destino final recebem uma penalidade severa (`99999.0 km`);
* **Seleção por Torneio:** Escolha de $k$ (3) indivíduos aleatórios da população, onde o que possui o menor custo vence e ganha o direito de reproduzir;
* **Cruzamento:** Como os cromossomos possuem tamanhos variáveis, o ponto de corte (locus) não é fixo. O algoritmo encontra uma **cidade de interseção** visitada por ambos os pais e realiza a "costura" das rotas a partir desse nó;
* **Mutação:** Com uma probabilidade baixa (ex: 10%), um indivíduo sofre mutação em uma cidade aleatória de sua rota. O caminho a partir dali é apagado, e uma nova caminhada aleatória é forçada até o destino, prevenindo a convergência prematura em Mínimos Locais;
* **Elitismo:** O melhor indivíduo de cada geração é garantido na próxima população sem sofrer alterações;

---

## Projeto 2: Sistema de Inferência Fuzzy (`ag_fuzzy.py` e `fuzzy.py`)
O segundo projeto expande o algoritmo genético, substituindo o custo estático da distância por um "Custo de Estresse", avaliado dinamicamente através de Lógica Nebulosa (Fuzzy).

### Arquitetura do Fuzzy:
O sistema atua como um avaliador de rodovias, recebendo dados do ambiente e devolvendo um multiplicador de dificuldade (peso) para a aresta do grafo.

* **Variáveis de Entrada (Antecedentes):**
  * `Qualidade do Asfalto`: Notas de 0 a 10 (Conjuntos: Ruim, Razoável, Bom).
  * `Nível de Tráfego`: Porcentagem de 0 a 100% (Conjuntos: Leve, Moderado, Pesado).
* **Variável de Saída (Consequente):**
  * `Multiplicador de Custo`: Valores de 1.0x a 3.0x (Conjuntos: Baixo, Médio, Alto).
* **Matriz de Regras (Inferência):** Um conjunto de 9 regras lógicas cobre todos os cenários possíveis. Exemplo: *SE o Asfalto é Ruim E o Tráfego é Pesado, ENTÃO o Multiplicador é Alto.*

---

## Visualização de Dados
O projeto conta com ferramentas visuais para facilitar a compreensão do processo evolutivo:
1. **Gráficos:** Gráficos gerados com `matplotlib` mostrando a queda do custo da melhor rota ao longo das gerações e um mapa final.
2. **Timelapse Animado (GIF):** Exportação automática em `.gif` que ilustra o cromossomo "esticando" e se corrigindo ao longo das gerações, provando o funcionamento dos operadores genéticos na prática.

---