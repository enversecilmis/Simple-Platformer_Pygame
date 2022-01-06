import pygame

class Menu:
    def __init__(self, display_surface: pygame.Surface):
        self.paused = False
        self.font = pygame.font.Font("assets/manaspc.ttf",30)
        self.display_surface = display_surface

        self.start_button = pygame.Surface((300,50))
        self.start_button.fill((235, 64, 52))
        self.start_rect = self.start_button.get_rect().move(300,250)
        self.start_text = self.font.render("Start New Game", False, (225, 255, 201))
        
        self.continue_button = pygame.Surface((250,50))
        self.continue_button.fill((235, 64, 52))
        self.continue_rect = self.continue_button.get_rect().move(320,150)
        self.continue_text = self.font.render("continue", False, (225, 255, 201))


    
    def drawMenu(self):
        self.display_surface.blit(self.start_button, self.start_rect)
        self.display_surface.blit(self.start_text, self.start_rect.move(10,10))

        if self.paused:
            self.display_surface.blit(self.continue_button, self.continue_rect)
            self.display_surface.blit(self.continue_text, self.continue_rect.move(50,10))


    def handleInput(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.start_rect.collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
                    return (True, False)

                if self.continue_rect.collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
                    return (True, True)

        return (False, False)


    def run(self, events):
        self.display_surface.fill((134, 235, 52))
        self.drawMenu()
        return self.handleInput(events)