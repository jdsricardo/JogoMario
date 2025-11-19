"""Entrada principal para o treinamento NEAT do Mario Runner."""

from __future__ import annotations

import argparse
import os
import pickle
import sys
from pathlib import Path

import neat
import pygame

from game.game import JogoMario
from game.mario import Mario
from utils.constants import (
    ACTION_COUNT,
    CHAO_Y,
    DISTANCIA_PARA_VENCER,
    FPS,
    SENSOR_COUNT,
)


# Variáveis globais utilizadas durante a avaliação NEAT
CURRENT_GENERATION = 1
TRAINING_SETTINGS = {
    "render": True,
    "max_score": 50000,
}


def build_arg_parser() -> argparse.ArgumentParser:
    """Cria o parser de argumentos para CLI."""

    parser = argparse.ArgumentParser(
        description="Treina o Mario automaticamente usando NEAT"
    )
    parser.add_argument(
        "--config",
        default="config-feedforward.txt",
        help="Caminho para o arquivo de configuração do NEAT",
    )
    parser.add_argument(
        "--generations",
        type=int,
        default=50,
        help="Quantidade de gerações para o treinamento",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Executa o treinamento sem abrir janela (modo rápido)",
    )
    parser.add_argument(
        "--best-path",
        default="melhor_genoma.pkl",
        help="Arquivo onde o melhor genoma será salvo",
    )
    parser.add_argument(
        "--no-save-best",
        action="store_true",
        help="Não salva o melhor genoma ao final do treinamento",
    )
    parser.add_argument(
        "--max-score",
        type=int,
        default=50000,
        help="Pontuação máxima por rodada para evitar loops infinitos",
    )
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=0,
        help="Salva checkpoints a cada N gerações (0 desativa)",
    )
    parser.add_argument(
        "--checkpoint-dir",
        default="checkpoints",
        help="Diretório onde os checkpoints serão gravados",
    )
    parser.add_argument(
        "--load-checkpoint",
        default="",
        help="Retoma o treinamento a partir de um checkpoint salvo",
    )
    return parser


def _validar_config(config: neat.Config) -> None:
    """Garante que a configuração do NEAT corresponde aos sensores/ações do jogo."""

    genome_cfg = config.genome_config
    if genome_cfg.num_inputs != SENSOR_COUNT:
        raise RuntimeError(
            f"Configuração NEAT espera {genome_cfg.num_inputs} inputs, \n"
            f"mas o ambiente fornece {SENSOR_COUNT}. Atualize 'num_inputs'."
        )
    if genome_cfg.num_outputs != ACTION_COUNT:
        raise RuntimeError(
            f"Configuração NEAT espera {genome_cfg.num_outputs} saídas, \n"
            f"mas o ambiente exige {ACTION_COUNT}. Atualize 'num_outputs'."
        )


def _remover_indice(i, marios, redes, genomas, jogo, extras=None):
    """Remove o Mario de todas as listas de acompanhamento."""

    marios.pop(i)
    redes.pop(i)
    genomas.pop(i)
    if i < len(jogo.marios):
        jogo.marios.pop(i)
    if extras:
        for lista in extras:
            lista.pop(i)


def eval_genomes(genomes, config):
    """Função de avaliação chamada pelo NEAT para cada geração."""

    global CURRENT_GENERATION

    jogo = JogoMario(modo='ia', render=TRAINING_SETTINGS["render"])
    jogo.geracao = CURRENT_GENERATION

    redes = []
    genomas = []
    marios = []
    frames_sem_melhoria = []
    ultimos_fitness = []

    for _, genome in genomes:
        genome.fitness = 0.0
        rede = neat.nn.FeedForwardNetwork.create(genome, config)
        redes.append(rede)
        genomas.append(genome)
        personagem = Mario(100, CHAO_Y)
        marios.append(personagem)
        jogo.adicionar_mario(personagem)
        frames_sem_melhoria.append(0)
        ultimos_fitness.append(0.0)

    rodando = True
    while rodando and marios:
        jogo.relogio.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        jogo.atualizar()

        for i in range(len(marios) - 1, -1, -1):
            mario = marios[i]
            sensores = mario.get_sensores(jogo.obstaculos, jogo.velocidade)
            saidas = redes[i].activate(sensores)

            salto = saidas[0] > 0.5
            abaixar = saidas[1] > 0.5
            mario.aplicar_comandos(pular=salto, abaixar=abaixar)
            mario.atualizar()

            if jogo.verificar_colisao(mario):
                genomas[i].fitness += jogo.distancia_percorrida * 0.01
                _remover_indice(i, marios, redes, genomas, jogo, [frames_sem_melhoria, ultimos_fitness])
                continue

            # Recompensas por sobreviver, ganhar velocidade e utilizar ações relevantes
            genomas[i].fitness += 0.3
            genomas[i].fitness += jogo.velocidade * 0.015

            obstaculo_chao_proximo = sensores[0] < 0.35
            bomba_proxima = sensores[3] > 0.5
            bomba_proxima_e_perto = bomba_proxima and sensores[2] < 0.35

            if obstaculo_chao_proximo and salto and mario.velocidade_y < 0:
                genomas[i].fitness += 1.2
            elif salto and not obstaculo_chao_proximo:
                genomas[i].fitness -= 0.05

            if bomba_proxima_e_perto and abaixar:
                genomas[i].fitness += 1.5
            elif abaixar and not bomba_proxima:
                genomas[i].fitness -= 0.05

            if jogo.vitoria:
                genomas[i].fitness += 2000

            if genomas[i].fitness > ultimos_fitness[i] + 0.1:
                ultimos_fitness[i] = genomas[i].fitness
                frames_sem_melhoria[i] = 0
            else:
                frames_sem_melhoria[i] += 1

            if frames_sem_melhoria[i] > FPS * 6:
                _remover_indice(i, marios, redes, genomas, jogo, [frames_sem_melhoria, ultimos_fitness])
                continue

        jogo.vivos = len(marios)
        jogo.desenhar()

        if not marios:
            rodando = False
        if jogo.vitoria:
            rodando = False
        if jogo.pontuacao > TRAINING_SETTINGS["max_score"]:
            rodando = False

    CURRENT_GENERATION += 1


def _carregar_config(config_path: Path) -> neat.Config:
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        str(config_path),
    )
    _validar_config(config)
    return config


def run_training(args: argparse.Namespace) -> None:
    """Inicializa a população NEAT e executa o treinamento."""

    TRAINING_SETTINGS["render"] = not args.headless
    TRAINING_SETTINGS["max_score"] = args.max_score

    if args.load_checkpoint:
        populacao = neat.Checkpointer.restore_checkpoint(args.load_checkpoint)
        config = populacao.config
        _validar_config(config)
        print(f"Checkpoint carregado: {args.load_checkpoint}")
    else:
        config_path = Path(args.config)
        if not config_path.exists():
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
        config = _carregar_config(config_path)
        populacao = neat.Population(config)
    populacao.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    populacao.add_reporter(stats)
    if args.checkpoint_every > 0:
        checkpoint_dir = Path(args.checkpoint_dir)
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        prefix = str(checkpoint_dir / "neat-checkpoint-")
        populacao.add_reporter(
            neat.Checkpointer(args.checkpoint_every, filename_prefix=prefix)
        )

    print("=" * 60)
    print("Treinamento Mario NEAT")
    print("=" * 60)
    print(f"Sensores: {SENSOR_COUNT}\tAções: {ACTION_COUNT}")
    print(f"Distância alvo: {DISTANCIA_PARA_VENCER} px")
    print(f"Renderização: {'Sim' if TRAINING_SETTINGS['render'] else 'Não'}")
    print("Iniciando...\n")

    vencedor = populacao.run(eval_genomes, args.generations)

    if not args.no_save_best and args.best_path:
        with open(args.best_path, "wb") as arquivo:
            pickle.dump(vencedor, arquivo)
        print(f"Melhor genoma salvo em: {args.best_path}")

    print("\n=== Treinamento concluído ===")
    print(f"Melhor Fitness: {vencedor.fitness:.2f}")
    print(f"Nós: {len(vencedor.nodes)} | Conexões: {len(vencedor.connections)}")


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    run_training(args)


if __name__ == "__main__":
    main()
