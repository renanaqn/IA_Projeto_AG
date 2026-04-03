import networkx as nx # biblioteca para grafos
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation #biblioteca para os gifs

# === Ingestão de Dados ===

def carregar_mapa(arquivo_pontos, arquivo_rotas):
    mapa = nx.Graph() # cria o grafo não-direcionado (mão dupla)
    
    # carrega os nós (cidades/entroncamentos)
    with open(arquivo_pontos, 'r', encoding='utf-8') as f:
        linhas = f.readlines()[1:] # pula o cabeçalho
        for linha in linhas:
            if linha.strip(): # evita linhas em branco
                partes = linha.strip().split(';')
                id_ponto = partes[0]
                nome = partes[1]
                lat = float(partes[2])
                lon = float(partes[3])
                # adiciona o nó no grafo guardando as coordenadas
                mapa.add_node(id_ponto, nome=nome, pos=(lon, lat))
                
    # carrega as arestas (rodovias) e as distâncias
    with open(arquivo_rotas, 'r', encoding='utf-8') as f:
        linhas = f.readlines()[1:] # pula o cabeçalho
        for linha in linhas:
            if linha.strip():
                partes = linha.strip().split(';')
                id_rota = partes[0]
                nome_rota = partes[1]
                origem = partes[2]
                destino = partes[3]
                comprimento = float(partes[4])
                # adiciona a estrada ligando a origem ao destino com o peso (distância)
                mapa.add_edge(origem, destino, weight=comprimento, nome_rota=nome_rota)
                
    return mapa

# teste de carregamento inicial
G = carregar_mapa('pontos.txt', 'rotas.txt')

print(f"Mapa carregado com sucesso!")
print(f"Total de Cidades/Entroncamentos: {G.number_of_nodes()}")
print(f"Total de Estradas: {G.number_of_edges()}")

# === Funções base do algoritmo genético ===
def gerar_individuo(grafo, origem, destino):
    """
    Cria uma rota aleatória do ponto de origem ao destino
    faz uma caminhada cega pelo grafo evitando voltar por onde já passou.
    Foi usado a Codificação por Valor, onde cada cromossomo é uma 
    sequencia de IDs das cidades.

    Um exemplo de cromossomo:
    ind = [#1, #3, #5, #5A, #63] -> representa a rota Natal (Viaduto de Ponta Negra) -> Parnamirim -> Macaiba -> Macaiba (Tabajara) -> Currais Novos
    todo: lembrar de fazer ym fluxograma dos individuos ao longo do tempo (e um gif)
    todo: possibilidade de a partir de um plano cartesiano entre a origem e destino, computar a rota
    """
    caminho = [origem]
    atual = origem
    
    # vamos tentar encontrar um caminho, mas com um limite para evitar loops infinitos
    limite_tentativas = 300 
    tentativas = 0
    
    while atual != destino and tentativas < limite_tentativas:
        # pega todos os vizinhos do nó atual
        vizinhos = list(grafo.neighbors(atual))
        
        # filtra para não voltar por onde já passou (evitar ficar andando em círculos)
        vizinhos_nao_visitados = [v for v in vizinhos if v not in caminho]
        
        # se entrar em beco sem saida, encerra a rota pela metade
        if not vizinhos_nao_visitados:
            break 
            
        # escolhe um vizinho aleatório e avança
        proximo_passo = random.choice(vizinhos_nao_visitados)
        caminho.append(proximo_passo)
        atual = proximo_passo
        tentativas += 1
        
    return caminho

def criar_populacao(grafo, tamanho_populacao, origem, destino):
    """Cria uma lista com N indivíduos (rotas aleatórias)"""
    return [gerar_individuo(grafo, origem, destino) for _ in range(tamanho_populacao)]

def calcular_custo(grafo, individuo, destino_desejado):
    """
    Função de fitness que verifica o f(x) de cada cromossomo.
    Quanto menor o custo final, melhor a rota. O custo é a soma das distâncias dos trechos percorridos.
    """
    custo_total = 0
    PENALIDADE = 99999.0 # valor para rotas impossíveis ou incompletas
    
    # checa se o individuo conseguiu chegar no destino
    if individuo[-1] != destino_desejado:
        custo_total += PENALIDADE
        
    # soma o peso de cada trecho percorrido
    for i in range(len(individuo) - 1):
        u = individuo[i]
        v = individuo[i+1]
        
        # verifica se realmente existe uma estrada ligando a cidade U e a cidade V
        if grafo.has_edge(u, v):
            custo_total += grafo[u][v]['weight']
        else:
            # penaliza saltos impossiveis gerados pelo crossover/mutacao
            custo_total += PENALIDADE 
            
    return custo_total

# === Operadores Genéticos ===

def cruzamento(pai1, pai2):
    """
    Crossover para Grafos: procura uma cidade em comum entre as duas rotas
    (além da origem e destino). Se achar, corta as rotas nessa cidade e 
    costura a primeira metade do Pai 1 com a segunda metade do Pai 2.
    """
    # ignora a origem (índice 0) e tenta achar cidades intermediárias em comum
    miolo_pai1 = pai1[1:-1]
    miolo_pai2 = pai2[1:-1]
    
    cidades_comuns = list(set(miolo_pai1) & set(miolo_pai2))
    
    if cidades_comuns:
        # escolhe uma cidade de interseção aleatória para ser o ponto de corte
        ponto_corte = random.choice(cidades_comuns)
        
        # encontra onde essa cidade está em cada pai
        idx1 = pai1.index(ponto_corte)
        idx2 = pai2.index(ponto_corte)
        
        # costura os genes: Início do pai 1 + Final do pai 2 (e vice-versa)
        filho1 = pai1[:idx1] + pai2[idx2:]
        filho2 = pai2[:idx2] + pai1[idx1:]
        
        return filho1, filho2
    else:
        # Se não têm cidades em comum, não tem como cruzar de forma válida. 
        # Retornamos cópias dos pais.
        return pai1.copy(), pai2.copy()

def mutacao(individuo, grafo, destino, taxa_mutacao=0.1):
    """
    Tenta apagar apenas um pequeno trecho no meio da rota
    e achar um caminho alternativo local, preservando o início e o fim.
    """
    if random.random() < taxa_mutacao and len(individuo) > 3:
        # Escolhe um ponto no meio
        idx_mutacao = random.randint(1, len(individuo) - 3)
        ponto_a = individuo[idx_mutacao]
        
        # Em vez de ir até o destino, tenta ir só até 2 cidades pra frente
        ponto_b = individuo[idx_mutacao + 2] 
        
        # Gera um desvio curto entre ponto_a e ponto_b
        desvio = gerar_individuo(grafo, ponto_a, ponto_b)
        
        # Se o desvio foi bem sucedido (chegou no ponto_b), costura a nova rota
        if desvio[-1] == ponto_b:
            nova_rota = individuo[:idx_mutacao] + desvio[:-1] + individuo[idx_mutacao+2:]
            return nova_rota
            
        # Se falhou, aplica a mutação antiga (vai até o destino) como plano B
        nova_rota_b = individuo[:idx_mutacao]
        caminho_restante = gerar_individuo(grafo, ponto_a, destino)
        nova_rota_b.extend(caminho_restante)
        return nova_rota_b
        
    return individuo

def selecao_torneio(populacao, grafo, destino, k=3):
    """
    A seleção usada é a de torneio, onde sorteia 'k' indivíduos aleatórios da população.
    O que tiver o menor custo (melhor fitness) vence e é escolhido para ser pai/mãe.
    """
    competidores = random.sample(populacao, k)
    melhor = min(competidores, key=lambda ind: calcular_custo(grafo, ind, destino))
    return melhor

# === Execução principal do AG ===
def executar_ag(grafo, origem, destino, num_geracoes=50, tamanho_pop=50, taxa_mutacao=0.1):
    print(f"\nIniciando a Evolução: Saindo de {grafo.nodes[origem]['nome']} para {grafo.nodes[destino]['nome']}")
    
    # cria a população inicial
    populacao = criar_populacao(grafo, tamanho_pop, origem, destino)
    
    melhor_rota_global = None
    menor_custo_global = float('inf')
    historico_custos = [] 
    historico_rotas_gif = [] # lista de rotas para o GIF
    
    # loop das gerações
    for geracao in range(num_geracoes):
        # avalia o custo de todo mundo da geração atual
        custos = [calcular_custo(grafo, ind, destino) for ind in populacao]
        
        # acha o melhor indivíduo desta geração específica
        melhor_indice = custos.index(min(custos))
        melhor_rota_atual = populacao[melhor_indice]
        menor_custo_atual = custos[melhor_indice]
        
        # atualiza o nosso recorde global (Elitismo)
        if menor_custo_atual < menor_custo_global:
            menor_custo_global = menor_custo_atual
            melhor_rota_global = melhor_rota_atual.copy()
            print(f"Geração {geracao+1}: Novo recorde! Custo baixou para {menor_custo_global:.2f} km")
            
        historico_custos.append(menor_custo_global)
        
        # salva o frame da geração atual
        historico_rotas_gif.append(melhor_rota_global.copy())

        # elitismo: salva o melhor global            
        nova_populacao = []

        # regra do Elitismo: O campeão atual passa direto para a próxima geração intacto
        nova_populacao.append(melhor_rota_global)
        
        # preenche o resto da população cruzando e mutando os melhores
        while len(nova_populacao) < tamanho_pop:
            # seleciona dois pais via torneio
            pai1 = selecao_torneio(populacao, grafo, destino)
            pai2 = selecao_torneio(populacao, grafo, destino)
            
            # cruza o DNA (rotas)
            filho1, filho2 = cruzamento(pai1, pai2)
            
            # aplica mutação com uma pequena chance
            filho1 = mutacao(filho1, grafo, destino, taxa_mutacao)
            filho2 = mutacao(filho2, grafo, destino, taxa_mutacao)
            
            nova_populacao.extend([filho1, filho2])
        
        # corta excessos caso a lista passe do tamanho exato
        populacao = nova_populacao[:tamanho_pop]
        
    print(f"\nEvolução Concluída após {num_geracoes} gerações!")
    print(f"Custo Total Final: {menor_custo_global:.2f} km\n")

    # imprime os nomes das cidades para ficar legível
    nomes_cidades = [grafo.nodes[n]['nome'] for n in melhor_rota_global]
    print(f"Rota Detalhada: {' -> '.join(nomes_cidades)}")
    print(f"Custo Total Final: {menor_custo_global:.2f} km\n")
    
    
    # Retorna o historico de rotas junto com o resto
    return melhor_rota_global, menor_custo_global, historico_custos, historico_rotas_gif

def gerar_gif_evolucao(grafo, historico_rotas, nome_arquivo="evolucao.gif"):
    print("\nRenderizando o GIF da evolução... Isso pode levar alguns segundos.")
    
    posicoes = nx.get_node_attributes(grafo, 'pos')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Esta função é chamada para desenhar CADA quadro do GIF
    def atualizar_frame(frame):
        ax.clear() # Limpa a tela anterior
        rota = historico_rotas[frame]
        
        # Desenha o mapa de fundo
        nx.draw(grafo, posicoes, node_size=15, node_color='lightgray', edge_color='lightgray', with_labels=False, ax=ax)
        
        if rota:
            # Desenha as cidades da rota e a linha vermelha
            nx.draw_networkx_nodes(grafo, posicoes, nodelist=rota, node_color='#1f78b4', node_size=50, ax=ax)
            arestas_rota = [(rota[i], rota[i+1]) for i in range(len(rota)-1)]
            nx.draw_networkx_edges(grafo, posicoes, edgelist=arestas_rota, edge_color='red', width=3.0, ax=ax)
        
        # Atualiza o título dinamicamente com o custo atual caindo
        custo = calcular_custo(grafo, rota, rota[-1]) if rota else 0
        ax.set_title(f"Geração {frame+1} | Melhor Rota: {custo:.2f} km", fontsize=14, fontweight='bold')
        ax.axis('equal')

    # Cria a animação: frames é a quantidade de gerações, interval é a velocidade em ms (200 = 5 frames por segundo)
    ani = animation.FuncAnimation(fig, atualizar_frame, frames=len(historico_rotas), interval=150)
    
    # Salva o arquivo na pasta do seu projeto
    ani.save(nome_arquivo, writer='pillow')
    print(f"GIF salvo com sucesso como '{nome_arquivo}'!")
    plt.close(fig) # Fecha a janela para não travar o programa


# === Decisão da rota a ser otimizada ===
origem = '#1'  # #1 - Viaduto de Ponta Negra (Natal)
destino = '#13' # #11 - Currais Novos

# rodando com 10 indivíduos por 50 gerações
melhor_caminho, custo, historico, rotas_gif = executar_ag(G, origem, destino, num_geracoes=80, tamanho_pop=40, taxa_mutacao=0.1)

# === Visualização dos Resultados ===
def plotar_convergencia(historico):
    plt.figure(figsize=(10, 5))
    
    # plota a linha azul com bolinhas marcando cada geração
    plt.plot(range(1, len(historico) + 1), historico, marker='o', linestyle='-', color='b', markersize=4)
    
    plt.title('Curva de Convergência do AG', fontsize=14, fontweight='bold')
    plt.xlabel('Gerações', fontsize=12)
    plt.ylabel('Melhor Custo (km)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # como as rotas iniciais tem custo de 99999, o gráfico pode ficar esmagado.
    # vamos focar apenas nos custos reais (< 10000) se eles existirem a partir da 2ª geracao
    custos_reais = [c for c in historico if c < 99000]
    if custos_reais:
        plt.ylim(min(custos_reais) - 50, max(custos_reais) + 50)
        
    plt.show(block=False) # mostra o gráfico sem bloquear a execução do programa

# plotagem do grafico com a rota final
def plotar_mapa(grafo, rota_vencedora):
    print("\nGerando o mapa visual...")
    
    # pega as coordenadas (Longitude e Latitude) que salvamos na hora de carregar o mapa
    posicoes = nx.get_node_attributes(grafo, 'pos')
    
    # cria uma figura grande para o mapa não ficar espremido
    plt.figure(figsize=(12, 8))
    
    # desenha o fundo do mapa em cinza
    nx.draw(grafo, posicoes, node_size=15, node_color='lightgray', edge_color='lightgray', with_labels=False)
    
    if rota_vencedora:
        # destaca as cidades e a linha do caminho
        nx.draw_networkx_nodes(grafo, posicoes, nodelist=rota_vencedora, node_color='#1f78b4', node_size=50)
        
        # desenha a linha vermelha grossa conectando a rota
        arestas_rota = [(rota_vencedora[i], rota_vencedora[i+1]) for i in range(len(rota_vencedora)-1)]
        nx.draw_networkx_edges(grafo, posicoes, edgelist=arestas_rota, edge_color='red', width=3.0)
        
        # adiciona as labels so nas cidades da rota pra nao poluir
        nomes_rota = {no: grafo.nodes[no]['nome'].split(' - ')[0] for no in rota_vencedora} # pega só o primeiro nome
        nx.draw_networkx_labels(grafo, posicoes, labels=nomes_rota, font_size=9, font_weight='bold', verticalalignment='bottom')
    
    plt.title(f"Algoritmo Genético: Rota Otimizada ({custo:.2f} km)", fontsize=16, fontweight='bold')
    plt.axis('equal') # Garante que o mapa não fique esticado
    plt.show() # Abre a janela com o gráfico


gerar_gif_evolucao(G, rotas_gif, "evolucao_rotas.gif")

# plota a curva de convergencia do AG
plotar_convergencia(historico)

# função para desenhar a arte final
plotar_mapa(G, melhor_caminho)