import pyxel 
from  katakana import KATAKANA

FALLING_POWER = 1
STAGE_COLOR = "green"

class Player:
    def __init__(self):
        #ウィンドウ内での座標
        self.dot_x = 8
        self.dot_y = 8

        #何枚目のマップにいるか
        if STAGE_COLOR == "green":
            self.minimap_x = 1
            self.minimap_y = 1
        elif STAGE_COLOR == "blue":
            self.minimap_x = 7
            self.minimap_y = 1
        elif STAGE_COLOR == "yellow":
            self.minimap_x = 1
            self.minimap_y = 3
        elif STAGE_COLOR == "gray":
            self.minimap_x = 9
            self.minimap_y = 4
        elif STAGE_COLOR == "red":
            self.minimap_x = 1
            self.minimap_y = 7
        else:
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

        #攻撃できる回数(アイテム取って増える)
        self.bullet = 0

        #ゲームオーバーか否か
        self.is_game_over = False

        #操作可能か否か
        self.is_playing = True

        #どの色のステージにいるか
        #self.stage_color = "green"

    def player_update(self, x, y):
        self.dot_x = x
        self.dot_y = y
    
    def player_minimap_update(self, x, y):
        self.minimap_x = x
        self.minimap_y = y

    def whole_tile_coordinate_X(self):
        x = 16*(self.minimap_x-1)
        return self.dot_x/8 + x

    def whole_tile_coordinate_Y(self):
        y = 16*(self.minimap_y-1)
        return self.dot_y/8 + y
        
class App:
    def __init__(self):
        self.player = Player()
        self.katakana = KATAKANA()


        pyxel.init(128, 128, title="scroll")
        pyxel.load("scroll.pyxres")
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.player.is_playing == True:
            self.update_player()
            
            self.jump()
            self.down()
            self.check_sign()
            self.check_door()
            self.check_needle_magma()
            self.check_stage()
            self.check_big_jump()
            self.update_stage()
            
            #print(STAGE_COLOR)

        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if pyxel.btnp(pyxel.KEY_R) and self.player.is_playing == False:
            self.player.is_playing == True
            self.restart()

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
        wall_list = [(0,2),(1,2),(2,2),(3,2),(4,2),(8,5),(6,5),(6,1)]
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
        map_x = self.player.whole_tile_coordinate_X()
        map_y = self.player.whole_tile_coordinate_Y()
        
        if self.get_tilemap(map_x, map_y) == (0,3):
            self.player.is_reading = True
        else:
            self.player.is_reading = False

    def check_door(self):
        map_x = self.player.whole_tile_coordinate_X()
        map_y = self.player.whole_tile_coordinate_Y()
        door_list = [(5,3), (5,4), (6,3), (6,4)]
        if self.get_tilemap(map_x, map_y) in door_list:
            self.player.is_standing_door = True
        else:
            self.player.is_standing_door = False


    def check_needle_magma(self):
        map_x = self.player.whole_tile_coordinate_X()
        map_y = self.player.whole_tile_coordinate_Y()
        enemy_list = [(5,2), (6,2), (7,2), (5,5), (7,1)]
        if self.get_tilemap(map_x, map_y) in enemy_list:
            self.player.is_game_over = True
        else:
            self.player.is_game_over = False

    def check_stage(self):
        global STAGE_COLOR
        minimap_coordinate = (self.player.minimap_x, self.player.minimap_y)
        if minimap_coordinate == (1,1):
            STAGE_COLOR = "green"
        if minimap_coordinate == (7,1):
            STAGE_COLOR = "blue"
        if minimap_coordinate == (1,3):
            STAGE_COLOR = "yellow"
        if minimap_coordinate == (9,4):
            STAGE_COLOR = "gray"
        if minimap_coordinate == (1,7):
            STAGE_COLOR = "red"

    def check_big_jump(self):
        map_x = self.player.whole_tile_coordinate_X()
        map_y = self.player.whole_tile_coordinate_Y()
        if self.get_tilemap(map_x, map_y) == (3,5):
            self.player.jump_power = -13
            self.player.can_jump = False
            self.jump()

    def restart(self):
        self.player=Player()
    
    def change_magma(self):
        #print(True)
        for x in range(0,16):
            for y in range(0, 16):
                if self.get_tilemap(16*(self.player.minimap_x-1)+x, 16*(self.player.minimap_y-1)+y)==(6,2):
                    if pyxel.frame_count % 100 >= 50:
                        pyxel.tilemap(0).pset(16*(self.player.minimap_x-1)+x, 16*(self.player.minimap_y-1)+y, (5,2))
                if self.get_tilemap(16*(self.player.minimap_x-1)+x, 16*(self.player.minimap_y-1)+y)==(5,2):
                    if pyxel.frame_count % 100 < 40:
                        pyxel.tilemap(0).pset(16*(self.player.minimap_x-1)+x, 16*(self.player.minimap_y-1)+y, (6,2))
        
    def change_green_block(self):
        for x in range(0,16):
            for y in range(0, 16):
                if self.get_tilemap(16*(self.player.minimap_x-1)+x, 16*(self.player.minimap_y-1)+y)==(8,5):
                    if pyxel.frame_count % 100 >= 50:
                        pyxel.tilemap(0).pset(16*(self.player.minimap_x-1)+x, 16*(self.player.minimap_y-1)+y, (9,5))
                if self.get_tilemap(16*(self.player.minimap_x-1)+x, 16*(self.player.minimap_y-1)+y)==(9,5):
                    if pyxel.frame_count % 100 < 40:
                        pyxel.tilemap(0).pset(16*(self.player.minimap_x-1)+x, 16*(self.player.minimap_y-1)+y, (8,5))

    def change_laser(self):
        for x in range(0,16):
            for y in range(0, 16):
                if self.get_tilemap(16*(self.player.minimap_x-1)+x, 16*(self.player.minimap_y-1)+y)==(6,1):
                    #print(True)
                    if pyxel.frame_count % 100 < 20:
                        for i in range(1, 4):
                            pyxel.tilemap(0).pset(16*(self.player.minimap_x-1)+x+i, 16*(self.player.minimap_y-1)+y, (7,1))
                
                if self.get_tilemap(16*(self.player.minimap_x-1)+x, 16*(self.player.minimap_y-1)+y)==(7,1):
                    if pyxel.frame_count % 100 >= 20:
                        pyxel.tilemap(0).pset(16*(self.player.minimap_x-1)+x, 16*(self.player.minimap_y-1)+y, (2,3))

#DRAW------------------------------------------------------
    def draw(self):
        pyxel.cls(0)
        self.draw_tilemap()
        self.draw_player()
        self.draw_sign()
        self.change_magma()
        self.change_green_block()
        self.change_laser()

        if self.player.is_game_over == True:
            self.player.is_playing = False
            pyxel.cls(0)
            pyxel.text(20, 30, "YOU ARE DEAD", 8)
            pyxel.text(20, 70, "R = RETRY", 8)
        

    def draw_tilemap(self):
        u = 128*(self.player.minimap_x -1)
        v = 128*(self.player.minimap_y -1)
        pyxel.bltm(0,0,0,u,v,128,128)

    def draw_player(self):
        pyxel.blt(self.player.dot_x, self.player.dot_y, 0, self.player.pose[0], self.player.pose[1], 8, 8, pyxel.COLOR_PEACH)

    def draw_sign(self):
        if self.player.is_reading == True:
            if self.player.minimap_y == 1:
                if self.player.minimap_x == 2:
                    self.katakana.draw_katakana(8, 40 , ["SI", "DAKUTEN", "YA", "NN", "HU", "HANDAKUTEN", "SI", "TE", "MI", "YO", "U", "!"])
                #elif self.player.minimap_x == 3:
                    #self.katakana.draw_katakana(8, 40, ["O", "KA", "SI", "WO", "TA", "HE", "DAKUTEN", "TA", "RA"])
                    #self.katakana.draw_katakana(8, 50, ["TO", "HE", "DAKUTEN", "NA", "KU", "NA", "RU", "YO"])
                elif self.player.minimap_x == 4:
                    self.katakana.draw_katakana(8,40, ["TO", "KE", "DAKUTEN", "HA"])
                    self.katakana.draw_katakana(8, 50, ["YO", "KE", "YO", "U", "NE", "!"])
                #elif self.player.minimap_x == 5:
                    #self.katakana.draw_katakana(8, 40, ["O", "KA", "SI", "WO", "TA", "HE", "DAKUTEN","TE", "TA", "RA"])
                    #self.katakana.draw_katakana(8, 50, ["SU", "HE", "HANDAKUTEN", "I", "SU", "KI", "I", "TE", "DAKUTEN"])
                    #self.katakana.draw_katakana(8, 60, ["TI", "KA", "KU", "NO", "TE", "KI", "WO"])
                    #self.katakana.draw_katakana(8, 70, ["KO", "U", "KE", "DAKUTEN", "KI", "TE", "DAKUTEN", "KI", "RU"])
                elif self.player.minimap_x == 6:
                    self.katakana.draw_katakana(8, 40, ["KO", "KO", "KA", "RA", "HO", "NN", "HA", "DAKUTEN", "NN"])
                    self.katakana.draw_katakana(8, 50, ["KA", "DAKUTEN", "NN", "HA", "DAKUTEN", "RE", "!"])
            elif self.player.minimap_y ==3:
                if self.player.minimap_x == 4:
                    self.katakana.draw_katakana(8, 40, ["TO", "RA", "NN", "HO", "HANDAKUTEN","RI", "NN", "TE", "DAKUTEN"])
                    self.katakana.draw_katakana(8, 50, ["TA","DAKUTEN", "I", "SI", "DAKUTEN", "YA", "NN", "HU", "HANDAKUTEN"])
            elif self.player.minimap_y ==4:
                if self.player.minimap_x == 2:
                    self.katakana.draw_katakana(8, 40, ["KO", "NO", "SA", "KI"])
                    self.katakana.draw_katakana(8, 50, ["KI", "E", "RU", "YU", "KA"])
                if self.player.minimap_x == 3:
                    self.katakana.draw_katakana(8, 40, ["KA", "HE", "DAKUTEN", "SO", "DAKUTEN", "I", "NI"])
                    self.katakana.draw_katakana(8, 50, ["O", "TI", "TE", "MI", "TE", "!"])
                if self.player.minimap_x == 9:
                    self.katakana.draw_katakana(8, 20, ["RE", "I", "SA", "DAKUTEN", "A", "NI"])
                    self.katakana.draw_katakana(8, 30, ["TI", "YU", "U", "I"])
            elif self.player.minimap_y == 9:
                if self.player.minimap_x == 1:
                    self.katakana.draw_katakana(8, 40, ["KO", "NO", "SA", "KI","KI", "WO", "TU", "KE", "TE", "!"])
                    self.katakana.draw_katakana(8, 50, ["TO", "DAKUTEN", "U", "TA", "I", "SI", "RI", "YO", "KU"])
                    self.katakana.draw_katakana(8, 60, ["MA", "TU", "KU", "SU", "TE", "DAKUTEN", "!"])
App()
