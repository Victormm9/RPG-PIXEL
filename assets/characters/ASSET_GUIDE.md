# Guia de sprites de personagens

Os sprites individuais ainda não foram fornecidos. O aplicativo carrega somente PNGs de camadas; não recorta nem usa a prancha de referência como sprite. Enquanto os arquivos não existirem, a tela mostra os caminhos ausentes e não desenha um personagem improvisado.

## Formato obrigatório

- PNG com canal alpha quando a camada tiver áreas transparentes.
- Cada quadro mede exatamente **64 × 64 px**.
- Cada spritesheet tem 4 linhas nesta ordem: sul/frente, norte/costas, oeste/esquerda, leste/direita.
- Os quadros de animação ficam em colunas. Uma sheet com 4 quadros por direção mede 256 × 256 px.
- Todas as camadas usadas juntas precisam ter o mesmo número de quadros e o mesmo ponto de origem. Desenhe cada peça na mesma grade 64 × 64, sem deslocar o personagem entre arquivos.
- A composição mantém transparência e amplia a prévia por escala inteira sem suavização.

## Arquivos esperados

O catálogo completo e editável está em `data/character_catalog.json`. Para a seleção inicial do Guerreiro, faltam:

```text
assets/characters/base/boy_light.png
assets/characters/faces/face_light.png
assets/characters/faces/eyes_brown.png
assets/characters/hair/short_brown.png
assets/characters/clothes/shirts/crimson.png
assets/characters/armor/chainmail.png
assets/characters/clothes/pants/charcoal.png
assets/characters/clothes/boots/leather.png
assets/characters/weapons/steel_sword.png
assets/characters/accessories/iron_shield.png
```

Os caminhos variáveis são:

- Corpos: `characters/base/{boy|girl}_{light|warm|deep}.png`.
- Rostos: `characters/faces/face_{light|warm|deep}.png`.
- Olhos: `characters/faces/eyes_{brown|blue|green|gray}.png`.
- Cabelos: `characters/hair/{short|long|curly|messy|braided}_{black|brown|blonde|red|silver}.png`.
- Roupas, armaduras, calças, botas, capas, armas e acessórios: use os caminhos dos itens correspondentes em `data/character_catalog.json`. Itens “sem capa/armadura/acessório” não precisam de PNG.

## Adicionar equipamento

1. Coloque o PNG alinhado em uma pasta de `assets/characters/`, seguindo as dimensões e direções acima.
2. Adicione um item com `id`, `name` e caminho relativo a `assets/` na categoria correspondente de `data/character_catalog.json`.
3. Para definir o item como equipamento inicial de uma classe, atualize o campo correspondente em `data/classes.json`.
4. Execute os testes e abra o criador. O catálogo apresenta a miniatura assim que o PNG válido estiver no caminho configurado.

