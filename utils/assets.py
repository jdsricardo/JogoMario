"""Carregamento e cache de sprites externos."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pygame

BASE_DIR = Path(__file__).resolve().parents[1]
SPRITES_DIR = BASE_DIR / "sprites"


@lru_cache(maxsize=None)
def load_sprite(filename: str, size: tuple[int, int] | None = None) -> pygame.Surface:
    """Carrega uma imagem PNG da raiz do projeto e aplica escala opcional."""

    caminho = BASE_DIR / filename
    if not caminho.exists():
        caminho = SPRITES_DIR / filename
    if not caminho.exists():
        raise FileNotFoundError(f"Sprite não encontrado: {caminho}")

    imagem = pygame.image.load(str(caminho))
    if pygame.display.get_surface():
        imagem = imagem.convert_alpha()
    if size is not None:
        imagem = pygame.transform.scale(imagem, size)
    return imagem
