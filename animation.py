from constants import *
from loading_files import load_image


class Animation:
    def __init__(self, obj_class):

        self.delay = FPS // 2
        self.frame_counter = 0
        self.prev_name = "stay"
        if obj_class == "player":
            self.sides = {}
            names = "left", "right", "stay", "jump", "jump_l", "jump_r" 
            consts = ANIMATION_LEFT, ANIMATION_RIGHT, ANIMATION_STAY, ANIMATION_JUMP, ANIMATION_JUMP_LEFT, ANIMATION_JUMP_RIGHT
            for i in range(len(consts)):
                self.sides[names[i]] = [load_image(x) for x in consts[i]]

    def next(self, left, right, jump, on_ground):
        if self.frame_counter % self.delay != 0:
            self.frame_counter += 1
            return None
        if left and right:
            i = self.count_stage("stay")
            return self.sides["stay"][i]
        if left:
            if jump and on_ground:
                i = self.count_stage("jump_l")
                return self.sides["jump_l"][i]
            i = self.count_stage("left")
            return self.sides["left"][i]
        elif right:
            if jump and on_ground:
                i = self.count_stage("jump_r")
                return self.sides["jump_r"][i]
            i = self.count_stage("right")
            return self.sides["right"][i]
        elif jump and on_ground:
            i = self.count_stage("jump")
            return self.sides["jump"][i]
        else:
            i = self.count_stage("stay")
            return self.sides["stay"][i]

    def count_stage(self, name2):
        if self.prev_name != name2:
            self.frame_counter = 0
            self.prev = name2
            return 0
        return (self.frame_counter // (self.delay + 1)) % len(self.sides[name2])