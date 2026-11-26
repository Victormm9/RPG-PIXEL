#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DRAKMOR — RPG 3D (Ursina)
Reino aberto + Masmorra infinita por andares.
Requer: pip install ursina
Rode antes: python gerar_modelos_3d.py   (para criar assets_rpg_3d/)
"""

from __future__ import annotations

import math
import random
from typing import List, Optional

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

# ---------------------------------------------------------------------------
# DADOS DE CLASSES, ITENS E PROGRESSÃO
# ---------------------------------------------------------------------------
CLASSES_INFO = {
    "Guerreiro": {
        "arma_inicial": "Espada de Aço",
        "modelo_arma": "assets_rpg_3d/armas/espada.obj",
        "hp_bonus": 40,
        "mp_bonus": 0,
        "magia_nome": "Golpe Sísmico (Q)",
        "custo_mana": 20,
        "cor": color.light_gray,
    },
    "Arqueiro": {
        "arma_inicial": "Arco Longo",
        "modelo_arma": "assets_rpg_3d/armas/arco.obj",
        "hp_bonus": 15,
        "mp_bonus": 20,
        "magia_nome": "Disparo Triplo (Q)",
        "custo_mana": 25,
        "cor": color.lime,
    },
    "Mago": {
        "arma_inicial": "Cajado Arcano",
        "modelo_arma": "assets_rpg_3d/armas/cajado.obj",
        "hp_bonus": 0,
        "mp_bonus": 60,
        "magia_nome": "Bola de Fogo (Q)",
        "custo_mana": 30,
        "cor": color.cyan,
    },
}

CATALOGO_ITENS = {
    "Espada de Aço": {"tipo": "arma", "classe": "Guerreiro", "dano": 28,
                      "modelo": "assets_rpg_3d/armas/espada.obj"},
    "Arco Longo": {"tipo": "arma", "classe": "Arqueiro", "dano": 24,
                   "modelo": "assets_rpg_3d/armas/arco.obj"},
    "Cajado Arcano": {"tipo": "arma", "classe": "Mago", "dano": 32,
                      "modelo": "assets_rpg_3d/armas/cajado.obj"},
    "Poção de Vida": {"tipo": "consumivel", "efeito": "hp", "valor": 50},
    "Poção de Mana": {"tipo": "consumivel", "efeito": "mp", "valor": 50},
}
# ==============================================================================
# SISTEMAS DO JOGADOR (NÍVEIS, XP, INVENTÁRIO, CLASSES)
# ==============================================================================
class SistemaJogador:
    def __init__(self, controller: FirstPersonController):
        self.ctrl = controller
        self.nivel = 1
        self.xp = 0
        self.xp_proximo = 100
        self.classe = "Guerreiro"
        self.arma_equipada = "Espada de Aço"

        self.hp_max = 140
        self.hp = 140
        self.mp_max = 50
        self.mp = 50

        self.inventario: List[str] = [
            "Espada de Aço",
            "Arco Longo",
            "Cajado Arcano",
            "Poção de Vida",
            "Poção de Mana",
        ]

        # Modelo 3D da arma na mão (filho da câmera)
        self.modelo_mao = Entity(
            parent=camera,
            model=CATALOGO_ITENS[self.arma_equipada]["modelo"],
            position=(0.45, -0.45, 0.8),
            rotation=(15, -20, 10),
            scale=0.55,
        )

    def ganhar_xp(self, qtd: int) -> None:
        self.xp += qtd
        notificar(f"+{qtd} XP!")
        while self.xp >= self.xp_proximo:
            self.xp -= self.xp_proximo
            self.nivel += 1
            self.xp_proximo = int(self.xp_proximo * 1.4)
            self.recalcular_status(curar_tudo=True)
            notificar(f"SUBIU DE NÍVEL! Agora você é Nível {self.nivel}!",
                      color.gold)

    def recalcular_status(self, curar_tudo: bool = False) -> None:
        info = CLASSES_INFO[self.classe]
        self.hp_max = 100 + (self.nivel * 20) + info["hp_bonus"]
        self.mp_max = 50 + (self.nivel * 15) + info["mp_bonus"]
        if curar_tudo:
            self.hp = self.hp_max
            self.mp = self.mp_max
        else:
            self.hp = min(self.hp, self.hp_max)
            self.mp = min(self.mp, self.mp_max)

    def trocar_classe(self, nova_classe: str) -> None:
        if nova_classe not in CLASSES_INFO:
            return
        self.classe = nova_classe
        arma_padrao = CLASSES_INFO[nova_classe]["arma_inicial"]
        self.equipar_arma(arma_padrao)
        self.recalcular_status(curar_tudo=False)
        notificar(
            f"Classe alterada para {nova_classe} | Magia: "
            f"{CLASSES_INFO[nova_classe]['magia_nome']}",
            color.azure,
        )

    def equipar_arma(self, nome_arma: str) -> None:
        dados = CATALOGO_ITENS.get(nome_arma)
        if not dados or dados["tipo"] != "arma":
            return
        self.arma_equipada = nome_arma
        self.classe = dados["classe"]
        self.modelo_mao.model = dados["modelo"]
        self.recalcular_status(curar_tudo=False)
        notificar(f"Equipado: {nome_arma} ({self.classe})")

    def usar_item(self, indice: int) -> None:
        if indice >= len(self.inventario):
            return
        item_nome = self.inventario[indice]
        dados = CATALOGO_ITENS[item_nome]
        if dados["tipo"] == "arma":
            self.equipar_arma(item_nome)
        elif dados["tipo"] == "consumivel":
            if dados["efeito"] == "hp":
                self.hp = min(self.hp_max, self.hp + dados["valor"])
                notificar(f"Usou {item_nome}: +{dados['valor']} HP", color.lime)
            elif dados["efeito"] == "mp":
                self.mp = min(self.mp_max, self.mp + dados["valor"])
                notificar(f"Usou {item_nome}: +{dados['valor']} Mana", color.cyan)
            self.inventario.pop(indice)
        hud.atualizar_inventario()

    def dano_atual(self) -> int:
        base = CATALOGO_ITENS[self.arma_equipada]["dano"]
        return int(base + (self.nivel - 1) * 6)

# ==============================================================================
# PROJÉTEIS E MAGIAS 3D
# ==============================================================================
projeteis_ativos: List[Entity] = []


class Projetil(Entity):
    def __init__(self, pos, direcao, velocidade, dano, cor, escala=0.25,
                 explosivo=False, mundo=None):
        super().__init__(
            model='sphere',
            position=pos,
            scale=escala,
            color=cor,
            collider='box',
        )
        self.direcao = direcao.normalized()
        self.velocidade = velocidade
        self.dano = dano
        self.explosivo = explosivo
        self.tempo_vida = 3.0
        self.mundo = mundo
        projeteis_ativos.append(self)

    def atualizar(self) -> None:
        self.position += self.direcao * self.velocidade * time.dt
        self.tempo_vida -= time.dt
        if self.tempo_vida <= 0:
            self.destruir()
            return

        if self.mundo is None:
            return

        alvo_atingido = None
        for ent in list(self.mundo.entidades_ativas):
            if hasattr(ent, 'eh_monstro') and \
               distance(self.position, ent.position + Vec3(0, 0.8, 0)) < 1.5:
                alvo_atingido = ent
                break

        if alvo_atingido is not None:
            if self.explosivo:
                # Dano em área (Bola de Fogo)
                for alvo_area in list(self.mundo.entidades_ativas):
                    if hasattr(alvo_area, 'eh_monstro') and \
                       distance(self.position, alvo_area.position) < 5.0:
                        self.mundo.aplicar_dano_monstro(alvo_area, self.dano)
            else:
                self.mundo.aplicar_dano_monstro(alvo_atingido, self.dano)
            self.destruir()
            return

    def destruir(self) -> None:
        if self in projeteis_ativos:
            projeteis_ativos.remove(self)
        destroy(self)

# ==============================================================================
# GERENCIADOR DE MUNDO (REINO ABERTO + MASMORRA INFINITA POR ANDARES)
# ==============================================================================
class GerenciadorMundo:
    def __init__(self):
        self.modo = "REINO"
        self.andar_masmorra = 0
        self.entidades_ativas: List[Entity] = []
        self.portal_masmorra: Optional[Entity] = None
        self.portal_retorno: Optional[Entity] = None
        self.escada_descida: Optional[Entity] = None

    def limpar_mundo(self) -> None:
        for ent in self.entidades_ativas:
            destroy(ent)
        self.entidades_ativas.clear()
        self.portal_masmorra = None
        self.portal_retorno = None
        self.escada_descida = None

    def carregar_reino(self, ctrl_jogador: FirstPersonController) -> None:
        self.limpar_mundo()
        self.modo = "REINO"
        self.andar_masmorra = 0
        window.color = color.rgb(135, 206, 235)  # Céu azul

        # Terreno vasto do Reino (220x220)
        chao = Entity(
            model='plane',
            scale=(220, 1, 220),
            color=color.rgb(55, 130, 50),
            texture='white_cube',
            texture_scale=(60, 60),
            collider='box',
        )
        self.entidades_ativas.append(chao)

        # Estrada de pedra ligando Castelo -> Vila -> Caverna
        estrada = Entity(
            model='cube',
            position=(0, 0.02, 10),
            scale=(5, 0.05, 130),
            color=color.rgb(120, 115, 105),
        )
        self.entidades_ativas.append(estrada)

        # Castelo Real ao Sul
        castelo = Entity(
            model='assets_rpg_3d/cenario/castelo.obj',
            position=(0, 0, -45),
            scale=1.8,
            collider='box',
        )
        self.entidades_ativas.append(castelo)

        # Vila Central (Casas e NPCs)
        posicoes_casas = [(-14, 0, -10), (14, 0, -10),
                          (-16, 0, 12), (16, 0, 12), (-14, 0, 32)]
        for idx, pos in enumerate(posicoes_casas):
            rot_y = 90 if pos[0] < 0 else -90
            casa = Entity(
                model='assets_rpg_3d/cenario/casa.obj',
                position=pos,
                rotation=(0, rot_y, 0),
                scale=1.3,
                collider='box',
            )
            self.entidades_ativas.append(casa)

        # NPCs espalhados pela vila
        npcs_dados = [
            ('assets_rpg_3d/personagens/npc_aldeao.obj', (-6, 0, -5),
             "Aldeão: Cuidado com a caverna ao norte!"),
            ('assets_rpg_3d/personagens/mago.obj', (6, 0, 5),
             "Arquimago: Use [Q] para lançar magias poderosas."),
            ('assets_rpg_3d/personagens/arqueiro.obj', (-6, 0, 20),
             "Patrulheiro: Pressione [1], [2] ou [3] para trocar de classe."),
        ]
        for mod, pos, fala in npcs_dados:
            npc = Entity(model=mod, position=pos, scale=1.2, collider='box')
            npc.fala = fala
            self.entidades_ativas.append(npc)

        # Montanhas cercando o Reino
        for i in range(-90, 95, 30):
            self.entidades_ativas.append(
                Entity(model='assets_rpg_3d/cenario/montanha.obj',
                       position=(i, 0, 95), scale=1.6))
            self.entidades_ativas.append(
                Entity(model='assets_rpg_3d/cenario/montanha.obj',
                       position=(i, 0, -95), scale=1.6))
            self.entidades_ativas.append(
                Entity(model='assets_rpg_3d/cenario/montanha.obj',
                       position=(-95, 0, i), scale=1.6))
            self.entidades_ativas.append(
                Entity(model='assets_rpg_3d/cenario/montanha.obj',
                       position=(95, 0, i), scale=1.6))

        # Floresta (Árvores e Arbustos)
        random.seed(42)
        for _ in range(65):
            rx = random.uniform(-80, 80)
            rz = random.uniform(-75, 75)
            if abs(rx) < 12:  # Mantém a estrada e praça livres
                continue
            arvore = Entity(
                model='assets_rpg_3d/cenario/arvore.obj',
                position=(rx, 0, rz),
                scale=random.uniform(1.1, 1.7),
            )
            self.entidades_ativas.append(arvore)
            if random.random() > 0.4:
                arb = Entity(
                    model='assets_rpg_3d/cenario/arbusto.obj',
                    position=(rx + 2.2, 0, rz + 1.5),
                    scale=1.1,
                )
                self.entidades_ativas.append(arb)

        # Entrada da Grande Caverna (Norte)
        caverna = Entity(
            model='assets_rpg_3d/cenario/entrada_caverna.obj',
            position=(0, 0, 72),
            scale=1.8,
            collider='box',
        )
        self.entidades_ativas.append(caverna)

        # Portal da Masmorra dentro da Caverna
        self.portal_masmorra = Entity(
            model='cube',
            position=(0, 1.5, 72),
            scale=(3.2, 3.2, 1.5),
            color=color.rgba(160, 30, 240, 210),
            collider='box',
        )
        self.entidades_ativas.append(self.portal_masmorra)

        # Slimes selvagens na floresta para treino inicial
        for pos_slime in [(25, 0, 30), (-28, 0, 40), (32, 0, 55)]:
            self.spawnar_monstro(pos_slime, nivel=1)

        ctrl_jogador.position = (0, 2, -20)
        notificar("Bem-vindo ao Reino de Eldoria! Siga a estrada ao Norte "
                  "para a Caverna.", color.gold)

    def carregar_andar_masmorra(self, ctrl_jogador: FirstPersonController,
                                andar: int) -> None:
        self.limpar_mundo()
        self.modo = "MASMORRA"
        self.andar_masmorra = andar
        window.color = color.rgb(15, 12, 20)

        tam = 28 + min(andar * 2, 24)
        chao = Entity(
            model='plane',
            scale=(tam, 1, tam),
            color=color.rgb(40, 38, 45),
            texture='white_cube',
            texture_scale=(tam, tam),
            collider='box',
        )
        self.entidades_ativas.append(chao)

        paredes = [
            ((0, 3, tam / 2), (tam, 6, 1)),
            ((0, 3, -tam / 2), (tam, 6, 1)),
            ((tam / 2, 3, 0), (1, 6, tam)),
            ((-tam / 2, 3, 0), (1, 6, tam)),
        ]
        for pos, esc in paredes:
            self.entidades_ativas.append(
                Entity(model='cube', position=pos, scale=esc,
                       color=color.rgb(30, 28, 35), collider='box'))

        ctrl_jogador.position = (0, 1.5, -tam / 2 + 3)

        # Portal Vermelho: Descer para o próximo andar (escada)
        self.portal_masmorra = Entity(
            model='cube',
            position=(0, 1.0, tam / 2 - 3),
            scale=(2.5, 2.0, 2.5),
            color=color.red,
            collider='box',
        )
        self.entidades_ativas.append(self.portal_masmorra)
        self.escada_descida = self.portal_masmorra

        # Portal Verde: Retornar à superfície (Reino)
        self.portal_retorno = Entity(
            model='cube',
            position=(-tam / 2 + 3, 1.0, -tam / 2 + 3),
            scale=(2.0, 2.0, 2.0),
            color=color.green,
            collider='box',
        )
        self.entidades_ativas.append(self.portal_retorno)

        # Spawna monstros mais fortes a cada nível
        qtd = 3 + andar
        for _ in range(qtd):
            rx = random.uniform(-tam / 2 + 4, tam / 2 - 4)
            rz = random.uniform(-tam / 2 + 6, tam / 2 - 6)
            self.spawnar_monstro((rx, 0, rz), nivel=andar)

        # Drop de poção no andar
        tipo_pocao = random.choice(["Poção de Vida", "Poção de Mana"])
        mod_pocao = ("assets_rpg_3d/itens/pocao_vida.obj"
                     if tipo_pocao == "Poção de Vida"
                     else "assets_rpg_3d/itens/pocao_mana.obj")
        item_chao = Entity(
            model=mod_pocao,
            position=(random.uniform(-6, 6), 0.2, random.uniform(-6, 6)),
            scale=1.5,
            collider='box',
        )
        item_chao.item_coletavel = tipo_pocao
        self.entidades_ativas.append(item_chao)

        notificar(f"Masmorra — Andar -{andar} | Monstros Nível {andar}",
                  color.orange)

    def spawnar_monstro(self, pos, nivel: int) -> None:
        mult = 1 + (nivel - 1) * 0.4
        if nivel <= 2:
            mod, nome, esc = ('assets_rpg_3d/mobs/tier1_slime.obj',
                              "Slime", 1.2)
        elif nivel <= 5:
            mod, nome, esc = ('assets_rpg_3d/mobs/tier2_goblin.obj',
                              "Goblin Guerreiro", 1.3)
        else:
            mod, nome, esc = ('assets_rpg_3d/mobs/tier3_golem.obj',
                              "Golem Abissal",
                              1.0 + (nivel * 0.04))

        m = Entity(model=mod, position=pos, scale=esc, collider='box')
        m.eh_monstro = True
        m.nome = f"{nome} Nv.{nivel}"
        m.hp = int(45 * mult)
        m.dano = int(6 * mult)
        m.xp_recompensa = int(35 * mult)
        m.velocidade = 2.2 + min(nivel * 0.15, 2.8)
        m.cooldown_ataque = 0
        self.entidades_ativas.append(m)

    def aplicar_dano_monstro(self, monstro: Entity, dano: int) -> None:
        if not hasattr(monstro, 'hp'):
            return
        monstro.hp -= dano
        monstro.blink(color.white, duration=0.12)
        if monstro.hp <= 0:
            xp = monstro.xp_recompensa
            if monstro in self.entidades_ativas:
                self.entidades_ativas.remove(monstro)
            destroy(monstro)
            rpg.ganhar_xp(xp)
            # Chance de dropar poção ao morrer
            if random.random() < 0.35:
                drop = random.choice(["Poção de Vida", "Poção de Mana"])
                rpg.inventario.append(drop)
                hud.atualizar_inventario()
                notificar(f"Dropou: {drop}!", color.yellow)

# ==============================================================================
# INTERFACE DE USUÁRIO (HUD + INVENTÁRIO)
# ==============================================================================
class InterfaceRPG:
    def __init__(self):
        self.txt_status = Text(position=(-0.86, 0.47), scale=1.1,
                               color=color.white)
        self.txt_local = Text(position=(0.45, 0.47), scale=1.1,
                              color=color.gold)
        self.txt_andar = Text(position=(-0.86, 0.40), scale=1.0,
                              color=color.gold)
        self.txt_aviso = Text(position=(-0.45, 0.34), scale=1.05,
                              color=color.yellow)
        self.txt_controles = Text(
            text="[1/2/3] Classe | [Click] Atacar | [Q] Magia | [I] Inventário",
            position=(-0.86, -0.46),
            scale=0.9,
            color=color.light_gray,
        )

        # Painel de Inventário (oculto inicialmente)
        self.painel_inv = Entity(parent=camera.ui, enabled=False)
        self.fundo_inv = Entity(parent=self.painel_inv, model='quad',
                                scale=(0.65, 0.7), color=color.rgba(20, 20, 30, 230))
        Text(parent=self.painel_inv, text="INVENTÁRIO (Clique para usar/equipar)",
             position=(-0.27, 0.30), scale=1.1, color=color.gold)
        self.botoes_inv: List[Button] = []

    def atualizar_hud(self) -> None:
        self.txt_status.text = (
            f"Classe: {rpg.classe} (Nv.{rpg.nivel}) | XP: {rpg.xp}/{rpg.xp_proximo}\n"
            f"HP: {rpg.hp}/{rpg.hp_max} | Mana: {int(rpg.mp)}/{rpg.mp_max} | "
            f"Arma: {rpg.arma_equipada}"
        )
        if mundo.modo == "REINO":
            self.txt_local.text = "Local: Reino de Eldoria"
            self.txt_andar.text = ""
        else:
            self.txt_local.text = "Local: Masmorra"
            self.txt_andar.text = f"Andar: -{mundo.andar_masmorra}"

    def alternar_inventario(self) -> None:
        self.painel_inv.enabled = not self.painel_inv.enabled
        mouse.locked = not self.painel_inv.enabled
        player.enabled = not self.painel_inv.enabled
        if self.painel_inv.enabled:
            self.atualizar_inventario()

    def atualizar_inventario(self) -> None:
        for b in self.botoes_inv:
            destroy(b)
        self.botoes_inv.clear()

        for idx, item in enumerate(rpg.inventario[:10]):
            y_pos = 0.20 - (idx * 0.055)
            btn = Button(
                parent=self.painel_inv,
                text=f"{idx + 1}. {item}",
                position=(0, y_pos),
                scale=(0.55, 0.045),
                color=color.dark_gray,
                on_click=Func(rpg.usar_item, idx),
            )
            self.botoes_inv.append(btn)


def notificar(msg: str, cor=color.white) -> None:
    hud.txt_aviso.text = msg
    hud.txt_aviso.color = cor

# ==============================================================================
# INICIALIZAÇÃO E LOOP PRINCIPAL
# ==============================================================================
AmbientLight(color=color.rgba(150, 150, 160, 255))
DirectionalLight(y=25, z=15, shadows=True)

player = FirstPersonController(speed=8)
rpg = SistemaJogador(player)
mundo = GerenciadorMundo()
hud = InterfaceRPG()

mundo.carregar_reino(player)


def lancar_magia_classe() -> None:
    info = CLASSES_INFO[rpg.classe]
    custo = info["custo_mana"]
    if rpg.mp < custo:
        notificar("Mana insuficiente!", color.red)
        return
    rpg.mp -= custo
    dano_magico = int(rpg.dano_atual() * 1.8)

    if rpg.classe == "Guerreiro":
        # Golpe Sísmico em área ao redor do jogador
        notificar("GOLPE SÍSMICO!", color.orange)
        for ent in list(mundo.entidades_ativas):
            if hasattr(ent, 'eh_monstro') and \
               distance(player.position, ent.position) < 6.0:
                mundo.aplicar_dano_monstro(ent, dano_magico)
                ent.position += (ent.position - player.position).normalized() * 3.0

    elif rpg.classe == "Arqueiro":
        # Chuva de 3 flechas em leque
        notificar("DISPARO TRIPLO!", color.lime)
        for angulo in (-12, 0, 12):
            dir_flecha = Quaternion.from_axis_angle(
                Vec3(0, 1, 0), math.radians(angulo)).xform(camera.forward)
            Projetil(camera.world_position + camera.forward * 1.2,
                     dir_flecha, 32, int(dano_magico * 0.7),
                     color.lime, escala=0.2, mundo=mundo)

    elif rpg.classe == "Mago":
        # Bola de Fogo explosiva
        notificar("BOLA DE FOGO!", color.red)
        Projetil(camera.world_position + camera.forward * 1.2,
                 camera.forward, 24, dano_magico, color.orange,
                 escala=0.45, explosivo=True, mundo=mundo)


def input(key: str) -> None:
    if key == 'i':
        hud.alternar_inventario()
        return

    if hud.painel_inv.enabled:
        return

    if key == '1':
        rpg.trocar_classe("Guerreiro")
    elif key == '2':
        rpg.trocar_classe("Arqueiro")
    elif key == '3':
        rpg.trocar_classe("Mago")
    elif key == 'q':
        lancar_magia_classe()

    elif key == 'left mouse down':
        # Animação da arma na mão
        rpg.modelo_mao.animate_rotation((65, -20, 10), duration=0.08)
        invoke(rpg.modelo_mao.animate_rotation, (15, -20, 10),
               duration=0.12, delay=0.08)

        # Interação com NPC no Reino
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'fala'):
            if distance(player.position, mouse.hovered_entity.position) < 5.0:
                notificar(mouse.hovered_entity.fala, color.cyan)
                return

        # Ataque básico por classe
        if rpg.classe == "Guerreiro":
            if (mouse.hovered_entity
                    and hasattr(mouse.hovered_entity, 'eh_monstro')):
                if distance(player.position,
                            mouse.hovered_entity.position) < 4.5:
                    mundo.aplicar_dano_monstro(mouse.hovered_entity,
                                               rpg.dano_atual())
        elif rpg.classe == "Arqueiro":
            Projetil(camera.world_position + camera.forward * 1.1,
                     camera.forward, 35, rpg.dano_atual(),
                     color.yellow, escala=0.15, mundo=mundo)
        elif rpg.classe == "Mago":
            Projetil(camera.world_position + camera.forward * 1.1,
                     camera.forward, 26, rpg.dano_atual(),
                     color.cyan, escala=0.25, mundo=mundo)


def update() -> None:
    # Regeneração passiva suave de Mana
    if rpg.mp < rpg.mp_max:
        rpg.mp = min(rpg.mp_max, rpg.mp + 2.5 * time.dt)

    # Atualiza projéteis
    for p in list(projeteis_ativos):
        p.atualizar()

    # Verifica entrada nos portais
    if (mundo.portal_masmorra
            and distance(player.position, mundo.portal_masmorra.position) < 2.5):
        mundo.carregar_andar_masmorra(player, mundo.andar_masmorra + 1)

    if (mundo.portal_retorno
            and distance(player.position, mundo.portal_retorno.position) < 2.2):
        mundo.carregar_reino(player)

    # Coleta de itens no chão e IA dos monstros
    for ent in list(mundo.entidades_ativas):
        if (hasattr(ent, 'item_coletavel')
                and distance(player.position, ent.position) < 2.0):
            rpg.inventario.append(ent.item_coletavel)
            notificar(f"Coletou: {ent.item_coletavel}", color.lime)
            mundo.entidades_ativas.remove(ent)
            destroy(ent)

        elif hasattr(ent, 'eh_monstro'):
            dist = distance(ent.position, player.position)
            if dist < 15 and dist > 1.8:
                # Olha para o jogador apenas no eixo Y (corrigido look_at_2d)
                ent.look_at(Vec3(player.position.x, ent.position.y,
                                 player.position.z))
                ent.position += ent.forward * ent.velocidade * time.dt
            elif dist <= 1.8:
                ent.cooldown_ataque -= time.dt
                if ent.cooldown_ataque <= 0:
                    rpg.hp -= ent.dano
                    ent.cooldown_ataque = 1.2
                    notificar(f"Recebeu {ent.dano} de dano de {ent.nome}!",
                              color.red)
                    if rpg.hp <= 0:
                        notificar("Você foi derrotado! Retornando ao Reino...",
                                  color.red)
                        rpg.recalcular_status(curar_tudo=True)
                        mundo.carregar_reino(player)

    hud.atualizar_hud()

app.run()

