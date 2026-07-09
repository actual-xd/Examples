# План обучения: Tower Defense игра на Python
## Для ученика 11 лет, занятия по 60 минут

---

## 📋 Общая структура

| Занятие | Тема | Основная цель |
|---------|------|---------------|
| 1 | Основы Pygame | Окно, сетка, события мыши |
| 2 | Рисование башен | Размещение и выбор типов |
| 3 | Движение врагов | Враги следуют по пути |
| 4 | Стрельба и урон | Башни стреляют, враги теряют HP |
| 5 | Волны и ресурсы | Система волн, золото, жизни |
| 6 | Интерфейс | UI, кнопки, текст на экране |
| 7 | Полная игра | Объединение всего, баланс |
| 8 | Полировка | Эффекты, звуки, финал |

---

## 🎯 ЗАНЯТИЕ 1: ОСНОВЫ PYGAME (60 минут)

### Цель урока
В конце занятия ученик будет видеть:
- ✅ Окно 800×600 пикселей
- ✅ Зелёную сетку (как шахматная доска)
- ✅ Реакцию на клик мыши (квадратик появляется где кликнул)

### Что объяснить (15 минут)
- Что такое `pygame` — библиотека для игр
- Координаты: (0,0) это верхний левый угол
- FPS (частота обновления экрана)
- Главный цикл игры: **событие → обновление → рисование**

### Код для написания (40 минут)

```python
import pygame
import sys

# Инициализация
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 800, 600
FPS = 60
CELL = 40

# Цвета (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 150, 50)
DARK_GREEN = (30, 100, 30)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defence - Занятие 1")
clock = pygame.time.Clock()

# Переменные игры
click_pos = None
running = True

# ГЛАВНЫЙ ЦИКЛ
while running:
    clock.tick(FPS)
    
    # 1️⃣ СОБЫТИЯ (что произошло)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            click_pos = event.pos
            print(f"Клик в точке: {click_pos}")
    
    # 2️⃣ ОБНОВЛЕНИЕ (логика)
    # (пока ничего не меняем)
    
    # 3️⃣ РИСОВАНИЕ (что показать)
    # Заливка фона зелёным
    screen.fill(GREEN)
    
    # Рисование сетки
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, DARK_GREEN, (x, 0), (x, HEIGHT), 1)
    
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, DARK_GREEN, (0, y), (WIDTH, y), 1)
    
    # Если был клик - рисуем квадратик в том месте
    if click_pos:
        pygame.draw.rect(screen, (255, 100, 100), 
                        (click_pos[0] - 15, click_pos[1] - 15, 30, 30))
    
    # Обновляем экран
    pygame.display.flip()

pygame.quit()
sys.exit()
```

### Задание для проверки (5 минут)
Попросите ученика:
1. Изменить размер окна на 1000×700
2. Изменить цвет сетки
3. Вместо квадратика рисовать круг

---

## 🏰 ЗАНЯТИЕ 2: РИСОВАНИЕ БАШЕН (60 минут)

### Цель урока
- ✅ Башни разного цвета (Быстрая и Пушка)
- ✅ Можно кликать на пустое место и выбирать тип
- ✅ Башни сохраняются на поле

### Новые концепции (10 минут)
- **Класс** — шаблон для создания объектов
- **Список** — хранит много башен
- Как работает `isinstance()` для проверки типа

### Код для написания (40 минут)

```python
import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
CELL = 40
GRID_COLS = WIDTH // CELL
GRID_ROWS = HEIGHT // CELL

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 150, 50)
DARK_GREEN = (30, 100, 30)
CYAN = (0, 200, 200)
ORANGE = (255, 165, 0)

TOWER_TYPES = {
    "rapid": {"name": "Быстрая", "color": CYAN, "cost": 100},
    "cannon": {"name": "Пушка", "color": ORANGE, "cost": 250},
}

# 🏗️ КЛАСС БАШНИ
class Tower:
    def __init__(self, gx, gy, kind):
        """gx, gy - координаты в сетке (в клетках)"""
        self.gx = gx
        self.gy = gy
        self.kind = kind  # "rapid" или "cannon"
        self.x = gx * CELL + CELL // 2  # центр в пикселях
        self.y = gy * CELL + CELL // 2
    
    def draw(self, screen):
        """Рисует башню"""
        color = TOWER_TYPES[self.kind]["color"]
        # Квадратик башни
        rect = pygame.Rect(self.gx * CELL + 3, self.gy * CELL + 3, 
                          CELL - 6, CELL - 6)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)
        # Центр башни (точка прицела)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), 3)

# ============================================

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defence - Занятие 2: Башни")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16)

towers = []  # Список всех башен
selected = "rapid"  # Какую башню выбрали
placing_cell = None  # Для меню выбора типа
gold = 500  # Тестовое золото

running = True

while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            gx, gy = event.pos[0] // CELL, event.pos[1] // CELL
            
            # Проверка: клик в пределах сетки?
            if not (0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS):
                continue
            
            # Проверка: уже стоит башня в этом месте?
            tower_here = None
            for t in towers:
                if t.gx == gx and t.gy == gy:
                    tower_here = t
                    break
            
            if tower_here:
                # Удаляем башню если на неё кликнули
                towers.remove(tower_here)
                print(f"Башня удалена! Золото: +{TOWER_TYPES[tower_here.kind]['cost']}")
                gold += TOWER_TYPES[tower_here.kind]["cost"]
            else:
                # Показываем меню выбора
                placing_cell = (gx, gy)
        
        # Клавиши для быстрого выбора
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                selected = "rapid"
            elif event.key == pygame.K_2:
                selected = "cannon"
    
    # РИСОВАНИЕ
    screen.fill(GREEN)
    
    # Сетка
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, DARK_GREEN, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, DARK_GREEN, (0, y), (WIDTH, y), 1)
    
    # Башни
    for tower in towers:
        tower.draw(screen)
    
    # Если выбираем место - показываем меню
    if placing_cell:
        gx, gy = placing_cell
        cx = gx * CELL + CELL // 2
        cy = gy * CELL + CELL // 2
        
        # Полукруг для выбора типа
        rd = 50
        pygame.draw.circle(screen, (100, 100, 100), (cx, cy), rd)
        pygame.draw.circle(screen, WHITE, (cx, cy), rd, 2)
        
        # Два сектора - левый (rapid) и правый (cannon)
        for i, (key, info) in enumerate(TOWER_TYPES.items()):
            angle = i * 180  # 0° для rapid, 180° для cannon
            lx = cx + rd * 0.6 * math.cos(math.radians(angle))
            ly = cy + rd * 0.6 * math.sin(math.radians(angle))
            
            text = font.render(f"{info['name']} ${info['cost']}", True, WHITE)
            screen.blit(text, (lx - text.get_width() // 2, ly - 10))
        
        # Инструкция
        help_text = font.render("Нажми 1 или 2 для выбора", True, WHITE)
        screen.blit(help_text, (cx - 100, cy - 80))
    
    # UI внизу
    gold_text = font.render(f"ЗОЛОТО: {gold}", True, (255, 215, 0))
    selected_text = font.render(f"Выбрано: {TOWER_TYPES[selected]['name']}", 
                               True, WHITE)
    screen.blit(gold_text, (10, 10))
    screen.blit(selected_text, (10, 30))
    
    pygame.display.flip()

pygame.quit()
sys.exit()
```

### Интерактивные задачи (10 минут)
1. Добавить третий тип башни (например, "laser")
2. Показывать цену башни перед постройкой
3. Запретить строить, если не хватает золота

---

## 👾 ЗАНЯТИЕ 3: ВРАГИ И ДВИЖЕНИЕ (60 минут)

### Цель урока
- ✅ Враги появляются и движутся по заданному пути
- ✅ Враги получают урон (полоса HP над ними)
- ✅ Враги удаляются при смерти

### Новые концепции (10 минут)
- **Waypoints** — контрольные точки пути
- `math.hypot()` — расстояние между двумя точками
- Нормализация вектора (направление)

### Путь для врагов (объяснить)
```
Враги идут от левого края через весь экран змейкой:
(-40, 260) → (200, 260) → (200, 100) → ... → (840, 180)
```

### Код для написания (40 минут)

```python
import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
CELL = 40
GRID_COLS = WIDTH // CELL
GRID_ROWS = HEIGHT // CELL

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 150, 50)
DARK_GREEN = (30, 100, 30)
RED = (220, 50, 50)
HP_GREEN = (80, 200, 80)

# КОНТРОЛЬНЫЕ ТОЧКИ ПУТИ
WAYPOINTS = [
    (-40, 260),
    (200, 260),
    (200, 100),
    (460, 100),
    (460, 420),
    (700, 420),
    (700, 180),
    (840, 180),
]

# 👾 КЛАСС ВРАГА
class Enemy:
    def __init__(self, hp, speed):
        self.max_hp = hp
        self.hp = hp
        self.speed = speed  # пиксели в кадр
        self.waypoint_index = 0
        self.x, self.y = WAYPOINTS[0]  # начало пути
        self.alive = True
        self.reached_end = False
    
    def update(self):
        """Двигаем врага к следующей точке"""
        if not self.alive or self.reached_end:
            return
        
        # Текущая цель
        tx, ty = WAYPOINTS[self.waypoint_index]
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        
        # Если достигли точки - идём дальше
        if dist < self.speed:
            self.x, self.y = tx, ty
            self.waypoint_index += 1
            if self.waypoint_index >= len(WAYPOINTS):
                self.reached_end = True
        else:
            # Нормализуем и двигаемся
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed
    
    def draw(self, screen):
        """Рисует врага + полоса HP"""
        if not self.alive:
            return
        
        # Сам враг (красный квадратик)
        pygame.draw.rect(screen, RED, (self.x - 8, self.y - 8, 16, 16))
        
        # Полоса здоровья
        bar_w, bar_h = 22, 3
        ratio = self.hp / self.max_hp
        bx = self.x - bar_w // 2
        by = self.y - 14
        
        # Чёрная рамка
        pygame.draw.rect(screen, BLACK, (bx - 1, by - 1, bar_w + 2, bar_h + 2))
        # Зелёная полоса
        pygame.draw.rect(screen, HP_GREEN, (bx, by, bar_w * ratio, bar_h))
    
    def take_damage(self, damage):
        """Враг получает урон"""
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False

# ============================================

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defence - Занятие 3: Враги")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16)

# Тестируем: создаём несколько врагов
enemies = [
    Enemy(hp=50, speed=1.5),
    Enemy(hp=50, speed=1.5),
    Enemy(hp=50, speed=1.5),
]

# Добавляем нескольких врагов с небольшой задержкой
test_wave = [Enemy(50, 1.5) for _ in range(5)]
spawn_timer = 0

running = True

while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Спаун новой волны
                test_wave = [Enemy(50, 1.5) for _ in range(5)]
                spawn_timer = 0
    
    # ОБНОВЛЕНИЕ
    spawn_timer += 1
    if spawn_timer > 20 and test_wave:
        enemies.append(test_wave.pop(0))
        spawn_timer = 0
    
    # Обновляем врагов
    for e in enemies:
        e.update()
    
    # Удаляем мертвецов и вышедших за карту
    enemies = [e for e in enemies if e.alive and not e.reached_end]
    
    # РИСОВАНИЕ
    screen.fill(GREEN)
    
    # Сетка
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, DARK_GREEN, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, DARK_GREEN, (0, y), (WIDTH, y), 1)
    
    # Путь (линия)
    pygame.draw.lines(screen, (200, 150, 100), WAYPOINTS, 3)
    
    # Враги
    for e in enemies:
        e.draw(screen)
    
    # UI
    info = font.render(f"Врагов: {len(enemies)} | "
                      f"Нажми SPACE для волны", True, WHITE)
    screen.blit(info, (10, 10))
    
    pygame.display.flip()

pygame.quit()
sys.exit()
```

### Проверка понимания (10 минут)
- Что такое `waypoint_index`?
- Как враг узнаёт, что достиг точку?
- Как нормализовать вектор? (показать математику)

---

## 🎯 ЗАНЯТИЕ 4: БАШНИ СТРЕЛЯЮТ (60 минут)

### Цель урока
- ✅ Башни следят за врагами в радиусе
- ✅ Рисуют радиус наведения
- ✅ Стреляют снарядами (жёлтые кружки)
- ✅ Враги получают урон от снарядов

### Новые концепции (10 минут)
- **Range** (радиус поражения) — круг вокруг башни
- **Cooldown** (перезарядка) — не может стрелять сразу
- Поиск ближайшего врага

### Код для написания (40 минут)

```python
# (код из занятия 2 и 3, плюс добавляем...)

import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
CELL = 40

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 150, 50)
DARK_GREEN = (30, 100, 30)
RED = (220, 50, 50)
HP_GREEN = (80, 200, 80)
CYAN = (0, 200, 200)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)

WAYPOINTS = [
    (-40, 260), (200, 260), (200, 100), (460, 100),
    (460, 420), (700, 420), (700, 180), (840, 180),
]

TOWER_TYPES = {
    "rapid": {"name": "Быстрая", "damage": 10, "fire_rate": 10, 
              "range": 150, "color": CYAN, "cost": 100},
    "cannon": {"name": "Пушка", "damage": 40, "fire_rate": 60, 
              "range": 120, "color": ORANGE, "cost": 250},
}

# 🎯 КЛАСС СНАРЯДА
class Projectile:
    def __init__(self, x, y, target, damage):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = 6
        self.alive = True
    
    def update(self):
        """Движит снаряд к цели"""
        if not self.alive or not self.target.alive:
            self.alive = False
            return
        
        # Направление к цели
        tx, ty = self.target.x, self.target.y
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        
        if dist < self.speed:
            # Попали!
            self.target.take_damage(self.damage)
            self.alive = False
        else:
            # Движимся
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed
    
    def draw(self, screen):
        if self.alive:
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), 3)

# 🏰 БАШНЯ (расширенная)
class Tower:
    def __init__(self, gx, gy, kind):
        self.gx = gx
        self.gy = gy
        self.kind = kind
        self.x = gx * CELL + CELL // 2
        self.y = gy * CELL + CELL // 2
        self.stats = TOWER_TYPES[kind]
        self.cooldown = 0
    
    def update(self, enemies):
        """Обновляет башню и возвращает новые снаряды"""
        if self.cooldown > 0:
            self.cooldown -= 1
            return []
        
        # Ищем ближайшего врага в радиусе
        best_enemy = None
        best_dist = self.stats["range"]
        
        for e in enemies:
            if not e.alive or e.reached_end:
                continue
            
            dist = math.hypot(self.x - e.x, self.y - e.y)
            if dist < best_dist:
                best_dist = dist
                best_enemy = e
        
        if not best_enemy:
            return []  # Нет врагов в радиусе
        
        # Стреляем!
        self.cooldown = self.stats["fire_rate"]
        return [Projectile(self.x, self.y, best_enemy, 
                          self.stats["damage"])]
    
    def draw(self, screen, show_range=False):
        color = self.stats["color"]
        rect = pygame.Rect(self.gx * CELL + 3, self.gy * CELL + 3, 
                          CELL - 6, CELL - 6)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), 3)
        
        # Показываем радиус если hovering
        if show_range:
            pygame.draw.circle(screen, (100, 100, 100), 
                              (int(self.x), int(self.y)), 
                              self.stats["range"], 1)

# 👾 ВРАГ (из прошлого урока)
class Enemy:
    def __init__(self, hp, speed):
        self.max_hp = hp
        self.hp = hp
        self.speed = speed
        self.waypoint_index = 0
        self.x, self.y = WAYPOINTS[0]
        self.alive = True
        self.reached_end = False
    
    def update(self):
        if not self.alive or self.reached_end:
            return
        
        tx, ty = WAYPOINTS[self.waypoint_index]
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        
        if dist < self.speed:
            self.x, self.y = tx, ty
            self.waypoint_index += 1
            if self.waypoint_index >= len(WAYPOINTS):
                self.reached_end = True
        else:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed
    
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
    
    def draw(self, screen):
        if not self.alive:
            return
        pygame.draw.rect(screen, RED, (self.x - 8, self.y - 8, 16, 16))
        bar_w, bar_h = 22, 3
        ratio = self.hp / self.max_hp
        bx = self.x - bar_w // 2
        by = self.y - 14
        pygame.draw.rect(screen, BLACK, (bx - 1, by - 1, bar_w + 2, bar_h + 2))
        pygame.draw.rect(screen, HP_GREEN, (bx, by, bar_w * ratio, bar_h))

# ============================================

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defence - Занятие 4: Стрельба")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16)

towers = []
enemies = []
projectiles = []
test_wave = [Enemy(50, 1.5) for _ in range(10)]
spawn_timer = 0

running = True

while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            gx, gy = event.pos[0] // CELL, event.pos[1] // CELL
            if 0 <= gx < WIDTH // CELL and 0 <= gy < HEIGHT // CELL:
                # Быстрое размещение башни
                towers.append(Tower(gx, gy, "rapid"))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                test_wave = [Enemy(50, 1.5) for _ in range(10)]
                spawn_timer = 0
            elif event.key == pygame.K_c:
                towers.append(Tower(5, 5, "cannon"))
    
    # ОБНОВЛЕНИЕ
    spawn_timer += 1
    if spawn_timer > 15 and test_wave:
        enemies.append(test_wave.pop(0))
        spawn_timer = 0
    
    for e in enemies:
        e.update()
    
    for t in towers:
        new_projectiles = t.update(enemies)
        projectiles.extend(new_projectiles)
    
    for p in projectiles:
        p.update()
    
    enemies = [e for e in enemies if e.alive and not e.reached_end]
    projectiles = [p for p in projectiles if p.alive]
    
    # РИСОВАНИЕ
    screen.fill(GREEN)
    
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, DARK_GREEN, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, DARK_GREEN, (0, y), (WIDTH, y), 1)
    
    pygame.draw.lines(screen, (200, 150, 100), WAYPOINTS, 3)
    
    for t in towers:
        t.draw(screen, show_range=True)
    
    for e in enemies:
        e.draw(screen)
    
    for p in projectiles:
        p.draw(screen)
    
    info = font.render(f"Врагов: {len(enemies)} | "
                      f"Башен: {len(towers)} | "
                      f"SPACE=волна | Клик=башня | C=пушка", 
                      True, WHITE)
    screen.blit(info, (10, 10))
    
    pygame.display.flip()

pygame.quit()
sys.exit()
```

### Задание (10 минут)
Добавить свой тип башни с другими характеристиками.

---

## 💰 ЗАНЯТИЕ 5: ВОЛНЫ И РЕСУРСЫ (60 минут)

### Цель урока
- ✅ Система волн (враги появляются волнами)
- ✅ Золото за убитых врагов
- ✅ Система жизней (враги проходят - теряем жизни)
- ✅ Нельзя строить башни на пути врагов

### Новые концепции (10 минут)
- **Состояния волны**: active (идёт волна) / waiting (ждём)
- **Queue** — очередь врагов на спаун
- Геймовер условие

### Основной код (из предыдущих занятий, добавляем Game класс)

```python
# Создаём класс для управления игрой

class Game:
    def __init__(self):
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.gold = 300
        self.lives = 3
        self.wave = 0
        
        self.wave_active = False
        self.spawn_q = 0  # очередь на спаун
        self.spawn_timer = 0
        
        self.game_over = False
    
    def start_wave(self):
        """Начинает новую волну"""
        if self.wave_active or self.game_over:
            return
        
        self.wave += 1
        # Каждая волна сложнее
        enemy_count = int(5 * (1 + (self.wave - 1) * 0.3))
        enemy_hp = int(50 * (1 + (self.wave - 1) * 0.3))
        enemy_speed = 1.5 + (self.wave - 1) * 0.05
        
        self.spawn_q = enemy_count
        self.spawn_timer = 0
        self.wave_active = True
        
        print(f"🌊 Волна {self.wave}: {enemy_count} врагов HP={enemy_hp}")
    
    def update(self):
        if self.game_over:
            return
        
        # Спаун врагов из очереди
        if self.wave_active and self.spawn_q > 0:
            self.spawn_timer -= 1
            if self.spawn_timer <= 0:
                hp = int(50 * (1 + (self.wave - 1) * 0.3))
                spd = 1.5 + (self.wave - 1) * 0.05
                self.enemies.append(Enemy(hp, spd))
                self.spawn_q -= 1
                self.spawn_timer = 25
        
        # Обновляем врагов
        for e in self.enemies:
            e.update()
            if e.reached_end:
                self.lives -= 1
                print(f"❌ Враг прошёл! Жизней: {self.lives}")
        
        # Башни стреляют
        for t in self.towers:
            for p in t.update(self.enemies):
                self.projectiles.append(p)
        
        # Снаряды летят
        for p in self.projectiles:
            p.update()
        
        # Уборка
        alive_enemies = []
        for e in self.enemies:
            if e.alive and not e.reached_end:
                alive_enemies.append(e)
            elif not e.alive:
                self.gold += 8  # За убитого врага
        
        self.enemies = alive_enemies
        self.projectiles = [p for p in self.projectiles if p.alive]
        
        # Волна закончилась?
        if self.wave_active and self.spawn_q == 0 and not self.enemies:
            self.wave_active = False
            print(f"✅ Волна {self.wave} завершена!")
        
        # Проверка геймовера
        if self.lives <= 0:
            self.game_over = True
            print("💀 GAME OVER")

# В main цикле теперь:
game = Game()
game.start_wave()  # Начнём с первой волны

while running:
    # ...
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            game.start_wave()
    
    game.update()
    game.draw(screen)
```

---

## 🎨 ЗАНЯТИЕ 6: ИНТЕРФЕЙС (60 минут)

### Цель урока
- ✅ Красивый UI с информацией
- ✅ Кнопки выбора башни
- ✅ Меню удаления/покупки
- ✅ Экран GAME OVER с рестартом

### Код интерфейса (основная часть рисования)

Используем из готового кода функции `game.draw()` с:
- Текст информации (золото, жизни, волна)
- Кнопки типов башен (с подсвечиванием)
- Радиальное меню выбора (как в оригинале)
- Экран поражения

---

## ⚙️ ЗАНЯТИЕ 7: ОБЪЕДИНЕНИЕ И БАЛАНС (60 минут)

### Цель урока
- ✅ Полная работающая игра
- ✅ Баланс сложности
- ✅ Стратегия игрока

### Что проверить:
- Волны становятся всё сложнее?
- Башни справляются с врагами?
- Хватает золота на оборону?
- Интерфейс понятный?

### Балансировка (примеры):
```python
# Если игра слишком лёгкая:
- Враги быстрее: speed *= 1.1
- Башни дороже: cost *= 1.2
- Волн больше врагов

# Если слишком сложная:
- Враги слабее: hp *= 0.9
- Башни дешевле: cost *= 0.8
- Стартовое золото больше
```

---

## 🎆 ЗАНЯТИЕ 8: ПОЛИРОВКА И ЭФФЕКТЫ (60 минут)

### Цель урока
- ✅ Визуальные эффекты (анимации)
- ✅ Звуки (опционально)
- ✅ Игра выглядит как "настоящая"

### Что добавить:
1. **Цветовые эффекты**:
   - Враг краснеет когда получает урон
   - Башня светится когда стреляет
   - Эффект взрыва при смерти врага

2. **Анимации**:
   - Врагов подрагивают при урон
   - Снаряды оставляют след

3. **Звуки** (если есть pygame.mixer):
   ```python
   pygame.mixer.init()
   shoot_sound = pygame.mixer.Sound("shoot.wav")
   # shoot_sound.play()
   ```

4. **Частицы**:
   - Маленькие точки разлетаются от взрывов

---

## 📊 СВОДНАЯ ТАБЛИЦА ПРОГРЕССА

| Занятие | Видимый результат |
|---------|-------------------|
| 1 | Окно + сетка + реакция мыши |
| 2 | Башни разных типов, ставятся/удаляются |
| 3 | Враги движутся по пути со своим HP |
| 4 | **Башни стреляют! Враги умирают!** 🎯 |
| 5 | Полная система волн, золото, жизни |
| 6 | Красивый интерфейс, кнопки работают |
| 7 | Полная балансированная игра |
| 8 | Эффекты, звуки, игра "живая" |

---

## 💡 СОВЕТЫ ДЛЯ УЧИТЕЛЯ

### Как объяснять коду 11-летнему:
- ✅ Используй аналогии (класс = чертёж дома)
- ✅ Показывай результат сразу после кода
- ✅ Позволяй экспериментировать (изменять цвета, скорости)
- ✅ Хвали за попытки, не только за результат
- ✅ Один новый концепт за занятие

### Если ребёнок отстаёт:
- Пропусти детали (не нужно объяснять каждую математику)
- Дай готовый код, попроси его изменить значения
- Раздели задачу на ещё более мелкие части
- Добавь break (перерыв) на 10 минут посередине

### Если ребёнок впереди:
- Дай задачу усложнить: новый тип башни
- Добавить бонусы/powerups
- Сделать сохранение рекордов
- Улучшить графику (спрайты вместо квадратиков)

---

## 🎓 САМОПРОВЕРКА УЧЕНИКА

В конце каждого урока спроси:
- "Что мы создали сегодня?"
- "Как работает [концепт]?"
- "Что будем делать в следующий раз?"

Это помогает закрепить знания и показать прогресс!
