# 🎮 Super Mario Runner - Jogo com IA (NEAT)

Um jogo estilo "Dino do Chrome" com temática completa do Mario, onde você pode jogar manualmente OU treinar uma IA usando NEAT (NeuroEvolution of Augmenting Topologies).

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)
![NEAT](https://img.shields.io/badge/NEAT--Python-0.92+-orange.svg)

## 🌟 Características

### 🎨 Visual Aprimorado
- **Mario detalhado**: Chapéu vermelho com logo "M", bigode, olhos, camisa vermelha com botões
- **Canos verdes**: Com borda superior e detalhes internos
- **Goombas**: Cogumelos marrons com olhos raivosos e animação
- **Koopa Troopas**: Tartarugas verdes com casco detalhado e animação de caminhada
- **Bob-ombs**: Bombas voadoras que cruzam o céu em linha reta com rastro e propulsão
- **Cenário**: Céu azul, nuvens, montanhas, chão com grama

### 🎮 Jogabilidade
- **Modo Manual**: Controle total do Mario (movimento + pulo)
- **Modo IA**: Assista dezenas de agentes evoluindo automaticamente (população padrão 70)
- **4 Tipos de Obstáculos**:
  - Canos (3 alturas diferentes)
  - Goombas (cogumelos no chão)
  - Tartarugas (Koopas no chão)
  - Bombas (voando em alturas variadas)
- **Sistema de Pontuação**: Pontos por distância e por ultrapassar obstáculos
- **Objetivo**: Percorrer 15.000 pixels para vencer!
- **Dificuldade Progressiva**: Velocidade aumenta gradualmente

### 🧠 Inteligência Artificial NEAT

#### 6 Sensores:
1. **Distância ao próximo obstáculo no chão** (normalizada)
2. **Altura/Tipo do obstáculo no chão** (baixo/médio/alto)
3. **Distância ao próximo obstáculo no ar** (bomba)
4. **Existe bomba no ar?** (booleano)
5. **Velocidade atual do jogo** (normalizada)
6. **Posição Y do Mario** (altura do pulo)

#### Configuração NEAT:
- População padrão: 70 agentes por geração (ajuste em `config-feedforward.txt`)
- Gerações recomendadas: 80+ ou até atingir o `fitness_threshold` (3200)
- Fitness: Distância + velocidade + bônus situacionais (pulos e agachamentos corretos) + vitória
- Topologia: Rede neural feedforward com ativações `tanh/sigmoid/relu` evoluindo dinamicamente
- Checkpoints: use `--checkpoint-every` para salvar/retomar sessões longas

## 📁 Estrutura do Projeto

```
JogoMario/
├── game/
│   ├── __init__.py
│   ├── mario.py          # Classe do personagem Mario
│   ├── obstacles.py      # Classes dos obstáculos
│   └── game.py           # Lógica principal do jogo
├── utils/
│   ├── __init__.py
│   └── constants.py      # Constantes e configurações
├── main.py               # 🎮 Jogo manual (execute este!)
├── neat_train.py         # 🤖 Treinamento IA
├── config-feedforward.txt # Configuração NEAT
└── README.md
```

## 🚀 Instalação e Execução

### 1️⃣ Clonar o Repositório

```bash
git clone https://github.com/jdsricardo/JogoMario.git
cd JogoMario
```

### 2️⃣ Criar Ambiente Virtual

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Instalar Dependências

```bash
pip install pygame neat-python
```

### 4️⃣ Executar o Jogo

**Modo Manual (Jogar você mesmo):**
```bash
python main.py
```

**Modo IA (Treinar NEAT):**
```bash
python app.py --generations 80 --headless --checkpoint-every 5
```

> Dica: `neat_train.py` continua disponível como atalho, mas agora o `app.py` expõe todos os parâmetros via CLI.

### ⚙️ CLI do Treinamento NEAT

| Opção | Descrição |
|-------|-----------|
| `--generations N` | Define quantas gerações serão executadas (padrão 50) |
| `--headless` | Oculta a janela do Pygame para acelerar o treinamento |
| `--config caminho` | Usa um arquivo `config-feedforward` customizado |
| `--max-score valor` | Limita a pontuação de cada rodada para evitar loops |
| `--best-path arquivo.pkl` | Caminho para salvar o melhor genoma evoluído |
| `--checkpoint-every N` | Salva checkpoints do NEAT a cada N gerações |
| `--checkpoint-dir pasta` | Diretório onde os checkpoints são gravados |
| `--load-checkpoint arquivo` | Retoma o treinamento a partir de um checkpoint existente |
| `--no-save-best` | Pula o salvamento automático do melhor genoma |

## 🎯 Controles (Modo Manual)

| Tecla | Ação |
|-------|------|
| **ESPAÇO** ou **↑** | Pular |
| **←** ou **A** | Mover para esquerda |
| **→** ou **D** | Mover para direita |
| **P** | Pausar jogo |
| **R** | Reiniciar |
| **ESC** | Sair |

## 🏆 Como Jogar

1. **Objetivo**: Percorra 15.000 pixels sem colidir
2. **Obstáculos**:
   - **Canos**: Altos no chão - pule sobre eles
   - **Goombas**: Cogumelos pequenos - pule
   - **Tartarugas**: Médias - pule no momento certo
   - **Bombas**: Voam no ar - NÃO pule quando elas vierem!
3. **Estratégia**: 
   - Pule para desviar de obstáculos no chão
   - Fique no chão para desviar de bombas no ar
   - Use movimento horizontal para melhor posicionamento
4. **Vitória**: Barra de progresso no topo direito

## 🤖 Treinamento da IA

### Como Funciona:

1. **Geração 1**: 70 Marios com redes neurais aleatórias
2. **Avaliação**: Todos correm simultaneamente; quem colide é removido
3. **Fitness**: Distância + velocidade + bônus por ações corretas (pulo/abaixar) + vitória
4. **Seleção**: NEAT preserva as melhores espécies e aplica mutações controladas
5. **Mutação/Cruzamento**: Novas conexões/neurônios surgem, pesos são ajustados
6. **Repetir**: Até alcançar o `fitness_threshold` ou o número de gerações definido

### Evolução da Rede:

- Adiciona/remove conexões sinápticas
- Adiciona/remove neurônios ocultos
- Ajusta pesos e bias
- Estrutura da rede evolui automaticamente

### Acompanhar Progresso:

- **Terminal**: Fitness máximo/médio por geração
- **Tela**: Geração atual e agentes vivos
- **Genoma salvo**: `melhor_genoma.pkl` (desativável com `--no-save-best`)
- **Checkpoints**: `checkpoints/neat-checkpoint-*` permitem pausar e retomar sessões longas

## ⚙️ Personalização

### Ajustar Dificuldade

Edite `utils/constants.py`:

```python
VELOCIDADE_INICIAL = 6      # Velocidade inicial (padrão: 6)
VELOCIDADE_MAXIMA = 14      # Velocidade máxima (padrão: 14)
DISTANCIA_PARA_VENCER = 15000  # Distância para vencer (padrão: 15000)
```

### Ajustar Probabilidade de Obstáculos

Em `utils/constants.py`:

```python
CHANCE_BOMBA = 0.3       # 30% bombas (padrão)
CHANCE_TARTARUGA = 0.4   # 40% tartarugas (padrão)
# Restante: Canos e Goombas
```

### Ajustar População NEAT

Em `config-feedforward.txt`:

```ini
pop_size = 70  # Número de agentes (padrão atual)
```

No CLI, altere o número de gerações sem editar código:

```bash
python app.py --generations 150 --headless
```

## 📊 Comparação Modo Manual vs IA

| Aspecto | Manual | IA (NEAT) |
|---------|--------|-----------|
| Controle | Teclado (4 direções + pulo) | Rede neural (apenas pulo) |
| Aprendizado | Humano | Evolutivo |
| Velocidade | Tempo real | Tempo real |
| Objetivo | Vencer 1 vez | Evoluir por gerações |
| Diversão | Alta 🎮 | Observar evolução 🧠 |

## 🐛 Solução de Problemas

### Erro: "No module named 'pygame'"
```bash
pip install pygame
```

### Erro: "No module named 'neat'"
```bash
pip install neat-python
```

### Jogo muito rápido/lento
Ajuste `FPS` em `utils/constants.py` (padrão: 60)

### IA não aprende
- Aumente o número de gerações
- Ajuste `pop_size` para 100+
- Reduza a dificuldade inicial

## 🎓 Conceitos Aprendidos

- **Pygame**: Gráficos 2D, física, colisões
- **NEAT**: Algoritmos genéticos, redes neurais evolutivas
- **POO**: Classes, herança, encapsulamento
- **Arquitetura**: Separação em módulos
- **Game Design**: Balanceamento, progressão, feedback visual

## 📈 Melhorias Futuras

- [ ] Sprites reais (imagens PNG)
- [ ] Sistema de som e música
- [ ] Múltiplos níveis/mundos
- [ ] Power-ups (cogumelo, estrela)
- [ ] Leaderboard online
- [ ] Modo replay do melhor genoma
- [ ] Salvar/carregar progresso

## 👨‍💻 Tecnologias

- **Python 3.8+**
- **Pygame 2.0+**: Engine gráfica
- **NEAT-Python 0.92+**: Framework de neuroevolução

## 📝 Licença

Este projeto é livre para uso educacional e pessoal.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir features
- Melhorar gráficos
- Otimizar código

---

**Desenvolvido com ❤️ para aprender IA e Game Development**

🎮 **Divirta-se jogando e vendo a IA aprender!** 🤖

