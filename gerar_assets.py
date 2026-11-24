#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de assets para o jogo DRAKMOR - RPG PIXEL

Valida e copia imagens do asset pack para os caminhos esperados pelo jogo.

Requisitos:
    pip install Pillow

Como usar:
    1. Baixe as imagens do asset pack e coloque em uma pasta (SOURCE_DIR).
    2. Ajuste SOURCE_DIR abaixo para onde estao as imagens.
    3. Rode: python gerar_assets.py
"""

from PIL import Image
import os
import sys

# ==================== CONFIGURACAO ====================

# Pasta onde estao as imagens grandes do asset pack
SOURCE_DIR = r"C:\caminho\para\as\imagens\do\asset\pack"

# Pasta raiz do jogo (onde fica a pasta assets/)
DEST_DIR = r"c:\Users\victor_monteiro\Documents\GitHub\RPG-PIXEL\assets"

# ======================================================

criados = []
faltando_fontes = []
erros = []


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def salvar_png(imagem, caminho_destino):
    ensure_dir(os.path.dirname(caminho_destino))
    imagem.save(caminho_destino, "PNG", optimize=True)


def copiar_arquivo(nome_arquivo, caminho_destino_relativo, dimensoes_esperadas=None):
    src = os.path.join(SOURCE_DIR, nome_arquivo)
    if not os.path.exists(src):
        faltando_fontes.append(nome_arquivo)
        print(f"[FONTE AUSENTE] {nome_arquivo}")
        return False

    dst = os.path.join(DEST_DIR, caminho_destino_relativo)
    try:
        imagem = Image.open(src).convert("RGBA")
        largura, altura = imagem.size
        pasta_destino = caminho_destino_relativo.replace("\\", "/").split("/")[0]
        if pasta_destino == "characters" and (
            altura != 64 * 4 or largura < 64 or largura % 64
        ):
            raise ValueError(
                "folha de personagem deve ter 4 linhas de 64 px "
                "e largura multipla de 64 px"
            )
        if pasta_destino == "characters" and not imagem.getchannel("A").getbbox():
            raise ValueError("folha de personagem esta totalmente transparente")
        if dimensoes_esperadas and imagem.size != dimensoes_esperadas:
            raise ValueError(
                f"dimensoes esperadas: {dimensoes_esperadas[0]}x"
                f"{dimensoes_esperadas[1]} px; recebidas: {largura}x{altura} px"
            )

        salvar_png(imagem, dst)
        criados.append(caminho_destino_relativo)
        print(f"[OK] {caminho_destino_relativo}")
        return True
    except Exception as e:
        erros.append((caminho_destino_relativo, str(e)))
        print(f"[ERRO] {caminho_destino_relativo}: {e}")
        return False

def processar_corpos():
    mapeamento = {
        "boy_light.png": "characters/base/boy_light.png",
        "boy_warm.png": "characters/base/boy_warm.png",
        "boy_deep.png": "characters/base/boy_deep.png",
        "girl_light.png": "characters/base/girl_light.png",
        "girl_warm.png": "characters/base/girl_warm.png",
        "girl_deep.png": "characters/base/girl_deep.png",
    }
    for src, dst in mapeamento.items():
        copiar_arquivo(src, dst)


def processar_rostos_olhos():
    mapeamento = {
        "face_light.png": "characters/faces/face_light.png",
        "face_warm.png": "characters/faces/face_warm.png",
        "face_deep.png": "characters/faces/face_deep.png",
        "eyes_brown.png": "characters/faces/eyes_brown.png",
        "eyes_blue.png": "characters/faces/eyes_blue.png",
        "eyes_green.png": "characters/faces/eyes_green.png",
        "eyes_gray.png": "characters/faces/eyes_gray.png",
    }
    for src, dst in mapeamento.items():
        copiar_arquivo(src, dst)


def processar_cabelos():
    estilos = ["short", "long", "curly", "messy", "braided"]
    cores = ["black", "brown", "blonde", "red", "silver"]

    for estilo in estilos:
        for cor in cores:
            src = f"{estilo}_{cor}.png"
            dst = f"characters/hair/{estilo}_{cor}.png"
            copiar_arquivo(src, dst)


def processar_camisas():
    mapeamento = {
        "linen.png": "characters/clothes/shirts/linen.png",
        "crimson.png": "characters/clothes/shirts/crimson.png",
        "blue.png": "characters/clothes/shirts/blue.png",
        "forest.png": "characters/clothes/shirts/forest.png",
        "arcane.png": "characters/clothes/shirts/arcane.png",
        "shadow.png": "characters/clothes/shirts/shadow.png",
        "white.png": "characters/clothes/shirts/white.png",
    }
    for src, dst in mapeamento.items():
        copiar_arquivo(src, dst)


def processar_calcas():
    mapeamento = {
        "charcoal.png": "characters/clothes/pants/charcoal.png",
        "brown.png": "characters/clothes/pants/brown.png",
        "blue.png": "characters/clothes/pants/blue.png",
        "forest.png": "characters/clothes/pants/forest.png",
    }
    for src, dst in mapeamento.items():
        copiar_arquivo(src, dst)


def processar_botas():
    mapeamento = {
        "leather.png": "characters/clothes/boots/leather.png",
        "forest.png": "characters/clothes/boots/forest.png",
        "blue.png": "characters/clothes/boots/blue.png",
        "shadow.png": "characters/clothes/boots/shadow.png",
        "plate.png": "characters/clothes/boots/plate.png",
    }
    for src, dst in mapeamento.items():
        copiar_arquivo(src, dst)


def processar_capas():
    mapeamento = {
        "blue.png": "characters/clothes/cloaks/blue.png",
        "crimson.png": "characters/clothes/cloaks/crimson.png",
        "shadow.png": "characters/clothes/cloaks/shadow.png",
        "white.png": "characters/clothes/cloaks/white.png",
        "leaves.png": "characters/clothes/cloaks/leaves.png",
    }
    for src, dst in mapeamento.items():
        copiar_arquivo(src, dst)


def processar_armaduras():
    mapeamento = {
        "chainmail.png": "characters/armor/chainmail.png",
        "leather.png": "characters/armor/leather.png",
        "solar_plate.png": "characters/armor/solar_plate.png",
        "leaf.png": "characters/armor/leaf.png",
    }
    for src, dst in mapeamento.items():
        copiar_arquivo(src, dst)


def processar_armas():
    mapeamento = {
        "steel_sword.png": "characters/weapons/steel_sword.png",
        "solar_sword.png": "characters/weapons/solar_sword.png",
        "twin_daggers.png": "characters/weapons/twin_daggers.png",
        "yew_bow.png": "characters/weapons/yew_bow.png",
        "arcane_staff.png": "characters/weapons/arcane_staff.png",
        "thorn_staff.png": "characters/weapons/thorn_staff.png",
    }
    for src, dst in mapeamento.items():
        copiar_arquivo(src, dst)


def processar_acessorios():
    mapeamento = {
        "iron_shield.png": "characters/accessories/iron_shield.png",
        "quiver.png": "characters/accessories/quiver.png",
        "blue_amulet.png": "characters/accessories/blue_amulet.png",
        "shadow_mask.png": "characters/accessories/shadow_mask.png",
        "nature_brooch.png": "characters/accessories/nature_brooch.png",
    }
    for src, dst in mapeamento.items():
        copiar_arquivo(src, dst)


def processar_sprites_animados():
    mapeamento = {
        "player.png": ("characters/player.png", (448, 256)),
        "npcs.png": ("characters/npcs.png", (448, 256)),
        "slime.png": ("enemies/slime.png", (448, 256)),
        "goblin.png": ("enemies/goblin.png", (448, 256)),
        "wolf.png": ("enemies/wolf.png", (448, 256)),
        "skeleton.png": ("enemies/skeleton.png", (448, 256)),
        "bandit.png": ("enemies/bandit.png", (448, 256)),
        "boss.png": ("enemies/boss.png", (448, 256)),
    }
    for src, (dst, dimensoes) in mapeamento.items():
        copiar_arquivo(src, dst, dimensoes_esperadas=dimensoes)


def processar_tileset_props_efeitos():
    mapeamento = [
        ("Tileset Eldoria (Melhorado).png", "tilesets/eldoria.png"),
        ("Tileset Eldoria.png", "tilesets/eldoria.png"),
        ("eldoria.png", "tilesets/eldoria.png"),
        ("Props.png", "tilesets/props.png"),
        ("props.png", "tilesets/props.png"),
        ("Efeitos.png", "effects/combat.png"),
        ("efeitos.png", "effects/combat.png"),
        ("combat.png", "effects/combat.png"),
    ]
    processados = set()
    for src, dst in mapeamento:
        if dst in processados:
            continue
        if os.path.exists(os.path.join(SOURCE_DIR, src)):
            if copiar_arquivo(src, dst):
                processados.add(dst)


def main():
    print("=" * 60)
    print("GERADOR DE ASSETS - DRAKMOR RPG PIXEL")
    print("=" * 60)
    print(f"SOURCE_DIR: {SOURCE_DIR}")
    print(f"DEST_DIR:   {DEST_DIR}")
    print()

    if not os.path.isdir(SOURCE_DIR):
        print(f"ERRO: SOURCE_DIR nao existe: {SOURCE_DIR}")
        print("Ajuste o caminho no inicio do script e rode novamente.")
        sys.exit(1)

    processar_sprites_animados()
    processar_corpos()
    processar_rostos_olhos()
    processar_cabelos()
    processar_camisas()
    processar_calcas()
    processar_botas()
    processar_capas()
    processar_armaduras()
    processar_armas()
    processar_acessorios()
    processar_tileset_props_efeitos()

    # Relatorio final
    print()
    print("=" * 60)
    print("RELATORIO FINAL")
    print("=" * 60)
    print(f"Arquivos criados com sucesso: {len(criados)}")
    print(f"Fontes nao encontradas:       {len(faltando_fontes)}")
    print(f"Erros:                        {len(erros)}")
    print()

    if faltando_fontes:
        print("ARQUIVOS NA SOURCE_DIR QUE FALTAM:")
        for f in faltando_fontes:
            print(f"  - {f}")
        print()

    if erros:
        print("ERROS AO PROCESSAR:")
        for nome, msg in erros:
            print(f"  - {nome}: {msg}")
        print()

    if criados:
        print("PRIMEIROS ARQUIVOS CRIADOS:")
        for c in criados[:20]:
            print(f"  - {c}")
        if len(criados) > 20:
            print(f"  ... e mais {len(criados) - 20} arquivos.")
        print()

    print("Concluido. Verifique a pasta assets/ do seu projeto.")


if __name__ == "__main__":
    main()

