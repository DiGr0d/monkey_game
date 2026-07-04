import pygame

class Menu:
    name = "menu"
    buttons = [{"name": "button1", "callback": lambda : print("button1 pressed")},
               {"name": "quit", "callback": lambda: print("button2 presed")}] # must provede a dict of {"name": ..., "callback": ...}
    button_rects = {} # position of left upper corner of every button (sorted by names)
    works = False
    # то как расположены кнопки зависит от отступов(типа масштабирование для области внутри отступов)
    # пока что кнопки расположены сверху вниз(возможно потом будет по-другому)
    def __init__(self, game_engine):
        self.obj_name = "undefined"
        self.game_engine = game_engine
        width, height = game_engine.screen.get_size()
        self.height_indent =  height * 0.05

        self.with_indent = 0
        self.spacing = 0
        self.button_width = 0
        self.button_heigth = 0
        self.calculate_button_sizes()

    #эта функция должна быть у всех отображаемых объектов
    def resize_object(self):
        self.calculate_button_sizes()

    def calculate_button_sizes(self):
        width, height = self.game_engine.screen.get_size()
        self.height_indent =  height * 0.05

        self.with_indent = width * 0.2
        num_buttons = len(Menu.buttons)
        
        num_buttons = num_buttons if num_buttons != 0 else 1
        self.spacing =  height * 0.2 / (1 if num_buttons <= 1 else num_buttons)

        self.button_width = width - self.with_indent * 2
        self.button_heigth = (height - height * 0.2 - self.height_indent * 2) / num_buttons

        self._fill_button_rect()


    def _fill_button_rect(self):
        pos_x = self.with_indent
        pos_y = self.height_indent
        num_buttons = len(Menu.buttons)
        for i in range(num_buttons):
            Menu.button_rects[(pos_x, pos_y + i * (self.spacing + self.button_heigth))] = i
    
#finds rect where the mouse was clicked(supposed to do nothing if click landed on spacing returns False in that case)
    def process_click(self, pos):
        if len(pos) != 2:
            raise ValueError("In menu class, process_click needs a tuple of two elements (x, y)")
        x, y = pos
        if not all(isinstance(a, int) for a in pos):
            raise ValueError("Every tuple element must be an integar in process_click function of menu class")
        
        x_landed = True if x > self.with_indent and x < self.game_engine.screen.get_size()[0] - self.with_indent else False
        y_landed = True if y > self.height_indent and y < self.game_engine.screen.get_size()[1] - self.height_indent else False
        
        if not (x_landed and y_landed):
            return False
        
        x_pos = self.with_indent
        y_pos = self.height_indent
        rect_hei = (self.spacing + self.button_heigth)
        rect_num = (y - y_pos) // rect_hei
        y_pos += rect_num * rect_hei
        if y_pos + self.button_heigth < y:
            return False
        return Menu.buttons[Menu.button_rects[(x_pos, y_pos)]]["callback"]
        
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
        
        scr = self.game_engine.screen
        scr.fill(self.game_engine.WHITE)
        font = pygame.font.Font(None, 26)
        num_buttons = len(Menu.buttons)
        pos_x = self.with_indent
        pos_y = self.height_indent
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
            
            button = Menu.buttons[Menu.button_rects[(pos_x, pos_y)]]

            text_surface = font.render(button["name"], True, self.game_engine.BLACK)
            text_rect = text_surface.get_rect(center=prect.center)
            scr.blit(text_surface, text_rect)
            pos_y += rect_hei
        
            
        

