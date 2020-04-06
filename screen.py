import pygame
import random
import math

SCREEN_DIM = (800, 600)


class Vec2d:
    """Класс 2-мерных векторов
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, vec):
        """"возвращает разность двух векторов"""
        return Vec2d(self.x - vec.x, self.y - vec.y)

    def __add__(self, vec):
        """возвращает сумму двух векторов"""
        return Vec2d(self.x + vec.x, self.y + vec.y)

    def __mul__(self, k):
        """возвращает произведение вектора на число"""
        return Vec2d(self.x * k, self.y * k)

    def __len__(self, x):
        """возвращает длину вектора"""
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def int_pair(self):
        """возвращает пару координат, определяющих вектор (координаты точки конца вектора),
        координаты начальной точки вектора совпадают с началом системы координат (0, 0)"""
        return (int(self.x), int(self.y))


class Polyline:
    """Класс замкнутых ломаных линий
    """

    def __init__(self):
        self.points = []
        self.speeds = []

    def add_point(self, point, speed):
        self.points.append(point)
        self.speeds.append(speed)

    def delete_last_point(self):
        if self.points:
            self.points.pop()
            self.speeds.pop()

    def set_points(self):
        """функция перерасчета координат опорных точек.
        Если точка достигает конца экрана, знак вектора ее скорости (speed)
        меняется на противоположный
        """
        for i in range(len(self.points)):
            self.points[i] += self.speeds[i]
            if self.points[i].x > SCREEN_DIM[0] or self.points[i].x < 0:
                self.speeds[i].x = - self.speeds[i].x
            if self.points[i].y > SCREEN_DIM[1] or self.points[i].y < 0:
                self.speeds[i].y = - self.speeds[i].y

    def change_speed(self, k):
        """изменить скорость линии, k > 1 - увеличить, 0 < k < 1 - уменьшить"""
        for i in range(len(self.speeds)):
            self.speeds[i].x *= k
            self.speeds[i].y *= k

    def draw_points(self, width=3, color=(255, 255, 255)):
        """функция отрисовки опорных точек на экране"""
        for p in self.points:
            pygame.draw.circle(gameDisplay, color, p.int_pair(), width)

    def draw_line(self, width=3, color=(255, 255, 255)):
        """функция отрисовки ломаной линии на экране"""
        for p in range(-1, len(self.points) - 1):
            pygame.draw.line(
                gameDisplay,
                color,
                self.points[p].int_pair(),
                self.points[p + 1].int_pair(),
                width
            )


class Knot(Polyline):
    """Класс сглаженных кривый линий
    """

    def __init__(self, steps):
        super().__init__()
        self.steps = steps

    def get_point(self, points, alpha, deg=None):
        '''Вспомогательная функция для построения кривой'''
        if deg is None:
            deg = len(points) - 1
        if deg == 0:
            return points[0]
        return (points[deg] * alpha) + \
            (self.get_point(points, alpha, deg - 1) * (1 - alpha))

    def get_points(self, base_points):
        '''Вспомогательная функция для построения кривой'''
        alpha = 1 / self.steps
        res = []
        for i in range(self.steps):
            res.append(self.get_point(base_points, i * alpha))
        return res

    def get_knot(self):
        '''Расчет точек для построения кривой. Если точек
        больше 2-х создает массив.  Возвращает массив, содержащий
        координаты точек для построения кривой
        '''
        if len(self.points) < 3:
            return []
        res = []
        for i in range(-2, len(self.points) - 2):
            ptn = []
            ptn.append((self.points[i] + self.points[i + 1]) * 0.5)
            ptn.append(self.points[i + 1])
            ptn.append((self.points[i + 1] + self.points[i + 2]) * 0.5)

            res.extend(self.get_points(ptn))
        return res

    def draw_line(self, width=3, color=(255, 255, 255)):
        """функция отрисовки кривой на экране"""
        points = self.get_knot()
        for p_n in range(-1, len(points) - 1):
            pygame.draw.line(
                gameDisplay,
                color,
                points[p_n].int_pair(),
                points[p_n + 1].int_pair(),
                width
            )


def draw_help():
    """функция отрисовки экрана справки программы"""
    gameDisplay.fill((50, 50, 50))
    font1 = pygame.font.SysFont("courier", 24)
    font2 = pygame.font.SysFont("serif", 24)
    data = []
    data.append(["F1", "Show Help"])
    data.append(["R", "Restart"])
    data.append(["P", "Pause/Play"])
    data.append(["Num+", "More points"])
    data.append(["Num-", "Less points"])
    data.append(["D", "Delete last added point of polyline"])
    data.append(["N", "Add new polyline"])
    data.append(["S", "Increase speed of current polyline"])
    data.append(["Ctrl+S", "Increase speed of all polylines"])
    data.append(["A", "Decrease speed of current polyline"])
    data.append(["Ctrl+A", "Decrease speed of all polylines"])
    data.append(["", ""])
    for i, k in enumerate(knots, 1):
        data.append([str(k.steps), f"Polyline №{i} points"])

    pygame.draw.lines(gameDisplay, (255, 50, 50, 255), True, [
        (0, 0), (800, 0), (800, 600), (0, 600)], 5)
    for i, text in enumerate(data):
        gameDisplay.blit(font1.render(
            text[0], True, (128, 128, 255)), (100, 100 + 30 * i))
        gameDisplay.blit(font2.render(
            text[1], True, (128, 128, 255)), (200, 100 + 30 * i))


if __name__ == "__main__":
    # Initilize library and set up drawing window
    pygame.init()
    gameDisplay = pygame.display.set_mode(SCREEN_DIM)
    pygame.display.set_caption("MyScreenSaver")

    steps = 35  # Basic polyline smoothness
    working = True
    knots = [Knot(steps)]
    idx = 0
    show_help = False
    pause = True

    hue = 0
    color = pygame.Color(0)

    while working:
        for event in pygame.event.get():
            # Program quit
            if event.type == pygame.QUIT:
                working = False
            # Keystroke handling
            if event.type == pygame.KEYDOWN:
                # Press Esc to exit
                if event.key == pygame.K_ESCAPE:
                    working = False
                # Press R to restart
                if event.key == pygame.K_r:
                    knots = [Knot(steps)]
                    idx = 0
                    knots[idx].points.clear()
                    knots[idx].points.clear()
                # Pause
                if event.key == pygame.K_p:
                    pause = not pause
                # Delete previous added point
                if event.key == pygame.K_d:
                    knots[idx].delete_last_point()
                # Add new polyline, make it active
                if event.key == pygame.K_n:
                    knots.append(Knot(steps))
                    idx += 1
                # Increase speed
                if event.key == pygame.K_s:
                    if pygame.key.get_mods() & pygame.KMOD_CTRL:
                        # Increase speed of all polylines
                        for knot in knots:
                            knot.change_speed(2)
                    else:
                        # Increase speed of current active polyline
                        knots[idx].change_speed(2)
                # Decrease speed
                if event.key == pygame.K_a:
                    if pygame.key.get_mods() & pygame.KMOD_CTRL:
                        # Decrease speed of all polylines
                        for knot in knots:
                            knot.change_speed(0.5)
                    else:
                        # Decrease speed of current active polyline
                        knots[idx].change_speed(0.5)
                # Increase steps of polyline smoothness
                if event.key == pygame.K_KP_PLUS:
                    knots[idx].steps += 1
                # Decrease steps of polyline smoothness
                if event.key == pygame.K_KP_MINUS:
                    knots[idx].steps -= 1 if knots[idx].steps > 1 else 0
                # Press F1 to show help message
                if event.key == pygame.K_F1:
                    show_help = not show_help

            # Mouse click to add new point and speed (random)
            if event.type == pygame.MOUSEBUTTONDOWN:
                knots[idx].add_point(
                    Vec2d(*event.pos),
                    Vec2d(random.random() * 2, random.random() * 2)
                )

        # Fill the background with black
        gameDisplay.fill((0, 0, 0))

        # Changing color of polyline
        hue = (hue + 1) % 360

        for i, knot in enumerate(knots):
            color.hsla = ((hue + 90 * i) % 360, 100, 50, 100)
            # Draw points
            knot.draw_points()
            # Draw lines
            knot.draw_line(color=color)

        if not pause:
            for knot in knots:
                knot.set_points()
        if show_help:
            draw_help()

        pygame.display.flip()

    pygame.display.quit()
    pygame.quit()
    exit(0)
