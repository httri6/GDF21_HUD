import pygame
import sys
import math

# 色定義
BLACK      = (0, 0, 0)
WHITE      = (255, 255, 255)
YELLOW     = (255, 255, 0)
GREEN      = (0, 255, 0)
BRIGHT_RED = (255, 80, 80)
GRAY       = (40, 40, 40)

WIDTH, HEIGHT = 900, 500

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('HUD Dashboard Gear Arc Tachometer')
font_big = pygame.font.SysFont(None, 230)
font_sml = pygame.font.SysFont(None, 90)
rpm_font = pygame.font.SysFont(None, 36)  # 小さめ

clock = pygame.time.Clock()
GEARS = ['N', '1', '2', '3', '4']

# ロゴ画像ロード（大きめ、端に寄せるためmargin大きめ）
icon_size = 200
indicator_margin = 18  # 端に寄せる
water_icon = pygame.image.load("water_icon.png").convert_alpha()
water_icon = pygame.transform.smoothscale(water_icon, (icon_size, icon_size))
battery_icon = pygame.image.load("battery_icon.png").convert_alpha()
battery_icon = pygame.transform.smoothscale(battery_icon, (icon_size, icon_size))
engine_icon = pygame.image.load("engine_icon.png").convert_alpha()
engine_icon = pygame.transform.smoothscale(engine_icon, (icon_size, icon_size))
oil_icon = pygame.image.load("oil_icon.png").convert_alpha()
oil_icon = pygame.transform.smoothscale(oil_icon, (icon_size, icon_size))

def tint_icon(icon, color):
    arr = pygame.surfarray.pixels3d(icon.copy())
    mask = (arr[:,:,0] < 128) & (arr[:,:,1] < 128) & (arr[:,:,2] < 128)
    arr[mask] = color
    surface = pygame.Surface(icon.get_size(), pygame.SRCALPHA)
    surface.blit(icon, (0,0))
    arr_out = pygame.surfarray.pixels3d(surface)
    arr_out[:,:,:] = arr
    return surface

def get_arc_angles(gear_rect, center):
    left_down = (gear_rect.left, gear_rect.bottom)
    right_down = (gear_rect.right, gear_rect.bottom)
    cx, cy = center
    angle_start = math.degrees(math.atan2(left_down[1]-cy, left_down[0]-cx))
    angle_end   = math.degrees(math.atan2(right_down[1]-cy, right_down[0]-cx))
    if angle_end <= angle_start:
        angle_end += 360
    return angle_start, angle_end

def draw_gear_arc_tachometer(center, gear_rect, radius, rpm, fixed_angles=None):
    n = 48
    min_rpm = 6000
    yellow_rpm = 8000
    red_rpm = 9000
    max_rpm = 10000

    cx, cy = center

    if fixed_angles is not None:
        angle_start, angle_end = fixed_angles
    else:
        angle_start, angle_end = get_arc_angles(gear_rect, center)
    arc_total = angle_end - angle_start

    points = []
    for i in range(n):
        theta_deg = angle_start + arc_total * (i / (n-1))
        theta_rad = math.radians(theta_deg)
        x = cx + radius * math.cos(theta_rad)
        y = cy + radius * math.sin(theta_rad)
        points.append((x, y))

    progress = min(max((rpm - min_rpm) / (max_rpm - min_rpm), 0.0), 1.0)
    lit_count = int(progress * (n-1)) + 1 if rpm >= min_rpm else 0

    def get_color(idx):
        ratio = idx/(n-1)
        now_rpm = min_rpm + (max_rpm-min_rpm) * ratio
        if now_rpm < yellow_rpm:
            return GREEN
        elif now_rpm < red_rpm:
            return YELLOW
        else:
            return BRIGHT_RED

    thick_width = 32
    for i in range(n-1):
        color = GRAY
        if i < lit_count-1:
            color = get_color(i)
        pygame.draw.line(screen, color, points[i], points[i+1], thick_width)

    memori_font = pygame.font.SysFont(None, 28)
    dot_outer_r = radius + thick_width//2 + 16
    dot_inner_r = radius + thick_width//2 + 4

    percent_9000 = (9000 - min_rpm) / (max_rpm - min_rpm)
    theta_deg_9000 = angle_start + arc_total * percent_9000
    theta_rad_9000 = math.radians(theta_deg_9000)
    lx_9000 = cx + (dot_outer_r + 28) * math.cos(theta_rad_9000)
    ly_9000 = cy + (dot_outer_r + 28) * math.sin(theta_rad_9000) + 20  # +20ピクセル下

    percent_7000 = (7000 - min_rpm) / (max_rpm - min_rpm)
    theta_deg_7000 = angle_start + arc_total * percent_7000
    theta_rad_7000 = math.radians(theta_deg_7000)
    lx_7000 = cx + (dot_outer_r + 28) * math.cos(theta_rad_7000)
    ly_7000 = ly_9000  # 9000と同じy座標

    for t_rpm in range(6000, 10001, 100):
        percent = (t_rpm - min_rpm) / (max_rpm - min_rpm)
        if percent < 0 or percent > 1: continue
        theta_deg = angle_start + arc_total * percent
        theta_rad = math.radians(theta_deg)
        x = cx + dot_outer_r * math.cos(theta_rad)
        y = cy + dot_outer_r * math.sin(theta_rad)
        if t_rpm % 1000 == 0:
            pygame.draw.circle(screen, WHITE, (int(x), int(y)), 8)
            label = memori_font.render(str(t_rpm), True, WHITE)
            label_offset = 28
            if t_rpm == 7000:
                lx = lx_7000
                ly = ly_7000
            elif t_rpm == 9000:
                lx = lx_9000
                ly = ly_9000
            else:
                lx = cx + (dot_outer_r + label_offset) * math.cos(theta_rad)
                ly = cy + (dot_outer_r + label_offset) * math.sin(theta_rad)
            label_rect = label.get_rect(center=(lx, ly))
            screen.blit(label, label_rect)
        else:
            pygame.draw.circle(screen, WHITE, (int(x), int(y)), 3)

    for t_rpm, color in [(8000, YELLOW), (9000, BRIGHT_RED)]:
        percent = (t_rpm - min_rpm) / (max_rpm - min_rpm)
        theta_deg = angle_start + arc_total * percent
        theta_rad = math.radians(theta_deg)
        x = cx + dot_outer_r * math.cos(theta_rad)
        y = cy + dot_outer_r * math.sin(theta_rad)
        pygame.draw.circle(screen, color, (int(x), int(y)), 11)

    rpm_txt = rpm_font.render(str(rpm), True, WHITE)
    rpm_rect = rpm_txt.get_rect(center=(cx, cy+radius//2+25))
    screen.blit(rpm_txt, rpm_rect)

def draw_gear(center, gear):
    txt = font_big.render(str(gear), True, WHITE)
    rect = txt.get_rect(center=center)
    screen.blit(txt, rect)
    return rect  # rectを返却

def draw_corner_icon(x, y, icon, color, value_str, font=font_sml):
    icon_colored = tint_icon(icon, color)
    screen.blit(icon_colored, (x, y))
    txt = font.render(value_str, True, WHITE)
    rect = txt.get_rect(center=(x+icon.get_width()//2, y+icon.get_height()-8))
    screen.blit(txt, rect)

def get_lamp_color(val, kind):
    # 水温ランプ: ~70°C緑、~90°Cイエロー、90°C超で赤
    if kind == "water":
        if val <= 70:
            return GREEN
        elif val <= 90:
            return YELLOW
        else:
            return BRIGHT_RED
    # 油温ランプ: ~100°C緑、~120°Cイエロー、120°C超で赤
    elif kind == "oil":
        if val <= 100:
            return GREEN
        elif val <= 120:
            return YELLOW
        else:
            return BRIGHT_RED
    elif kind == "battery":
        return GREEN if val >= 12.0 else BRIGHT_RED
    elif kind == "engine":
        return GREEN if val >= 100 else BRIGHT_RED
    return (128,128,128)

def main():
    rpm = 6000
    gear_idx = 0
    water_temp = 65
    oil_temp = 90
    battery_v = 12.5
    oil_press = 110
    step = 0

    margin = indicator_margin
    font = font_sml

    # やや下に配置（+40pxずらし）
    center_offset_y = 40

    gear_center = (WIDTH//2, HEIGHT//2-20+center_offset_y)
    base_gear_rect = draw_gear(gear_center, GEARS[0])
    fixed_angles = get_arc_angles(base_gear_rect, gear_center)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: gear_idx = min(gear_idx+1, 4)
                if event.key == pygame.K_DOWN: gear_idx = max(gear_idx-1, 0)

        step += 1
        rpm = 6000 + int(4000 * abs(math.sin(step/70)))  # 6000〜10000で上下
        water_temp = 60 + int(40 * abs(math.sin(step/60)))
        oil_temp   = 90 + int(50 * abs(math.sin(step/120)))
        battery_v  = 11.8 + 1.0 * abs(math.sin(step/45))
        oil_press  = 50 + int(350 * abs(math.sin(step/80)))  # 50~400で動く

        screen.fill(BLACK)

        gear_center = (WIDTH//2, HEIGHT//2-20+center_offset_y)
        gear_rect = draw_gear(gear_center, GEARS[gear_idx])

        draw_gear_arc_tachometer(gear_center, gear_rect, 180, rpm, fixed_angles=fixed_angles)

        draw_corner_icon(margin, margin, water_icon, get_lamp_color(water_temp, "water"), f"{water_temp}", font)
        draw_corner_icon(margin, HEIGHT-margin-icon_size, battery_icon, get_lamp_color(battery_v, "battery"), f"{battery_v:.1f}", font)
        draw_corner_icon(WIDTH-margin-icon_size, margin, oil_icon, get_lamp_color(oil_temp, "oil"), f"{oil_temp}", font)
        draw_corner_icon(WIDTH-margin-icon_size, HEIGHT-margin-icon_size, engine_icon, get_lamp_color(oil_press, "engine"), f"{oil_press}", font)

        pygame.display.update()
        clock.tick(30)

if __name__ == "__main__":
    main()
