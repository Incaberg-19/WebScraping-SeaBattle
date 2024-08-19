import pygame  
from pygame.locals import *
from abc import ABC, abstractmethod

class InvalidPositionError(Exception):
    """Исключение, возникающее при попытке установить недопустимую позицию."""
    pass

class EmptyTeamError(Exception):
    """Исключение, возникающее при попытке удалить позицию из пустой команды."""
    pass

class Team(ABC):
    @abstractmethod
    def get_positions(self):
        pass

    @abstractmethod
    def set_position(self, position):
        pass

class Modified_Team(Team):
    def __init__(self):
        super().__init__()
        self.positions = []

    def get_positions(self):
        return self.positions 
    
    def set_position(self, position):
        if not isinstance(position, tuple) or len(position)!= 2:
            raise InvalidPositionError("Позиция должна быть кортежем из двух чисел")
        if not position in self.positions:
            self.positions.append(position)

    def del_position(self, position):
        if len(self.positions) == 0:
            raise EmptyTeamError("Список позиций пуст")
        self.positions.remove(position)

    def get_len(self):
        return len(self.positions)

class Ship:
    def __init__(self, size, pos):
        self.size = size
        self.pos = pos
        self.image = pygame.Surface((size*70, 70))  # Создаем изображение корабля
        self.image.fill((100, 100, 100))  # Заполняем изображение серым цветом

class MyGameClass():
    def __init__(self):
        pygame.init()
        self.count=0
        self.previous_color=0
        self.key_for_change_team=1
        self.screen_width, self.screen_height = 1425, 950
        self.screen_sizes = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(self.screen_sizes)  # pygame.RESIZABLE
        pygame.display.set_caption('Морской бой')
        self.screen.fill((51, 153, 255))
        self.Modified_Team = Modified_Team()
        self.Modified_Team = Modified_Team()


        self.ships_1 = [
            Ship(size=4, pos=(10, 650)),
            Ship(size=3, pos=(250, 730)),
            Ship(size=2, pos=(370, 810)),
            Ship(size=1, pos=(550, 670))
        ]

        self.ships_2 = [
            Ship(size=4, pos=(10+750, 650)),
            Ship(size=3, pos=(250+700, 730)),
            Ship(size=2, pos=(370+700, 810)),
            Ship(size=1, pos=(550+700, 670))
        ]
        self.dragging_ship = None

        self.WHITE=(255,255,255)
        
        self.rect_sizes_delimiter = (25, self.screen_sizes[1])
        self.rect_delimiter = pygame.Surface(self.rect_sizes_delimiter)  
        self.rect_delimiter.fill(self.WHITE)
        self.position_delimiter=(700, 0)

        self.spaces_rect_sizes=(self.position_delimiter[0],630)
        self.spaces_rect = pygame.Surface(self.spaces_rect_sizes, pygame.SRCALPHA) #тут первые два параметра это на сколько можно растянуть этот прямоугольник
        self.spaces_rect2 = pygame.Surface(self.spaces_rect_sizes, pygame.SRCALPHA)
    
        self.butter_sizes=(350,150)
        self.font = pygame.font.Font(None, 56)

        # Создайте поверхность для кнопки
        self.button_surface = pygame.Surface((self.butter_sizes[0], self.butter_sizes[1]),pygame.SRCALPHA)

        # Отображение текста на кнопке
        self.text = self.font.render("Ready", True, (0, 0, 0))
        self.text_rect = self.text.get_rect(
            center=(self.button_surface.get_width() /2, 
                    self.button_surface.get_height()/2))

        # Создайте объект pygame.Rect, который представляет границы кнопки
        self.button_rect = pygame.Rect(self.screen_width//2-self.butter_sizes[0]//2, self.screen_height-self.butter_sizes[1], self.butter_sizes[0], self.butter_sizes[1])  # Отрегулируйте положение

    def draw_squares(self,surface, was_x,was_y):
        for y in range(0,was_y,70):
            for x in range(0,was_x,70):
                pygame.draw.rect(surface, self.WHITE, (x, y, 70, 70),2)

    def change_square_color(self, x, y, color):
        if 0 <= x < self.spaces_rect_sizes[0] and 0 <= y < self.spaces_rect_sizes[1]:
            self.spaces_rect.blit(pygame.Surface((70, 70), pygame.SRCALPHA), (x, y), special_flags=pygame.BLEND_RGBA_MULT)
            pygame.draw.rect(self.spaces_rect, color, (x, y, 70, 70))
        elif self.spaces_rect_sizes[0] + 25 <= x < self.spaces_rect_sizes[0] + 25 + self.spaces_rect_sizes[0] and 0 <= y < self.spaces_rect_sizes[1]:
            self.spaces_rect2.blit(pygame.Surface((70, 70), pygame.SRCALPHA), (x - self.spaces_rect_sizes[0] - 25, y), special_flags=pygame.BLEND_RGBA_MULT)
            pygame.draw.rect(self.spaces_rect2, color, (x - self.spaces_rect_sizes[0] - 25, y, 70, 70))

    def snap_to_grid(self, x, y,size,key):
        grid_size = 70
        offset_x = 0

        if x > self.spaces_rect_sizes[0]:  # Если позиция находится на втором поле
            offset_x = self.spaces_rect_sizes[0] + 25  # Учитываем ширину первого поля и разделитель
        
        # Находим ближайшую точку сетки
        snapped_x = round((x - offset_x) / grid_size) * grid_size + offset_x
        snapped_y = round(y / grid_size) * grid_size
        
        max_x = self.spaces_rect_sizes[0] + 25 + self.spaces_rect_sizes[0]
        max_y = self.spaces_rect_sizes[1]
        delimiter_x_start = self.spaces_rect_sizes[0]
        delimiter_x_end = self.spaces_rect_sizes[0] + 25  

        if snapped_x >= 0 and snapped_x <= max_x and snapped_y >= 0 and snapped_y <= max_y:

            if not (snapped_x + 70 > delimiter_x_start and snapped_x < delimiter_x_end):  

                for i in range(0,70*size,70):
                    if key==1:
                        self.Modified_Team.set_position(((i+snapped_x),snapped_y))
                    elif(key==0):
                        self.Modified_Team.set_position(((i+snapped_x),snapped_y))

                return snapped_x, snapped_y
        return x, y  

    def BadaBOOM(self, x_index, y_index):
        if self.key_for_change_team==1:
            if 0 <= x_index < self.spaces_rect_sizes[0] // 70 and 0 <= y_index < self.spaces_rect_sizes[1] // 70:
                if (x_index * 70, y_index * 70) in self.Modified_Team.get_positions():
                    self.change_square_color(x_index * 70, y_index * 70, (247, 103, 103))
                    self.Modified_Team.del_position((x_index * 70, y_index * 70))  
                else:
                    self.key_for_change_team=0
                    self.change_square_color(x_index * 70, y_index * 70, (32, 32, 32))
        if self.key_for_change_team==0:
            if 10 <= x_index <= 19 and 0 <= y_index <= 8:
                if (x_index * 70 + 25, y_index * 70) in self.Modified_Team.get_positions():
                    self.change_square_color(x_index * 70 + 25, y_index * 70, (247, 103, 103))
                    self.Modified_Team.del_position((x_index * 70 + 25, y_index * 70))  
                else:
                    self.key_for_change_team=1
                    self.change_square_color(x_index * 70 + 25, y_index * 70, (32, 32, 32))


    def run(self):
        running = True;check=0
        self.sizesis=0
        while running:
            self.screen.fill((51, 153, 255))  

            self.draw_squares(self.spaces_rect, self.spaces_rect_sizes[0], self.spaces_rect_sizes[1])
            self.screen.blit(self.spaces_rect, (0, 0))
            self.draw_squares(self.spaces_rect2, self.spaces_rect_sizes[0], self.spaces_rect_sizes[1])
            self.screen.blit(self.spaces_rect2, (self.spaces_rect_sizes[0] + 25, 0))
            self.screen.blit(self.rect_delimiter, self.position_delimiter)

            pygame.draw.rect(self.button_surface, self.WHITE, (0, 0, self.butter_sizes[0], self.butter_sizes[1]))
            self.button_surface.blit(self.text, self.text_rect)
            self.screen.blit(self.button_surface, (self.screen_width//2-self.butter_sizes[0]//2, self.screen_height-self.butter_sizes[1]))

            if check!=1:
                for ship in self.ships_1:
                    if ship!= self.dragging_ship:
                        self.screen.blit(ship.image, ship.pos)
                for ship in self.ships_2:
                    if ship!= self.dragging_ship:
                        self.screen.blit(ship.image, ship.pos)

            # Если есть перетаскиваемый корабль, рисуем его последним
            if self.dragging_ship:
                self.screen.blit(self.dragging_ship.image, self.dragging_ship.pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.key_for_change_team!=2 and check==0:
                        if self.button_rect.collidepoint(event.pos):
                            if self.key_for_change_team!=0:
                                self.key_for_change_team=0
                            else:
                                check=1
                                self.key_for_change_team=2

                        if self.key_for_change_team==1:
                            for ship in self.ships_1:
                                if ship.image.get_rect(topleft=ship.pos).collidepoint(event.pos):
                                    self.dragging_ship = ship
                                    self.sizesis=ship.size
                                    # self.original_ship_pos = ship.pos
                                    break

                        if self.key_for_change_team==0:
                            for ship in self.ships_2:
                                if ship.image.get_rect(topleft=ship.pos).collidepoint(event.pos):
                                    self.dragging_ship = ship
                                    # self.original_ship_pos = ship.pos
                                    self.sizesis=ship.size
                                    break
                    else:

                        if self.key_for_change_team==2:
                            self.key_for_change_team=1

                        x, y = event.pos
                        if x>=730:
                            x=x-25

                        x_index = x // 70
                        y_index = y // 70
                        self.BadaBOOM(x_index,y_index)

                        if self.Modified_Team.get_len() == 0:
                            running = False

                            self.button_surface = pygame.Surface((self.butter_sizes[0], self.butter_sizes[1]),pygame.SRCALPHA)

                            # Отображение текста на кнопке
                            self.text = self.font.render("Left win", True, (0, 0, 0))
                            self.text_rect = self.text.get_rect(
                                center=(self.button_surface.get_width() /2, 
                                        self.button_surface.get_height()/2))

                            self.button_rect = pygame.Rect(self.screen_width//2-self.butter_sizes[0]//2, self.screen_height-self.butter_sizes[1], self.butter_sizes[0], self.butter_sizes[1])  # Отрегулируйте положение

                            pygame.draw.rect(self.button_surface, self.WHITE, (0, 0, self.butter_sizes[0], self.butter_sizes[1]))
                            self.button_surface.blit(self.text, self.text_rect)
                            self.screen.blit(self.button_surface, (self.screen_width//2-self.butter_sizes[0]//2, self.screen_height-self.butter_sizes[1]))

                            pygame.display.update()  
                            pygame.time.delay(3000)

                        elif self.Modified_Team.get_len() == 0:
                            running=False
                            self.button_surface = pygame.Surface((self.butter_sizes[0], self.butter_sizes[1]),pygame.SRCALPHA)

                            # Отображение текста на кнопке
                            self.text = self.font.render("Right win", True, (0, 0, 0))
                            self.text_rect = self.text.get_rect(
                                center=(self.button_surface.get_width() /2, 
                                        self.button_surface.get_height()/2))

                            self.button_rect = pygame.Rect(self.screen_width//2-self.butter_sizes[0]//2, self.screen_height-self.butter_sizes[1], self.butter_sizes[0], self.butter_sizes[1])  # Отрегулируйте положение

                            pygame.draw.rect(self.button_surface, self.WHITE, (0, 0, self.butter_sizes[0], self.butter_sizes[1]))
                            self.button_surface.blit(self.text, self.text_rect)
                            self.screen.blit(self.button_surface, (self.screen_width//2-self.butter_sizes[0]//2, self.screen_height-self.butter_sizes[1]))

                            pygame.display.update()  
                            pygame.time.delay(3000)
                            pygame.time.delay(3000)

                elif event.type == pygame.MOUSEMOTION and self.dragging_ship:
                    self.dragging_ship.pos = event.pos
                elif event.type == pygame.MOUSEBUTTONUP and self.dragging_ship:
                    new_pos = self.snap_to_grid(*self.dragging_ship.pos,self.sizesis,self.key_for_change_team)
                    # if self.is_valid_position(new_pos):
                    self.dragging_ship.pos = new_pos
                        # print(self.dragging_ship.pos)
                        # self.put_ship_in_team(self.Modified_Team_Team, self.dragging_ship.pos, 70)
                    # else:
                        # self.dragging_ship.pos = self.original_ship_pos  # Восстанавливаем исходное положение
                    self.dragging_ship = None  # Завершаем перетаскивание
            
            pygame.display.update()

if __name__ == '__main__':
    MyGameClass().run()
