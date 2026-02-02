import constants
from game.scripting.action import Action
from game.shared.point import Point

LEFT = Point(-constants.CELL_SIZE, 0)
RIGHT = Point(constants.CELL_SIZE, 0)
UP = Point(0, -constants.CELL_SIZE)
DOWN = Point(0, constants.CELL_SIZE)

class ControlActorsAction(Action):
    """
    An input action that controls the snake.
    
    The responsibility of ControlActorsAction is to get the direction and move the snake's head.

    Attributes:
        _keyboard_service (KeyboardService): An instance of KeyboardService.
    """

    def __init__(self, keyboard_service):
        """Constructs a new ControlActorsAction using the specified KeyboardService.
        
        Args:
            keyboard_service (KeyboardService): An instance of KeyboardService.
        """
        self._keyboard_service = keyboard_service
        self._direction_player_1 = RIGHT
        self._direction_player_2 = RIGHT

    def execute(self, cast, script):
        """Executes the control actors action.

        Args:
            cast (Cast): The cast of Actors in the game.
            script (Script): The script of Actions in the game.
        """

        players = cast.get_actors("snakes")

        # left
        if self._keyboard_service.is_key_down('a') and self._direction_player_1 != RIGHT: 
            self._direction_player_1 = LEFT

        if self._keyboard_service.is_key_down('left') and self._direction_player_2 != RIGHT: 
            self._direction_player_2 = LEFT
        
        # right
        if self._keyboard_service.is_key_down('d') and self._direction_player_1 != LEFT:
            self._direction_player_1 = RIGHT

        if self._keyboard_service.is_key_down('right') and self._direction_player_2 != LEFT: 
            self._direction_player_2 = RIGHT
        
        # up
        if self._keyboard_service.is_key_down('w') and self._direction_player_1 != DOWN:
            self._direction_player_1 = UP
        
        if self._keyboard_service.is_key_down('up') and self._direction_player_2 != DOWN:
            self._direction_player_2 = UP
        
        # down
        if self._keyboard_service.is_key_down('s') and self._direction_player_1 != UP:
            self._direction_player_1 = DOWN

        if self._keyboard_service.is_key_down('down') and self._direction_player_2 != UP:
            self._direction_player_2 = DOWN
        
        player_1_head = players[0].get_segments()[0]
        opposite_head_velocity = player_1_head.get_velocity().reverse()

        if self._direction_player_1.equals(opposite_head_velocity) == False: #I added To fix bug where snake turns 180 degrees, which I think works better
            players[0].turn_head(self._direction_player_1)

        player_2_head = players[1].get_segments()[0]
        opposite_head_velocity = player_2_head.get_velocity().reverse()

        if self._direction_player_2.equals(opposite_head_velocity) == False: #I added To fix bug where snake turns 180 degrees, which I think works better
            players[1].turn_head(self._direction_player_2)

        