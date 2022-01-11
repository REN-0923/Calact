import pyxel

class KATAKANA:
    def __init__(self):
        self.katakana_dic = {
            "A":(0,0),
            "I":(1,0),
            "U":(2,0),
            "E":(3,0),
            "O":(4,0),
            "KA":(0,1),
            "KI":(1,1),
            "KU":(2,1),
            "KE":(3,1),
            "KO":(4,1),
            "SA":(0,2),
            "SI":(1,2),
            "SU":(2,2),
            "SE":(3,2),
            "SO":(4,2),
            "TA":(0,3),
            "TI":(1,3),
            "TU":(2,3),
            "TE":(3,3),
            "TO":(4,3),
            "NA":(0,4),
            "NI":(1,4),
            "NU":(2,4),
            "NE":(3,4),
            "NO":(4,4),
            "HA":(0,5),
            "HI":(1,5),
            "HU":(2,5),
            "HE":(3,5),
            "HO":(4,5),
            "MA":(0,6),
            "MI":(1,6),
            "MU":(2,6),
            "ME":(3,6),
            "MO":(4,6),
            "YA":(0,7),
            "YU":(2,7),
            "YO":(4,7),
            "RA":(0,8),
            "RI":(1,8),
            "RU":(2,8),
            "RE":(3,8),
            "RO":(4,8),
            "WA":(0,9),
            "WO":(2,9),
            "NN":(4,9),
            "!":(0,10),
            "?":(1,10,),
            "KUTEN":(2,10),
            "TOUTEN":(3,10),
            "DAKUTEN":(4,10),
            "HANDAKUTEN":(5,10),
        }

    def draw_katakana(self, x, y, text_array): 
        for i in range(len(text_array)):
            text = self.katakana_dic[text_array[i]]
            text_x = text[0]*8
            text_y = text[1]*8
            pyxel.blt(x+i*8, y, 1, text_x, text_y, 8, 8, )



