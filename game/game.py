"""
Módulo principal do jogo Mario
"""
import pygame
import random
import sys
from game.mario import Mario
from game.obstacles import criar_bomba, gerar_obstaculo
from utils.constants import *


class JogoMario:
    def __init__(self, modo='manual', render=True):
        """
        Inicializa o jogo
        modo: 'manual' para jogar manualmente, 'ia' para treinamento NEAT
        """
        pygame.init()
        self.render = render
        if self.render:
            self.tela = pygame.display.set_mode((LARGURA, ALTURA))
            pygame.display.set_caption("Super Mario Runner")
        else:
            self.tela = pygame.Surface((LARGURA, ALTURA))
        self.relogio = pygame.time.Clock()
        self.fonte_grande = pygame.font.Font(None, 48)
        self.fonte_media = pygame.font.Font(None, 36)
        self.fonte_pequena = pygame.font.Font(None, 24)
        self.modo = modo
        self.resetar()
    
    def resetar(self):
        """Reseta o jogo para o início"""
        self.mario = Mario(100, CHAO_Y)
        self.marios = [self.mario] if self.modo == 'manual' else []
        self.obstaculos = []
        self.pontuacao = 0
        self.distancia_percorrida = 0
        self.velocidade = VELOCIDADE_INICIAL
        self.ultimo_obstaculo_x = LARGURA
        self.ultimo_bomba_x = LARGURA
        self.frames_desde_obstaculo_chao = 999
        self.jogo_ativo = True
        self.vitoria = False
        self.pausado = False
        self.geracao = 1
        self.vivos = 1
        
    def adicionar_mario(self, mario):
        """Adiciona um Mario (usado no modo IA)"""
        self.marios.append(mario)
    
    def gerar_obstaculo(self):
        """Gera novos obstáculos"""
        if self.ultimo_obstaculo_x < LARGURA - random.randint(
            DISTANCIA_MIN_OBSTACULOS, DISTANCIA_MAX_OBSTACULOS):
            obstaculo = gerar_obstaculo(LARGURA, self.velocidade)
            self.obstaculos.append(obstaculo)
            self.ultimo_obstaculo_x = LARGURA
            if obstaculo.tipo in {'cano', 'goomba', 'tartaruga'}:
                self.frames_desde_obstaculo_chao = 0

        bomba_intervalo = random.randint(320, 520)
        if (
            self.frames_desde_obstaculo_chao > 45
            and self.ultimo_bomba_x < LARGURA - bomba_intervalo
            and not self._tem_obstaculo_chao_proximo(260)
            and random.random() < CHANCE_BOMBA
        ):
            altura_mode = 'alto' if random.random() < 0.4 else 'baixo'
            if altura_mode == 'alto' and self.frames_desde_obstaculo_chao < 90:
                altura_mode = 'baixo'

            bomba_x = LARGURA + 20
            if self._conflito_com_obstaculo_chao(bomba_x, altura_mode):
                return

            bomba = criar_bomba(bomba_x, self.velocidade, altura_mode=altura_mode)
            self.obstaculos.append(bomba)
            self.ultimo_bomba_x = LARGURA

    def _tem_obstaculo_chao_proximo(self, distancia_limite=220):
        """Retorna True se existir obstáculo terrestre perto da borda direita."""
        for obs in self.obstaculos:
            if obs.tipo in {'cano', 'goomba', 'tartaruga'}:
                if LARGURA - obs.x < distancia_limite:
                    return True
        return False

    def _conflito_com_obstaculo_chao(self, bomba_x, altura_mode):
        """Evita bombas no mesmo alinhamento horizontal que obstáculos terrestres."""
        separacao = 320 if altura_mode == 'alto' else 260
        for obs in self.obstaculos:
            if obs.tipo in {'cano', 'goomba', 'tartaruga'}:
                centro_obs = obs.x + obs.largura / 2
                if abs(centro_obs - bomba_x) < separacao:
                    return True
        return False
    
    def atualizar(self):
        """Atualiza o estado do jogo"""
        if not self.jogo_ativo or self.pausado:
            return
        
        # Atualizar obstáculos
        for obstaculo in self.obstaculos:
            obstaculo.atualizar()
        
        # Remover obstáculos fora da tela e contar pontos
        for obstaculo in self.obstaculos[:]:
            if obstaculo.fora_da_tela():
                self.obstaculos.remove(obstaculo)
            elif not obstaculo.passou and obstaculo.x + obstaculo.largura < self.mario.x:
                obstaculo.passou = True
                self.pontuacao += PONTOS_INIMIGO
        
        # Gerar novos obstáculos
        self.gerar_obstaculo()
        self.ultimo_obstaculo_x -= self.velocidade
        self.ultimo_bomba_x -= self.velocidade
        self.frames_desde_obstaculo_chao += 1
        
        # Aumentar velocidade gradualmente
        if self.velocidade < VELOCIDADE_MAXIMA:
            self.velocidade += ACELERACAO
            for obs in self.obstaculos:
                obs.velocidade = self.velocidade
        
        # Aumentar distância e pontuação
        self.distancia_percorrida += self.velocidade
        self.pontuacao += PONTOS_POR_FRAME
        
        # Verificar vitória
        if self.distancia_percorrida >= DISTANCIA_PARA_VENCER:
            self.vitoria = True
            self.jogo_ativo = False
    
    def verificar_colisao(self, mario):
        """Verifica colisão do Mario com obstáculos"""
        if not mario.vivo:
            return False
            
        mario_rect = mario.get_rect()
        for obstaculo in self.obstaculos:
            if mario_rect.colliderect(obstaculo.get_rect()):
                return True
        return False
    
    def processar_eventos(self):
        """Processa eventos do pygame"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return False
                
                if self.modo == 'manual':
                    if evento.key == pygame.K_SPACE or evento.key == pygame.K_UP:
                        if self.jogo_ativo:
                            self.mario.pular()
                        elif not self.vitoria:  # Reiniciar se perdeu
                            self.resetar()
                    
                    if evento.key == pygame.K_p:
                        self.pausado = not self.pausado
                    
                    if evento.key == pygame.K_r:
                        self.resetar()
        
        # Controles contínuos (segurar tecla)
        if self.modo == 'manual' and self.jogo_ativo:
            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
                self.mario.mover_esquerda()
            elif teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
                self.mario.mover_direita()
            else:
                self.mario.parar()
        
        return True
    
    def atualizar_mario(self, mario=None):
        """Atualiza um Mario específico"""
        if mario is None:
            mario = self.mario
        
        mario.atualizar()
        
        if self.verificar_colisao(mario):
            mario.morrer()
            if self.modo == 'manual':
                self.jogo_ativo = False
    
    def desenhar_fundo(self):
        """Desenha o fundo do jogo"""
        # Ceu azul de fundo
        self.tela.fill(CEU_AZUL)
        
        # Nuvens simples
        for i in range(3):
            x = (self.distancia_percorrida // 3 + i * 400) % LARGURA
            y = 80 + i * 60
            pygame.draw.ellipse(self.tela, BRANCO, (x, y, 80, 40))
            pygame.draw.ellipse(self.tela, BRANCO, (x + 30, y - 10, 60, 40))
            pygame.draw.ellipse(self.tela, BRANCO, (x + 50, y, 70, 35))
        
        # Montanhas ao fundo
        for i in range(4):
            x = (self.distancia_percorrida // 5 + i * 350) % (LARGURA + 200) - 100
            pygame.draw.polygon(self.tela, (100, 150, 100), [
                (x, CHAO_Y + 40),
                (x + 150, CHAO_Y - 100),
                (x + 300, CHAO_Y + 40)
            ])
        
        # Chão
        pygame.draw.rect(self.tela, VERDE_ESCURO, 
                        (0, CHAO_Y + 40, LARGURA, ALTURA - CHAO_Y - 40))
        
        # Linha do chão
        pygame.draw.line(self.tela, PRETO, (0, CHAO_Y + 40), 
                        (LARGURA, CHAO_Y + 40), 3)
        
        # Detalhes do chão (grama)
        for i in range(0, LARGURA, 50):
            x = (i + int(self.distancia_percorrida) % 50)
            # Tufos de grama
            for j in range(3):
                offset_x = x + j * 8
                pygame.draw.line(self.tela, (0, 180, 0), 
                               (offset_x, CHAO_Y + 40), 
                               (offset_x + 2, CHAO_Y + 35), 2)
    
    def desenhar_hud(self):
        """Desenha a interface do usuário"""
        # Pontuação
        texto_pontos = self.fonte_media.render(
            f'Pontos: {self.pontuacao}', True, PRETO)
        self.tela.blit(texto_pontos, (10, 10))
        
        # Barra de progresso
        progresso = min(self.distancia_percorrida / DISTANCIA_PARA_VENCER, 1.0)
        largura_barra = 300
        pygame.draw.rect(self.tela, CINZA, (LARGURA - largura_barra - 20, 15, largura_barra, 25))
        pygame.draw.rect(self.tela, VERDE, 
                        (LARGURA - largura_barra - 20, 15, 
                         int(largura_barra * progresso), 25))
        pygame.draw.rect(self.tela, PRETO, 
                        (LARGURA - largura_barra - 20, 15, largura_barra, 25), 2)
        
        # Texto do progresso
        texto_prog = self.fonte_pequena.render(
            f'{int(progresso * 100)}%', True, BRANCO)
        self.tela.blit(texto_prog, (LARGURA - largura_barra // 2 - 30, 18))
        
        # Velocidade
        texto_vel = self.fonte_pequena.render(
            f'Velocidade: {self.velocidade:.1f}', True, PRETO)
        self.tela.blit(texto_vel, (10, 50))
        
        # Distância
        texto_dist = self.fonte_pequena.render(
            f'Distância: {int(self.distancia_percorrida)}/{DISTANCIA_PARA_VENCER}', 
            True, PRETO)
        self.tela.blit(texto_dist, (10, 75))
        
        # Modo IA - informações adicionais
        if self.modo == 'ia':
            texto_gen = self.fonte_pequena.render(
                f'Geração: {self.geracao}', True, PRETO)
            self.tela.blit(texto_gen, (10, 100))
            
            texto_vivos = self.fonte_pequena.render(
                f'Vivos: {self.vivos}', True, PRETO)
            self.tela.blit(texto_vivos, (10, 125))
    
    def desenhar_tela_final(self):
        """Desenha tela de vitória ou derrota"""
        # Overlay semi-transparente
        overlay = pygame.Surface((LARGURA, ALTURA))
        overlay.set_alpha(200)
        overlay.fill(PRETO if not self.vitoria else (0, 100, 0))
        self.tela.blit(overlay, (0, 0))
        
        if self.vitoria:
            # Tela de vitória
            texto_titulo = self.fonte_grande.render(
                'VOCÊ VENCEU!', True, AMARELO)
            texto_pontos = self.fonte_media.render(
                f'Pontuação Final: {self.pontuacao}', True, BRANCO)
            texto_reiniciar = self.fonte_pequena.render(
                'Pressione R para jogar novamente', True, BRANCO)
        else:
            # Tela de derrota
            texto_titulo = self.fonte_grande.render(
                'GAME OVER', True, VERMELHO)
            texto_pontos = self.fonte_media.render(
                f'Pontuação: {self.pontuacao}', True, BRANCO)
            texto_reiniciar = self.fonte_pequena.render(
                'Pressione ESPAÇO para tentar novamente', True, BRANCO)
        
        texto_sair = self.fonte_pequena.render(
            'ESC para sair', True, BRANCO)
        
        # Centralizar textos
        self.tela.blit(texto_titulo, 
                      (LARGURA // 2 - texto_titulo.get_width() // 2, 
                       ALTURA // 2 - 100))
        self.tela.blit(texto_pontos, 
                      (LARGURA // 2 - texto_pontos.get_width() // 2, 
                       ALTURA // 2 - 20))
        self.tela.blit(texto_reiniciar, 
                      (LARGURA // 2 - texto_reiniciar.get_width() // 2, 
                       ALTURA // 2 + 40))
        self.tela.blit(texto_sair, 
                      (LARGURA // 2 - texto_sair.get_width() // 2, 
                       ALTURA // 2 + 80))
    
    def desenhar(self):
        """Desenha todos os elementos do jogo"""
        # Fundo
        self.desenhar_fundo()
        
        # Obstáculos
        for obstaculo in self.obstaculos:
            obstaculo.desenhar(self.tela)
        
        # Mario(s)
        for mario in self.marios:
            mario.desenhar(self.tela)
        
        # HUD
        self.desenhar_hud()
        
        # Tela de pausa
        if self.pausado:
            overlay = pygame.Surface((LARGURA, ALTURA))
            overlay.set_alpha(150)
            overlay.fill(PRETO)
            self.tela.blit(overlay, (0, 0))
            
            texto_pausa = self.fonte_grande.render('PAUSADO', True, BRANCO)
            self.tela.blit(texto_pausa, 
                          (LARGURA // 2 - texto_pausa.get_width() // 2, 
                           ALTURA // 2 - 30))
        
        # Tela final
        if not self.jogo_ativo and self.modo == 'manual':
            self.desenhar_tela_final()
        
        if self.render:
            pygame.display.flip()
    
    def executar(self):
        """Loop principal do jogo (modo manual)"""
        rodando = True
        
        while rodando:
            self.relogio.tick(FPS)
            
            # Processar eventos
            rodando = self.processar_eventos()
            
            # Atualizar
            if self.jogo_ativo and not self.pausado:
                self.atualizar()
                self.atualizar_mario()
            
            # Desenhar
            self.desenhar()
        
        pygame.quit()
        sys.exit()
