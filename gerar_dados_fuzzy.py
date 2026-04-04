import random

def gerar_dataset_fuzzy(arquivo_entrada, arquivo_saida):
    print(f"Lendo o arquivo original: {arquivo_entrada}...")

    with open(arquivo_entrada, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    # pega o cabeçalho original e adiciona as novas colunas
    cabecalho_original = linhas[0].strip()
    novo_cabecalho = f"{cabecalho_original};asfalto;trafego\n"

    print(f"Gerando os dados simulados para {len(linhas)-1} rodovias")

    with open(arquivo_saida, 'w', encoding='utf-8') as f_out:
        f_out.write(novo_cabecalho)

        for linha in linhas[1:]:
            if linha.strip():
                # onde 0 é cheio de crateras e 10 é a estrada da paraiba
                asfalto = random.randint(0,10)
                # onde 0 é o deserto e 100 é sao paulo no dia mais leve
                trafego = random.randint(0,100)

                nova_linha = f"{linha.strip()};{asfalto};{trafego}\n"
                f_out.write(nova_linha)
        
        print(f"Sucesso, o novo arquivo '{arquivo_saida}' está pronto.")

gerar_dataset_fuzzy('rotas.txt', 'rotas_fuzzy.txt')