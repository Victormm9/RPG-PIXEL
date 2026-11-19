# Vale de Eldoria — mapa e arte

O mapa lógico é uma grade conectada de 96 × 72 tiles de 32 × 32 px. A camada de dados permite caminhar pela Vila de Eldoria, Floresta dos Sussurros, Campos do Norte, Rio, caminhos, ponte e entrada da Caverna Esquecida. A cripta da história continua como região separada.

## Sprites PNG necessários

As imagens a seguir ainda não existem. Quando adicionadas, marque `available: true` para o recurso correspondente em `assets/asset-manifest.js`; então serão carregadas e validadas pelo gerenciador em `assets/asset-manager.js`. O jogo não faz requisições para imagens marcadas como ausentes, evitando erros 404 no console. Não usa quadrados, formas ou a arte da tela de título para substituir esses recursos.

| Caminho | Dimensões | Conteúdo |
| --- | ---: | --- |
| `assets/tilesets/eldoria.png` | 256 × 128 px | Atlas de 8 × 4 tiles, cada célula 32 × 32 px; índice e ordem definidos abaixo. |
| `assets/tilesets/props.png` | 256 × 128 px | Atlas de 8 × 4 props 32 × 32; placas, ervas, baús e portais. Índices 0 placa, 1 erva, 2 baú, 3 portal selado, 4 portal aberto, 5 saída da cripta. |
| `assets/characters/player.png` | 448 × 256 px | Sprite 64 × 64; 7 colunas × 4 direções. |
| `assets/characters/npcs.png` | 448 × 256 px | NPCs 64 × 64; linhas norte, sul, oeste e leste, 7 colunas. |
| `assets/enemies/slime.png` | 448 × 256 px | Slime 64 × 64; 4 direções, quadros idle, caminhada e ataque. |
| `assets/enemies/goblin.png` | 448 × 256 px | Goblin 64 × 64; 4 direções, quadros idle, caminhada e ataque. |
| `assets/enemies/wolf.png` | 448 × 256 px | Lobo 64 × 64; 4 direções, quadros idle, caminhada e ataque. |
| `assets/enemies/skeleton.png` | 448 × 256 px | Esqueleto 64 × 64; 4 direções, quadros idle, caminhada e ataque. |
| `assets/enemies/bandit.png` | 448 × 256 px | Saqueador 64 × 64; 4 direções, quadros idle, caminhada e ataque. |
| `assets/enemies/boss.png` | 448 × 256 px | Cavaleiro da cripta 64 × 64; 4 direções, quadros idle, caminhada e ataque. |
| `assets/effects/combat.png` | 384 × 64 px | Seis quadros de efeito de impacto, 64 × 64 px cada, sequência horizontal. |

O atlas deve ter células nesta ordem, da esquerda para a direita e de cima para baixo:

```text
0 grama          1 grama variante  2 grama com flores  3 relva alta
4 terra          5 caminho         6 borda do caminho  7 margem
8 água           9 margem d'água    10 ponte horizontal 11 ponte vertical
12 árvore        13 pinheiro       14 rocha            15 cerca horizontal
16 cerca vertical 17 canto de cerca 18 portão          19 piso de pedra
20 parede        21 telhado        22 porta            23 entrada da caverna
24 arbusto       25 plantação      26 píer             27 piso rachado
28 entulho       29 piso de caverna 30 parede musgosa  31 pilar de caverna
```

Nos sprites de ator, cada linha representa uma direção — sul/frente, norte/costas, oeste/esquerda, leste/direita. As colunas são:

```text
0 parado, 1–3 caminhada (ciclo), 4–6 ataque (ciclo)
```

Cada camada deve usar transparência PNG, a mesma grade de quadros e o mesmo ponto de apoio nos pés. Não redimensione cada eixo de forma diferente.

