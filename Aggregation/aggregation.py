from typing import TYPE_CHECKING, Any, Generator, Optional
from pygame.mask import Mask
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.sprite import Group, Sprite
from pygame.surface import Surface
from typing_extensions import Self


import math
import numpy as np
import pygame as pg
import pygame.camera as pgc
from pygame.math import Vector2
from vi.util import random_angle, random_pos, round_pos
from vi import Agent, Simulation, HeadlessSimulation
from vi.config import Config, dataclass, deserialize


@deserialize
@dataclass
class AggregationConfig(Config):
    random_weight = 3

    weigth_leave = 0.2
    weight_join = 0.9

    delta_time: float = 2
    mass: int = 20



class Cockroach(Agent):
    config: AggregationConfig
    def __init__(self, images: list[Surface], simulation: HeadlessSimulation, pos: Optional[Vector2] = None, move: Optional[Vector2] = None):
        Agent.__init__(self, images=images, simulation=simulation,pos=pos,move=move)
        self.loneliness = 0.5
        self.on_place = 0
        self.last_move = pg.Vector2((0,0))

    def change_position(self):
        n = list(self.in_proximity_accuracy()) #list of neighbors
        len_n = len(n)


        P_leave = self.config.weigth_leave / len_n ** math.log(len_n) if len_n > 0 else self.config.weigth_leave
        P_join = 1-(0.8**math.log(len_n)) if len_n > 2 else 0.5

        self.on_place += 1 if self.on_site() else 0


        self.move = self.move / np.linalg.norm(self.move) if np.linalg.norm(self.move) > 0 else self.move
        f_total = (self.config.random_weight * np.random.uniform(low = -1, high = 1, size = 2))/self.config.mass
        self.move += f_total

        self.move *= 0.5 ** self.on_place
        print(np.linalg.norm(self.move))
        if np.linalg.norm(self.move) < 0.3:
            self.last_move = self.move = self.move / np.linalg.norm(self.move) if np.linalg.norm(self.move) > 0 else self.last_move
            self.move = pg.Vector2((0,0)) if np.random.uniform() < P_join else self.move
            self.change_image(1)

            self.move = self.last_move * (1-(0.9 + self.loneliness)/2) if np.random.uniform() < P_leave else self.move
        else: self.change_image(0)



        #collision detection
        coll = list(self.obstacle_intersections(scale = 2))
        if len(coll) > 0:
            for c in coll:
                nm = self.move-(c-self.pos) #current move velocity - distance to the obstacle
                self.move = nm / np.linalg.norm(nm) #normalize vector

        self.loneliness = 1/(1+np.exp(-0.5*len_n+3))
        self.pos += self.move * self.config.delta_time  #update pos




x, y = AggregationConfig().window.as_tuple()

df = (
    Simulation(
        AggregationConfig(
            fps_limit = 0,
            movement_speed=1,
            radius=50,
            seed=1,
        )
    )
    .spawn_obstacle("images/boundary.png", x//2,  y//2)
    .spawn_site("images/shadow_norm.png", x//2 , y//2)
    .batch_spawn_agents(50, Cockroach, images=["images/white.png","images/red.png"])
    .run()
)


dfs = df.snapshots
#dfs.write_csv(f"Experiments/A{FlockingConfig.alignment_weight:.2f}_C{FlockingConfig.cohesion_weight:.2f}_S{FlockingConfig.separation_weight:.2f}_W{FlockingConfig.random_weight:.2f}.csv")