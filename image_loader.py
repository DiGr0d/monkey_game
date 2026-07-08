import os
import pygame
from pathlib import Path
from enum import Enum

class ImageLoader:
    """Класс для загрузки и управления изображениями"""
    
    def __init__(self, folder_path="images"):
        self.folder_path = folder_path
        self.images = {}
        pygame.init()
    
    def load_by_prefix(self, prefix, convert_alpha=True):
        """
        Загружает изображения с указанным префиксом
        
        Args:
            prefix (str): Префикс для фильтрации
            convert_alpha (bool): Использовать convert_alpha() для прозрачности
        
        Returns:
            dict: Словарь с загруженными изображениями
        """
        result = {}
        
        if not os.path.exists(self.folder_path):
            print(f"Папка '{self.folder_path}' не найдена!")
            return result
        
        # Поддерживаемые расширения изображений
        extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
        
        for file_path in Path(self.folder_path).iterdir():
            if not file_path.is_file():
                continue
                
            filename = file_path.name
            ext = file_path.suffix.lower()
            
            # Проверяем префикс и расширение
            if filename.startswith(prefix) and ext in extensions:
                name = file_path.stem  # Имя без расширения
                
                try:
                    # Загружаем изображение
                    image = pygame.image.load(str(file_path))
                    
                    # Конвертируем для лучшей производительности
                    if convert_alpha:
                        image = image.convert_alpha()
                    else:
                        image = image.convert()
                    
                    result[name] = image
                    
                except pygame.error as e:
                    print(f"Ошибка загрузки {filename}: {e}")
        
        return result
    
    def load_all_by_prefixes(self, prefixes):
        """
        Загружает изображения для нескольких префиксов
        
        Args:
            prefixes (dict): {префикс: ключ_для_словаря}
        
        Returns:
            dict: Словарь {ключ: {имя_файла: изображение}}
        """
        result = {}
        for prefix, key in prefixes.items():
            result[key] = self.load_by_prefix(prefix)
        return result

# Пример использования класса
def main():
    # Создаем загрузчик
    loader = ImageLoader("images")
    
    # Загружаем изображения с разными префиксами
    images = loader.load_all_by_prefixes({
        "player_": "player",
        "enemy_": "enemy", 
        "bg_": "backgrounds",
        "item_": "items"
    })
    
    # Использование загруженных изображений
    if "player" in images:
        player_images = images["player"]
        print(f"Загружено изображений игрока: {len(player_images)}")
        
        # Доступ к конкретному изображению
        if "player_idle" in player_images:
            player_idle = player_images["player_idle"]
            print(f"Размер: {player_idle.get_size()}")
    
    # Вывод всех загруженных изображений
    for category, img_dict in images.items():
        print(f"\n{category}: {list(img_dict.keys())}")
    
    pygame.quit()

if __name__ == "__main__":
    main()


class mobAnimation:
    # Оригинальные изображения (НЕ ИЗМЕНЯЮТСЯ)
    _ORIGINAL_IMAGES = None
    # Кэш для масштабированных изображений (глобальный)
    _SCALED_CACHE = {}
    
    MOVE_ANIMATION_DURATION = 0.2
    MOVE_ANIMATION_FRAMES = 2
    MOVE_FRAME_DURATION = MOVE_ANIMATION_DURATION / MOVE_ANIMATION_FRAMES
    ATTACK_ANIMATION_DURATION = 1
    ATTACK_ANIMATION_FRAMES = 1
    ATTACK_FRAME_DURATION = ATTACK_ANIMATION_DURATION / ATTACK_ANIMATION_FRAMES
    DAMAGED_ANIMATION_DURATION = 0.1
    DAMAGED_ANIMATION_FRAMES = 1
    DAMAGED_FRAME_DURATION = DAMAGED_ANIMATION_DURATION / DAMAGED_ANIMATION_FRAMES

    @classmethod
    def load_images(cls, loader):
        """Загружает оригинальные изображения один раз"""
        if cls._ORIGINAL_IMAGES is None:
            cls._ORIGINAL_IMAGES = loader.load_by_prefix(prefix="mob")
            print(f"Загружено {len(cls._ORIGINAL_IMAGES)} оригинальных изображений")
            cls._SCALED_CACHE = {}
        return cls._ORIGINAL_IMAGES

    @classmethod
    def clear_cache(cls):
        """Очищает кэш масштабированных изображений (при изменении размера экрана)"""
        cls._SCALED_CACHE = {}
        print("Кэш масштабированных изображений очищен")

    def __init__(self):
        if mobAnimation._ORIGINAL_IMAGES is None:
            raise RuntimeError("Сначала вызовите MobAnimation.load_images()")
        
        self.state = MobState.IDLE
        self.prev_state = MobState.IDLE
        self.move_anim_accumulator = 0
        self.frame = 0
        self.facing = (1, 0)
        
        self._my_cache = {}

    def set_state(self, state, dt):
        self.prev_state = self.state
        self.state = state
        if self.state != self.prev_state:
            self.move_anim_accumulator = 0
            self.frame = 0
        else:
            self.update_animation(dt)

    def get_cur_animation_name(self):
        if self.state == MobState.MOVES:
            name = f"mob{self.facing[0]}{self.facing[1]}{self.frame}"
        elif self.state == MobState.ATTACKS:
            name = f"mob_attack{self.facing[0]}{self.facing[1]}{self.frame}"
        elif self.state == MobState.DAMAGED:
            name = "mob_damaged"
        else:
            name = "mob_damaged"
        
        if name not in mobAnimation._ORIGINAL_IMAGES:
            for key in mobAnimation._ORIGINAL_IMAGES.keys():
                if key.startswith("mob") and not key.startswith("mob_attack"):
                    name = key
                    break
        
        return name

    def update_animation(self, dt):
        self.move_anim_accumulator += dt
        
        if self.state == MobState.MOVES:
            duration = self.MOVE_FRAME_DURATION
            frames = self.MOVE_ANIMATION_FRAMES
        elif self.state == MobState.ATTACKS:
            duration = self.ATTACK_FRAME_DURATION
            frames = self.ATTACK_ANIMATION_FRAMES
        elif self.state == MobState.DAMAGED:
            duration = self.DAMAGED_FRAME_DURATION
            frames = self.DAMAGED_ANIMATION_FRAMES
        else:
            duration = 0.2
            frames = 1
            
        if self.move_anim_accumulator >= duration:
            self.move_anim_accumulator -= duration
            self.frame += 1
            if self.frame >= frames:
                self.frame = 0

    @staticmethod
    def get_direction(dx):
        if dx < 0:
            return -1
        elif dx == 0:
            return 0
        else:
            return 1

    def update_facing(self, dxdy):
        dx, dy = dxdy
        self.facing = (mobAnimation.get_direction(dx), mobAnimation.get_direction(dy))

    def get_animation(self, tile_w, tile_h):
        """Возвращает масштабированное изображение"""
        try:
            if tile_w <= 0 or tile_h <= 0:
                print(f"ОШИБКА: Неверный размер {tile_w}x{tile_h}")
                tile_w = max(1, tile_w)
                tile_h = max(1, tile_h)
            
            anim_name = self.get_cur_animation_name()
            
            if anim_name not in mobAnimation._ORIGINAL_IMAGES:
                print(f"ОШИБКА: Изображение '{anim_name}' не найдено!")
                # Создаем заглушку
                dummy = pygame.Surface((int(tile_w), int(tile_h)))
                dummy.fill((255, 0, 255))
                return dummy
            cache_key = (anim_name, int(tile_w), int(tile_h))
            
            if cache_key in mobAnimation._SCALED_CACHE:
                return mobAnimation._SCALED_CACHE[cache_key]
            
            # Масштабируем из оригинала
            original = mobAnimation._ORIGINAL_IMAGES[anim_name]
            
            if original is None:
                print(f"ОШИБКА: Оригинал '{anim_name}' равен None")
                dummy = pygame.Surface((int(tile_w), int(tile_h)))
                dummy.fill((0, 255, 0))
                return dummy
            
            new_im = pygame.transform.scale(original, (int(tile_w), int(tile_h)))
            
            mobAnimation._SCALED_CACHE[cache_key] = new_im
            
            return new_im
            
        except Exception as e:
            print(f"ОШИБКА в get_animation: {e}")
            import traceback
            traceback.print_exc()
            dummy = pygame.Surface((max(1, int(tile_w)), max(1, int(tile_h))))
            dummy.fill((255, 0, 0))
            return dummy

class MobState(Enum):
    """Состояния моба"""
    IDLE = 1
    MOVES = 2
    ATTACKS = 3
    DAMAGED = 4
    DEATH = 5