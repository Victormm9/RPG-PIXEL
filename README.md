# RPG-PIXEL

O jogo web existente continua em `index.html`, `style.css` e `script.js`. A aplicação Python/Pygame é uma versão paralela para criação e personalização de personagens; ela não substitui nem altera o jogo web.

## RPG web

Sirva a pasta do projeto em HTTP (por exemplo, com a extensão Live Server do VS Code) e abra `index.html` no navegador. A área exterior usa um mapa contínuo de 128 × 96 tiles de 32 px e câmera, com Vila de Eldoria, Campos do Norte, Floresta dos Sussurros, rio, ponte, Caverna Esquecida e as Montanhas do Eco. Após derrotar o chefe da cripta, reúna os três fragmentos do sino, vença o guardião e ajude Lia; isso abre o Capítulo III, com a Fenda Além da Pedra, o Rei sem Voz e o resgate de Joren. A Carga Perdida é uma missão secundária nas montanhas. Armas, armaduras e amuletos podem ser encontrados, comprados com Doran e equipados: seus bônus alteram ataque, defesa, atributos e limites de mana/vida. Nina conta rumores diferentes conforme o dia, Nilo reage às missões e a mercadora reduz os preços após a caravana ser ajudada. Itens aparecem no mundo e no minimapa; poções e pão podem ser coletados, e a poção azul recupera mana. Saves anteriores continuam compatíveis. Cada classe ganha habilidades próprias nos níveis 3, 5, 8 e 10, além da habilidade inicial. WASD/setas movem, Espaço ou clique esquerdo atacam, E interage e Q/Z/X/C/V ativam habilidades; seis classes, salvamento no navegador e a cripta existente foram preservados.

### Prévia de migração para 3D

Na tela inicial, escolha **Experimentar a prévia 3D** para testar uma primeira área em terceira pessoa. O protótipo usa WebGL sem bibliotecas externas, com movimento, câmera giratória, uma conversa e um inimigo de teste. WASD/setas movem, Espaço ataca, E interage, arraste o mouse para girar a câmera e use a rodinha para aproximar/afastar. Essa área é uma etapa experimental independente: ainda não compartilha o progresso, os personagens ou os salvamentos do jogo 2D.

A iluminação e as partículas ambientais mudam conforme a região; na cripta, um brilho suave acompanha o personagem para reforçar a sensação de exploração subterrânea. Os impactos de combate também exibem faíscas pixeladas na cor do ataque.

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
