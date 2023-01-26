import pygame as pg
import random
import sys
from functools import partial
from base import *
from units import *
from configs import *

'''TODO:
Show fps
settings(like music)
'''

class Road(pg.sprite.Group):#Scroll, active
    def __init__(self, road):
        super().__init__()
        self.road = road

class LoseScene(Scene):
    def __init__(self, draw, camp, show):
        self.drawfunc = draw

        if camp == "l":
            text = "失 败"
            color = (255, 0, 0)
        elif camp == "r":
            text = "胜 利"
            color = (0, 255, 255)
        else:
            text = "平 局"
            color = (255, 255, 255)

        self.background = pg.Surface((WIDTH, HEIGHT)).convert_alpha()
        self.background.fill((0, 0, 0, 150))
        
        r = render(text, color, 40)
        r2 = render(show[0], (255, 255, 255), 16)
        self.background.blit(r, r.get_rect(center=(WIDTH/2, HEIGHT/3)))
        self.background.blit(r2, r2.get_rect(center=(WIDTH/2, HEIGHT/3+170)))
        if show[1]:
            r = render(show[1], size=18)
            self.background.blit(r, r.get_rect(center=(WIDTH/2, HEIGHT*2/3)))

        super().__init__()
        
    def draw(self):
        self.drawfunc()
        self.screen.blit(self.background, (0, 0))
    
class Battle(Scene):
    def __init__(self, l_units, r_units, difficulty,
                 command_win=lambda x: None, command_lose=lambda x: None, command_same=lambda x: None):
        sys.stdout.battle = self
        self.time_offset = 0
        self.l_units = l_units
        self.r_units = r_units
        self.difficulty = difficulty
        self.command_win = partial(command_win, self)
        self.command_lose = partial(command_lose, self)
        self.command_same = partial(command_same, self)

        self.background = random.choice(("forest", "sand", "rock"))
        self.battle_projectile_offset = "choice((0.95, 0.97, 1))"

        super().__init__()
            
    def init(self):
        self.mm = MusicManager()
        pg.mixer.music.set_volume(0.3)
        
        self.background = load_image("bg_" + self.background + ".png").convert()
        self.background_width = self.background.get_width()

        self.period = 0
        self.next_period_to = None
        self.period_events = {1:[0, "现在，开始进攻！", lambda self: None],
                              2:[180000, "倒计时180秒", lambda self:exec("self.money_got[1]*=2")],
                              3:[120000, "倒计时60秒", lambda self:exec("self.money_got[1]*=1.5")],
                              4:[50000, "倒计时10秒", lambda self: None],
                              5:[10000, "", lambda self:self.endmatch("时间到")]}
        
        self.action_bar = load_image("action_bar.png").copy()
        self.action_bar_height = self.action_bar.get_height()
        self.cost_bar = pg.Surface((400, self.action_bar_height)).convert_alpha()
        self.cost_bar.fill((0, 0, 0, 0))

        self.pause = False
        self.pause_screen = pg.Surface((WIDTH, self.background.get_height())).convert_alpha()
        self.pause_screen.fill((0, 0, 0, 100))
        r = render("- 按P键取消暂停 -", size=18)
        self.pause_screen.blit(r, r.get_rect(center=(WIDTH//2, (HEIGHT - self.action_bar_height)//2)))

        self.maxroad = 7
        self.roadheight = (HEIGHT - self.action_bar_height) / (self.maxroad+1)

        self.camera = 0
        self.camera_max = self.background_width - WIDTH
        self.minimap = load_image("minimap.png").copy()
        self.minimap_rect = self.minimap.get_rect(x=WIDTH-self.minimap.get_width(),
                                                  y=HEIGHT-self.minimap.get_height())
        self.minimap_real_width = self.minimap_rect.width - load_image("minimap_camera.png").get_width()
        self.minimap_scale = self.minimap_real_width / WIDTH
        self.minimap_height_scale = self.minimap_rect.height / (HEIGHT - self.action_bar_height)
        self.minimap_fg = pg.Surface(self.minimap_rect.size).convert_alpha()
        self.minimap.fill((0, 0, 0, 0))
        self.update_minimap()

        self.soldiers = [Road(i) for i in range(self.maxroad+1)]
        self.l_health = self.r_health = self.maxhealth = 100

        self.spell = pg.sprite.Group()
        self.repeated_spell = pg.sprite.Group()
        
        self.money_got = [100, 0.2]
        self.maxmoney = 50
        self.l_money = self.r_money = 0
        self.l_last_getmoney = self.r_last_getmoney = self.money_got[0]
        self.p_bar = pg.Surface((400, 33)).convert_alpha()

        self.tip_sprites = pg.sprite.Group()
        self.effect_sprites = pg.sprite.Group()
        self.low_effect_sprites = pg.sprite.Group()
        self.l_projectile_group = pg.sprite.Group()
        self.r_projectile_group = pg.sprite.Group()

        self.start_battle_time = pg.time.get_ticks()
        self.total_battle_time = 360000 # 6min
        
        self.barricades = pg.sprite.Group()
        for i in range(self.maxroad//2+1):
            unit = self.add_soldier("barricade", "l", road=i*2+1, startswith="cs_")
            self.barricades.add(unit)
            self.soldiers[i*2].add(unit)
            unit.moveto("centerx", 100)
            
            unit = self.add_soldier("barricade", "r", road=i*2+1, startswith="cs_")
            self.barricades.add(unit)
            self.soldiers[i*2].add(unit)
            unit.moveto("centerx", self.background_width-100)
            
        self.unit_keys = (pg.K_q, pg.K_w, pg.K_e, pg.K_r,
                          pg.K_a, pg.K_s, pg.K_d, pg.K_f)
        self.unit_indicator = Static(0, 0, "unit_selected.png")
        self.update_active_unit(None)
        self.add_unit_rect = pg.Rect((0, self.action_bar_height, WIDTH, HEIGHT - self.action_bar_height))
        
        self.unit_icons = []
        self.unit_rects = []
        self.unit_tip_rects = []
        self.unit_tips = []
        self.add_indicators = []
        self.add_indicator_rects = []
        for i in range(8):
            row = i // 4
            column = i % 4

            icon = load_image(self.l_units[i] + "_icon.png")
            icon_rect = pg.Rect((column*85+40, row*62+11, 65, 65))
            self.unit_rects.append(icon_rect)
            self.unit_tip_rects.append(icon_rect)
            self.action_bar.blit(icon, icon_rect)

            try:
                unit = eval("c_"+self.l_units[i]+"('l',{})")
            except TypeError:
                unit = eval("c_"+self.l_units[i]+"('l')")
            self.unit_tips.append(self.get_unit_tip(unit))
            self.cost_bar.blit(render(str(unit.cost), size=11),
                               (column*85+100, row*62+68))
            self.unit_icons.append(UnitIcon(unit, icon_rect))
            self.add_indicator_rects.append((0, self.action_bar_height+(i+1)*self.roadheight))

            if unit.unittype == "soldier":
                unit.update_road(i)
                add_indicator = load_image(self.l_units[i] + "_a1.png").convert_alpha()
                add_indicator.set_alpha(100)
                self.add_indicators.append(("soldier", add_indicator))
            else:
                self.add_indicators.append(("spell", unit.image))

        for i in range(8):
            row = i // 4
            column = i % 4

            icon = load_image(self.r_units[i] + "_icon.png")
            icon_rect = pg.Rect((column*85+840, row*62+11, 65, 65))
            self.unit_tip_rects.append(icon_rect)
            self.action_bar.blit(icon, icon_rect)

        for i in range(8):
            row = i // 4
            column = i % 4
            
            try:
                unit = eval("c_"+self.r_units[i]+"('r',{})")
            except TypeError:
                unit = eval("c_"+self.r_units[i]+"('r')")
            self.unit_tips.append(self.get_unit_tip(unit))
            self.action_bar.blit(render(str(unit.cost), size=11),
                                 (column*85+900, row*62+68))

        self.add_money("l", 0)

    @property
    def timer(self):
        return pg.time.get_ticks() - self.start_battle_time - self.time_offset
        
    def rand(self, expr, camp):
        return eval(f"random.{expr}")
    
    def add_money(self, camp, count):
        if eval(f"self.{camp}_money + count") > self.maxmoney:
            exec(f"self.{camp}_money = self.maxmoney")
        else:
            exec(f"self.{camp}_money += count")
        if camp == "l":
            for icon in self.unit_icons:
                icon.update(self.l_money)
        self.update_pbar()
        
    def add_soldier(self, name, camp, road, startswith="c_", money=0):
        if money:
            self.add_money(camp, -money)
        imgkw = {} if camp == "l" else {"walk":{"flip":(True, False)},
                                        "attack":{"flip":(True, False)}}
        if not name.startswith("cs_"):
            name = startswith + name
        unit = eval(name+f"(camp, imgkw={imgkw})")

        unit.update_road(road)
        self.soldiers[road].add(unit)

        return unit

    def add_spell(self, name, camp, pos, startswith="c_", money=0):
        if money:
            self.add_money(camp, -money)

        if not name.startswith("cs_"):
            name = startswith + name
        spell = eval(f"{name}(camp)")
        spell.rect.center = pos
        spell.go()
        self.spell.add(spell)
        
    def add_unit_event(self, pos):
        if self.active_unit == None or not self.unit_icons[self.active_unit].can_buy(self.l_money):
            return
        
        unit_icon = self.unit_icons[self.active_unit]
        unit_icon.freeze()
        if unit_icon.unittype == "soldier":
            road = int((pos[1] - self.action_bar_height) // self.roadheight)
            self.add_soldier(self.l_units[self.active_unit], "l", road, money=unit_icon.cost)
        elif unit_icon.unittype == "spell":
            self.add_spell(self.l_units[self.active_unit], "l", vec(pos)+vec(self.camera, 0), money=unit_icon.cost)

    def show_tip(self, text, **kw):
        self.tip_sprites.add(FadeOutText(text, **kw))
        
    def get_unit_tip(self, unit):
        tip = renders([(unit.cn_name, (255, 255, 255), 18),
                       (unit.__doc__, (255, 255, 255), 13)], bg=(0, 0, 0, 150))
        return tip
    
    def take_damage(self, camp, damage):
        exec(f"self.{camp}_health -= damage")
        if eval(f"self.{camp}_health <= 0"):
            self.endmatch("攻破敌阵" if camp == "r" else "")
        else:
            self.update_pbar()

    def update_active_unit(self, active_unit):
        self.active_unit = active_unit
        if self.active_unit != None:
            self.unit_indicator.state = ""     
            self.unit_indicator.rect.center = self.unit_rects[self.active_unit].center
        else:
            self.unit_indicator.state = "HIDE"

    def update_camera(self, value):
        self.camera = set_threshold(self.camera+value, 0, self.camera_max)
        self.update_minimap()
            
    def update_minimap(self):
        self.minimap = load_image("minimap.png").copy()
        self.minimap.blit(load_image("minimap_camera.png"), (self.camera*self.minimap_scale, 0))

    def update_pbar(self):
        self.p_bar.fill((0, 0, 0, 0))
        self.p_bar.blit(load_image("bar.png"), (20, 0))
        self.p_bar.blit(load_image("bar.png"), (278, 0))

        w = self.l_health*102//self.maxhealth
        self.p_bar.blit(load_image("bar_hp.png").subsurface((0, 0, w, 14)), (22, 2))
        
        w = self.l_money*102//self.maxmoney
        self.p_bar.blit(load_image("bar_mp.png").subsurface((0, 0, w, 14)), (22, 17))

        w = self.r_health*102//self.maxhealth
        self.p_bar.blit(load_image("bar_hp.png").subsurface((102-w, 0, w, 14)), (382-w, 2))
        
        w = self.r_money*102//self.maxmoney
        self.p_bar.blit(load_image("bar_mp.png").subsurface((102-w, 0, w, 14)), (382-w, 17))

        time = (self.total_battle_time - self.timer) // 1000
        minute = time // 60
        time_render = render((str(minute)+":"+str(time%60)) if minute >= 0 else "0:0", color=(255, 255, 255) if minute > 0 else (255, 0, 0))
        self.p_bar.blit(time_render, time_render.get_rect(center=(self.p_bar.get_width()//2,
                                                          self.p_bar.get_height()//2)))

    def update_ai(self):
        if random.random() < self.difficulty:
            soldier = random.choice(self.r_units)
            cost = sys.stdout.all_units[soldier][2]
            if self.r_money >= cost:
                try:
                    self.add_soldier(soldier, "r", random.randint(0, self.maxroad))
                except TypeError:
                    pass
                else:
                    self.r_money -= cost
            
    def pos(self, x, y):
        return (x-self.camera, y)

    def drawgroup(self, group):
        for sprite in sorted(group, key=lambda sprite: sprite.rect.bottom):
            self.screen.blit(sprite.image, self.pos(*sprite.rect.topleft))

    def endmatch(self, wintype):
        if self.l_health > self.r_health:
            camp = "r"
        elif self.l_health < self.r_health:
            camp = "l"
        else:
            barricade_health = [0, 0]
            
            for road in self.soldiers:
                for sprite in road:
                    if sprite.en_name == "barricade":
                        barricade_health[0 if sprite.camp == "l" else 1] += sprite.health

            if barricade_health[0] > barricade_health[1]:
                camp = "r"
            elif barricade_health[0] < barricade_health[1]:
                camp = "l"
            else:
                camp = None

        self.mm.stop()
        if camp == "r":
            show = self.command_win()
            play_sound("victory")
        elif camp == "l":
            show = self.command_lose()
            play_sound("defeat")
        else:
            show = self.command_same()
            
        LoseScene(self.draw_base, camp, (wintype, show))
        self.quit_scene()

        return True

    def loop(self):
        self.scene_running = True
        
        while self.scene_running:
            self.screen.fill(self.bg)
            if self.pause:
                self.time_offset += (self.timer - self.pause)
            else:
                if self.update():
                    break
            self.draw()
            time = pg.time.get_ticks()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.onexit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.onexit()
                    elif event.key == pg.K_p:
                        self.pause = False if self.pause else self.timer
                if not self.pause:
                    self.events(event)
            self.time_offset += pg.time.get_ticks() - time
            self.draw2()
            
            self.clock.tick(self.fps)
            pg.display.update()

    def onexit(self):
        delattr(sys.stdout, "battle")
        self.mm.stop()
        play_sound("defeat")
        LoseScene(self.draw_base, "l", ["离开战场", self.command_lose()])
        self.fade_out(draw=self.draw_base)
        self.quit_scene()
        
    def events(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                play_sound("button_click")
                for rect in self.unit_rects:
                    if rect.collidepoint(event.pos):
                        idx = self.unit_rects.index(rect)
                        self.update_active_unit(idx)
                        break
                else:
                    if self.minimap_rect.collidepoint(event.pos):
                        self.camera = set_threshold(event.pos[0] - self.minimap_rect.width / 4 - \
                                                    self.minimap_rect.x, 0, self.minimap_real_width) / self.minimap_scale
                        self.update_minimap()
            elif event.button == 4:
                self.update_camera(-50)
            elif event.button == 5:
                self.update_camera(50)
                    
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                if self.add_unit_rect.collidepoint(event.pos) and not self.minimap_rect.collidepoint(event.pos):
                    self.add_unit_event(event.pos)
                
        elif event.type == pg.KEYDOWN:
            if event.key in self.unit_keys:
                idx = self.unit_keys.index(event.key)
                self.update_active_unit(idx)

    def draw_base(self):
        pos = pg.mouse.get_pos()
        
        self.screen.blit(self.background, self.pos(0, 0))
        for sprite in self.repeated_spell:
            self.screen.blit(sprite.image_repeat_area, self.pos(*sprite.rect.topleft))
        self.screen.blit(self.action_bar, (0, 0))
        self.screen.blit(self.p_bar, (400, 20))

        for sprite in self.unit_icons:
            sprite.draw(self.screen)
        self.screen.blit(self.cost_bar, (0, 0))
        self.unit_indicator.draw(self.screen)

        
        self.drawgroup(self.low_effect_sprites)

        for sprite in self.barricades:
            sprite.draw()

        self.minimap_fg.fill((0, 0, 0, 0))
        
        for road in self.soldiers:
            for sprite in road:
                if sprite.en_name != "barricade":
                    sprite.draw()
                    color = (0, 0, 255) if sprite.camp == "l" else (255, 0, 0)
                    pg.draw.circle(self.minimap_fg, color, (sprite.rect.centerx*self.minimap_scale,
                                                            (sprite.rect.centery-self.action_bar_height)*self.minimap_height_scale), 4, width=2)

        self.drawgroup(self.effect_sprites)
        self.drawgroup(self.l_projectile_group)
        self.drawgroup(self.r_projectile_group)
        self.screen.blit(self.minimap, self.minimap_rect)
        self.screen.blit(self.minimap_fg, self.minimap_rect)

    def draw(self):
        self.draw_base()
        pos = pg.mouse.get_pos()
        
        road = int((pos[1] - self.action_bar_height) // self.roadheight)
        if self.active_unit != None and self.unit_icons[self.active_unit].can_buy(self.l_money) and \
           self.add_unit_rect.collidepoint(pos):
            add_indicator = self.add_indicators[self.active_unit]
            if add_indicator[0] == "soldier":
                self.screen.blit(add_indicator[1], add_indicator[1].get_rect(bottomleft=self.add_indicator_rects[road]))
            else:
                self.screen.blit(add_indicator[1], add_indicator[1].get_rect(center=pos))

        self.tip_sprites.draw(self.screen)

        for i, rect in enumerate(self.unit_tip_rects):
            if rect.collidepoint(pos):
                if pos[0] > WIDTH//2:
                    self.screen.blit(self.unit_tips[i], self.unit_tips[i].get_rect(topright=pos))
                else:
                    self.screen.blit(self.unit_tips[i], pos)
                break

    def draw2(self):
        if self.pause:
            self.screen.blit(self.pause_screen, (0, self.action_bar_height))
            
    def update(self):
        self.mm.update()
        
        key = pg.key.get_pressed()
        now = self.timer
        
        if key[pg.K_LEFT]:
            self.update_camera(-5)
        elif key[pg.K_RIGHT]:
            self.update_camera(5)

        if self.next_period_to != False:
            if self.next_period_to == None:
                try:
                    self.next_period_to = now + self.period_events[self.period+1][0]
                except KeyError:
                    self.next_period_to = False
            else:
                if now >= self.next_period_to:
                    self.period += 1
                    self.next_period_to = None
                    self.show_tip(self.period_events[self.period][1], color=(0, 0, 255))
                    if self.period_events[self.period][2](self):
                        return True

        for camp in ("l", "r"):
            if eval(f"now - self.{camp}_last_getmoney > self.money_got[0]"):
                exec(f"self.{camp}_last_getmoney = now")
                self.add_money(camp, self.money_got[1])

        for road in self.soldiers:
            for sprite in road:
                sprite.update()

                if sprite.camp == "l":
                    enemy_projectile = self.r_projectile_group
                else:
                    enemy_projectile = self.l_projectile_group
                for projectile in enemy_projectile:
                    if projectile.col(sprite):
                        att = False
                        if sprite.en_name == "barricade":
                            if set(projectile.road) & {sprite.road, sprite.road -1}:
                                if projectile not in sprite.damage_list:
                                    sprite.take_damage(projectile.damage, projectile)
                                    projectile.attack[0](projectile, sprite)
                                    att = True
                        else:
                            if sprite.road in projectile.road:
                                if projectile not in sprite.damage_list:
                                    sprite.take_damage(projectile.damage, projectile)
                                    projectile.attack[0](projectile, sprite)
                                    att = True
                        if att:
                            projectile.maxtarget -= 1
                            if projectile.maxtarget <= 0:
                                projectile.kill()
                                break

        for spell in self.spell:
            spell.update()
        for sprite in self.effect_sprites:
            sprite.animate()
        for sprite in self.low_effect_sprites:
            sprite.animate()
        self.tip_sprites.update()
        self.l_projectile_group.update()
        self.r_projectile_group.update()

        self.update_ai()
