# RPG-PIXEL

O jogo web existente continua em `index.html`, `style.css` e `script.js`. A aplicação Python/Pygame é uma versão paralela para criação e personalização de personagens; ela não substitui nem altera o jogo web.

## RPG web

Sirva a pasta do projeto em HTTP (por exemplo, com a extensão Live Server do VS Code) e abra `index.html` no navegador. A área exterior agora usa um mapa contínuo de 96 × 72 tiles de 32 px e câmera, com Vila de Eldoria, Campos do Norte, Floresta dos Sussurros, rio, ponte e caminho até a Caverna Esquecida. WASD/setas movem, Espaço ou clique esquerdo atacam, e E interage; as missões, seis classes, salvamento no navegador e cripta existente foram preservados.

O mapa lógico e as colisões funcionam sem os PNGs. O cenário e os personagens só são desenhados quando os PNGs pixel art estão no caminho e dimensões descritos em [assets/maps/eldoria/ASSET_REQUIREMENTS.md](assets/maps/eldoria/ASSET_REQUIREMENTS.md). Sem eles, a interface lista os arquivos ausentes e o Canvas não desenha substitutos. Atualize `available` em [assets/asset-manifest.js](assets/asset-manifest.js) ao adicionar cada imagem; o carregador valida e armazena os PNGs em cache em [assets/asset-manager.js](assets/asset-manager.js).

## Executar o criador Pygame

Requer Python 3.10 ou superior e usa Pygame CE (compatível com a API `pygame`).

```powershell
python -m pip install -r requirements.txt
python main.py
```

O criador começa pelo menu, permite escolher classe e aparência, e grava/carrega o personagem em `saves/player.json`.

## Imagens de personagens

Os PNGs das camadas ainda não estão no repositório. O aplicativo não desenha personagens substitutos: lista os caminhos selecionados que estão faltando e só mostra a prévia quando os arquivos corretos são adicionados. A prancha de referência não é usada como spritesheet. Consulte [assets/characters/ASSET_GUIDE.md](assets/characters/ASSET_GUIDE.md) para nomes, dimensões, direções e alinhamento.

## Testes

```powershell
python -m unittest discover -s tests -v
```
