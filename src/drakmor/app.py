from __future__ import annotations

import random

import pygame

from .catalog import default_character, item_for_character, load_character_catalog, load_classes
from .compositor import compose_character
from .creator import CATEGORY_SPECS, CharacterCreator
from .models import load_character, save_character
from .paths import SAVE_PATH
from .sprite_manager import Direction, SpriteAssetError, SpriteManager


BACKGROUND = (13, 16, 23)
PANEL = (25, 29, 39)
PANEL_ALT = (32, 37, 48)
GOLD = (218, 180, 112)
GOLD_BRIGHT = (244, 211, 151)
TEXT = (235, 231, 220)
MUTED = (167, 174, 187)
WARNING = (237, 177, 115)
ERROR = (240, 129, 129)


class DrakmorApp:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Drakmor — Criação de personagem")
        self.screen = pygame.display.set_mode((1280, 800), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 22)
        self.small_font = pygame.font.Font(None, 17)
        self.tiny_font = pygame.font.Font(None, 14)
        self.title_font = pygame.font.Font(None, 58)

        self.classes = load_classes()
        self.catalog = load_character_catalog()
        self.character = default_character(self.classes)
        self.creator = CharacterCreator(self.classes, self.catalog, self.character)
        self.sprites = SpriteManager()
        self.state = "menu"
        self.fullscreen = False
        self.name_focused = False
        self.focused_category = 0
        self.missing_scroll = 0
        self.status_message = ""
        self.status_color = MUTED
        self.asset_error = ""
        self.running = True

    def run(self) -> None:
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            self._handle_key(event)
        elif event.type == pygame.TEXTINPUT and self.state == "creator" and self.name_focused:
            self.character.name = (self.character.name + event.text)[:24]
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)
        elif event.type == pygame.MOUSEWHEEL and self.state == "creator":
            if self._creator_layout()["preview"].collidepoint(pygame.mouse.get_pos()):
                self.missing_scroll = max(0, self.missing_scroll - event.y)

    def _handle_key(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_F11:
            self._toggle_fullscreen()
            return
        if event.key == pygame.K_ESCAPE:
            if self.state != "menu":
                self.state = "menu"
                self._set_name_focus(False)
            else:
                self.running = False
            return

        if self.state != "creator":
            if self.state == "menu" and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._new_character()
            return

        if event.key == pygame.K_BACKSPACE and self.name_focused:
            self.character.name = self.character.name[:-1]
        elif event.key == pygame.K_TAB:
            self._set_name_focus(False)
            self.focused_category = (self.focused_category + 1) % len(CATEGORY_SPECS)
        elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            if self.name_focused:
                return
            step = -1 if event.key == pygame.K_LEFT else 1
            _, category, _ = CATEGORY_SPECS[self.focused_category]
            self.creator.cycle(category, step)
        elif event.key in (pygame.K_UP, pygame.K_DOWN):
            self._set_name_focus(False)
            class_ids = tuple(self.classes)
            current = class_ids.index(self.character.class_id)
            step = -1 if event.key == pygame.K_UP else 1
            self.creator.select_class(class_ids[(current + step) % len(class_ids)])
        elif event.key == pygame.K_r and not self.name_focused:
            self.creator.randomize(random.Random())
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._confirm_character()

    def _handle_click(self, position: tuple[int, int]) -> None:
        if self.state == "menu":
            self._handle_menu_click(position)
        elif self.state == "settings":
            self._handle_settings_click(position)
        elif self.state == "creator":
            self._handle_creator_click(position)

    def _handle_menu_click(self, position: tuple[int, int]) -> None:
        buttons = self._menu_buttons()
        if buttons["create"].collidepoint(position):
            self._new_character()
        elif buttons["continue"].collidepoint(position) and SAVE_PATH.is_file():
            try:
                self.character = load_character(SAVE_PATH, self.classes, self.catalog)
                self.creator = CharacterCreator(self.classes, self.catalog, self.character)
                self.state = "creator"
                self.status_message = "Personagem salvo carregado."
                self.status_color = GOLD_BRIGHT
            except (OSError, ValueError, TypeError) as error:
                self._set_status(f"Não foi possível carregar: {error}", ERROR)
        elif buttons["settings"].collidepoint(position):
            self.state = "settings"
        elif buttons["exit"].collidepoint(position):
            self.running = False

    def _handle_settings_click(self, position: tuple[int, int]) -> None:
        toggle, back = self._settings_buttons()
        if toggle.collidepoint(position):
            self._toggle_fullscreen()
        elif back.collidepoint(position):
            self.state = "menu"

    def _handle_creator_click(self, position: tuple[int, int]) -> None:
        layout = self._creator_layout()
        if layout["name"].collidepoint(position):
            self._set_name_focus(True)
            return
        self._set_name_focus(False)

        for class_id, rect in layout["classes"].items():
            if rect.collidepoint(position):
                self.creator.select_class(class_id)
                return

        for _, category, rects in layout["categories"]:
            previous, following, card = rects
            if previous.collidepoint(position):
                self.creator.cycle(category, -1)
                return
            if following.collidepoint(position):
                self.creator.cycle(category, 1)
                return
            if card.collidepoint(position):
                self.focused_category = next(
                    index for index, (_, key, _) in enumerate(CATEGORY_SPECS) if key == category
                )
                self.creator.cycle(category, 1)
                return

        buttons = layout["buttons"]
        if buttons["random"].collidepoint(position):
            self.creator.randomize()
        elif buttons["back"].collidepoint(position):
            self.state = "menu"
        elif buttons["confirm"].collidepoint(position):
            self._confirm_character()

    def _new_character(self) -> None:
        self.character = default_character(self.classes)
        self.creator = CharacterCreator(self.classes, self.catalog, self.character)
        self.state = "creator"
        self._set_name_focus(False)
        self.status_message = ""

    def _confirm_character(self) -> None:
        try:
            save_character(SAVE_PATH, self.character, self.classes, self.catalog)
        except (OSError, ValueError, TypeError) as error:
            self._set_status(f"Não foi possível salvar: {error}", ERROR)
            return
        missing_count = len(self.creator.missing_assets(self.sprites))
        message = "Personagem salvo em saves/player.json."
        if missing_count:
            message += f" PNGs selecionados ausentes: {missing_count}."
        self._set_status(message, WARNING if missing_count else GOLD_BRIGHT)
        self.state = "menu"
        self._set_name_focus(False)

    def _set_name_focus(self, focused: bool) -> None:
        if self.name_focused == focused:
            return
        self.name_focused = focused
        if focused:
            pygame.key.start_text_input()
        else:
            pygame.key.stop_text_input()

    def _set_status(self, message: str, color: tuple[int, int, int]) -> None:
        self.status_message = message
        self.status_color = color

    def _toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((1280, 800), pygame.RESIZABLE)

    def _menu_buttons(self) -> dict[str, pygame.Rect]:
        width, height = self.screen.get_size()
        button_width, button_height, gap = min(390, width - 48), 54, 14
        left = (width - button_width) // 2
        first_y = max(210, height // 2 - 115)
        return {
            "create": pygame.Rect(left, first_y, button_width, button_height),
            "continue": pygame.Rect(left, first_y + button_height + gap, button_width, button_height),
            "settings": pygame.Rect(left, first_y + 2 * (button_height + gap), button_width, button_height),
            "exit": pygame.Rect(left, first_y + 3 * (button_height + gap), button_width, button_height),
        }

    def _settings_buttons(self) -> tuple[pygame.Rect, pygame.Rect]:
        width, height = self.screen.get_size()
        left = (width - 360) // 2
        return (
            pygame.Rect(left, height // 2 - 15, 360, 54),
            pygame.Rect(left, height // 2 + 55, 360, 54),
        )

    def _creator_layout(self) -> dict:
        width, height = self.screen.get_size()
        margin = 24
        panel_top = 92
        panel_height = max(360, height - 178)
        preview_width = min(320, max(260, int(width * 0.27)))
        preview = pygame.Rect(margin, panel_top, preview_width, panel_height)
        form_left = preview.right + 18
        form = pygame.Rect(form_left, panel_top, max(320, width - form_left - margin), panel_height)

        inner_gap = 8
        card_left = form.left + 14
        card_width = (form.width - 28 - inner_gap * 2) // 3
        class_rects = {}
        class_ids = tuple(self.classes)
        class_top = form.top + 12
        class_height = 88
        for index, class_id in enumerate(class_ids):
            column, row = index % 3, index // 3
            class_rects[class_id] = pygame.Rect(
                card_left + column * (card_width + inner_gap),
                class_top + row * (class_height + inner_gap),
                card_width,
                class_height,
            )

        category_top = class_top + 272
        category_gap = 8
        category_width = (form.width - 28 - category_gap * 3) // 4
        category_height = min(
            88,
            max(76, (form.bottom - category_top - category_gap * 2 - 8) // 3),
        )
        category_rects = []
        for index, (label, category, _) in enumerate(CATEGORY_SPECS):
            column, row = index % 4, index // 4
            rect = pygame.Rect(
                card_left + column * (category_width + category_gap),
                category_top + row * (category_height + category_gap),
                category_width,
                category_height,
            )
            previous = pygame.Rect(rect.right - 54, rect.bottom - 31, 24, 23)
            following = pygame.Rect(rect.right - 27, rect.bottom - 31, 24, 23)
            category_rects.append((label, category, (previous, following, rect)))

        name_rect = pygame.Rect(preview.left + 14, preview.top + 39, preview.width - 28, 34)
        footer_y = height - 66
        button_width = min(190, max(120, (width - 72) // 5))
        button_gap = 12
        total_width = button_width * 3 + button_gap * 2
        button_left = width - margin - total_width
        buttons = {
            "random": pygame.Rect(button_left, footer_y, button_width, 44),
            "back": pygame.Rect(button_left + button_width + button_gap, footer_y, button_width, 44),
            "confirm": pygame.Rect(button_left + (button_width + button_gap) * 2, footer_y, button_width, 44),
        }
        return {
            "preview": preview,
            "form": form,
            "name": name_rect,
            "classes": class_rects,
            "categories": category_rects,
            "buttons": buttons,
        }

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)
        if self.state == "menu":
            self._draw_menu()
        elif self.state == "settings":
            self._draw_settings()
        elif self.state == "creator":
            self._draw_creator()
        if self.status_message:
            self._draw_status()

    def _draw_menu(self) -> None:
        width, height = self.screen.get_size()
        title = self.title_font.render("DRAKMOR", True, GOLD_BRIGHT)
        subtitle = self.font.render("REGISTRO DE JORNADA · CRIADOR DE PERSONAGENS", True, MUTED)
        self.screen.blit(title, title.get_rect(center=(width // 2, max(100, height // 3))))
        self.screen.blit(subtitle, subtitle.get_rect(center=(width // 2, max(145, height // 3 + 42))))
        labels = {
            "create": "Criar personagem",
            "continue": "Carregar personagem salvo",
            "settings": "Configurações",
            "exit": "Sair",
        }
        for key, rect in self._menu_buttons().items():
            enabled = key != "continue" or SAVE_PATH.is_file()
            self._draw_button(rect, labels[key], enabled=enabled)
        self._draw_centered("Enter: criar personagem · F11: tela cheia", height - 40, self.small_font, MUTED)

    def _draw_settings(self) -> None:
        width, height = self.screen.get_size()
        panel = pygame.Rect(width // 2 - 250, height // 2 - 135, 500, 300)
        self._draw_panel(panel)
        self._draw_centered("Configurações", panel.top + 42, self.title_font, GOLD_BRIGHT)
        toggle, back = self._settings_buttons()
        self._draw_button(toggle, f"Tela cheia: {'Ativada' if self.fullscreen else 'Desativada'}")
        self._draw_button(back, "Voltar")
        self._draw_centered("F11 alterna o modo de tela em qualquer tela.", panel.bottom - 24, self.small_font, MUTED)

    def _draw_creator(self) -> None:
        layout = self._creator_layout()
        self._draw_text("CRIADOR DE PERSONAGEM", 26, 22, self.title_font, GOLD_BRIGHT)
        self._draw_panel(layout["preview"])
        self._draw_panel(layout["form"])
        self._draw_preview(layout["preview"], layout["name"])
        self._draw_classes(layout["form"], layout["classes"])
        self._draw_categories(layout["categories"])
        for key, rect in layout["buttons"].items():
            label = {"random": "Aleatório", "back": "Voltar", "confirm": "Confirmar"}[key]
            self._draw_button(rect, label, highlighted=key == "confirm")
        self._draw_text(
            "Tab seleciona opção · ←/→ altera · ↑/↓ classe · R aleatório · Enter confirma · Esc volta",
            26,
            self.screen.get_height() - 24,
            self.small_font,
            MUTED,
        )

    def _draw_preview(self, panel: pygame.Rect, name_rect: pygame.Rect) -> None:
        self._draw_text("NOME", panel.left + 16, panel.top + 15, self.small_font, MUTED)
        pygame.draw.rect(self.screen, PANEL_ALT, name_rect, border_radius=5)
        pygame.draw.rect(
            self.screen,
            GOLD if self.name_focused else (82, 86, 97),
            name_rect,
            width=2,
            border_radius=5,
        )
        name_surface = self.font.render(self.character.name or "", True, TEXT)
        self.screen.blit(name_surface, (name_rect.left + 9, name_rect.centery - name_surface.get_height() // 2))
        preview_size = min(256, panel.width - 48, panel.height // 2)
        image_rect = pygame.Rect(
            panel.centerx - preview_size // 2,
            panel.top + 91,
            preview_size,
            preview_size,
        )
        missing = self.creator.missing_assets(self.sprites)
        if missing:
            self._draw_text(
                "Prévia indisponível: PNGs de camadas ausentes.",
                panel.left + 14,
                image_rect.bottom + 5,
                self.small_font,
                WARNING,
                max_width=panel.width - 28,
            )
        else:
            try:
                image = compose_character(
                    self.sprites,
                    self.creator.layer_assets(),
                    Direction.SOUTH,
                    0,
                )
                scaled = pygame.transform.scale(image, image_rect.size)
                self.screen.blit(scaled, image_rect)
            except SpriteAssetError as error:
                self.asset_error = str(error)
                self._draw_text(
                    "Erro no sprite selecionado.",
                    panel.left + 14,
                    image_rect.bottom + 5,
                    self.small_font,
                    ERROR,
                    max_width=panel.width - 28,
                )

        profile = self.classes[self.character.class_id]
        profile_y = image_rect.bottom + 30
        self._draw_text(
            f"{profile['name']} · Nv. 1",
            panel.left + 14,
            profile_y,
            self.font,
            GOLD_BRIGHT,
            max_width=panel.width - 28,
        )
        self._draw_text(
            f"PV {profile['stats']['hp']}  PM {profile['stats']['mp']}  "
            f"FOR {profile['stats']['strength']}  INT {profile['stats']['intelligence']}",
            panel.left + 14,
            profile_y + 23,
            self.small_font,
            TEXT,
            max_width=panel.width - 28,
        )

        missing_y = profile_y + 53
        if missing:
            self._draw_text(
                f"PNG selecionados ausentes ({len(missing)}):",
                panel.left + 14,
                missing_y,
                self.small_font,
                WARNING,
            )
            line_y = missing_y + 19
            available_height = max(0, panel.bottom - line_y - 10)
            line_height = 14
            max_lines = max(1, available_height // line_height)
            max_scroll = max(0, len(missing) - max_lines)
            self.missing_scroll = min(self.missing_scroll, max_scroll)
            visible_paths = missing[self.missing_scroll : self.missing_scroll + max_lines]
            for asset_path in visible_paths:
                self._draw_text(
                    asset_path,
                    panel.left + 14,
                    line_y,
                    self.tiny_font,
                    MUTED,
                    max_width=panel.width - 28,
                )
                line_y += line_height
            if max_scroll:
                self._draw_text(
                    f"Roda do mouse: ver outros caminhos ({self.missing_scroll + 1}-{self.missing_scroll + len(visible_paths)} de {len(missing)}).",
                    panel.left + 14,
                    panel.bottom - 24,
                    self.tiny_font,
                    MUTED,
                    max_width=panel.width - 28,
                )
        elif self.asset_error:
            self._draw_text(
                self.asset_error,
                panel.left + 14,
                missing_y,
                self.tiny_font,
                ERROR,
                max_width=panel.width - 28,
            )

    def _draw_classes(self, panel: pygame.Rect, rects: dict[str, pygame.Rect]) -> None:
        for class_id, rect in rects.items():
            profile = self.classes[class_id]
            selected = class_id == self.character.class_id
            pygame.draw.rect(self.screen, PANEL_ALT if selected else BACKGROUND, rect, border_radius=7)
            pygame.draw.rect(
                self.screen,
                GOLD if selected else (74, 78, 89),
                rect,
                width=2 if selected else 1,
                border_radius=7,
            )
            self._draw_text(profile["name"], rect.left + 9, rect.top + 7, self.font, GOLD_BRIGHT if selected else TEXT)
            self._draw_text(
                profile["description"],
                rect.left + 9,
                rect.top + 31,
                self.tiny_font,
                MUTED,
                max_width=rect.width - 18,
            )
            stats = profile["stats"]
            self._draw_text(
                f"PV {stats['hp']} · PM {stats['mp']} · FOR {stats['strength']} · INT {stats['intelligence']}",
                rect.left + 9,
                rect.top + 50,
                self.tiny_font,
                TEXT,
                max_width=rect.width - 18,
            )
            self._draw_text(
                f"AGI {stats['agility']} · DEF {stats['defense']} · ATQ {stats['attack']}",
                rect.left + 9,
                rect.top + 66,
                self.tiny_font,
                TEXT,
                max_width=rect.width - 18,
            )

        selected = self.classes[self.character.class_id]
        gear_names = [
            item_for_character(self.character, self.catalog, category)["name"]
            for category in ("shirts", "armor", "pants", "boots", "cloaks", "weapons", "accessories")
        ]
        equipment = " · ".join(name for name in gear_names if not name.startswith("Sem "))
        detail_y = panel.top + 205
        ability = selected["ability"]
        detail = (
            f"Habilidade: {ability['name']} ({ability['mana_cost']} mana) — {ability['description']}"
        )
        self._draw_text(detail, panel.left + 14, detail_y, self.small_font, GOLD_BRIGHT, max_width=panel.width - 28)
        self._draw_text(
            f"Equipamento inicial: {equipment}",
            panel.left + 14,
            detail_y + 18,
            self.tiny_font,
            MUTED,
            max_width=panel.width - 28,
        )

    def _draw_categories(self, categories: list) -> None:
        if categories:
            self._draw_text(
                "APARÊNCIA E EQUIPAMENTOS",
                categories[0][2][2].left,
                categories[0][2][2].top - 22,
                self.small_font,
                GOLD_BRIGHT,
            )
        for index, (label, category, rects) in enumerate(categories):
            previous, following, card = rects
            selected = index == self.focused_category
            pygame.draw.rect(self.screen, PANEL_ALT, card, border_radius=6)
            pygame.draw.rect(
                self.screen,
                GOLD if selected else (74, 78, 89),
                card,
                width=2 if selected else 1,
                border_radius=6,
            )
            self._draw_text(label, card.left + 8, card.top + 7, self.tiny_font, GOLD_BRIGHT)
            item = item_for_character(self.character, self.catalog, category)
            asset_path = self.creator.layer_assets().get(
                {
                    "genders": "body",
                    "skin_tones": "face",
                    "hair_styles": "hair",
                    "hair_colors": "hair",
                    "eye_colors": "eyes",
                    "shirts": "shirt",
                    "armor": "armor",
                    "pants": "pants",
                    "boots": "boots",
                    "cloaks": "cloak",
                    "weapons": "weapon",
                    "accessories": "accessory",
                }[category]
            )
            image_rect = pygame.Rect(card.left + 7, card.top + 30, 40, 40)
            if asset_path and self.sprites.exists(asset_path):
                try:
                    icon = self.sprites.frame(asset_path, Direction.SOUTH, 0)
                    self.screen.blit(pygame.transform.scale(icon, image_rect.size), image_rect)
                except SpriteAssetError as error:
                    self.asset_error = str(error)
                    self._draw_text("PNG inválido", image_rect.left, image_rect.top + 12, self.tiny_font, ERROR)
            else:
                state = "Opcional" if asset_path is None else "PNG ausente"
                state_color = MUTED if asset_path is None else WARNING
                self._draw_text(state, image_rect.left, image_rect.top + 12, self.tiny_font, state_color)

            name_rect = pygame.Rect(card.left + 53, card.top + 28, card.width - 112, 42)
            self._draw_text(
                item["name"],
                name_rect.left,
                name_rect.top,
                self.tiny_font,
                TEXT,
                max_width=name_rect.width,
            )
            self._draw_button(previous, "<", compact=True)
            self._draw_button(following, ">", compact=True)

    def _draw_button(
        self,
        rect: pygame.Rect,
        label: str,
        enabled: bool = True,
        highlighted: bool = False,
        compact: bool = False,
    ) -> None:
        fill = (65, 51, 35) if highlighted else PANEL_ALT
        border = GOLD if highlighted else (89, 75, 55)
        if not enabled:
            fill = (30, 32, 39)
            border = (56, 59, 67)
        pygame.draw.rect(self.screen, fill, rect, border_radius=5)
        pygame.draw.rect(self.screen, border, rect, width=1, border_radius=5)
        font = self.small_font if compact else self.font
        color = TEXT if enabled else MUTED
        label_surface = font.render(label, True, color)
        self.screen.blit(label_surface, label_surface.get_rect(center=rect.center))

    def _draw_panel(self, rect: pygame.Rect) -> None:
        pygame.draw.rect(self.screen, PANEL, rect, border_radius=10)
        pygame.draw.rect(self.screen, (95, 78, 55), rect, width=1, border_radius=10)

    def _draw_text(
        self,
        text: str,
        x: int,
        y: int,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        max_width: int | None = None,
    ) -> int:
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if max_width and current and font.size(candidate)[0] > max_width:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
        for line_index, line in enumerate(lines):
            surface = font.render(line, True, color)
            self.screen.blit(surface, (x, y + line_index * (font.get_linesize() + 1)))
        return len(lines)

    def _draw_centered(
        self,
        text: str,
        y: int,
        font: pygame.font.Font,
        color: tuple[int, int, int],
    ) -> None:
        surface = font.render(text, True, color)
        self.screen.blit(surface, surface.get_rect(center=(self.screen.get_width() // 2, y)))

    def _draw_status(self) -> None:
        width, height = self.screen.get_size()
        surface = self.small_font.render(self.status_message, True, self.status_color)
        max_width = max(100, width - 40)
        if surface.get_width() > max_width:
            surface = self.small_font.render(self.status_message[: max(10, len(self.status_message) // 2)] + "...", True, self.status_color)
        self.screen.blit(surface, surface.get_rect(center=(width // 2, height - 18)))


def main() -> None:
    app = DrakmorApp()
    try:
        app.run()
    finally:
        pygame.quit()

