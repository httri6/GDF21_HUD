import pygame
import sys
import math

# 色定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE  = (0, 180, 255)
GREEN = (0, 255, 0)
RED   = (255, 0, 0)
YELLOW = (255, 255, 0)
DARK_BLUE = (0, 60, 150)
ORANGE = (255, 128, 0)
GRAY = (180, 180, 180)

# 画面サイズ
WIDTH = 800
HEIGHT = 480

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('HUD Dashboard')
font_l = pygame.font.SysFont(None, 80)
font_m = pygame.font.SysFont(None, 48)
font_s = pygame.font.SysFont(None, 32)
clock = pygame.time.Clock()

def get_tacho_color(rpm):
    if rpm < 7500:
        return BLUE
    elif rpm < 8500:
        return GREEN
    else:
        return RED

def get_temp_color(value, blue_max, green_max):
    if value <= blue_max:
        return BLUE
    elif value <= green_max:
        return GREEN
    else:
        return RED

def get_pressure_color(pressure):
    # 値と色の対応は任意。例として
    if pressure < 2:
        return RED
    elif pressure < 4:
        return ORANGE
    elif pressure < 6:
        return GREEN
    else:
        return BLUE

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def draw_tachometer(rpm):
    cx, cy, radius = WIDTH//2, 350, 200
    pygame.draw.circle(screen, GRAY, (cx, cy), radius, 3)
    # 1000～9000rpmをアークで表示
    for i in range(10, 91, 1):  # 1000rpm～9000rpm: 100rpmごと
        angle = (i-10)/80 * 240 - 120   # -120°～120°に配置
        rad = angle * 3.1416 / 180
        length = radius - 20 if i%5==0 else radius - 10
        x1 = cx + int(length * math.cos(rad))
        y1 = cy + int(length * math.sin(rad))
        x2 = cx + int(radius * math.cos(rad))
        y2 = cy + int(radius * math.sin(rad))
        color = None
        if i*100 >= 8500:
            color = RED
        elif i*100 >= 7500:
            color = GREEN
        elif i*100 >= 6500:
            color = BLUE
        else:
            color = GRAY
        width = 6 if int(rpm/100) >= i else 2
        pygame.draw.line(screen, color, (x1, y1), (x2, y2), width)
    # 針
    percent = min(max((rpm-1000)/8000, 0), 1)
    angle = percent*240 - 120
    rad = angle * 3.1416 / 180
    x = cx + int((radius-60) * math.cos(rad))
    y = cy + int((radius-60) * math.sin(rad))
    pygame.draw.line(screen, YELLOW, (cx, cy), (x, y), 6)
    # 数字
    draw_text(f'{rpm:.0f} rpm', font_m, WHITE, cx-90, cy-40)

def main():
    rpm = 1000
    water_temp = 60
    oil_temp = 90
    oil_pressure = 4.5
    fuel_pressure = 3.5
    step = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # ダミー値変化
        step += 1
        rpm = 1000 + (step % 80) * 100   # 1000～9000rpm
        water_temp = 60 + (step % 50)    # 60～109℃
        oil_temp = 85 + (step % 60)      # 85～144℃
        oil_pressure = 1.0 + ((step % 60)/10)  # 1.0～7.0
        fuel_pressure = 2.0 + ((step % 30)/5)  # 2.0～8.0

        screen.fill(BLACK)

        # タコメーター
        draw_tachometer(rpm)

        # 水温・油温・油圧・燃圧（数値とランプ）
        draw_text("水温", font_s, WHITE, 30, 30)
        draw_text(f"{water_temp:.0f} ℃", font_m, WHITE, 30, 60)
        pygame.draw.circle(screen, get_temp_color(water_temp, 70, 90), (180, 75), 20)

        draw_text("油温", font_s, WHITE, 30, 150)
        draw_text(f"{oil_temp:.0f} ℃", font_m, WHITE, 30, 180)
        pygame.draw.circle(screen, get_temp_color(oil_temp, 110, 125), (180, 195), 20)

        draw_text("油圧", font_s, WHITE, 30, 270)
        draw_text(f"{oil_pressure:.1f} kg/cm2", font_m, WHITE, 30, 300)
        pygame.draw.circle(screen, get_pressure_color(oil_pressure), (180, 315), 20)

        draw_text("燃圧", font_s, WHITE, 30, 370)
        draw_text(f"{fuel_pressure:.1f} kg/cm2", font_m, WHITE, 30, 400)
        pygame.draw.circle(screen, get_pressure_color(fuel_pressure), (180, 415), 20)

        pygame.display.update()
        clock.tick(20)

if __name__ == "__main__":
    main()
