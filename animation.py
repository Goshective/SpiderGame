from constants import *
from loading_files import load_image


class Animation:
    def __init__(self, obj_class):

        self.delay = FPS // 4
        self.frame_counter = 0
        #self.prev_name = "stay"
        if obj_class == "player":
            self.sides = {}
            #names = "left", "right", "stay", "jump", "jump_l", "jump_r" 
            #consts = ANIMATION_LEFT, ANIMATION_RIGHT, ANIMATION_STAY, ANIMATION_JUMP, ANIMATION_JUMP_LEFT, ANIMATION_JUMP_RIGHT
            self.f1 = load_image("pauk1.png")
            self.f2 = load_image("pauk2.png")
            self.f3 = load_image("pauk3.png")

    def update(self, idle=False):
        if idle:
            return self.f1
        self.frame_counter = (self.frame_counter + 1) % self.delay
        limit = self.delay // 3
        if self.frame_counter < limit:
            return self.f1
        elif self.frame_counter < limit*2:
            return self.f2
        else:
            if self.frame_counter == self.delay:
                self.frame_counter = 0
            return self.f3