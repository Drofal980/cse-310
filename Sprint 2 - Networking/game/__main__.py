from constants import *

from casting.cast import Cast
from casting.food import Food
from casting.score import Score
from casting.snake import Snake
from scripting.script import Script
from scripting.control_actors_action import ControlActorsAction
from scripting.move_actors_action import MoveActorsAction
from scripting.handle_collisions_action import HandleCollisionsAction
from scripting.draw_actors_action import DrawActorsAction
from directing.director import Director
from services.keyboard_service import KeyboardService
from services.video_service import VideoService


def main():
    
    # create the cast
    cast = Cast()
    cast.add_actor("foods", Food())
    cast.add_actor("scores", Score())
    cast.add_actor("snakes", Snake(PLAYER_1_X, PLAYER_1_Y, YELLOW, GREEN))
    cast.add_actor("snakes", Snake(PLAYER_2_X, PLAYER_2_Y, YELLOW, BLUE))
    
   
    # start the gamesa
    keyboard_service = KeyboardService()
    video_service = VideoService()

    script = Script()
    script.add_action("input", ControlActorsAction(keyboard_service))
    script.add_action("update", MoveActorsAction())
    script.add_action("update", HandleCollisionsAction())
    script.add_action("output", DrawActorsAction(video_service))
    
    director = Director(video_service)
    director.start_game(cast, script)


if __name__ == "__main__":
    main()