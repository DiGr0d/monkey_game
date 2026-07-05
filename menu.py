import pygame

class Menu:
    name = "menu"
    works = False
    # то как расположены кнопки зависит от отступов(типа масштабирование для области внутри отступов)
    # пока что кнопки расположены сверху вниз(возможно потом будет по-другому)
    def __init__(self, game_engine, **kwargs):
        self.button_rects = {} # position of left upper corner of every button (sorted by names)
        self.buttons = [{"name": "button1", "callback": lambda : print("button1 pressed")},
               {"name": "quit", "callback": lambda: print("button2 presed")},
               {"name": "negr", "callback": lambda: print("negr")},
               {"name": "govno", "callback": lambda: print("govno")}] # must provede a dict of {"name": ..., "callback": ...}
        
        self.obj_name = "undefined"
        self.game_engine = game_engine
        width, height = game_engine.screen.get_size()
        self.height_indent =  height * 0.05
        self.x, self.y = kwargs.get("x", 0), kwargs.get("y", 0)
        self.w, self.h = kwargs.get("width", width), kwargs.get("height", height)
        self.with_indent, self.spacing, self.button_width, self.button_heigth = 0, 0, 0, 0
        self.rel_x = self.x / width
        self.rel_y = self.y / height
        self.rel_w = self.w / width
        self.rel_h = self.h / height
        self.resize_object(x=self.x,y=self.y,width=self.w,height=self.h)

    def get_buttons(self):
        return self.buttons()

    #эта функция должна быть у всех отображаемых объектов
    def resize_object(self, **kwargs):
        self.calculate_button_sizes(**kwargs)

    def update_geometry(self, screen_width, screen_height):
        if self.w < 10:
            self.w = 10
        if self.h < 10:
            self.h = 10
        self.x = int(self.rel_x * screen_width)
        self.y = int(self.rel_y * screen_height)
        self.w = int(self.rel_w * screen_width)
        self.h = int(self.rel_h * screen_height)
        self.resize_object(x=self.x, y=self.y, width=self.w, height=self.h)

    def calculate_button_sizes(self, **kwargs):
        width, height = self.game_engine.screen.get_size()
        x,y=kwargs.get("x", 0), kwargs.get("y",0)
        if not(x >= 0 and x <= width  and y >= 0 and y <= height):
            raise ValueError("x or y more than screen width/height in calculate_button_sizes")
        w, h = kwargs.get("width", abs(width - x)), kwargs.get("height", abs(height - y))
        if not(w >= 0 and h >= 0):
            raise ValueError("menu width/height below zero")
        if x + w > width:
            w = width - x
        if y + h > height:
            h = height - y
        
        self.x, self.y, self.w, self.h = x, y, w, h
        
        self.height_indent =  self.h * 0.05
        self.with_indent = self.w * 0.2
        num_buttons = len(self.buttons)
        
        if num_buttons == 0:
            self.spacing=0
            self.button_width=0
            self.button_heigth=0
            return 

        self.spacing = self.h * 0.2 / (1 if num_buttons <= 1 else num_buttons)
        self.button_width = self.w - self.with_indent * 2
        self.button_heigth = (self.h * 0.8 - self.height_indent * 2) / num_buttons

    #required in shawable classes
    def get_pos(self):
        return (self.x, self.y)

    def scale(self, **kwargs):
        resize_pos = kwargs.get("pos_too", False)
        scale_x, scale_y = kwargs.get("scale_x", 1), kwargs.get("scale_y", 1)
        self.w *= scale_x
        self.h *= scale_y
        #print(scale_x, scale_y, self.w, self.h)
        if resize_pos:
            self.x *= scale_x
            self.y *= scale_y
        #print(type(self.resize_object))
        self.resize_object(x=self.x, y=self.y, height=self.h, width=self.w)

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            callback = self.process_click(mouse_pos)
            if callback:
                callback()
            
#finds rect where the mouse was clicked(supposed to do nothing if click landed on spacing returns False in that case)
    def process_click(self, pos):
        if len(pos) != 2:
            raise ValueError("In menu class, process_click needs a tuple of two elements (x, y)")
        x, y = pos
        if not all(isinstance(a, int) for a in pos):
            raise ValueError("Every tuple element must be an integar in process_click function of menu class")
        
        x_pos = self.with_indent + self.x
        y_pos = self.height_indent + self.y
        x_right_pos = self.x + self.w - self.with_indent
        y_down_pos = self.y + self.h - self.height_indent

        x_landed = True if x > x_pos and x < x_right_pos else False
        y_landed = True if y > y_pos and y < y_down_pos else False
       
        if not (x_landed and y_landed):
            return None
        
        rect_hei = self.spacing + self.button_heigth
        if rect_hei <= 0:
            return None
        rect_num = int(round((y - y_pos)) // rect_hei)

        y_pos += rect_num * rect_hei
        if y_pos + self.button_heigth < y:
            return None

        return self.buttons[rect_num]["callback"]
        
    def object_name(self):
        return self.obj_name

    def switch_on(self):
        self.works = True

    def switch_off(self):
        self.works = False

    def quit_game_callback(self):
        self.game_engine.runs = False

    def show(self):
        if not self.works:
            raise Exception("Trying to show switched off menu")
        if self.w <= 0 or self.h <= 0:
            return

        scr = self.game_engine.screen
        scrrect = pygame.Rect(self.x, self.y, self.w, self.h)
        background_color = None
        if scrrect.collidepoint(pygame.mouse.get_pos()):
            color = self.game_engine.WHITE
        else:
            color = self.game_engine.ALPHA_GRAY
    
        pygame.draw.rect(scr, color , scrrect)
        font = pygame.font.Font(None, 26)
        num_buttons = len(self.buttons)
        pos_x = self.with_indent + self.x
        pos_y = self.height_indent + self.y
        rect_hei = (self.spacing + self.button_heigth)
        for i in range(num_buttons):
            rect = (pos_x, pos_y, self.button_width, self.button_heigth)
            prect = pygame.Rect(rect)

            if prect.collidepoint(pygame.mouse.get_pos()):
                color = self.game_engine.BLUE
            else:
                color = self.game_engine.GRAY

            pygame.draw.rect(scr, color, rect)
            pygame.draw.rect(scr, self.game_engine.BLACK, rect, 1)
            
            button = self.buttons[i]

            text_surface = font.render(button["name"], True, self.game_engine.BLACK)
            text_rect = text_surface.get_rect(center=prect.center)
            scr.blit(text_surface, text_rect)
            pos_y += rect_hei
        