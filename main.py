import pygame
import sys
import time
from utils.gui import Widget, Button, Window, Slider, Canvas
from utils.net import Host, PointHandler

pygame.init()

def main():

    POPUP_WINDOW_SIZE = (300, 100)
    MAIN_WINDOW_SIZE = (1350, 580)

    host = Host()

    ##### WELCOMING POPUP INIT #####

    popup_window = Window("Szukam robota", POPUP_WINDOW_SIZE, "white")        
    popup_window.warning('Tworzenie WEBSocket')

    while True: ##### WELCOMING POPUP LOOP #####

        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                pygame.quit()
                host.server.close()
                sys.exit()

        if host.connect():
            pygame.display.quit()
            break 
        else:
            popup_window.warning(host.message)

    ##### DRAWING WINDOW INIT #####

    main_window = Window("Tablica", MAIN_WINDOW_SIZE, "gray")

    handler = PointHandler(idle_offset=25)

    slider = Slider(main_window.window, 1278, 280, 48, 250)

    canvas = Canvas(main_window.window, 8, 8, 1244, 564)

    z=0

    test_button = Button(main_window.window, 1267, 8, 70, 40, "Test", lambda: handler.test_canvas(canvas, z))

    move_button = Button(main_window.window, 1267, 88, 70, 40, "Move", lambda: handler.move_robot(canvas, z, host))

    clear_button = Button(main_window.window, 1267, 168, 70, 40, "Clear", lambda: handler.clear_canvas(canvas))

    Run = True

    while Run:   ##### DRAWING WINDOW LOOP #####
        
        for event in pygame.event.get():
            
            if event.type==pygame.QUIT:
                pygame.display.quit()
                handler.move_robot(canvas, z, host)
                Run = False
                break

            coursor_position = pygame.mouse.get_pos()

            if pygame.mouse.get_pressed()[0]:
                
                test_button.click(coursor_position)
                move_button.click(coursor_position)
                clear_button.click(coursor_position)
                slider.click(coursor_position)
                if not handler.special_active:
                    handler.follow(canvas.draw(coursor_position), z)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if Widget.active_widget == canvas:
                        handler.follow(canvas.end_draw(coursor_position), z)
                    Widget.active_widget = False
        
        if handler.special_active and len(handler.point_buffer)==0:
            handler.special_active = False
        
        if len(handler.point_buffer)!=0:
            if host.ready_to_send:
                raw_points, points_to_send = handler.fetch(slider.z)
                print("raw: ", raw_points)
                print("sending: ", points_to_send)
                #print("cooked: ", points_to_send)
                sent_points_bin = host.send_data(points_to_send)
                host.ready_to_send = False
            feedback = host.get_data()
            if len(points_to_send)==0:
                host.ready_to_send = True
            elif feedback == sent_points_bin:
                if not handler.special_active:
                    canvas.update_drawings(raw_points)
                host.ready_to_send = True
        
        if not Run:
            break

        pygame.display.update()

    host.server.close()

    ##### EXIT POPUP #####

    popup_window = Window("Zamykam program", POPUP_WINDOW_SIZE, "white")
    popup_window.warning('Wyłączanie...')

    time.sleep(1)
    pygame.quit()
    sys.exit()

if __name__=="__main__":
    main()