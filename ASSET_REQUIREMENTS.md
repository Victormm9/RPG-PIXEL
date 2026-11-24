# Requisitos de imagens PNG

Este inventário foi conferido contra `assets/asset-manifest.js`,
`assets/asset-manager.js` e os usos de imagens em `index.html`. Inclui os PNGs
do manifesto e a imagem da tela de título, que é referenciada diretamente pelo
HTML/CSS e não passa pelo gerenciador.

## Sprites e atlases do manifesto

As dimensões são as validadas pelo gerenciador. Para os sprites de atores, cada
quadro mede 64 × 64 px; para os atlases de tiles e objetos, cada célula mede
32 × 32 px.

| Arquivo | Caminho no projeto | Dimensões | Quadros e direções | Animações/quadros usados | Elemento do jogo |
| --- | --- | ---: | --- | --- | --- |
| `eldoria.png` | `assets/tilesets/eldoria.png` | 256 × 128 px | Atlas 8 × 4: 32 tiles de 32 × 32 px; sem direções | Tiles estáticos, selecionados pelos índices 0–31; sem animação | Terreno, água, caminhos, ponte, vegetação, construções e pisos da região/caverna |
| `props.png` | `assets/tilesets/props.png` | 256 × 128 px | Atlas 8 × 4: 32 células de 32 × 32 px; sem direções | Células usadas: 0 placa, 1 erva, 2 baú, 3 portal fechado, 4 portal aberto, 5 saída; sem animação | Objetos interativos e portais |
| `player.png` | `assets/characters/player.png` | 448 × 256 px | 28 células: 7 colunas × 4 linhas de 64 × 64 px | O jogador masculino usa as linhas 0–1; a linha 1 é espelhada para os lados. As linhas 2–3 da arte atual estão danificadas. A personagem feminina é gerada pelo código em uma sheet direcional 448 × 256 | Personagem controlado pelo jogador |
| `npcs.png` | `assets/characters/npcs.png` | 448 × 256 px | 28 células: 7 colunas × 4 direções (sul, norte, oeste, leste), 64 × 64 px | O código desenha apenas a coluna 0 (parado). As colunas 1–6 não são animadas para NPCs atualmente | NPCs do mundo |
| `slime.png` | `assets/enemies/slime.png` | 448 × 256 px | 28 quadros: 7 colunas × 4 linhas de 64 × 64 px. A arte-fonte tem frente e lateral, não quatro direções distintas | Parado (0), caminhada (1–3) e ataque (4–6) | Slimes |
| `goblin.png` | `assets/enemies/goblin.png` | 448 × 256 px | 28 quadros: 7 colunas × 4 linhas de 64 × 64 px. A arte-fonte tem frente e lateral, não quatro direções distintas | Parado (0), caminhada (1–3) e ataque (4–6) | Goblins |
| `wolf.png` | `assets/enemies/wolf.png` | 448 × 256 px | 28 quadros: 7 colunas × 4 linhas de 64 × 64 px. A arte-fonte tem frente e lateral, não quatro direções distintas | Parado (0), caminhada (1–3) e ataque (4–6) | Lobos selvagens |
| `skeleton.png` | `assets/enemies/skeleton.png` | 448 × 256 px | 28 quadros: 7 colunas × 4 linhas de 64 × 64 px. A arte-fonte tem frente e lateral, não quatro direções distintas | Parado (0), caminhada (1–3) e ataque (4–6) | Esqueletos da região e da cripta |
| `bandit.png` | `assets/enemies/bandit.png` | 448 × 256 px | 28 quadros: 7 colunas × 4 linhas de 64 × 64 px. A arte-fonte tem frente e lateral, não quatro direções distintas | Parado (0), caminhada (1–3) e ataque (4–6) | Saqueador definido no catálogo de inimigos. Não há spawn desse tipo nas regiões atuais |
| `boss.png` | `assets/enemies/boss.png` | 448 × 256 px | 28 células de 64 × 64 px; a arte-fonte contém uma pose repetida | Sem animação direcional disponível | Cavaleiro sem Rosto, chefe da cripta |
| `combat.png` | `assets/effects/combat.png` | 384 × 64 px | 6 quadros de 64 × 64 px, em uma linha; sem direções | Sequência horizontal de impacto, quadros 0–5 | Efeito visual ao acertar um ataque |

### Quadros e direções dos atores

O jogador feminino gerado pelo código usa uma linha por direção, nesta ordem:

1. Sul/frente (`down`, linha 0).
2. Norte/costas (`up`, linha 1).
3. Oeste/esquerda (`left`, linha 2).
4. Leste/direita (`right`, linha 3).

As colunas do jogador são: `0` parado, `1–3` caminhada e `4–6` ataque. O sprite
masculino existente não tem linhas laterais válidas: usa a frente e as costas
para cima/baixo e espelha a linha de costas para os lados. Para inimigos, a
folha tem apenas poses frontais e laterais: a lateral é usada para
esquerda/direita, com espelhamento para a esquerda; frente é usada para cima e
baixo. Para NPCs, somente o quadro parado (coluna 0) é desenhado.

### Índices do atlas de tiles

O tile de cada célula do mapa é convertido em linha/coluna usando uma grade de
8 colunas. Portanto, preserve esta ordem de 0 a 31 no arquivo
`assets/tilesets/eldoria.png`:

| Índices | Conteúdo |
| --- | --- |
| 0–3 | Grama, grama variante, grama com flores, relva alta |
| 4–7 | Terra, caminho, borda do caminho, margem |
| 8–11 | Água, margem d'água, ponte horizontal, ponte vertical |
| 12–15 | Árvore, pinheiro, rocha, cerca horizontal |
| 16–19 | Cerca vertical, canto de cerca, portão, piso de pedra |
| 20–23 | Parede, telhado, porta, entrada da caverna |
| 24–27 | Arbusto, plantação, píer, piso rachado |
| 28–31 | Entulho, piso de caverna, parede musgosa, pilar de caverna |

## Imagem da tela de título

Este arquivo não está no manifesto: `index.html` o carrega diretamente como
imagem e fundo da tela inicial. Ele já existe no projeto.

| Arquivo | Caminho no projeto | Dimensões atuais | Quadros/direções/animações | Elemento do jogo |
| --- | --- | ---: | --- | --- |
| `title-screen.png` | `assets/title-screen.png` | 1365 × 768 px | Imagem única; sem direções ou animações | Fundo e ilustração da tela de título |

## Estado dos assets e limitações da imagem-fonte

Os 11 PNGs do manifesto estão nos caminhos e dimensões acima. As entradas
correspondentes estão marcadas como `available: true` em
`assets/asset-manifest.js`. A tela de título também já existia.

A prancha era uma composição, não spritesheets individuais no layout do jogo.
Para ajustá-la sem desenhar arte nova:

- O atlas de terreno de origem tinha 9 × 8 células; foi recortado e remapeado
  para 8 × 4, reutilizando algumas células.
- Os quadros de caminhada do jogador foram reutilizados para preencher os
  quadros de ataque que não existiam na prancha.
- A imagem de NPC usa um personagem repetido; o jogo atualmente desenha apenas
  o quadro parado.
- Nos sprites dos inimigos, a prancha não oferece quatro direções completas;
  agora a lateral é espelhada para não desenhar a mesma pose frontal ao andar
  para os dois lados.
- O painel do chefe tinha apenas uma pose; por isso o chefe continua sem
  animação direcional.
- O atlas de objetos usa o desenho de entrada/porta disponível na prancha para
  os quadros de portal, pois não havia portais separados.

Esses preenchimentos tornam os arquivos compatíveis com o carregador, mas não
acrescentam as poses/direções ausentes na arte-fonte. O gerenciador verifica
decodificação e dimensões, não a semântica dos quadros. Uma prancha futura com
spritesheets individuais pode substituir esses PNGs para corrigir as
animações. Os ícones da seção “Extras” da imagem não foram exportados porque
não são referenciados pelo manifesto nem pelo código atual.

O mapa lógico, a HUD e o minimapa são desenhados pelo código e não requerem
arquivos PNG adicionais.
