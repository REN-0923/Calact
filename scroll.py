import pyxel 

FALLING_POWER = 1

class Player:
    def __init__(self):
        #ウィンドウ内での座標
        self.dot_x = 8
        self.dot_y = 112

        #何枚目のマップにいるか
        self.minimap_x = 1
        self.minimap_y = 1
        
        #どのポーズか
        self.pose = (0,0)

        #ジャンプできるか
        self.can_jump = True

        #ジャンプでどのくらい上に行くか
        self.jump_power = 0

    def player_update(self, x, y):
        self.dot_x = x
        self.dot_y = y
    
        
class App:
    def __init__(self):
        self.player = Player()

        pyxel.init(128, 128, title="scroll")
        pyxel.load("assets//scroll.pyxres")
        pyxel.run(self.update, self.draw)

    def update(self):
        self.update_player()
        self.jump()
        self.down()
        print(self.player.jump_power)
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
                self.player.pose = (0,0)
                #貫通対策。ここからはdownの処理が始まる
                self.player.dot_y -= 8

            #もしブロックに頭当たったら
            if self.check_wall("up", self.player.dot_x, self.player.dot_y):
                #貫通対策
                self.player.dot_y += 2
                self.player.jump_power = 0
                
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

            #もし床に着いたら
            if self.check_wall("down", self.player.dot_x, self.player.dot_y):
                self.player.can_jump = True
                FALLING_POWER = 0
                #貫通対策
                self.player.dot_y -= 8
                #仕上げ
                while self.check_wall("down", self.player.dot_x, self.player.dot_y)==False:
                    self.player.dot_y += 1
#CHECK-----------------------------------------------------
    def check_wall(self, vec, x, y) :
        wall_list = [(0,2),(1,2),(2,2),(3,2),(4,2)]
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
            player_map_x_left = x // 8 + base_x
            player_map_y = y // 8 + base_y
            """
            衝突判定
   こことleft→_________←rightここで フォーリンラブ
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

        
#DRAW------------------------------------------------------
    def draw(self):
        pyxel.cls(0)
        self.draw_tilemap()
        self.draw_player()

    def draw_tilemap(self):
        u = 16*(self.player.minimap_x-1)
        pyxel.bltm(0,0,0,u,0,16,16)

    def draw_player(self):
        pyxel.blt(self.player.dot_x, self.player.dot_y, 0, self.player.pose[0], self.player.pose[1], 8, 8, pyxel.COLOR_PEACH)

App()