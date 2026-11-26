#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador procedural de modelos 3D DETALHADOS para o DRAKMOR (RPG-PIXEL).

Modelos low-to-mid poly com normais suavizadas, UVs, materiais (.mtl),
nomes de objetos/grupos, faces trianguladas e formas organicas.
Sem dependencias externas: apenas biblioteca padrao do Python.

Como usar:
    python gerar_modelos_3d.py
Depois abra preview-3d.html para inspecionar.
"""

from __future__ import annotations

import math
import os
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Paleta expandida (RGB 0..1)
# ---------------------------------------------------------------------------
PALETA: Dict[str, Tuple[float, float, float]] = {
    "pele":             (0.85, 0.68, 0.52),
    "pele_escura":      (0.70, 0.50, 0.35),
    "cabelo":           (0.25, 0.18, 0.12),
    "cabelo_loiro":     (0.90, 0.78, 0.40),
    "barba":            (0.20, 0.16, 0.12),
    "roupa_base":       (0.55, 0.36, 0.24),
    "manto_mago":       (0.40, 0.25, 0.55),
    "manto_mago_borda": (0.60, 0.45, 0.75),
    "couro":            (0.48, 0.33, 0.22),
    "couro_escuro":     (0.35, 0.22, 0.14),
    "armadura_couro":   (0.52, 0.38, 0.28),
    "armadura_metal":   (0.72, 0.74, 0.78),
    "metal_aco":        (0.78, 0.80, 0.84),
    "metal_ouro":       (0.92, 0.75, 0.18),
    "madeira":          (0.60, 0.42, 0.26),
    "madeira_escura":   (0.42, 0.28, 0.16),
    "pedra":            (0.72, 0.72, 0.74),
    "pedra_escura":     (0.50, 0.50, 0.54),
    "slime":            (0.40, 0.85, 0.45),
    "slime_escuro":     (0.25, 0.65, 0.30),
    "goblin":           (0.45, 0.60, 0.18),
    "goblin_escuro":    (0.30, 0.45, 0.10),
    "golem":            (0.65, 0.65, 0.68),
    "golem_racha":      (0.45, 0.45, 0.48),
    "fogo":             (0.95, 0.40, 0.10),
    "cristal":          (0.55, 0.85, 1.00),
    "cristal_roxo":     (0.70, 0.40, 0.95),
    "vidro":            (0.75, 0.88, 0.95),
    "pocao_vida":       (0.92, 0.18, 0.25),
    "pocao_mana":       (0.18, 0.45, 0.95),
    "folha_verde":      (0.18, 0.58, 0.20),
    "folha_escura":     (0.10, 0.40, 0.12),
    "telhado":          (0.65, 0.15, 0.12),
    "parede_creme":     (0.88, 0.84, 0.74),
}


def _normalizar(v: Tuple[float, float, float]) -> Tuple[float, float, float]:
    x, y, z = v
    tamanho = math.sqrt(x * x + y * y + z * z)
    if tamanho == 0:
        return (0.0, 0.0, 1.0)
    return (x / tamanho, y / tamanho, z / tamanho)


def _produto_vetorial(
    a: Tuple[float, float, float], b: Tuple[float, float, float]
) -> Tuple[float, float, float]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _normal_face(
    p1: Tuple[float, float, float],
    p2: Tuple[float, float, float],
    p3: Tuple[float, float, float],
) -> Tuple[float, float, float]:
    u = (p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2])
    v = (p3[0] - p1[0], p3[1] - p1[1], p3[2] - p1[2])
    return _normalizar(_produto_vetorial(u, v))


# ---------------------------------------------------------------------------
# Construtor de malha detalhado
# ---------------------------------------------------------------------------
@dataclass
class ConstrutorMalha3D:
    """Construi uma malha 3D indexada pronta para exportar como OBJ + MTL."""

    nome: str = "objeto"
    posicoes: List[Tuple[float, float, float]] = field(default_factory=list)
    normais: List[Tuple[float, float, float]] = field(default_factory=list)
    uvs: List[Tuple[float, float]] = field(default_factory=list)
    vertices: List[Tuple[int, int, int]] = field(default_factory=list)
    _chave_para_indice: Dict[Tuple[int, int, int], int] = field(
        default_factory=dict
    )
    faces: List[Tuple[str, str, List[int]]] = field(default_factory=list)
    materiais: Dict[str, Tuple[float, float, float]] = field(default_factory=dict)
    material_atual: Optional[str] = None
    grupo_atual: str = "default"

    # ------------------------------------------------------------------
    def adicionar_vertice(
        self,
        x: float,
        y: float,
        z: float,
        nx: float = 0.0,
        ny: float = 0.0,
        nz: float = 1.0,
        u: float = 0.0,
        v: float = 0.0,
    ) -> int:
        normal = _normalizar((nx, ny, nz))
        p_idx = len(self.posicoes) + 1
        self.posicoes.append((x, y, z))
        n_idx = len(self.normais) + 1
        self.normais.append(normal)
        uv_idx = len(self.uvs) + 1
        self.uvs.append((u, v))
        chave = (p_idx, n_idx, uv_idx)
        indice = self._chave_para_indice.get(chave)
        if indice is None:
            indice = len(self.vertices) + 1
            self._chave_para_indice[chave] = indice
            self.vertices.append(chave)
        return indice

    def definir_material(self, nome: str, cor: Tuple[float, float, float]) -> None:
        self.material_atual = nome
        if nome not in self.materiais:
            self.materiais[nome] = cor

    def definir_grupo(self, nome: str) -> None:
        self.grupo_atual = nome

    def _material(self) -> str:
        return self.material_atual or "padrao"

    def adicionar_face(self, indices: List[int], material: Optional[str] = None,
                       grupo: Optional[str] = None) -> None:
        if len(indices) < 3:
            return
        mat = material if material is not None else self._material()
        grp = grupo if grupo is not None else self.grupo_atual
        for i in range(1, len(indices) - 1):
            self.faces.append((mat, grp, [indices[0], indices[i], indices[i + 1]]))

    def _face_uv_plana(
        self,
        pontos: List[Tuple[float, float, float]],
        normal: Tuple[float, float, float],
        escala_u: float = 1.0,
        escala_v: float = 1.0,
        flip_v: bool = True,
    ) -> List[Tuple[float, float]]:
        nx, ny, nz = abs(normal[0]), abs(normal[1]), abs(normal[2])
        uvs: List[Tuple[float, float]] = []
        for x, y, z in pontos:
            if nz > nx and nz > ny:
                uu, vv = x, y
            elif ny > nx and ny > nz:
                uu, vv = x, z
            else:
                uu, vv = z, y
            u = (uu * escala_u + 0.5)
            v = (vv * escala_v + 0.5)
            if flip_v:
                v = 1.0 - v
            uvs.append((u, v))
        return uvs

    # ------------------------------------------------------------------
    # primitivos detalhados
    # ------------------------------------------------------------------
    def adicionar_caixa(
        self,
        cx: float,
        cy: float,
        cz: float,
        lx: float,
        ay: float,
        pz: float,
        material: str = "padrao",
        grupo: Optional[str] = None,
        suave: bool = False,
    ) -> None:
        """Paralelepipedo centrado com arestas duras (ou suaves se suave=True)."""
        hx, hy, hz = lx / 2.0, ay / 2.0, pz / 2.0
        corners = [
            (cx - hx, cy - hy, cz - hz),  # 0
            (cx + hx, cy - hy, cz - hz),  # 1
            (cx + hx, cy + hy, cz - hz),  # 2
            (cx - hx, cy + hy, cz - hz),  # 3
            (cx - hx, cy - hy, cz + hz),  # 4
            (cx + hx, cy - hy, cz + hz),  # 5
            (cx + hx, cy + hy, cz + hz),  # 6
            (cx - hx, cy + hy, cz + hz),  # 7
        ]
        faces_def = [
            ([0, 3, 2, 1], (0.0, 0.0, -1.0)),  # tras
            ([4, 5, 6, 7], (0.0, 0.0, 1.0)),   # frente
            ([0, 1, 5, 4], (-1.0, 0.0, 0.0)),  # esquerda
            ([2, 3, 7, 6], (1.0, 0.0, 0.0)),   # direita
            ([0, 4, 7, 3], (0.0, -1.0, 0.0)),  # embaixo
            ([1, 2, 6, 5], (0.0, 1.0, 0.0)),   # cima
        ]
        self.definir_material(material, PALETA.get(material, (0.8, 0.8, 0.8)))
        if grupo is not None:
            self.definir_grupo(grupo)
        for indices, normal in faces_def:
            pts = [corners[i] for i in indices]
            n = normal if not suave else _normal_face(pts[0], pts[1], pts[2])
            uvs = self._face_uv_plana(pts, normal, lx, ay)
            vidxs = []
            for pt, uv in zip(pts, uvs):
                vi = self.adicionar_vertice(pt[0], pt[1], pt[2], n[0], n[1], n[2], uv[0], uv[1])
                vidxs.append(vi)
            self.adicionar_face(vidxs, material=material, grupo=grupo)

    def adicionar_cone(
        self,
        cx: float,
        cy: float,
        cz: float,
        raio: float,
        altura: float,
        segmentos: int = 16,
        material: str = "padrao",
        grupo: Optional[str] = None,
        sem_base: bool = False,
        topo_aberto: bool = False,
    ) -> None:
        """Cone / piramide com mais segmentos para ficar menos angular."""
        self.definir_material(material, PALETA.get(material, (0.8, 0.8, 0.8)))
        if grupo is not None:
            self.definir_grupo(grupo)

        base_idx: List[int] = []
        for i in range(segmentos):
            ang = (2 * math.pi * i) / segmentos
            vx = cx + math.cos(ang) * raio
            vz = cz + math.sin(ang) * raio
            nx = math.cos(ang)
            nz = math.sin(ang)
            normal = _normalizar((nx, 0.25, nz))
            u = i / segmentos
            base_idx.append(self.adicionar_vertice(vx, cy, vz, normal[0], normal[1], normal[2], u, 0.0))

        centro_base_idx = self.adicionar_vertice(cx, cy, cz, 0.0, -1.0, 0.0, 0.5, 0.5)
        topo_idx = self.adicionar_vertice(cx, cy + altura, cz, 0.0, 1.0, 0.0, 0.5, 1.0)

        for i in range(segmentos):
            prox = (i + 1) % segmentos
            self.adicionar_face(
                [base_idx[i], topo_idx, base_idx[prox]],
                material=material, grupo=grupo,
            )

        if not sem_base:
            for i in range(segmentos):
                prox = (i + 1) % segmentos
                self.adicionar_face(
                    [centro_base_idx, base_idx[prox], base_idx[i]],
                    material=material, grupo=grupo,
                )

    def adicionar_cilindro(
        self,
        cx: float,
        cy: float,
        cz: float,
        raio: float,
        altura: float,
        segmentos: int = 16,
        material: str = "padrao",
        grupo: Optional[str] = None,
        sem_topo: bool = False,
        sem_base: bool = False,
    ) -> None:
        """Cilindro com mais segmentos para ficar menos angular."""
        self.definir_material(material, PALETA.get(material, (0.8, 0.8, 0.8)))
        if grupo is not None:
            self.definir_grupo(grupo)

        inf_idx: List[int] = []
        sup_idx: List[int] = []
        for i in range(segmentos):
            ang = (2 * math.pi * i) / segmentos
            vx = cx + math.cos(ang) * raio
            vz = cz + math.sin(ang) * raio
            nx = math.cos(ang)
            nz = math.sin(ang)
            normal = _normalizar((nx, 0.0, nz))
            u = i / segmentos
            inf_idx.append(self.adicionar_vertice(vx, cy, vz, normal[0], normal[1], normal[2], u, 0.0))
            sup_idx.append(self.adicionar_vertice(vx, cy + altura, vz, normal[0], normal[1], normal[2], u, 1.0))

        centro_inf = self.adicionar_vertice(cx, cy, cz, 0.0, -1.0, 0.0, 0.5, 0.5)
        centro_sup = self.adicionar_vertice(cx, cy + altura, cz, 0.0, 1.0, 0.0, 0.5, 0.5)

        for i in range(segmentos):
            prox = (i + 1) % segmentos
            self.adicionar_face(
                [inf_idx[i], sup_idx[i], sup_idx[prox], inf_idx[prox]],
                material=material, grupo=grupo,
            )
        if not sem_base:
            for i in range(segmentos):
                prox = (i + 1) % segmentos
                self.adicionar_face(
                    [centro_inf, inf_idx[prox], inf_idx[i]],
                    material=material, grupo=grupo,
                )
        if not sem_topo:
            for i in range(segmentos):
                prox = (i + 1) % segmentos
                self.adicionar_face(
                    [centro_sup, sup_idx[i], sup_idx[prox]],
                    material=material, grupo=grupo,
                )

    # ------------------------------------------------------------------
    # Suavizacao e formas organicas
    # ------------------------------------------------------------------
    def suavizar_normais(self) -> None:
        """Media as normais das faces adjacentes para remover aspecto faceto."""
        grupos: Dict[Tuple[float, float, float], List[int]] = {}
        for vi, (p_idx, n_idx, uv_idx) in enumerate(self.vertices, start=1):
            pos = self.posicoes[p_idx - 1]
            grupos.setdefault(pos, []).append(vi)

        somas: Dict[int, List[float]] = {}
        for material, grupo, indices in self.faces:
            vns = [self.normais[self.vertices[i - 1][1] - 1] for i in indices]
            n_face = _normalizar((
                sum(v[0] for v in vns) / len(vns),
                sum(v[1] for v in vns) / len(vns),
                sum(v[2] for v in vns) / len(vns),
            ))
            for vi in indices:
                somas.setdefault(vi, [0.0, 0.0, 0.0])
                somas[vi][0] += n_face[0]
                somas[vi][1] += n_face[1]
                somas[vi][2] += n_face[2]

        for pos, vis in grupos.items():
            sx = sy = sz = 0.0
            for vi in vis:
                s = somas.get(vi, [0.0, 0.0, 0.0])
                sx += s[0]; sy += s[1]; sz += s[2]
            n_media = _normalizar((sx, sy, sz))
            for vi in vis:
                p_idx, _, uv_idx = self.vertices[vi - 1]
                n_idx = len(self.normais) + 1
                self.normais.append(n_media)
                self.vertices[vi - 1] = (p_idx, n_idx, uv_idx)

    def adicionar_esfera_organica(
        self,
        cx: float,
        cy: float,
        cz: float,
        raio_base: float,
        segmentos: int = 18,
        irregularidade: float = 0.10,
        material: str = "padrao",
        grupo: Optional[str] = None,
        semente: Optional[int] = None,
    ) -> None:
        """Esfera com raio variado por ruido senoidal (pedras, orbs, slimes)."""
        if semente is not None:
            random.seed(semente)
        self.definir_material(material, PALETA.get(material, (0.8, 0.8, 0.8)))
        if grupo is not None:
            self.definir_grupo(grupo)

        aneis = max(4, segmentos // 2)
        fatias = segmentos
        vertices_anel: List[List[int]] = []

        for r in range(aneis + 1):
            lat0 = math.pi * (-0.5 + (r / aneis))
            seno_lat = math.sin(lat0)
            coss_lat = math.cos(lat0)
            linha: List[int] = []
            for s in range(fatias + 1):
                lon = 2 * math.pi * (s / fatias)
                variacao = (
                    math.sin(lon * 3 + lat0 * 5) *
                    math.cos(lon * 5 - lat0 * 3) *
                    irregularidade
                )
                raio = raio_base * (1.0 + variacao)
                x = cx + math.cos(lon) * coss_lat * raio
                y = cy + seno_lat * raio
                z = cz + math.sin(lon) * coss_lat * raio
                nx = math.cos(lon) * coss_lat
                nz = math.sin(lon) * coss_lat
                ny = seno_lat
                normal = _normalizar((nx, ny, nz))
                u = s / fatias
                v = r / aneis
                linha.append(self.adicionar_vertice(x, y, z,
                                                    normal[0], normal[1], normal[2], u, v))
            vertices_anel.append(linha)

        for r in range(aneis):
            for s in range(fatias):
                a = vertices_anel[r][s]
                b = vertices_anel[r][s + 1]
                c = vertices_anel[r + 1][s + 1]
                d = vertices_anel[r + 1][s]
                self.adicionar_face([a, b, c], material=material, grupo=grupo)
                self.adicionar_face([a, c, d], material=material, grupo=grupo)

        if semente is not None:
            random.seed(None)

    def adicionar_blob(
        self,
        cx: float,
        cy: float,
        cz: float,
        raio_base: float,
        segmentos: int = 16,
        material: str = "slime",
        grupo: Optional[str] = None,
        semente: Optional[int] = None,
    ) -> None:
        """Blob organico (slime/gelatina): sobrepoe esferas irregulares."""
        if semente is not None:
            random.seed(semente)
        self.definir_material(material, PALETA.get(material, (0.8, 0.8, 0.8)))
        if grupo is not None:
            self.definir_grupo(grupo)

        camadas = random.randint(4, 6)
        for camada in range(camadas):
            offset_y = (camada - camadas / 2) * raio_base * 0.30
            raio = raio_base * random.uniform(0.70, 1.10)
            self.adicionar_esfera_organica(
                cx + random.uniform(-0.12, 0.12),
                cy + offset_y + random.uniform(-0.08, 0.08),
                cz + random.uniform(-0.12, 0.12),
                raio,
                segmentos=segmentos,
                irregularidade=random.uniform(0.06, 0.18),
                material=material,
                grupo=f"{grupo or 'blob'}_{camada}",
                semente=semente + camada if semente is not None else None,
            )

        if semente is not None:
            random.seed(None)

    def adicionar_arvore_organica(
        self,
        cx: float,
        cy: float,
        cz: float,
        altura_tronco: float = 2.2,
        raio_tronco: float = 0.28,
        material_madeira: str = "madeira",
        material_folha: str = "folha_verde",
        grupo: Optional[str] = None,
        semente: Optional[int] = None,
    ) -> None:
        """Arvore com tronco levemente torto e copa de esferas sobrepostas."""
        if semente is not None:
            random.seed(semente)
        # tronco com pequena curva (varios cilindros sobrepostos)
        segmentos_tronco = int(altura_tronco / 0.5)
        for i in range(segmentos_tronco):
            y_base = cy + i * 0.5
            desvio_x = math.sin(i * 0.8) * 0.06
            desvio_z = math.cos(i * 0.8) * 0.06
            raio = raio_tronco * random.uniform(0.85, 1.15)
            self.adicionar_cilindro(
                cx + desvio_x, y_base, cz + desvio_z,
                raio, 0.55, segmentos=10,
                material=material_madeira, grupo=f"{grupo or 'arvore'}_tronco",
            )
        # copa: 5-7 esferas organicas em alturas variadas
        niveis_copa = random.randint(5, 7)
        for n in range(niveis_copa):
            h = cy + altura_tronco + n * altura_tronco * 0.50 + random.uniform(-0.25, 0.25)
            r = random.uniform(1.0, 1.6)
            self.adicionar_esfera_organica(
                cx + random.uniform(-0.35, 0.35),
                h,
                cz + random.uniform(-0.35, 0.35),
                r,
                segmentos=14,
                irregularidade=random.uniform(0.10, 0.25),
                material=material_folha,
                grupo=f"{grupo or 'arvore'}_copa_{n}",
                semente=semente + 100 + n if semente is not None else None,
            )

        if semente is not None:
            random.seed(None)

    def adicionar_montanha_organica(
        self,
        cx: float,
        cy: float,
        cz: float,
        raio_base: float,
        altura: float,
        picos: int = 5,
        material: str = "pedra",
        grupo: Optional[str] = None,
        semente: Optional[int] = None,
    ) -> None:
        """Montanha com varios picos de raios e alturas variados."""
        if semente is not None:
            random.seed(semente)
        self.definir_material(material, PALETA.get(material, (0.8, 0.8, 0.8)))
        if grupo is not None:
            self.definir_grupo(grupo)

        for p in range(picos):
            rx = random.uniform(-raio_base * 0.45, raio_base * 0.45)
            rz = random.uniform(-raio_base * 0.45, raio_base * 0.45)
            r = raio_base * random.uniform(0.45, 1.0)
            h = altura * random.uniform(0.55, 1.0)
            seg = random.randint(10, 16)
            self.adicionar_cone(
                cx + rx, cy, cz + rz,
                r, h, segmentos=seg,
                material=material,
                grupo=f"{grupo or 'montanha'}_pico_{p}",
                sem_base=True,
            )

        if semente is not None:
            random.seed(None)

