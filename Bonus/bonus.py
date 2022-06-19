from enum import Enum, auto

import numpy as np
import pygame as pg
import pygame.camera as pgc
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
GLOBAL_SEED = 1

@deserialize
@dataclass
class Conf(Config):
    random_weight = 3
    delta_time: float = 2
    mass: int = 20


class Fox(Agent):
    config: Conf
    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.energy = 100
        self.age = 0
        self.max_age = 14

    def random_move(self):
        self.move = self.move / np.linalg.norm(self.move) if np.linalg.norm(self.move) > 0 else self.move
        f_total = (self.config.random_weight * np.random.uniform(low = -1, high = 1, size = 2))/self.config.mass
        self.move += f_total
    def update_location(self):
        self.pos += self.move * self.config.delta_time

    def change_position(self):
        self.there_is_no_escape()
        if self.energy == 0: self.kill()

        if self.is_alive():
            self.age += 0.01
            self.energy -= 1

            self.random_move()
            self.update_location()

            if self.energy < 70:
                self.change_image(1)
                r = list(set(self.in_proximity_accuracy().filter_kind(Rabbit)))
                if len(r)>0:
                    r[0][0].kill()
                    self.energy += 50 if self.energy < 60 else 100
                    self.change_image(0)
            else:
                f = list(set(self.in_proximity_accuracy().filter_kind(Fox)))
                if len(f)>0 and self.age > 1 and f[0][0].age > 1:
                    f[0][0].change_image(2)
                    self.change_image(2)
                    f[0][0].energy -= 20
                    self.energy -= 20
                    self.reproduce()



class Rabbit(Agent):
    config: Conf
    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.energy = 100
        self.age = 0
        self.max_age = 12

    def random_move(self):
        self.move = self.move / np.linalg.norm(self.move) if np.linalg.norm(self.move) > 0 else self.move
        f_total = (self.config.random_weight * np.random.uniform(low = -1, high = 1, size = 2))/self.config.mass
        self.move += f_total
    def update_location(self):
        self.pos += self.move * self.config.delta_time

    def change_position(self):
        self.there_is_no_escape()

        if self.energy == 0: self.kill()
        if self.is_alive():
            self.random_move()
            self.update_location()

            print(f"found fox: {self.in_proximity_accuracy().filter_kind(Fox)}")



class Live(Simulation):
    config: Conf

x, y = Conf().window.as_tuple()
df = (
    Live(
        Conf(
            movement_speed=1,
            image_rotation=True,
            radius=50,
            seed=GLOBAL_SEED,
        )
    )
        .batch_spawn_agents(50, Rabbit, images=["images/white.png","images/red.png","images/green.png"])
        .batch_spawn_agents(5, Fox, images=["images/bird.png","images/bird_red.png","images/bird_green.png"])
        .run()
)


dfs = df.snapshots
#dfs.write_csv(f"Experiments/A{FlockingConfig.alignment_weight:.2f}_C{FlockingConfig.cohesion_weight:.2f}_S{FlockingConfig.separation_weight:.2f}_W{FlockingConfig.random_weight:.2f}.csv")

