"""Classe do personagem Mario."""

import pygame

from utils.assets import load_sprite
from utils.constants import *


class Mario:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.largura = MARIO_LARGURA
        self.altura = MARIO_ALTURA
        self.velocidade_y = 0
        self.velocidade_x = 0
        self.no_chao = True
        self.vivo = True
        self.pulando = False
        self.agachado = False
        self.sprite_padrao = load_sprite("mario.png", (self.largura, self.altura))
        self.sprite_agachado = pygame.transform.scale(
            self.sprite_padrao, (self.largura, MARIO_AGACHADO_ALTURA)
        )
        self.sprite_morto = pygame.transform.rotate(self.sprite_padrao, 90)
        self.sprite_morto = pygame.transform.scale(
            self.sprite_morto, (MARIO_ALTURA, MARIO_LARGURA)
        )
        
    def pular(self):
        """Faz o Mario pular se estiver no chão"""
        if self.no_chao and self.vivo:
            self.velocidade_y = FORCA_PULO
            self.no_chao = False
            self.pulando = True
            self.agachado = False

    def abaixar(self):
        """Coloca o Mario em estado agachado (usado para desviar de bombas)"""
        if self.no_chao and self.vivo:
            self.agachado = True

    def levantar(self):
        """Sai do estado agachado"""
        self.agachado = False

    def aplicar_comandos(self, pular=False, abaixar=False):
        """Executa ações vindas da IA"""
        if pular:
            self.pular()
        if abaixar:
            self.abaixar()
        else:
            self.levantar()
    
    def mover_direita(self):
        """Move Mario para direita"""
        self.velocidade_x = 5
    
    def mover_esquerda(self):
        """Move Mario para esquerda"""
        self.velocidade_x = -5
    
    def parar(self):
        """Para o movimento horizontal"""
        self.velocidade_x = 0
    
    def atualizar(self):
        """Atualiza física do Mario"""
        if not self.vivo:
            return
            
        # Aplicar gravidade
        self.velocidade_y += GRAVIDADE
        self.y += self.velocidade_y
        
        # Movimento horizontal
        self.x += self.velocidade_x
        
        # Limitar movimento horizontal na tela
        if self.x < 0:
            self.x = 0
        if self.x > LARGURA - self.largura:
            self.x = LARGURA - self.largura
        
        # Verificar colisão com o chão
        if self.y >= CHAO_Y:
            self.y = CHAO_Y
            self.velocidade_y = 0
            self.no_chao = True
            self.pulando = False
        else:
            # No ar não é possível continuar agachado
            self.agachado = False
    
    def morrer(self):
        """Mario morre"""
        self.vivo = False
        self.velocidade_y = -10  # Pequeno pulo ao morrer
    
    def desenhar(self, tela):
        if not self.vivo:
            tela.blit(self.sprite_morto, (self.x, self.y - 10))
            return

        if self.agachado:
            tela.blit(self.sprite_agachado, (self.x, self.y + MARIO_AGACHADO_OFFSET))
            return

        tela.blit(self.sprite_padrao, (self.x, self.y))
    def get_rect(self):
        """Retorna o retângulo de colisão do Mario"""
        altura = MARIO_AGACHADO_ALTURA if self.agachado else self.altura
        offset = MARIO_AGACHADO_OFFSET if self.agachado else 0
        return pygame.Rect(self.x + 4, self.y + offset, self.largura - 8, altura)
    
    def get_sensores(self, obstaculos, velocidade_jogo):
        """
        Retorna 6 sensores para a IA:
        1. Distância até o próximo obstáculo no chão
        2. Altura/Tipo do próximo obstáculo no chão (0=baixo, 0.5=médio, 1=alto)
        3. Distância até o próximo obstáculo no ar
        4. Existe bomba no ar? (0=não, 1=sim)
        5. Velocidade do jogo (normalizada)
        6. Posição Y do Mario (normalizada)
        """
        # Encontrar próximo obstáculo no chão
        obs_chao = None
        obs_ar = None
        
        for obs in obstaculos:
            if obs.x + obs.largura > self.x:
                if obs.tipo in ['cano', 'goomba', 'tartaruga']:
                    if obs_chao is None:
                        obs_chao = obs
                elif obs.tipo == 'bomba':
                    if obs_ar is None:
                        obs_ar = obs
        
        # Sensor 1: Distância até obstáculo no chão
        if obs_chao:
            dist_chao = (obs_chao.x - self.x) / LARGURA
            dist_chao = max(0, min(1, dist_chao))
            
            # Sensor 2: Altura do obstáculo no chão
            if obs_chao.tipo == 'cano':
                altura_norm = obs_chao.altura / CANO_ALTURA_MAX
            elif obs_chao.tipo == 'tartaruga':
                altura_norm = 0.3
            else:  # goomba
                altura_norm = 0.2
        else:
            dist_chao = 1.0
            altura_norm = 0.0
        
        # Sensor 3: Distância até obstáculo no ar
        if obs_ar:
            dist_ar = (obs_ar.x - self.x) / LARGURA
            dist_ar = max(0, min(1, dist_ar))
            tem_bomba = 1.0
        else:
            dist_ar = 1.0
            tem_bomba = 0.0
        
        # Sensor 5: Velocidade do jogo
        vel_norm = (velocidade_jogo - VELOCIDADE_INICIAL) / (VELOCIDADE_MAXIMA - VELOCIDADE_INICIAL)
        vel_norm = max(0, min(1, vel_norm))
        
        # Sensor 6: Posição Y
        y_norm = (CHAO_Y - self.y) / CHAO_Y
        y_norm = max(0, min(1, y_norm))
        
        return [dist_chao, altura_norm, dist_ar, tem_bomba, vel_norm, y_norm]
