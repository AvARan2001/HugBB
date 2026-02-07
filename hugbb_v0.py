import pygame
import math
import sys
import random

# --- 1. 初始化 ---
pygame.init()
WIDTH, HEIGHT = 800, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption("抱抱模拟器 - 温馨满屋版")
clock = pygame.time.Clock()

# --- 2. 配色方案 (V8 高级配色 + 新增宠物植物配色) ---
BG_WALL_COLOR = (120, 110, 105)
FLOOR_COLOR = (200, 160, 120)
FLOOR_LINE_COLOR = (180, 140, 100)

LIGHT_COLOR = (255, 250, 230, 40)    # 暖白光
SHADOW_COLOR = (0, 0, 0, 60)

# 床品配色
BED_FRAME_COLOR = (90, 60, 40)
SHEET_COLOR = (245, 240, 230)        # 米白床单
PILLOW_COLOR = (230, 225, 220)       # 枕头色
BLANKET_COLOR = (200, 100, 80)       # 砖红被子
BLANKET_SHADOW = (150, 70, 50)       # 被子阴影

# 人物配色
SKIN_COLOR = (255, 230, 210)
BLUSH_COLOR = (255, 170, 170)
BOY_HAIR = (60, 60, 70)              # 深灰发
GIRL_HAIR = (130, 90, 60)            # 棕发
GLASSES_COLOR = (30, 30, 40)
BOY_CLOTHES = (150, 170, 190)        # 灰蓝睡衣
GIRL_CLOTHES = (220, 190, 190)       # 藕粉睡衣

# 新增：植物与宠物配色
POT_COLOR = (160, 90, 60)            # 陶土花盆
PLANT_STEM = (100, 70, 40)
PLANT_LEAF = (60, 110, 60)           # 深绿叶子
CAT_COLOR = (230, 150, 50)           # 橘猫底色
CAT_STRIPE = (200, 120, 30)          # 橘猫条纹
DOG_COLOR = (245, 240, 235)          # 拉布拉多米白

# 粒子与UI
DUST_COLOR = (255, 240, 200)
HEART_COLOR = (235, 80, 80)
BUTTON_COLOR = (100, 170, 240)
BUTTON_HOVER_COLOR = (120, 190, 255)
TEXT_COLOR = (255, 255, 255)

# --- 3. 辅助类 ---

class Button:
    def __init__(self, x, y, width, height, text, action_code):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action_code = action_code
        self.is_hovered = False

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(surface, SHADOW_COLOR, self.rect.move(3,3), border_radius=10)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (255,255,255), self.rect, 2, border_radius=10)
        try: font = pygame.font.SysFont("arial", 20, bold=True)
        except: font = pygame.font.Font(None, 24)
        text_surf = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class Particle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(2, 5)
        self.speed_x = random.uniform(0.2, 0.6)
        self.speed_y = random.uniform(-0.2, 0.2)
        self.alpha = random.randint(100, 255)
        self.fade_dir = -2

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.alpha += self.fade_dir
        if self.alpha >= 255: self.alpha = 255; self.fade_dir = -2
        elif self.alpha <= 50: self.alpha = 50; self.fade_dir = 2
        if self.x > WIDTH: self.x = 0
        if self.y < 0: self.y = HEIGHT
        if self.y > HEIGHT: self.y = 0

    def draw(self, surface):
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        safe_alpha = int(max(0, min(255, self.alpha)))
        pygame.draw.circle(s, (*DUST_COLOR, safe_alpha), (self.size//2, self.size//2), self.size//2)
        surface.blit(s, (self.x, self.y))

# --- 4. 绘图函数 (保持 V2 几何画风) ---

def draw_room_bg(surface):
    pygame.draw.rect(surface, BG_WALL_COLOR, (0, 0, WIDTH, 250))
    pygame.draw.rect(surface, FLOOR_COLOR, (0, 250, WIDTH, HEIGHT-250))
    for i in range(0, WIDTH, 150):
        pygame.draw.line(surface, FLOOR_LINE_COLOR, (i, 250), (i, HEIGHT), 2)
    pygame.draw.line(surface, (90, 80, 75), (0, 250), (WIDTH, 250), 4)

# --- 新增：绘制植物和宠物 ---
# --- 新增的辅助配色 (为了更精美的细节) ---
PLANT_LEAF_LIGHT = (90, 140, 90)  # 亮部叶色
PLANT_VEIN = (40, 70, 40)         # 深色叶脉
POT_RIM = (170, 100, 70)          # 花盆沿口色
POT_SHADOW = (130, 70, 50)        # 花盆阴影色

def draw_fiddle_leaf_fig(surface, x, y):
    """绘制精美、有细节和层次感的琴叶榕 (左下角)"""

    # --- 内部核心：绘制精美叶片的函数 ---
    def draw_exquisite_leaf(surf, connect_x, connect_y, scale, angle):
        """
        绘制一片有形状、光影和叶脉的精美叶子
        scale: 缩放比例 (1.0 为标准大小约 80x60)
        angle: 旋转角度
        """
        base_w, base_h = 80 * scale, 100 * scale
        surf_w, surf_h = int(base_w + 20), int(base_h + 20)
        leaf_surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        cx, cy = surf_w // 2, surf_h // 2

        # 1. 叶片主体造型 (模拟小提琴形状：基部窄，端部宽)
        # 通过叠加两个椭圆实现
        # 端部大椭圆
        tip_rect = pygame.Rect(cx - base_w*0.45, cy - base_h*0.4, base_w*0.9, base_h*0.6)
        # 基部小椭圆
        base_rect = pygame.Rect(cx - base_w*0.3, cy + base_h*0.1, base_w*0.6, base_h*0.3)
        
        # 绘制深色底座 (描边效果)
        pygame.draw.ellipse(leaf_surf, PLANT_VEIN, tip_rect.inflate(4,4))
        pygame.draw.ellipse(leaf_surf, PLANT_VEIN, base_rect.inflate(4,4))
        
        # 绘制主体深绿
        pygame.draw.ellipse(leaf_surf, PLANT_LEAF, tip_rect)
        pygame.draw.ellipse(leaf_surf, PLANT_LEAF, base_rect)
        
        # 2. 绘制亮部高光 (向左上方偏移，制造立体感)
        highlight_offset_x = -base_w * 0.05
        highlight_offset_y = -base_h * 0.05
        pygame.draw.ellipse(leaf_surf, PLANT_LEAF_LIGHT, tip_rect.move(highlight_offset_x, highlight_offset_y).inflate(-10, -10))
        
        # 3. 绘制叶脉细节
        # 主脉
        vein_start = (cx, cy + base_h*0.35)
        vein_end = (cx, cy - base_h*0.3)
        pygame.draw.line(leaf_surf, PLANT_VEIN, vein_start, vein_end, 3)
        # 侧脉 (简单的几条肋线)
        for i in range(3):
            pos_y = cy - base_h*0.2 + i * base_h*0.15
            # 左侧脉
            pygame.draw.line(leaf_surf, PLANT_VEIN, (cx, pos_y), (cx - base_w*0.3, pos_y - 5), 2)
            # 右侧脉
            pygame.draw.line(leaf_surf, PLANT_VEIN, (cx, pos_y), (cx + base_w*0.3, pos_y - 5), 2)

        # 4. 旋转与定位
        rotated_surf = pygame.transform.rotate(leaf_surf, angle)
        # 计算旋转后的中心点，使其叶柄对齐连接点
        # 这里做一个简化的近似对齐
        offset_x = -math.sin(math.radians(angle)) * (base_h * 0.3)
        offset_y = math.cos(math.radians(angle)) * (base_h * 0.3)
        
        draw_rect = rotated_surf.get_rect(center=(connect_x + offset_x, connect_y + offset_y))
        surf.blit(rotated_surf, draw_rect)
        
        # 画个小叶柄连接一下
        pygame.draw.line(surf, PLANT_STEM, (connect_x, connect_y), (connect_x + offset_x*0.5, connect_y + offset_y*0.5), 4)


    # --- 1. 精美花盆 (带沿口和阴影) ---
    pot_y_base = y + 60
    # 盆体主体
    pot_poly = [(x-25, y+10), (x+25, y+10), (x+18, pot_y_base), (x-18, pot_y_base)]
    pygame.draw.polygon(surface, POT_COLOR, pot_poly)
    # 盆体阴影 (右侧)
    shadow_poly = [(x+10, y+10), (x+25, y+10), (x+18, pot_y_base), (x+5, pot_y_base)]
    pygame.draw.polygon(surface, POT_SHADOW, shadow_poly)
    # 盆沿 (宽一点，带厚度)
    pygame.draw.rect(surface, POT_RIM, (x-32, y, 64, 12), border_radius=4)
    pygame.draw.rect(surface, POT_COLOR, (x-30, y+2, 60, 8)) # 盆口内侧

    # --- 2. 树干结构 (下粗上细) ---
    # 主干底部
    pygame.draw.polygon(surface, PLANT_STEM, [(x-4, y+5), (x+4, y+5), (x+3, y-120), (x-3, y-120)])
    # 主干中上部
    pygame.draw.polygon(surface, PLANT_STEM, [(x-3, y-120), (x+3, y-120), (x+2, y-200), (x-2, y-200)])
    
    # 分枝连接点
    branch_y_1 = y - 90
    branch_y_2 = y - 140

    # --- 3. 精美叶片布局 (位置, 缩放, 角度) ---
    # 角度：正值逆时针(向左倒), 负值顺时针(向右倒)
    leaves_layout = [
        # 底层大叶
        (x-20, branch_y_1+20, 1.1, 70),   # 左下大
        (x+20, branch_y_1+10, 1.1, -65),  # 右下大
        # 中层
        (x-5, y-110, 1.0, 10),            # 中间正
        (x-25, branch_y_2, 0.9, 85),      # 左中
        (x+25, branch_y_2-10, 0.95, -80), # 右中
        # 顶层嫩叶
        (x-10, y-180, 0.8, 45),           # 顶左
        (x+10, y-210, 0.7, -30),          # 顶尖
    ]

    # 绘制所有叶片
    for lx, ly, scale, ang in leaves_layout:
        draw_exquisite_leaf(surface, lx, ly, scale, ang)

# 绘制一只有清晰头/耳/尾巴、会呼吸睡觉的橘猫
def draw_sleeping_cat(surface, x, y):
    """
    绘制 "液体猫猫"：严格按照照片形体，像一碗金黄的面团/牛角包
    特点：头埋在左边，背部在右边拱起，整体呈完美的圆形填满空间。
    """
    # --- 1. 呼吸动画 (沉睡的起伏) ---
    # 频率慢，幅度小，模拟深呼吸
    breath_scale = 1.0 + math.sin(pygame.time.get_ticks() * 0.0025) * 0.015
    
    # --- 2. 创建画布 ---
    # 照片里的猫是非常圆润的一团，不需要太宽
    canvas_w, canvas_h = 120, 110
    cat_surf = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)
    cx, cy = canvas_w // 2, canvas_h // 2

    # --- 配色准备 (模拟照片里的阳光感) ---
    # 假设外部定义了 CAT_COLOR (橘色), CAT_STRIPE (深橘色)
    # 我们需要额外的“高光色”来模拟照片右侧背部的强光
    c_base = CAT_COLOR
    c_shadow = CAT_STRIPE
    # 阳光高光色 (比底色更亮更白一点)
    c_sunlight = (min(255, c_base[0]+30), min(255, c_base[1]+30), min(255, c_base[2]+20))
    # 阴影色 (身体蜷缩的深处)
    c_deep = (max(0, c_base[0]-30), max(0, c_base[1]-30), max(0, c_base[2]-30))

    # --- 3. 绘制 "液体" 形体 (从下往上堆叠) ---

    # A. 基础填充 (那个完美的圆形底座)
    # 就像面团填满了圆形的猫抓板
    base_rect = pygame.Rect(10, 15, 100, 85)
    pygame.draw.ellipse(cat_surf, c_base, base_rect)

    # B. 背部 (照片右侧/上侧是被阳光照亮的背)
    # 这是一个覆盖在右上方的大的亮色弧形
    back_rect = pygame.Rect(10, 15, 85, 80)
    pygame.draw.ellipse(cat_surf, c_sunlight, back_rect)

    # C. 身体卷曲的纹理 (模拟牛角包的螺旋结构)
    # 从左下往右上的弧线，表现身体蜷缩的紧致感
    # 阴影线条 1 (外圈)
    pygame.draw.arc(cat_surf, c_shadow, (15, 20, 90, 80), 0.5, 3.5, 3)
    # 阴影线条 2 (内圈，区分头和身体)
    pygame.draw.arc(cat_surf, c_shadow, (30, 30, 60, 60), 1.0, 3.8, 2)

    # D. 头部 (左侧，深深埋进去)
    # 在照片里，头在左边，大约 9-10 点钟方向，几乎和身体融为一体
    head_x, head_y = 45, 50
    # 画一个稍暗的圆代表头部阴影区
    pygame.draw.circle(cat_surf, c_base, (head_x, head_y), 22)
    
    # E. 耳朵 (非常关键的特征)
    # 照片里耳朵是平贴着的，在左上角
    # 左耳
    ear_l_poly = [(30, 35), (40, 25), (45, 40)]
    pygame.draw.polygon(cat_surf, c_shadow, ear_l_poly) 
    # 右耳 (稍微后面一点)
    ear_r_poly = [(48, 22), (60, 28), (55, 45)]
    pygame.draw.polygon(cat_surf, c_shadow, ear_r_poly)

    # F. 阳光的高光细节 (点睛之笔)
    # 在背部最高点加一点强光
    #pygame.draw.ellipse(cat_surf, (255, 240, 220, 100), (60, 25, 40, 20))

    # G. 修正边缘 (让它看起来是装在碗里的)
    # 稍微切一下底部的圆弧，让它看起来有重力感
    # 这一步通过不画正圆，而是略微压扁的椭圆(base_rect)已经实现了

    # --- 4. 呼吸与输出 ---
    target_w = int(canvas_w * breath_scale)
    target_h = int(canvas_h * breath_scale)
    scaled_cat = pygame.transform.smoothscale(cat_surf, (target_w, target_h))
    
    # 修正位置：因为形状变圆了，可能需要微调一下显示的中心
    surface.blit(scaled_cat, (x - target_w//2, y - target_h//2))

DOG_COLOR = (245, 240, 235) # 米白底色
def draw_sleeping_dog(surface, x, y, color_base=DOG_COLOR):
    """
    绘制一只毛绒绒、会呼吸睡觉的拉布拉多
    x, y: 狗狗的中心位置
    color_base: 狗狗的基础色 (例如 DOG_COLOR)
    """
    # 1. 计算呼吸缩放比例 (速度慢一点，幅度小一点，看起来睡得很沉)
    # 利用时间生成一个在 1.0 到 1.03 之间波动的系数
    breath_scale = 1.0 + math.sin(pygame.time.get_ticks() * 0.003) * 0.015
    
    # 2. 创建临时画布 (足够大能放下整个狗)
    # 使用 SRCALPHA 确保背景透明
    canvas_w, canvas_h = 160, 130
    dog_surf = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)
    # 临时画布的中心坐标，用于相对绘图
    cx, cy = canvas_w // 2, canvas_h // 2
    
    # --- 配色准备 (制造毛发层次感) ---
    c_main = color_base
    # 稍浅一点的颜色（高光区）
    c_light = (min(255, c_main[0]+15), min(255, c_main[1]+15), min(255, c_main[2]+15))
    # 稍深一点的颜色（阴影区/耳朵/尾巴）
    c_shadow = (max(0, c_main[0]-20), max(0, c_main[1]-20), max(0, c_main[2]-20))
    # 更深的耳朵阴影
    c_ear_shadow = (max(0, c_main[0]-40), max(0, c_main[1]-40), max(0, c_main[2]-40))

    # --- 开始绘制毛绒绒的身体 (用多个圆叠加) ---
    
    # 身体主体 (一大团)
    pygame.draw.ellipse(dog_surf, c_main, (cx-50, cy-30, 100, 60))
    
    # 后腿/屁股区域的毛发
    pygame.draw.circle(dog_surf, c_main, (cx+35, cy), 20)
    pygame.draw.circle(dog_surf, c_shadow, (cx+25, cy+15), 18) # 腿部阴影

    # 背部的毛发层次
    pygame.draw.circle(dog_surf, c_light, (cx, cy-30), 15)
    pygame.draw.circle(dog_surf, c_main, (cx-25, cy-28), 16)
    pygame.draw.circle(dog_surf, c_main, (cx+20, cy-25), 16)

    # --- 尾巴 (卷在身后) ---
    # 用几个渐变色的圆模拟卷曲感
    pygame.draw.circle(dog_surf, c_shadow, (cx+50, cy+5), 15)
    pygame.draw.circle(dog_surf, c_main, (cx+55, cy-5), 12)
    pygame.draw.circle(dog_surf, c_light, (cx+58, cy-12), 10) # 尾巴尖

    # --- 脑袋和耳朵 ---
    # 脑袋主体
    pygame.draw.circle(dog_surf, c_main, (cx-35, cy+5), 24)
    # 脑袋顶部的毛
    pygame.draw.circle(dog_surf, c_light, (cx-35, cy-10), 18)

    # 耷拉的大耳朵 (关键特征)
    # 使用多边形画出一个软塌塌的形状盖在脑袋侧面
    ear_poly = [
        (cx-45, cy-5),  # 耳根上
        (cx-68, cy+10), # 耳朵外侧
        (cx-60, cy+35), # 耳尖下垂
        (cx-35, cy+25)  # 耳根下
    ]
    pygame.draw.polygon(dog_surf, c_shadow, ear_poly)
    # 耳朵内侧/下侧的深影
    pygame.draw.polygon(dog_surf, c_ear_shadow, [(cx-60, cy+35), (cx-35, cy+25), (cx-45, cy+30)])

    # 鼻子 (深棕色小圆点)
    pygame.draw.circle(dog_surf, (60, 50, 40), (cx-58, cy+15), 5)

    # --- 3. 应用呼吸缩放 ---
    target_w = int(canvas_w * breath_scale)
    target_h = int(canvas_h * breath_scale)
    # 使用 smoothscale 进行平滑缩放，抗锯齿
    scaled_dog = pygame.transform.smoothscale(dog_surf, (target_w, target_h))
    
    # 4. 绘制到主屏幕 (修正中心点，确保缩放时位置不变)
    surface.blit(scaled_dog, (x - target_w//2, y - target_h//2))

# --------------------------------

def draw_pill_shape(surface, color, rect):
    pygame.draw.rect(surface, color, rect, border_radius=int(rect.height//2))

def draw_glasses(surface, x, y):
    x, y = int(x), int(y)
    pygame.draw.circle(surface, GLASSES_COLOR, (x - 12, y), 10, 2)
    pygame.draw.circle(surface, GLASSES_COLOR, (x + 12, y), 10, 2)
    pygame.draw.line(surface, GLASSES_COLOR, (x - 2, y), (x + 2, y), 2)

def draw_hair_boy(surface, x, y, color):
    pygame.draw.circle(surface, color, (int(x), int(y - 5)), 36, draw_top_right=True, draw_top_left=True)
    pygame.draw.arc(surface, color, (x - 38, y - 40, 50, 50), 2.5, 4.7, 30)
    pygame.draw.arc(surface, color, (x + 5, y - 40, 30, 40), 5.0, 6.0, 20)

def draw_hair_girl_long(surface, x, y, color):
    pygame.draw.ellipse(surface, color, (x - 45, y - 45, 90, 100))
    pygame.draw.circle(surface, color, (int(x - 30), int(y + 40)), 20)
    pygame.draw.circle(surface, color, (int(x + 30), int(y + 40)), 20)

def draw_face(surface, x, y, is_boy, kiss_offset=(0,0)):
    x = int(x + kiss_offset[0])
    y = int(y + kiss_offset[1])
    if not is_boy: draw_hair_girl_long(surface, x, y, GIRL_HAIR)
    pygame.draw.circle(surface, SKIN_COLOR, (x, y), 35)
    if is_boy: draw_hair_boy(surface, x, y, BOY_HAIR)
    else:
        pygame.draw.circle(surface, GIRL_HAIR, (x, int(y - 15)), 30, draw_top_right=True, draw_top_left=True)
        pygame.draw.arc(surface, GIRL_HAIR, (x - 42, y - 40, 45, 60), 1.6, 3.5, 20)
        pygame.draw.arc(surface, GIRL_HAIR, (x - 3, y - 40, 45, 60), -0.4, 1.5, 20)
    eye_color = (80, 60, 60)
    pygame.draw.arc(surface, eye_color, (x - 25, y - 5, 20, 20), 3.14, 6.28, 2)
    pygame.draw.arc(surface, eye_color, (x + 5, y - 5, 20, 20), 3.14, 6.28, 2)
    if is_boy: draw_glasses(surface, x, y+5)
    pygame.draw.ellipse(surface, BLUSH_COLOR, (x - 25, y + 10, 10, 6))
    pygame.draw.ellipse(surface, BLUSH_COLOR, (x + 15, y + 10, 10, 6))
    if kiss_offset != (0,0): pygame.draw.circle(surface, (200, 100, 100), (x, y + 20), 5) 

def draw_heart(surface, x, y, scale, alpha=255):
    temp_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
    width = 40 * scale
    height = 40 * scale
    center_x, center_y = 50, 50
    triangle_pts = [(center_x - width//2, center_y), (center_x + width//2, center_y), (center_x, center_y + height//1.5)]
    safe_alpha = int(max(0, min(255, alpha)))
    color = (*HEART_COLOR, safe_alpha)
    pygame.draw.circle(temp_surf, color, (center_x - width//4, center_y - height//4), width//4)
    pygame.draw.circle(temp_surf, color, (center_x + width//4, center_y - height//4), width//4)
    pygame.draw.polygon(temp_surf, color, triangle_pts)
    surface.blit(temp_surf, (x - 50, y - 50))

# --- 5. 主程序 ---

def main():
    girl_x, girl_y = 300, 250
    boy_start_x, boy_y = 550, 250
    boy_x = boy_start_x
    
    progress = 0.0
    animation_speed = 0.01
    initial_anim_done = False
    
    girl_is_hugging_back = False
    kiss_action = None 
    kiss_timer = 0
    
    # 稍微向上移动按钮，给狗狗腾位置
    buttons = [
        Button(150, 620, 140, 45, "Hug Back", "hug_back"),
        Button(330, 620, 140, 45, "Fred Kiss", "boy_kiss"),
        Button(510, 620, 140, 45, "AvA Kiss", "girl_kiss")
    ]

    particles = [Particle() for _ in range(80)]

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if initial_anim_done:
                    for btn in buttons:
                        if btn.check_click(mouse_pos):
                            if btn.action_code == "hug_back":
                                girl_is_hugging_back = not girl_is_hugging_back
                                btn.text = "Relax" if girl_is_hugging_back else "Hug Back"
                            elif btn.action_code == "boy_kiss":
                                kiss_action, kiss_timer = "boy", 60
                            elif btn.action_code == "girl_kiss":
                                kiss_action, kiss_timer = "girl", 60

        if progress < 1.0:
            progress += animation_speed
            move_progress = 1 - math.pow(1 - progress, 3) 
            boy_x = boy_start_x - (boy_start_x - (girl_x + 60)) * move_progress
            roll_height = math.sin(progress * math.pi) * 30 
            current_boy_y = boy_y - roll_height
        else:
            progress = 1.0
            initial_anim_done = True
            boy_x = girl_x + 60
            current_boy_y = boy_y

        boy_offset, girl_offset = (0,0), (0,0)
        if kiss_timer > 0:
            kiss_timer -= 1
            if kiss_action == "boy": boy_offset = (-15, 5)
            elif kiss_action == "girl": girl_offset = (15, 0)
        else:
            kiss_action = None

        # --- 绘图 (严格图层顺序) ---
        
        # Layer 1: 背景
        draw_room_bg(screen) 
        
        # Layer 2: 环境物件 (植物、宠物) - 在床之前绘制
        draw_sleeping_dog(screen, 680, 680)   # 右下角的狗

        # Layer 3: 床主体
        bed_rect = pygame.Rect(100, 100, 600, 450)
        pygame.draw.rect(screen, BED_FRAME_COLOR, bed_rect.inflate(10, 10), border_radius=20)
        pygame.draw.rect(screen, SHEET_COLOR, bed_rect, border_radius=20)
        pygame.draw.rect(screen, PILLOW_COLOR, (girl_x - 60, girl_y - 80, 120, 80), border_radius=15)
        pygame.draw.rect(screen, PILLOW_COLOR, (boy_start_x - 60, boy_y - 80, 120, 80), border_radius=15)

        # Layer 4: 人物
        draw_pill_shape(screen, GIRL_CLOTHES, pygame.Rect(girl_x - 30, girl_y, 60, 120))
        draw_face(screen, girl_x, girl_y, is_boy=False, kiss_offset=girl_offset)

        if progress < 1.0:
            body_width = 60 - abs(math.sin(progress * math.pi)) * 20
            draw_pill_shape(screen, BOY_CLOTHES, pygame.Rect(boy_x - body_width/2, current_boy_y, body_width, 120))
            draw_face(screen, boy_x, current_boy_y, is_boy=True)
        else:
            draw_pill_shape(screen, BOY_CLOTHES, pygame.Rect(boy_x - 30, current_boy_y, 60, 120))
            pygame.draw.line(screen, BOY_CLOTHES, (boy_x, boy_y + 40), (girl_x, boy_y + 40), 20)
            draw_face(screen, boy_x, current_boy_y, is_boy=True, kiss_offset=boy_offset)
            if girl_is_hugging_back:
                 pygame.draw.line(screen, GIRL_CLOTHES, (girl_x, girl_y + 45), (boy_x - 10, boy_y + 45), 18)
                 pygame.draw.circle(screen, SKIN_COLOR, (boy_x - 10, boy_y + 45), 10)

        # Layer 5: 被子
        blanket_rect = pygame.Rect(100, 300, 600, 250)
        pygame.draw.rect(screen, BLANKET_SHADOW, blanket_rect.move(0, 5), border_radius=20)
        pygame.draw.rect(screen, BLANKET_COLOR, blanket_rect, border_radius=20)
        pygame.draw.line(screen, (220, 130, 110), (120, 350), (680, 350), 3)

        # 猫咪放在被子上，营造温馨感，同时呼吸动画让场景更生动
        draw_sleeping_cat(screen, 200, 450)   # 床左下角的猫 (会呼吸)
        draw_fiddle_leaf_fig(screen, 100, 680) # 左下角植物
        

        # Layer 6: 氛围层 (光照与粒子 - 最上层，盖住所有物体)
        light_s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(light_s, LIGHT_COLOR, [(0,0), (WIDTH, 0), (WIDTH, 500), (0, HEIGHT)])
        screen.blit(light_s, (0,0))
        for p in particles: p.update(); p.draw(screen)

        # Layer 7: UI与特效
        if kiss_timer > 0:
            mid_x = (girl_x + boy_x) // 2
            mid_y = (girl_y + boy_y) // 2 - 20
            scale = 1.0 + math.sin(kiss_timer * 0.2) * 0.2
            draw_heart(screen, mid_x, mid_y - 30, scale * 0.8)
            try: font_kiss = pygame.font.SysFont("arial", 24, bold=True)
            except: font_kiss = pygame.font.Font(None, 30)
            txt = font_kiss.render("Muah!", True, HEART_COLOR)
            screen.blit(txt, (mid_x - 20, mid_y - 80 - (60-kiss_timer)))

        if initial_anim_done:
            for btn in buttons:
                btn.check_hover(mouse_pos)
                btn.draw(screen)
        
        if initial_anim_done and kiss_timer == 0:
             heart_scale = 0.6 + math.sin(pygame.time.get_ticks() * 0.003) * 0.05
             draw_heart(screen, (girl_x + boy_x) // 2, girl_y - 50, heart_scale)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()