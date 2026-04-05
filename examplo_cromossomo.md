# Evolução de Cromossomo

Vamos simular exatamente o que acontece, passo a passo, usando a viagem de Natal (Origem) até Pau dos Ferros (Destino).

### Geração 1: Nascimento

Ele precisa criar a População Inicial usando a função `gerar_individuo` baseada em caminhada aleatória. O cromossomo sai de Natal e vai escolhendo estradas na sorte.

- **Pai 1 (Litoral):** Ele sai de Natal, sobe pra Ceará-Mirim, vai até João Câmara, desce para **Lajes**, sobe de novo pra Macau, desce pra Assú, vai até Mossoró, Apodi e finalmente chega em Pau dos Ferros.
    - O Cromossomo: `['Natal', 'Ceará-Mirim', 'João Câmara', 'Lajes', 'Macau', 'Assú', 'Mossoró', 'Apodi', 'Pau dos Ferros']`
- **Pai 2 (Seridó):** Ele sai de Natal, vai pra Macaíba, Riachuelo, **Lajes**, desce pra Currais Novos, Caicó, Patu e chega em Pau dos Ferros.
    - O Cromossomo: `['Natal', 'Macaíba', 'Riachuelo', 'Lajes', 'Currais Novos', 'Caicó', 'Patu', 'Pau dos Ferros']`

**Aptidão:** A nossa Função de Avaliação entra para calcular a aptidão (o custo) dessas viagens. Como ambos deram voltas gigantescas pelo estado, o custo deles é altíssimo. O Pai 1 deu 580 km e o Pai 2 deu 530 km.

Na Seleção por Torneio, eles disputam contra cromossomos que nem conseguiram chegar ao destino (aqueles que levaram a punição de 99999 km). Portanto, por piores que sejam, Pai 1 e Pai 2 são os "melhores dos piores" e ganham o direito de reproduzir.

### Geração 2: Cruzamento

A função `cruzamento` recebe o Pai 1 e o Pai 2. Como eles têm tamanhos diferentes e caminhos totalmente distintos. Como eles cruzam?

A nossa lógica varre os dois cromossomos procurando um gene (cidade) em comum. No exemplo: **ambos passaram por Lajes.**

O algoritmo corta os dois cromossomos em Lajes e faz a costura:

- Pega a primeira metade do Pai 2 (que foi mais direto: Natal -> Macaíba -> Riachuelo -> Lajes).
- Costura com a segunda metade do Pai 1 (Lajes -> Macau -> Assú -> Mossoró -> Apodi -> Pau dos Ferros).

Nasce o **Filho 1**! Ele herdou o início bom de um pai, mas infelizmente herdou aquele desvio horrível por Macau do outro pai. O custo dele cai para 500 km. Já é uma evolução!

### Geração 3 a 15: Mutação

O Filho 1 sobreviveu por várias gerações sendo o campeão, mas ele está preso naquele Mínimo Local: ele insiste em ir até Macau antes de descer para Assú. O *Crossover* sozinho não consegue tirar ele de lá.

É aqui que os 10% de chance da Mutação salvam o dia.

A função `mutacao` sorteia o Filho 1. O "raio" da mutação atinge exatamente a cidade de **Lajes**.
O que o nosso código faz?

1. Ele apaga toda a rota a partir de Lajes (deleta Macau, Assú, Mossoró...).
2. Força o agente cego a fazer uma nova caminhada aleatória saindo de Lajes até Pau dos Ferros.
3. Nessa nova tentativa, o agente acerta a rodovia BR-304 e ele acha o caminho: Lajes -> Angicos -> Fernando Pedroza -> Assú -> Caraúbas -> Pau dos Ferros.

O cromossomo do Filho 1 é reescrito. Aquela volta inútil pelo litoral norte foi completamente dizimada. O custo despenca de 500 km para 380 km de uma vez só! É aquele degrau gigante que você viu no gráfico de convergência.

### Geração 80: Chegando no Ótimo Global

Ao longo das próximas dezenas de gerações, esses pequenos cortes, costuras e mutações continuam podando qualquer cidade que desvie da linha reta. As rotas que dão voltas perdem os torneios e morrem. As mais diretas sobrevivem e passam seus genes para frente.

Quando o loop de 80 gerações termina, o cromossomo final que sobreviveu e está salvo na variável `melhor_rota_global`, passando unicamente pelas cidades que formam a menor distância física possível entre Natal e Pau dos Ferros.