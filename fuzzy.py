import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def criar_sistema_fuzzy():
    # definindo variáveis do universo 
    asfalto = ctrl.Antecedent(np.arange(0,11,1), 'asfalto')
    trafego = ctrl.Antecedent(np.arange(0,101,1), 'trafego')
    # o multiplicador de custo de viagem vai de 1.0 (viagem linda) até 3.0 (viagem horrível)
    multiplicador = ctrl.Consequent(np.arange(1.0,3.1,0.1), 'multiplicador')

    # mapeando os conjuntos fuzzy (usando função triangular)
    # todo: caso precise de mais precisão, podemos mudar para trepezoidal
    asfalto['ruim'] = fuzz.trimf(asfalto.universe, [0,0,5])
    asfalto['razoavel'] = fuzz.trimf(asfalto.universe, [2,5,8])
    asfalto['bom'] = fuzz.trimf(asfalto.universe, [5,10,10])
    
    trafego['leve'] = fuzz.trimf(trafego.universe, [0,0,40])
    trafego['moderado'] = fuzz.trimf(trafego.universe, [20,50,80])
    trafego['pesado'] = fuzz.trimf(trafego.universe, [60,100,100])

    multiplicador['baixo'] = fuzz.trimf(multiplicador.universe, [1.0,1.0,1.5])
    multiplicador['medio'] = fuzz.trimf(multiplicador.universe, [1.2,1.8,2.5])
    multiplicador['alto'] = fuzz.trimf(multiplicador.universe, [2.0,3.0,3.0])

    # definição das regras (3x3)
    regras = [
        # se Tráfego é LEVE
        ctrl.Rule(asfalto['bom'] & trafego['leve'], multiplicador['baixo']),
        ctrl.Rule(asfalto['razoavel'] & trafego['leve'], multiplicador['baixo']),
        ctrl.Rule(asfalto['ruim'] & trafego['leve'], multiplicador['medio']),
        
        # se Tráfego é MODERADO
        ctrl.Rule(asfalto['bom'] & trafego['moderado'], multiplicador['medio']),
        ctrl.Rule(asfalto['razoavel'] & trafego['moderado'], multiplicador['medio']),
        ctrl.Rule(asfalto['ruim'] & trafego['moderado'], multiplicador['alto']), 
        
        # se Tráfego é PESADO
        ctrl.Rule(asfalto['bom'] & trafego['pesado'], multiplicador['alto']),      # Trânsito trava tudo
        ctrl.Rule(asfalto['razoavel'] & trafego['pesado'], multiplicador['alto']), # Trânsito trava tudo
        ctrl.Rule(asfalto['ruim'] & trafego['pesado'], multiplicador['alto'])

        #todo: talvez ajustar algum para usar OU
    ]

    # compilando o sistema
    sistema_controle = ctrl.ControlSystem(regras)
    return sistema_controle

# instancia o simulador para ser importado por outros arquivos
sistema_controle_global = criar_sistema_fuzzy()

def avaliar_rodovia(nota_asfalto, nota_trafego):
    """
    Recebe as notas, processa no sistema fuzzy e devolve o multiplicador e instantia 
    o simulador para ser usado em outros arquivos.
    """
    # instancia um simulador novo para garantir que a memória esteja limpa a cada estrada analisada
    simulador = ctrl.ControlSystemSimulation(sistema_controle_global)
    
    simulador.input['asfalto'] = nota_asfalto
    simulador.input['trafego'] = nota_trafego
    simulador.compute()

    return simulador.output['multiplicador']

if __name__ == '__main__':
    print("--- Testando o Sistema Fuzzy de Rodovias ---")

    # teste 1: rodovia perfeita
    mult_bom = avaliar_rodovia(nota_asfalto=9, nota_trafego=10)
    print(f"Asfalto 9, Tráfego 10% -> Multiplicador de Dificuldade: {mult_bom:.2f}x")
    # teste 2: rodovia ruim
    mult_ruim = avaliar_rodovia(nota_asfalto=2, nota_trafego=80)
    print(f"Asfalto 2, Tráfego 80% -> Multiplicador de Dificuldade: {mult_ruim:.2f}x")
    # teste 3: rodovia ok
    mult_medio = avaliar_rodovia(nota_asfalto=5, nota_trafego=45)
    print(f"Asfalto 5, Tráfego 45% -> Multiplicador de Dificuldade: {mult_medio:.2f}x")
