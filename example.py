import pygame
import sys

# Инициализация Pygame
pygame.init()

# Параметры окна
WIDTH, HEIGHT = 400, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Меню с кнопками")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLUE = (70, 130, 180)

# Шрифт для текста
font = pygame.font.Font(None, 36)

# Список кнопок: каждая кнопка — словарь с именем и функцией-обработчиком
buttons = [
    {"name": "Играть", "callback": lambda: print("Нажата кнопка Играть")},
    {"name": "Настройки", "callback": lambda: print("Нажата кнопка Настройки")},
    {"name": "Выйти", "callback": lambda: print("Нажата кнопка Выйти")},
]

# Рассчитываем положение кнопок (вертикальный список с отступами)
button_width = 200
button_height = 50
spacing = 20
total_height = len(buttons) * (button_height + spacing) - spacing
start_y = (HEIGHT - total_height) // 2

button_rects = {}  # словарь: имя кнопки -> её прямоугольник

for i, btn in enumerate(buttons):
    x = (WIDTH - button_width) // 2
    y = start_y + i * (button_height + spacing)
    rect = pygame.Rect(x, y, button_width, button_height)
    button_rects[btn["name"]] = rect

# Основной цикл
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for btn in buttons:
                rect = button_rects[btn["name"]]
                if rect.collidepoint(mouse_pos):
                    btn["callback"]()  # вызываем функцию, привязанную к кнопке

    # Отрисовка
    screen.fill(WHITE)

    for btn in buttons:
        rect = button_rects[btn["name"]]

        # Рисуем прямоугольник кнопки
        # Изменяем цвет при наведении мыши (для интерактивности)
        if rect.collidepoint(pygame.mouse.get_pos()):
            color = BLUE
        else:
            color = GRAY
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)  # обводка

        # Рендерим текст и центрируем его внутри прямоугольника
        text_surface = font.render(btn["name"], True, BLACK)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()