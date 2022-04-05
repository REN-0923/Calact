import pyxel 
from  katakana import KATAKANA

FALLING_POWER = 1

class Player:
    def __init__(self):
        #ウィンドウ内での座標
        self.dot_x = 8
        self.dot_y = 8

        #何枚目のマップにいるか
        self.minimap_x = 1
        self.minimap_y = 1
        
        #どのポーズか
        self.pose = (8,0)

        #ジャンプできるか
        self.can_jump = True

        #ジャンプでどのくらい上に行くか
        self.jump_power = 0

        #看板読んでるか
        self.is_reading = False

        #ドアの前にいるか
        self.is_standing_door = False

    def player_update(self, x, y):
        self.dot_x = x
        self.dot_y = y
    
    def player_minimap_update(self, x, y):
        self.minimap_x = x
        self.minimap_y = y
        
class App:
    def __init__(self):
        self.player = Player()
        self.katakana = KATAKANA()

        pyxel.init(128, 128, title="scroll")
        pyxel.load("scroll.pyxres")
        pyxel.run(self.update, self.draw)

    def update(self):
        self.update_player()
        
        self.jump()
        self.down()
        self.check_sign()
        self.check_door()
        self.update_stage()

        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

#BASE------------------------------------------------------
    def get_tilemap(self, x, y):
        return pyxel.tilemap(0).pget(x, y)
#UPDATE----------------------------------------------------
    def update_player(self):    
        if pyxel.btn(pyxel.KEY_RIGHT):
            #衝突判定して壁じゃなかったら
            if self.check_wall("right", self.player.dot_x, self.player.dot_y) == False:
                self.player.dot_x += 2

                if (self.player.dot_x + 8) > 128:
                    self.player.minimap_x += 1
                    self.player.player_update(8, self.player.dot_y)

                if pyxel.btnp(pyxel.KEY_UP):
                    if self.player.can_jump: 
                        self.player.jump_power = -10
                        self.player.can_jump = False

                #姿変更
                if pyxel.frame_count % 4 >= 2:
                    self.player.pose = (8,0)
                else:
                    self.player.pose = (16,0)

        elif pyxel.btn(pyxel.KEY_LEFT):
            #衝突判定して壁じゃなかったら
            if self.check_wall("left", self.player.dot_x, self.player.dot_y) == False:
                self.player.dot_x -= 2

                if self.player.dot_x < 0:
                    self.player.player_update(2, self.player.dot_y)

                if pyxel.btnp(pyxel.KEY_UP):
                    if self.player.can_jump: 
                        self.player.jump_power = -10
                        self.player.can_jump = False

                #姿変更
                if pyxel.frame_count % 4 >= 2:
                    self.player.pose = (8,8)
                else:
                    self.player.pose = (16,8)
        
        elif pyxel.btnp(pyxel.KEY_UP):
            if self.player.can_jump: 
                self.player.jump_power = -10
                self.player.can_jump = False
        
        elif pyxel.btn(pyxel.KEY_SPACE):
            if self.check_wall("up", self.player.dot_x, self.player.dot_y) == False:
                self.player.dot_y -= 2

    def jump(self):
            #ジャンプできる時それは飛ぶ処理がいらない時！
            if self.player.can_jump:
                return

            #ブロックとブロックでサンドウィッチの時は反応しない
            if self.check_wall("down", self.player.dot_x, self.player.dot_y) and self.check_wall("up", self.player.dot_x, self.player.dot_y):
                return

            #よくわかりません
            y_prev = self.player.dot_y
            y_tmp = self.player.dot_y
            self.player.dot_y += (self.player.dot_y - y_prev ) + self.player.jump_power 
            y_prev = y_tmp
            self.player.jump_power += 1

            #加速度付きすぎたらブロック貫通するので制限
            if self.player.jump_power >= 8:
                self.player.jump_power = 8

            #もし下にブロックあったら
            if self.check_wall("down", self.player.dot_x, self.player.dot_y):
                self.player.can_jump = True
                self.player.jump_power = 0
                
                #貫通対策。ここからはdownの処理が始まる
                self.player.dot_y -= 8

            #もしブロックに頭当たったら
            if self.check_wall("up", self.player.dot_x, self.player.dot_y):
                #貫通対策
                self.player.dot_y += 3
                self.player.jump_power = 0
        
            #画面切り替え
            if (self.player.dot_y + 8) > 128:
                self.player.minimap_y += 1
                self.player.player_update(self.player.dot_x, 8)

            if (self.player.dot_y - 8) < 0:
                if self.check_wall("up", self.player.dot_x, self.player.dot_y) == False:
                    self.player.minimap_y -= 1
                    self.player.player_update(self.player.dot_x, 120)


                
    def down(self):
        #もし飛んでる時じゃなくて空中にいたら(笑神の大悟みたいな)
        if self.player.can_jump == True and self.check_wall("down", self.player.dot_x, self.player.dot_y) == False:
            #別にインスタンス変数にしなくてもいいかなと思った初期値1
            global FALLING_POWER

            y_prev = self.player.dot_y
            y_tmp = self.player.dot_y
            self.player.dot_y += (self.player.dot_y - y_prev ) + FALLING_POWER
            y_prev = y_tmp
            FALLING_POWER += 1

            #加速度制限
            if FALLING_POWER >= 8:
                FALLING_POWER = 8

            #画面切り替え
            if (self.player.dot_y + 8) > 128:
                    self.player.minimap_y += 1
                    self.player.player_update(self.player.dot_x, 8)

            #もし床に着いたら
            if self.check_wall("down", self.player.dot_x, self.player.dot_y):
                self.player.can_jump = True
                FALLING_POWER = 0
                #貫通対策
                self.player.dot_y -= 8
                #仕上げ
                while self.check_wall("down", self.player.dot_x, self.player.dot_y)==False:
                    self.player.dot_y += 1

    def update_stage(self):
        if self.player.is_standing_door == True:
            if self.player.minimap_x == 14 and self.player.minimap_y == 1:
                self.player.player_minimap_update(1, 3)
                self.player.player_update(16, 112)

            if self.player.minimap_x == 9 and self.player.minimap_y == 3:
                self.player.player_minimap_update(9, 4)
                self.player.player_update(16, 32)

            if self.player.minimap_x == 10 and self.player.minimap_y == 3:
                self.player.player_minimap_update(1, 7)
                self.player.player_update(16, 112) 

            if self.player.minimap_x == 14 and self.player.minimap_y == 4:
                self.player.player_minimap_update(1, 7)
                self.player.player_update(16, 112) 

            if self.player.minimap_x == 4 and self.player.minimap_y == 6:
                self.player.player_minimap_update(1,9)
                self.player.player_update(8, 112)
            
            if self.player.minimap_x == 2 and self.player.minimap_y == 11:
                self.player.player_minimap_update(15, 10)
                self.player.player_update(64, 64)

#CHECK-----------------------------------------------------
    def check_wall(self, vec, x, y):
        wall_list = [(0,2),(1,2),(2,2),(3,2),(4,2),(8,5),(6,5)]
        base_x = (self.player.minimap_x-1)*16
        base_y = (self.player.minimap_y-1)*16

        if vec=="right":
            player_map_x = x // 8 + base_x
            player_map_y_upper = y // 8 + base_y
            player_map_y_lower = (y+7) // 8 + base_y
            """
            衝突判定
  upperここと→_________ 
            |        |
            |        |
            |        |
 lowerここで→__________
            """

            if self.get_tilemap(player_map_x+1, player_map_y_upper) in wall_list or self.get_tilemap(player_map_x+1, player_map_y_lower) in wall_list:
                return True

        if vec=="left":
            player_map_x = (x+7) // 8 + base_x
            player_map_y_upper = y // 8 + base_y
            player_map_y_lower = (y+7) // 8 + base_y
            """
            衝突判定
             _________←upperここと
            |        |
            |        |
            |        |
            __________←lowerここで
            """

            if self.get_tilemap(player_map_x-1, player_map_y_upper) in wall_list or self.get_tilemap(player_map_x-1, player_map_y_lower) in wall_list:
                self.player.can_jump = True
                return True

        if vec == "down":
            player_map_x_right = (x+7) // 8 + base_x
            player_map_x_left = (x+1) // 8 + base_x
            player_map_y = y // 8 + base_y
            """
            衝突判定
   こことleft→_________←rightここで 
            |        |
            |        |
            |        |
            __________
            """

            if self.get_tilemap(player_map_x_right, player_map_y+1) in wall_list or self.get_tilemap(player_map_x_left, player_map_y+1) in wall_list:
                return True

        if vec == "up":
            player_map_x_right = (x+7) // 8 + base_x
            player_map_x_left = x // 8 + base_x
            player_map_y = (y+7) // 8 + base_y
            """
            衝突判定
             _________
            |        |
            |        |
            |        |
 こことleft→ __________←rightここで 
            """
            if self.get_tilemap(player_map_x_right, player_map_y-1) in wall_list or self.get_tilemap(player_map_x_left, player_map_y-1) in wall_list:
                return True

        #基本はFalse返す
        return False

    def check_sign(self):
        x = 16*(self.player.minimap_x-1)
        y = 16*(self.player.minimap_y-1)
        map_x = self.player.dot_x/8 + x
        map_y = self.player.dot_y/8 + y

        if self.get_tilemap(map_x, map_y) == (0,3):
            self.player.is_reading = True
        else:
            self.player.is_reading = False

    def check_door(self):
        x = 16*(self.player.minimap_x-1)
        y = 16*(self.player.minimap_y-1)
        map_x = self.player.dot_x/8 + x
        map_y = self.player.dot_y/8 + y
        door_list = [(5,3), (5,4), (6,3), (6,4)]
        if self.get_tilemap(map_x, map_y) in door_list:
            self.player.is_standing_door = True
        else:
            self.player.is_standing_door = False
        
#DRAW------------------------------------------------------
    def draw(self):
        pyxel.cls(0)
        self.draw_tilemap()
        self.draw_player()
        self.draw_sign()
        

    def draw_tilemap(self):
        u = 128*(self.player.minimap_x-1)
        v = 128*(self.player.minimap_y-1)
        pyxel.bltm(0,0,0,u,v,128,128)

    def draw_player(self):
        pyxel.blt(self.player.dot_x, self.player.dot_y, 0, self.player.pose[0], self.player.pose[1], 8, 8, pyxel.COLOR_PEACH)

    def draw_sign(self):
        if self.player.is_reading == True:
            if self.player.minimap_y == 1:
                if self.player.minimap_x == 2:
                    self.katakana.draw_katakana(8, 40 , ["SI", "DAKUTEN", "YA", "NN", "HU", "HANDAKUTEN", "SI", "TE", "MI", "YO", "U", "!"])
                elif self.player.minimap_x == 3:
                    self.katakana.draw_katakana(8, 40, ["O", "KA", "SI", "WO", "TA", "HE", "DAKUTEN", "TA", "RA"])
                    self.katakana.draw_katakana(8, 50, ["TO", "HE", "DAKUTEN", "NA", "KU", "NA", "RU", "YO"])
                elif self.player.minimap_x == 4:
                    self.katakana.draw_katakana(8,40, ["A", "RE", "KA", "DAKUTEN", "TE", "KI", "KUTEN"])
                    self.katakana.draw_katakana(8, 50, ["A", "TA", "RA", "NA", "I", "TE", "DAKUTEN", "!"])
                elif self.player.minimap_x == 5:
                    self.katakana.draw_katakana(8, 40, ["O", "KA", "SI", "WO", "TA", "HE", "DAKUTEN","TE", "TA", "RA"])
                    self.katakana.draw_katakana(8, 50, ["SU", "HE", "HANDAKUTEN", "I", "SU", "KI", "I", "TE", "DAKUTEN"])
                    self.katakana.draw_katakana(8, 60, ["TI", "KA", "KU", "NO", "TE", "KI", "WO"])
                    self.katakana.draw_katakana(8, 70, ["KO", "U", "KE", "DAKUTEN", "KI", "TE", "DAKUTEN", "KI", "RU"])
                elif self.player.minimap_x == 6:
                    self.katakana.draw_katakana(8, 40, ["KO", "KO", "KA", "RA", "HO", "NN", "HA", "DAKUTEN", "NN"])
                    self.katakana.draw_katakana(8, 50, ["KA", "DAKUTEN", "NN", "HA", "DAKUTEN", "RE", "!"])

App()
