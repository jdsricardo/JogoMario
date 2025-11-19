"""
Super Mario Runner - Jogo Principal (Modo Manual)

Execute este arquivo para jogar manualmente.
Use as setas ou WASD para controlar o Mario.
"""

from game.game import JogoMario


def main():
    print("=" * 50)
    print("SUPER MARIO RUNNER - Modo Manual")
    print("=" * 50)
    print("\nControles:")
    print("  ESPAÇO / SETA CIMA: Pular")
    print("  SETA ESQUERDA / A: Mover para esquerda")
    print("  SETA DIREITA / D: Mover para direita")
    print("  P: Pausar")
    print("  R: Reiniciar")
    print("  ESC: Sair")
    print("\nObjetivo:")
    print(f"  Percorra 15000 pixels sem colidir!")
    print("  Desvie de canos, Goombas, tartarugas e bombas!")
    print("\n" + "=" * 50)
    print("Iniciando jogo...\n")
    
    jogo = JogoMario(modo='manual')
    jogo.executar()


if __name__ == '__main__':
    main()
