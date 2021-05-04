import math
from random import randint, random

import tkinter as tk

from gamelib import Sprite, GameApp, Text

from consts import *

class BaseFruit(Sprite):
    def __init__(self, app, img, x, y):
        super().__init__(app, img, x, y)
        self.app = app

    def check_off_limits(self):
        if self.x < -30:
            self.to_be_deleted = True

class SlowFruit(BaseFruit):
    def __init__(self, app, x, y):
        super().__init__(app, 'images/apple.png', x, y)
        self.worth = 1

    def update(self):
        self.x -= FRUIT_SLOW_SPEED
        self.check_off_limits()


class FastFruit(BaseFruit):
    def __init__(self, app, x, y):
        super().__init__(app, 'images/banana.png', x, y)
        self.worth = 2

    def update(self):
        self.x -= FRUIT_FAST_SPEED
        self.check_off_limits()


class SlideFruit(BaseFruit):
    def __init__(self, app, x, y):
        super().__init__(app, 'images/cherry.png', x, y)
        self.direction = randint(0,1)*2 - 1
        self.worth = 3

    def update(self):
        self.x -= FRUIT_FAST_SPEED
        self.y += self.direction * 5
        self.check_off_limits()


class CurvyFruit(BaseFruit):
    def __init__(self, app, x, y):
        super().__init__(app, 'images/pear.png', x, y)
        self.t = randint(0,360) * 2 * math.pi / 360
        self.worth = 4

    def update(self):
        self.x -= FRUIT_SLOW_SPEED * 1.2
        self.t += 1
        self.y += math.sin(self.t*0.08)*10
        self.check_off_limits()


class Cat(Sprite):
    def __init__(self, app, x, y):
        super().__init__(app, 'images/cat.png', x, y)

        self.fruit_collected_observer = []

        self.app = app
        self.direction = None

    def update(self):
        if self.direction == CAT_UP:
            if self.y >= CAT_MARGIN:
                self.y -= CAT_SPEED
        elif self.direction == CAT_DOWN:
            if self.y <= CANVAS_HEIGHT - CAT_MARGIN:
                self.y += CAT_SPEED

    def check_collision(self, fruit):
        if self.distance_to(fruit) <= CAT_CATCH_DISTANCE:
            self.observers_notify(fruit)

    def observer_subscribe(self, observer):
        self.fruit_collected_observer.append(observer)

    def observers_notify(self, fruit):
        for observer in self.fruit_collected_observer:
            observer(fruit)


class CatGame(GameApp):
    def init_game(self):
        self.cat = Cat(self, 50, CANVAS_HEIGHT // 2)
        self.cat.observer_subscribe(self.fruit_collected_observer)
        self.elements.append(self.cat)

        self.key_bindings = {
            'Up': self.set_cat_dir(CAT_UP),
            'Down': self.set_cat_dir(CAT_DOWN)
        }

        self.score = 0
        self.score_text = Text(self, 'Score: 0', 100, 40)
        self.fruits = []

    def update_score(self):
        self.score_text.set_text('Score: ' + str(self.score))

    def random_fruits(self):
        if random() > 0.95:
            p = random()
            y = randint(50, CANVAS_HEIGHT - 50)
            if p <= 0.3:
                new_fruit = SlowFruit(self, CANVAS_WIDTH, y)
            elif p <= 0.6:
                new_fruit = FastFruit(self, CANVAS_WIDTH, y)
            elif p <= 0.8:
                new_fruit = SlideFruit(self, CANVAS_WIDTH, y)
            else:
                new_fruit = CurvyFruit(self, CANVAS_WIDTH, y)

            self.fruits.append(new_fruit)

    def process_collisions(self):
        for f in self.fruits:
            self.cat.check_collision(f)

    def update_and_filter_deleted(self, elements):
        new_list = []
        for e in elements:
            e.update()
            e.render()
            if e.to_be_deleted:
                e.delete()
            else:
                new_list.append(e)
        return new_list

    def post_update(self):
        self.process_collisions()

        self.random_fruits()

        self.fruits = self.update_and_filter_deleted(self.fruits)

    def on_key_pressed(self, event):
        key = event.keysym
        if key in self.key_bindings:
            self.key_bindings[key]()

    def set_cat_dir(self, direction):
        def f():
            self.cat.direction = direction
        return f

    def fruit_collected_observer(self, fruit):
        fruit.to_be_deleted = True
        self.score += fruit.worth
        self.update_score()
    

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Fruit Cat")
 
    # do not allow window resizing
    root.resizable(False, False)
    app = CatGame(root, CANVAS_WIDTH, CANVAS_HEIGHT, UPDATE_DELAY)
    app.start()
    root.mainloop()
