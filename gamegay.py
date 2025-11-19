import pygame
from sys import exit
import random
import time

# ตั้งค่า pygame และ window
pygame.init()
screen_width = 720
screen_height = 512
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Wordle by lnwza55+')
clock = pygame.time.Clock()

# color
yellow = (255,255,0)         
green = (0,255,0)           
gray = (128,128,128)        
greenfr = (149, 187, 137)
button_hotspot = (0, 0, 0, 0)
white = (255, 255, 255)
black = (0, 0, 0)      

# fonts
font_title = pygame.font.Font('Silkscreen/Silkscreen-Bold.ttf', 48)
font_key = pygame.font.Font('Silkscreen/Silkscreen-Regular.ttf', 18)
font_hint = pygame.font.Font('Silkscreen/Silkscreen-Regular.ttf', 24)
font_timer = pygame.font.Font('Silkscreen/Silkscreen-Regular.ttf', 28)
font_result = pygame.font.Font('Silkscreen/Silkscreen-Regular.ttf', 40)
font_tile = pygame.font.Font('Silkscreen/Silkscreen-Regular.ttf', 40)


# backgrounds
try:
    bgs = { 
        "menu": pygame.transform.scale(pygame.image.load('PygameBG 2/Screen.png').convert(), (screen_width, screen_height)),
        "about": pygame.transform.scale(pygame.image.load('PygameBG 2/About.png').convert(), (screen_width, screen_height)),
        "mode": pygame.transform.scale(pygame.image.load('PygameBG 2/Mode.png').convert(), (screen_width, screen_height)),
        "game_nh": pygame.transform.scale(pygame.image.load('PygameBG 2/Game.png').convert(), (screen_width, screen_height)),
        "game_t": pygame.transform.scale(pygame.image.load('PygameBG 2/timer.png').convert(), (screen_width, screen_height)),
        "win": pygame.transform.scale(pygame.image.load('PygameBG 2/Win.png').convert(), (screen_width, screen_height)),
        "lose": pygame.transform.scale(pygame.image.load('PygameBG 2/Lose.png').convert(), (screen_width, screen_height))
    }
except pygame.error as e:
    print(f"Error loading images: {e}. Using black fallback.")
    surf = pygame.Surface((screen_width, screen_height)); surf.fill(black);
    bgs = {k: surf for k in ["menu", "about", "mode", "game_nh", "game_t", "win", "lose"]}

 
# กำหนด game States
states = {"menu":"menu",
        "how_to_play":"h_t_p",
        "mode_select":"m_s",
        "gameplay_normal_hard":"gp_nh",
        "gameplay_time":"gp_t",
        "result_win":"r_w",
        "result_lose":"r_l"}

class button:
    def __init__ (self, rect, action=None, text="", text_color=white, font=font_key):
        self.rect = rect
        self.action = action
        self.color = button_hotspot 
        self.text = text
        self.text_color = text_color
        self.font = font
        
    def drawbutton (self,surface):
        # วาดปุ่มตามสี
        if self.color != button_hotspot:
             pygame.draw.rect(surface, self.color, self.rect, 0, 5)

        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        s.fill(self.color)
        surface.blit(s, self.rect.topleft)
        
        # ทำให้เป็นสีเขียวเวลาเม้าส์โดนปุ่ม
        if self.rect.collidepoint(pygame.mouse.get_pos()):
             pygame.draw.rect(surface, green, self.rect, 2)
             
        # วาดข้อความบนปุ่ม
        if self.text:
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def click (self,event):
        # ตรวจสอบการคลิกปุ่ม
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    return self.action()
        return None 

# Class ช่องตัวอักษร (Tile)
class Tile:
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)
        self.letter = ''
        self.color = gray
        self.text_color = white 
        self.font = font_tile 
        self.is_guessed = False

    def draw(self, surface):
        # วาดช่องตัวอักษร
        pygame.draw.rect(surface, self.color, self.rect, 0, 5) 
        
        # วาดกรอบถ้ายังไม่ถูกทาย
        if not self.is_guessed:
             pygame.draw.rect(surface, greenfr, self.rect, 2, 5)

        # วาดตัวอักษร
        if self.letter:
            text_surf = self.font.render(self.letter, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)


# Class ตรรกะเกม (ingame logic)
class ingame:
    def __init__ (self, rows=5, cols=5): 
        self.target_word = "" 
        self.rows = rows
        self.cols = cols
        self.current_row = 0
        self.current_col = 0
        self.guess = ''
        self.game_over = False

        # การจัดเรียง Grid/Tiles
        self.tile_size = 50 
        self.spacing = 8    
        self.grid_x = (screen_width - (self.cols * self.tile_size + (self.cols - 1) * self.spacing)) // 2 
        self.grid_y = 80
        self.tiles = [] 
        
        # สร้างแป้นพิมพ์บนหน้าจอ
        self.keyboard_buttons = self.create_keyboard()
        self.key_status = {} # สถานะสีของปุ่ม A-Z

    def create_grid(self, start_x, start_y):
        # สร้าง Grid ช่องตัวอักษร
        grid = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                x = start_x + c * (self.tile_size + self.spacing)
                y = start_y + r * (self.tile_size + self.spacing)
                row.append(Tile(x, y, self.tile_size))
            grid.append(row)
        self.tiles = grid 
        return grid

    def create_keyboard(self):
        # สร้างปุ่มแป้นพิมพ์ A-Z และ Enter
        keyboard_buttons = []
        
        key_width, key_height = 35, 35 
        start_x, start_y = 150, 370 
        
        layout = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM<"] 
        
        for r_index, row_keys in enumerate(layout):
            row_start_x = start_x + r_index * 20
            row_y = start_y + r_index * (key_height + 5) 
            for c_index, key in enumerate(row_keys):
                x = row_start_x + c_index * (key_width + 5)
                button_obj = button(pygame.Rect(x, row_y, key_width, key_height), 
                                action=lambda k=key: self.handle_key_click(k), text=key if key != '<' else 'ENTER', font=font_key)
                
                keyboard_buttons.append(button_obj)
        return keyboard_buttons

    def handle_key_click(self, key):
        # จัดการคลิกปุ่มบนหน้าจอ
        if self.game_over: return
        
        if key == 'ENTER' or key == '<': # รองรับทั้ง '<' และ 'ENTER'
            if self.current_col == self.cols:
                return self.check_guess() # ส่งคำทาย
        else:
            if self.current_col < self.cols:
                self.input_letter(key)
    
    def handle_input(self, key_event):
        # จัดการการพิมพ์จาก Keyboard จริง
        if self.game_over: return
        
        if key_event.key >= pygame.K_a and key_event.key <= pygame.K_z:
            if self.current_col < self.cols:
                self.input_letter(chr(key_event.key).upper())
                
        elif key_event.key == pygame.K_BACKSPACE:
            if self.current_col > 0:
                self.current_col -= 1
                tile = self.tiles[self.current_row][self.current_col]
                tile.letter = ''
                self.guess = self.guess[:-1] # ลบตัวอักษร

        elif key_event.key == pygame.K_RETURN and self.current_col == self.cols:
            return self.check_guess() # ส่งคำทาย

    def input_letter(self, letter):
        # พิมพ์ตัวอักษรลงในช่อง
        tile = self.tiles[self.current_row][self.current_col]
        tile.letter = letter
        self.guess += letter
        self.current_col += 1
        
    def check_guess(self):
        # ตรวจสอบคำทายและเปลี่ยนสีกระเบื้อง/ปุ่ม
        guess_word = self.guess
        target = list(self.target_word)
        current_tiles = self.tiles[self.current_row]

        # 1. ตรวจสอบสีเขียว (ถูกตำแหน่ง)
        for i in range(self.cols):
            if guess_word[i] == target[i]:
                current_tiles[i].color = greenfr
                current_tiles[i].is_guessed = True
                self.key_status[guess_word[i]] = greenfr
                target[i] = None

        # 2. ตรวจสอบสีเหลือง/เทา (ถูกตัว/ผิดทั้งหมด)
        for i in range(self.cols):
            if current_tiles[i].color != greenfr:
                if guess_word[i] in target:
                    current_tiles[i].color = yellow
                    current_tiles[i].is_guessed = True
                    if self.key_status.get(guess_word[i]) != greenfr:
                        self.key_status[guess_word[i]] = yellow
                    
                    try:
                        target[target.index(guess_word[i])] = None # ลบตัวอักษรที่ใช้ไปแล้ว
                    except ValueError:
                        pass
                else:
                    current_tiles[i].color = gray
                    current_tiles[i].is_guessed = True
                    if guess_word[i] not in self.key_status:
                        self.key_status[guess_word[i]] = gray
        # เปลี่ยนปุ่มเป็นสีดำ ถ้าไม่อยู่ในคำตอบเลย
        for char in set(guess_word): 
            if char not in self.target_word and self.key_status.get(char) == gray:
                 self.key_status[char] = black
                 
        if guess_word == self.target_word:
            self.game_over = True
            return "WIN" # ชนะ
        elif self.current_row == self.rows - 1:
            self.game_over = True
            return "LOSE" # แพ้
        else:
            self.current_row += 1
            self.current_col = 0
            self.guess = ''
            return None

    def give_hint(self):
        # การให้คำใบ้ (Hint Logic)
        if self.game_over: return
        target = self.target_word
        current_tiles = self.tiles[self.current_row]

        valid_indices = []
        for i in range(self.cols):
            if not current_tiles[i].letter or current_tiles[i].letter != target[i]:
                valid_indices.append(i)
        
        if valid_indices:
            hint_index = random.choice(valid_indices)
            correct_letter = target[hint_index]
            
            # อัปเดตช่อง/สี
            current_tiles[hint_index].letter = correct_letter
            current_tiles[hint_index].color = greenfr
            current_tiles[hint_index].is_guessed = True
            self.key_status[correct_letter] = greenfr

            # อัปเดตคำทายปัจจุบัน
            self.guess = "".join([t.letter if t.letter else '' for t in current_tiles])
            self.current_col = len(self.guess.replace(' ', '')) 
            if self.current_col > self.cols:
                 self.current_col = self.cols
            
    def draw(self, surface):
        # วาด Grid และ Keyboard
        for row in self.tiles:
            for tile in row:
                tile.draw(surface)
        
        for button in self.keyboard_buttons:
            key_char = button.text if button.text not in ['ENTER', 'BACKSPACE'] else None
            if key_char and key_char in self.key_status:
                button.color = self.key_status[key_char] # ใช้สีตามสถานะตัวอักษร
            else:
                button.color = gray
            button.drawbutton(surface)


# Class จัดการสถานะเกม (Game State Manager)
class gamestatemanager:
    def __init__(self, initial_state):
        self.state = initial_state
        self.target_word = ""
        self.game_mode = None
        self.current_game_screen = None 
        
        # ตัวแปร Timer
        self.timer_limit = 120 
        self.timer_start_time = 0
        self.remaining_time = self.timer_limit
        self.timer_running = False
        
        self.max_hints = 1
        self.hints_remaining = self.load_hint_data() # โหลด Hint คงเหลือ
        self.last_login_day = time.strftime("%Y-%m-%d")
        
        # Word Lists
        self.all_words = []
        self.normal_words = []
        self.hard_words = []
        
        self.load_resources()
        
    def load_hint_data(self):
        # โหลด/รีเซ็ตจำนวนคำใบ้รายวัน
        today = time.strftime("%Y-%m-%d")
        try:
            with open("hint_data.txt", "r") as f:
                data = [line.strip() for line in f.readlines()]
                if len(data) >= 2 and data[0] == today:
                    return int(data[1])
                
                self.save_hint_data(today, self.max_hints)
                return self.max_hints
        except:
            self.save_hint_data(today, self.max_hints)
            return self.max_hints

    def save_hint_data(self, day, hints):
        # บันทึกจำนวนคำใบ้
        with open("hint_data.txt", "w") as f:
            f.write(f"{day}\n")
            f.write(f"{hints}\n")

    def use_hint(self):
        # ใช้คำใบ้และเรียก give_hint
        if self.hints_remaining > 0 and self.current_game_screen and not self.current_game_screen.game_over:
            self.hints_remaining -= 1
            self.save_hint_data(self.last_login_day, self.hints_remaining)
            self.current_game_screen.give_hint()

    def _read_word_file(self, filename):
        # อ่านไฟล์คำศัพท์
        with open(filename) as f:
            return [word.strip().upper() for word in f.readlines() if len(word.strip()) == 5]

    def load_resources(self):
        # โหลดไฟล์คำศัพท์ทั้งหมด
        self.all_words = self._read_word_file("Words/all_answers.txt")
        self.normal_words = self._read_word_file("Words/normal_mode.txt")
        self.hard_words = self._read_word_file("Words/hard_mode.txt")
        self.bgs = bgs 

    def change_state(self, new_state):
        # เปลี่ยนสถานะเกม
        self.state = new_state
        if self.state != states["gameplay_time"]: 
            self.timer_running = False
            
    def start_game(self, mode):
        # เริ่มเกมใหม่ (เลือกโหมดและคำ)
        self.game_mode = mode
        
        target_list = []
        if mode == 'normal':
            target_list = self.normal_words      
        elif mode == 'hard':
            target_list = self.hard_words        
        elif mode == 'timer':
            target_list = self.all_words         
        
        if target_list:
            self.target_word = random.choice(target_list) # สุ่มคำ
        else:
            print(f"Warning: Word list for mode '{mode}' is empty. Using a word from all available words.")
            self.target_word = random.choice(self.all_words)
            
        self.current_game_screen = ingame(rows=5, cols=5) 
        self.current_game_screen.create_grid(self.current_game_screen.grid_x, self.current_game_screen.grid_y)
        self.current_game_screen.target_word = self.target_word
        
        if mode == 'timer':
            self.timer_start_time = pygame.time.get_ticks()
            self.remaining_time = self.timer_limit 
            self.timer_running = True
            self.change_state(states["gameplay_time"]) 
        else:
            self.timer_running = False
            self.change_state(states["gameplay_normal_hard"]) 
            
    def end_game(self, result):
        # สิ้นสุดเกม (Win/Lose)
        self.timer_running = False
        if result == "WIN":
            self.change_state(states["result_win"]) 
        else:
            self.change_state(states["result_lose"]) 
            
    def update_timer(self):
        # อัปเดตตัวนับเวลาสำหรับโหมดจับเวลา
        if self.timer_running and self.current_game_screen and not self.current_game_screen.game_over:
            elapsed_time = (pygame.time.get_ticks() - self.timer_start_time) / 1000
            self.remaining_time = max(0, self.timer_limit - int(elapsed_time))
            
            if self.remaining_time == 0:
                self.current_game_screen.game_over = True
                self.end_game("LOSE")


# Class จัดการแอปพลิเคชัน (App)
class App:
    def __init__(self):
        self.screen = screen
        self.clock = clock
        self.manager = gamestatemanager(states["menu"]) 
        
        # ปุ่มสำหรับ Menu
        self.menu_buttons = [
            button(pygame.Rect(60, 297, 246, 54), action=lambda: self.manager.change_state(states["mode_select"])), 
            button(pygame.Rect(61, 382, 246, 54), action=lambda: self.manager.change_state(states["how_to_play"]))
        ]

        # ปุ่มสำหรับ Mode Select
        self.mode_buttons = [
            button(pygame.Rect(232, 171, 246, 54), action=lambda: self.manager.start_game('normal')), 
            button(pygame.Rect(232, 271, 246, 54), action=lambda: self.manager.start_game('hard')),   
            button(pygame.Rect(232, 379, 246, 54), action=lambda: self.manager.start_game('timer')),  
            button(pygame.Rect(21, 20, 40, 40), action=lambda: self.manager.change_state(states["menu"]))
        ]
        
        # ปุ่มสำหรับ About
        self.about_buttons = [
            button(pygame.Rect(21, 20, 40, 40), action=lambda: self.manager.change_state(states["menu"]))
        ]

        # ปุ่มสำหรับ Gameplay
        self.game_buttons = [
            button(pygame.Rect(21, 20, 40, 40), action=lambda: self.manager.change_state(states["mode_select"])), 
            button(pygame.Rect(645, 20, 50, 50), action=lambda: self.manager.use_hint()) 
        ]
        
        # ปุ่มสำหรับ Result
        self.result_buttons = [
            button(pygame.Rect(21, 20, 40, 40), action=lambda: self.manager.change_state(states["menu"]))
        ]

    # จัดการ Event หลัก (Input/Click)
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                print(f"Mouse Clicked at: X={mouse_x}, Y={mouse_y}")
            
            current_buttons = []
            
            # เลือกชุดปุ่มตามสถานะเกม
            if self.manager.state == states["menu"]: current_buttons = self.menu_buttons
            elif self.manager.state == states["mode_select"]: current_buttons = self.mode_buttons
            elif self.manager.state == states["how_to_play"]: current_buttons = self.about_buttons
            elif self.manager.state in [states["gameplay_normal_hard"], states["gameplay_time"]]:
                if self.manager.current_game_screen:
                    current_buttons = self.game_buttons + self.manager.current_game_screen.keyboard_buttons
            elif self.manager.state in [states["result_win"], states["result_lose"]]: current_buttons = self.result_buttons

            for btn in current_buttons:
                action_result = btn.click(event)
                if action_result in ["WIN", "LOSE"]:
                    self.manager.end_game(action_result)
                    break
            
            # จัดการ Key Down ในหน้า Gameplay
            if self.manager.state in [states["gameplay_normal_hard"], states["gameplay_time"]] and self.manager.current_game_screen:
                if event.type == pygame.KEYDOWN:
                    game_result = self.manager.current_game_screen.handle_input(event)
                    if game_result in ["WIN", "LOSE"]:
                        self.manager.end_game(game_result)

    # วาดปุ่ม + text
    def draw_screen(self, bg_key, buttons=None, extra_text=None, text_pos=(375, 379)):
        self.screen.blit(self.manager.bgs[bg_key], (0, 0))
        
        if buttons:
            for button in buttons:
                button.drawbutton(self.screen)
        
        if extra_text:
             text_surf = font_result.render(extra_text, True, white) 
             text_rect = text_surf.get_rect(center=text_pos)
             self.screen.blit(text_surf, text_rect)

    # วาดหน้า Gameplay
    def draw_game_play(self):
        bg_key = "game_t" if self.manager.game_mode == 'timer' else "game_nh"
        self.screen.blit(self.manager.bgs[bg_key], (0, 0))
        
        if self.manager.current_game_screen:
             self.manager.current_game_screen.draw(self.screen) # วาด Grid/Keyboard
        
        for button in self.game_buttons:
            button.drawbutton(self.screen)

        # วาดตัวนับ Hint
        hint_text = str(self.manager.hints_remaining)
        hint_surf = font_hint.render(hint_text, True, black) 
        self.screen.blit(hint_surf, (665, 30))
        
        # วาด Timer (เฉพาะโหมด Timer)
        if self.manager.game_mode == 'timer':
            minutes = int(self.manager.remaining_time) // 60
            seconds = int(self.manager.remaining_time) % 60
            timer_str = f"{minutes:02}:{seconds:02}"
            
            timer_color = greenfr if self.manager.remaining_time > 10 else yellow
            timer_surf = font_timer.render(timer_str, True, timer_color) 
            timer_rect = timer_surf.get_rect(center=(360, 50))
            self.screen.blit(timer_surf, timer_rect)


    def draw(self):
        # การวาดหน้าจอตามสถานะปัจจุบัน
        current_state = self.manager.state
        
        if current_state == states["menu"]: self.draw_screen("menu", self.menu_buttons)
        elif current_state == states["mode_select"]: self.draw_screen("mode", self.mode_buttons)
        elif current_state == states["how_to_play"]: self.draw_screen("about", self.about_buttons)
        elif current_state in [states["gameplay_normal_hard"], states["gameplay_time"]]: self.draw_game_play()
        elif current_state == states["result_win"]: 
            self.draw_screen("win", self.result_buttons, extra_text=self.manager.target_word) # หน้าชนะ
        elif current_state == states["result_lose"]: 
            self.draw_screen("lose", self.result_buttons, extra_text=self.manager.target_word) # หน้าแพ้
            
    def run(self):
        # Game Loop หลัก
        while True:
            self.manager.update_timer()
            self.handle_events()
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(60)

# เริ่มรันโปรแกรม
if __name__ == '__main__':
    game = App()
    game.run()