"""
Classes de obstáculos do jogo Mario
"""
import math
import pygame
import random

from utils.assets import load_sprite
from utils.constants import *


class Obstaculo:
    """Classe base para todos os obstáculos"""
    def __init__(self, x, velocidade):
        self.x = x
        self.velocidade = velocidade
        self.passou = False
    
    def atualizar(self):
        """Move o obstáculo para a esquerda"""
        self.x -= self.velocidade
    
    def fora_da_tela(self):
        """Verifica se o obstáculo saiu da tela"""
        return self.x + self.largura < 0
    
    def get_rect(self):
        """Retorna o retângulo de colisão"""
        return pygame.Rect(self.x, self.y, self.largura, self.altura)


class Cano(Obstaculo):
    """Cano verde estilo Mario"""
    SPRITE_BASE = None

    def __init__(self, x, velocidade):
        super().__init__(x, velocidade)
        self.tipo = 'cano'
        self.largura = CANO_LARGURA
        self.altura = random.randint(CANO_ALTURA_MIN, CANO_ALTURA_MAX)
        self.y = CHAO_Y + 40 - self.altura
        if Cano.SPRITE_BASE is None:
            Cano.SPRITE_BASE = load_sprite("cano.png")
        self.sprite = pygame.transform.smoothscale(
            Cano.SPRITE_BASE, (self.largura, self.altura)
        )
    
    def desenhar(self, tela):
        tela.blit(self.sprite, (self.x, self.y))


class Goomba(Obstaculo):
    """Goomba - cogumelo inimigo marrom"""
    SPRITE = None

    def __init__(self, x, velocidade):
        super().__init__(x, velocidade)
        self.tipo = 'goomba'
        self.largura = GOOMBA_LARGURA
        self.altura = GOOMBA_ALTURA
        self.y = CHAO_Y + 40 - self.altura
        if Goomba.SPRITE is None:
            Goomba.SPRITE = load_sprite("Goomba.png", (self.largura, self.altura))
        self.sprite = Goomba.SPRITE
        self.osc_offset = random.randint(0, 20)
    
    def atualizar(self):
        super().atualizar()
    
    def desenhar(self, tela):
        deslocamento = 2 * math.sin((pygame.time.get_ticks() + self.osc_offset) / 200)
        tela.blit(self.sprite, (self.x, self.y + deslocamento))


class Tartaruga(Obstaculo):
    """Koopa Troopa - tartaruga verde"""
    SPRITE = None

    def __init__(self, x, velocidade):
        super().__init__(x, velocidade)
        self.tipo = 'tartaruga'
        self.largura = TARTARUGA_LARGURA
        self.altura = TARTARUGA_ALTURA
        self.y = CHAO_Y + 40 - self.altura
        if Tartaruga.SPRITE is None:
            Tartaruga.SPRITE = load_sprite("koopa.png", (self.largura, self.altura))
        self.sprite = Tartaruga.SPRITE
        self.osc_offset = random.randint(0, 300)
    
    def atualizar(self):
        super().atualizar()
    
    def desenhar(self, tela):
        deslocamento = 1.5 * math.sin((pygame.time.get_ticks() + self.osc_offset) / 250)
        tela.blit(self.sprite, (self.x, self.y + deslocamento))


class Bomba(Obstaculo):
    """Bomba Bob-omb que voa no ar"""
    SPRITE = None

    def __init__(self, x, velocidade, altura_mode: str = 'baixo'):
        super().__init__(x, velocidade)
        self.tipo = 'bomba'
        self.largura = BOMBA_LARGURA
        self.altura = BOMBA_ALTURA
        self.frame = 0
        self.trilha = []  # Pontos para rastro de fumaça
        if Bomba.SPRITE is None:
            Bomba.SPRITE = load_sprite("bomba.png", (self.largura, self.altura))
        self.sprite = Bomba.SPRITE
        self.altura_mode = altura_mode
        self._definir_altura(altura_mode)
        self.velocidade_extra = self._velocidade_por_altura(altura_mode)

    def _definir_altura(self, modo: str):
        if modo == 'alto':
            min_y = CHAO_Y - BOMBA_ALTURA - 160
            max_y = CHAO_Y - BOMBA_ALTURA - 105
        else:
            min_y = CHAO_Y - BOMBA_ALTURA - 50
            max_y = CHAO_Y - BOMBA_ALTURA - 28
        self.y = random.randint(min_y, max_y)

    def _velocidade_por_altura(self, modo: str) -> float:
        if modo == 'alto':
            return random.uniform(1.8, 3.8)
        return random.uniform(0.4, 1.5)
    
    def atualizar(self):
        deslocamento = self.velocidade + self.velocidade_extra
        self.x -= deslocamento
        self.frame += 1
        centro = (self.x + self.largura / 2, self.y + self.altura / 2)
        self.trilha.insert(0, centro)
        if len(self.trilha) > 6:
            self.trilha.pop()
    
    def desenhar(self, tela):
        for i, (tx, ty) in enumerate(self.trilha[1:], start=1):
            raio = max(1, (self.largura // 4) - i)
            pygame.draw.circle(tela, (80, 80, 80), (int(tx), int(ty)), raio)
        tela.blit(self.sprite, (self.x, self.y))


def gerar_obstaculo(x, velocidade):
    """Gera um obstáculo terrestre aleatório"""
    rand = random.random()

    if rand < CHANCE_TARTARUGA:
        return Tartaruga(x, velocidade)
    elif rand < CHANCE_TARTARUGA + 0.25:
        return Goomba(x, velocidade)
    else:
        return Cano(x, velocidade)


def criar_bomba(x, velocidade, altura_mode: str = 'baixo'):
    """Cria uma bomba aérea com modo de altura configurável."""
    return Bomba(x, velocidade, altura_mode=altura_mode)
