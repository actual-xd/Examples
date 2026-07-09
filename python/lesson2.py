"""
ЗАНЯТИЕ 1: ОСНОВЫ PYGAME + УСТАНОВКА БАШЕН
Время: 60 минут

Цель: создать окно, нарисовать сетку, реагировать на клик мыши,
устанавливать башни с выбором типа из радиального меню

🎯 К концу урока ученик увидит:
- Окно 800×600 пикселей
- Зелёную сетку (как шахматная доска)
- Возможность устанавливать башни разных типов
- Радиальное меню выбора типа башни
"""

import pygame
import sys
import math

# ============================================
# 1. ИНИЦИАЛИЗАЦИЯ PYGAME
# ============================================
pygame.init()

# ============================================
# 2. НАСТРОЙКИ ИГРЫ
# ============================================

# Размер окна в пикселях
WIDTH = 800
HEIGHT = 600

# Частота обновления (FPS = кадры в секунду)
FPS = 60

# Размер одной клетки сетки
CELL = 40

# ============================================
# 3. ЦВЕТА (RGB ФОРМАТ)
# ============================================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 150, 50)
DARK_GREEN = (30, 100, 30)
RED = (255, 100, 100)
YELLOW = (255, 255, 0)
CYAN = (0, 200, 200)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)
GOLD = (255, 215, 0)

# ============================================
# 4. ТИПЫ БАШЕН
# ============================================
TOWER_TYPES = {
    "rapid": {
        "name": "Rapid",
        "damage": 10,
        "fire_rate": 10,
        "range": 150,
        "color": CYAN,
        "cost": 100
    },
    "cannon": {
        "name": "Cannon",
        "damage": 60,
        "fire_rate": 75,
        "range": 120,
        "color": ORANGE,
        "cost": 250
    },
}

# ============================================
# 5. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def draw_text(surf, font, text, color, x, y, shadow=(0,0,0)):
    """Рисует текст с тенью"""
    if shadow:
        s = font.render(text, True, shadow)
        surf.blit(s, (x+1, y+1))
    t = font.render(text, True, color)
    surf.blit(t, (x, y))

# ============================================
# 6. КЛАСС БАШНИ
# ============================================

class Tower:
    def __init__(self, gx, gy, kind):
        """Создает башню в клетке (gx, gy) указанного типа"""
        self.gx = gx
        self.gy = gy
        self.x = gx * CELL + CELL // 2
        self.y = gy * CELL + CELL // 2
        self.kind = kind
        self.stats = TOWER_TYPES[kind]
        self.cooldown = 0

    def draw(self, screen, show_range=False):
        """Рисует башню на экране"""
        color = self.stats["color"]
        # Рисуем основание башни
        r = pygame.Rect(self.gx * CELL + 3, self.gy * CELL + 3, CELL - 6, CELL - 6)
        pygame.draw.rect(screen, color, r)
        pygame.draw.rect(screen, BLACK, r, 2)
        # Рисуем центр башни
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), 3)
        # Если нужно, показываем радиус обстрела
        if show_range:
            s = pygame.Surface((self.stats["range"] * 2,) * 2, pygame.SRCALPHA)
            s.fill((0, 0, 0, 0))
            pygame.draw.circle(s, (255, 255, 255, 60),
                             (self.stats["range"],) * 2, self.stats["range"])
            screen.blit(s, (self.x - self.stats["range"],
                          self.y - self.stats["range"]))

# ============================================
# 7. СОЗДАНИЕ ОКНА
# ============================================
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defence - Занятие 1")

# ============================================
# 8. ЧАСЫ ДЛЯ КОНТРОЛЯ FPS
# ============================================
clock = pygame.time.Clock()

# ============================================
# 9. ШРИФТЫ
# ============================================
font = pygame.font.SysFont("Segoe UI", 16)

# ============================================
# 10. ПЕРЕМЕННЫЕ ИГРЫ
# ============================================
towers = []              # Список установленных башен
selected_type = "rapid"  # Выбранный тип башни
placing_cell = None      # Клетка для установки башни (открыто меню)
hover_cell = None        # Клетка под курсором мыши
gold = 300               # Золото игрока
running = True           # Флаг работы программы

# ============================================
# 11. ГЛАВНЫЙ ЦИКЛ ИГРЫ
# ============================================

while running:
    # Ограничиваем FPS (60 кадров в секунду)
    clock.tick(FPS)

    # ========== ОБРАБОТКА СОБЫТИЙ ==========

    for event in pygame.event.get():
        # Закрытие окна
        if event.type == pygame.QUIT:
            running = False
            print("Окно закрыто!")

        # Клик мыши
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            print(f"Клик мыши! Позиция: {pos}")

            # Проверяем, кликнули ли по UI панели внизу
            if pos[1] >= HEIGHT - 60:
                # Выбор типа башни
                types = list(TOWER_TYPES.keys())
                for i, k in enumerate(types):
                    x = 230 + i * 180
                    if x <= pos[0] <= x + 80:
                        selected_type = k
                        print(f"Выбран тип: {k}")
                        placing_cell = None
                continue

            # Если открыто меню установки
            if placing_cell:
                gx, gy = placing_cell
                cx = gx * CELL + CELL // 2
                cy = gy * CELL + CELL // 2

                # Проверяем клик внутри радиального меню
                if math.hypot(pos[0] - cx, pos[1] - cy) <= 50:
                    # Определяем угол клика
                    angle = math.degrees(math.atan2(pos[1] - cy, pos[0] - cx))
                    # Верхняя половина = Rapid, нижняя = Cannon
                    kind = "cannon" if (angle < -90 or angle >= 90) else "rapid"
                    cost = TOWER_TYPES[kind]["cost"]

                    if gold >= cost:
                        # Устанавливаем башню
                        towers.append(Tower(gx, gy, kind))
                        gold -= cost
                        print(f"Установлена башня {kind} за {cost} золота")
                    else:
                        print(f"Недостаточно золота! Нужно {cost}, есть {gold}")
                placing_cell = None
                continue

            # Клик по сетке
            gx, gy = pos[0] // CELL, pos[1] // CELL

            # Проверяем, что клетка внутри поля и не в UI
            if not (0 <= gx < WIDTH // CELL and 0 <= gy < HEIGHT // CELL):
                continue
            if pos[1] >= HEIGHT - 60:  # Не кликаем по UI панели
                continue

            # Проверяем, есть ли уже башня в этой клетке
            has_tower = False
            for t in towers:
                if t.gx == gx and t.gy == gy:
                    has_tower = True
                    break

            if not has_tower:
                # Открываем меню установки
                placing_cell = (gx, gy)
                print(f"Открыто меню установки в клетке ({gx}, {gy})")
            else:
                print("Здесь уже есть башня!")

        # Движение мыши
        if event.type == pygame.MOUSEMOTION:
            gx, gy = event.pos[0] // CELL, event.pos[1] // CELL
            in_grid = (0 <= gx < WIDTH // CELL and
                      0 <= gy < HEIGHT // CELL and
                      event.pos[1] < HEIGHT - 60)
            hover_cell = (gx, gy) if in_grid else None

    # ========== ОБНОВЛЕНИЕ ==========
    # Обновляем логику игры
    # (пока здесь ничего не меняется)

    # ========== РИСОВАНИЕ ==========

    # 1. Заполняем весь экран зелёным цветом
    screen.fill(GREEN)

    # 2. Рисуем вертикальные линии сетки
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, DARK_GREEN, (x, 0), (x, HEIGHT), 1)

    # 3. Рисуем горизонтальные линии сетки
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, DARK_GREEN, (0, y), (WIDTH, y), 1)

    # 4. Рисуем все установленные башни
    for t in towers:
        # Проверяем, наведена ли мышь на эту башню
        show_range = (hover_cell and t.gx == hover_cell[0] and t.gy == hover_cell[1])
        t.draw(screen, show_range=show_range)

    # 5. Рисуем радиальное меню установки
    if placing_cell:
        gx, gy = placing_cell
        cx = gx * CELL + CELL // 2
        cy = gy * CELL + CELL // 2
        rd = 50

        # Фоновый круг
        s = pygame.Surface((rd * 2,) * 2, pygame.SRCALPHA)
        s.fill((0, 0, 0, 0))
        pygame.draw.circle(s, (40, 40, 40, 220), (rd, rd), rd)
        screen.blit(s, (cx - rd, cy - rd))

        # Сектора для каждого типа башни
        s2 = pygame.Surface((rd * 2,) * 2, pygame.SRCALPHA)
        for i, (key, info) in enumerate(TOWER_TYPES.items()):
            points = [(rd, rd)]
            for j in range(31):
                a = math.radians(i * 180 - 90 + 180 * j / 30)
                points.append((rd + rd * math.cos(a), rd + rd * math.sin(a)))
            pygame.draw.polygon(s2, info["color"] + (180,), points)
        screen.blit(s2, (cx - rd, cy - rd))

        # Контур круга
        pygame.draw.circle(screen, WHITE, (cx, cy), rd, 2)
        # Разделительная линия
        pygame.draw.line(screen, WHITE, (cx, cy - rd), (cx, cy + rd), 2)

        # Названия башен
        for i, (key, info) in enumerate(TOWER_TYPES.items()):
            mid_a = math.radians(i * 180)
            lx = cx + rd * 0.55 * math.cos(mid_a)
            ly = cy + rd * 0.55 * math.sin(mid_a)
            draw_text(screen, font, info["name"], BLACK,
                     lx - font.size(info["name"])[0] // 2, ly - 10)
            draw_text(screen, font, f"${info['cost']}", BLACK,
                     lx - font.size(f"${info['cost']}")[0] // 2, ly + 4)

    # 6. UI панель внизу
    pygame.draw.rect(screen, BLACK, (0, HEIGHT - 60, WIDTH, 60))

    # Золото
    draw_text(screen, font, f"Золото: {gold}", GOLD, 10, HEIGHT - 50)

    # Типы башен в UI
    types = list(TOWER_TYPES.items())
    for i, (k, v) in enumerate(types):
        x = 230 + i * 180
        # Кнопка типа башни
        is_selected = (k == selected_type)
        pygame.draw.rect(screen, v["color"], (x, HEIGHT - 52, 80, 44))
        border = YELLOW if is_selected else WHITE
        pygame.draw.rect(screen, border, (x, HEIGHT - 52, 80, 44), 2)
        draw_text(screen, font, f"{v['name']}", BLACK, x + 5, HEIGHT - 48)
        draw_text(screen, font, f"{v['cost']} золота", BLACK, x + 5, HEIGHT - 30)

    # 7. Обновляем экран
    pygame.display.flip()

# ============================================
# 12. ВЫХОД ИЗ ПРОГРАММЫ
# ============================================
pygame.quit()
sys.exit()

print("Программа завершена!")

# ============================================
# 📚 ОБЪЯСНЕНИЕ НОВЫХ КОНЦЕПЦИЙ
# ============================================

# 1. КЛАССЫ:
# Класс Tower - это шаблон для создания башен.
# Каждая башня имеет свои координаты, тип и характеристики.
# Метод draw() рисует башню на экране.

# 2. РАДИАЛЬНОЕ МЕНЮ:
# При клике на пустую клетку появляется круг, разделенный на две части.
# Верхняя часть = Rapid башня, нижняя = Cannon башня.
# Клик в соответствующую часть устанавливает башню этого типа.

# 3. СПИСКИ:
# towers = [] - пустой список для хранения всех башен.
# Добавление башни: towers.append(Tower(gx, gy, kind))

# 4. ОБРАБОТКА КЛИКОВ:
# Проверяем, где произошел клик:
# - В UI панели → выбрать тип башни
# - В радиальном меню → установить башню
# - На пустой клетке → открыть меню установки
# - На клетке с башней → показать информацию

# 5. РИСОВАНИЕ СЕКТОРОВ:
# Используем pygame.draw.polygon() для рисования секторов круга.
# math.atan2() вычисляет угол клика для определения типа башни.

# ============================================
# 💡 НОВЫЕ ЗАДАНИЯ ДЛЯ ЭКСПЕРИМЕНТА
# ============================================
# 1. Добавь третий тип башни в TOWER_TYPES
# 2. Добавь отображение радиуса обстрела при наведении
# 3. Сделай анимацию появления башни
# 4. Добавь возможность удалять башни (правый клик)
# 5. Сделай чтобы при клике на существующую башню показывалась её статистика

# ============================================
# 🔧 НОВЫЕ МЕТОДЫ PYGAME, ИСПОЛЬЗУЕМЫЕ В ФАЙЛЕ
# ============================================

# pygame.draw.polygon(surface, color, points)
# Рисует многоугольник. points - список координат вершин.

# pygame.Surface((width, height), pygame.SRCALPHA)
# Создает прозрачную поверхность для рисования с альфа-каналом.

# math.atan2(y, x)
# Вычисляет угол (в радианах) от оси X до точки (x, y).
# Используется для определения направления клика.

# math.degrees(radians)
# Преобразует радианы в градусы.

# pygame.font.SysFont(name, size)
# Создает системный шрифт с указанным именем и размером.

# font.size(text)
# Возвращает размеры текста (ширина, высота) в пикселях.

# font.render(text, antialias, color)
# Создает поверхность с отрендеренным текстом.

# surface.blit(source, dest)
# Копирует одну поверхность на другую в указанную позицию.

# pygame.Rect(left, top, width, height)
# Создает прямоугольник для рисования и коллизий.

# math.hypot(x, y)
# Вычисляет длину гипотенузы (расстояние между точками).
# Эквивалент: sqrt(x*x + y*y)
