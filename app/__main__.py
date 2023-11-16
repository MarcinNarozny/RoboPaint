import pygame
import sys
import time
from .utils.gui import Widget, Button, Window, Slider, Canvas
from .utils.net import Host, PointHandler

pygame.init()


def main():

    POPUP_WINDOW_SIZE = (300, 100)
    MAIN_WINDOW_SIZE = (1350, 580)

    host = Host()

    # WELCOMING POPUP INIT

    popup_window = Window("Connection", POPUP_WINDOW_SIZE, "white")
    popup_window.warning('Connecting')

    while True:  # WELCOMING POPUP LOOP

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

    # DRAWING WINDOW INIT

    main_window = Window("RoboPaint", MAIN_WINDOW_SIZE, "gray")

    handler = PointHandler(idle_offset=25)

    slider = Slider(main_window.window, x=1278, y=280, width=48, height=250)

    canvas = Canvas(main_window.window, 8, 8, 1244, 564)

    z = 0

    test_button = Button(main_window.window, 1267, 8, 70,
                         40, "Test", lambda: handler.test_canvas(canvas, z))

    move_button = Button(main_window.window, 1267, 88, 70,
                         40, "Move", lambda: handler.move_robot(canvas, z, host))

    clear_button = Button(main_window.window, 1267, 168,
                          70, 40, "Clear", lambda: handler.clear_canvas(canvas))

    Run = True

    while Run:  # DRAWING WINDOW LOOP

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
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

        if handler.special_active and not handler.point_buffer:
            handler.special_active = False

        if handler.point_buffer:
            if host.ready_to_send:
                unoptimized_points, optimized_points = handler.fetch(slider.z)
                sent_points = host.send_data(optimized_points)
                host.ready_to_send = False

            if sent_points == host.get_data():
                host.ready_to_send = True
                if not handler.special_active:
                    canvas.draw_progress(unoptimized_points)

        if not Run:
            break

        pygame.display.update()

    host.server.close()

    # EXIT POPUP

    popup_window = Window("Zamykam program", POPUP_WINDOW_SIZE, "white")
    popup_window.warning('Wyłączanie...')

    time.sleep(1)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()