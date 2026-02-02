import constants
from game.casting.actor import Actor
from game.scripting.action import Action
from game.shared.point import Point

class HandleCollisionsAction(Action):
    """
    An update action that handles interactions between the actors.
    
    The responsibility of HandleCollisionsAction is to handle the situation when the snake collides
    with the food, or the snake collides with its segments, or the game is over.

    Attributes:
        _is_game_over (boolean): Whether or not the game is over.
    """

    def __init__(self):
        """Constructs a new HandleCollisionsAction."""
        self._is_game_over = False
        self._loser = None

    def execute(self, cast, script):
        """Executes the handle collisions action.

        Args:
            cast (Cast): The cast of Actors in the game.
            script (Script): The script of Actions in the game.
        """
        if not self._is_game_over:
            self._handle_food_collision(cast)
            self._handle_segment_collision(cast)
            self._handle_player_collision(cast)
            self._handle_game_over(cast)

    def _handle_food_collision(self, cast):
        """Updates the score nd moves the food if the snake collides with the food.
        
        Args:
            cast (Cast): The cast of Actors in the game.
        """
        score = cast.get_first_actor("scores")
        food = cast.get_first_actor("foods")
        players = cast.get_actors("snakes")
        
        for player in players:
            head = player.get_head()

            if head.get_position().equals(food.get_position()):
                points = food.get_points()
                player.grow_tail(points)
                score.add_points(points)
                food.reset()
    
    def _handle_segment_collision(self, cast):
        """Sets the game over flag if the snake collides with one of its segments.
        
        Args:
            cast (Cast): The cast of Actors in the game.
        """
        players = cast.get_actors("snakes")
        for player in players:
            head = player.get_segments()[0]
            segments = player.get_segments()[1:]
            
            # if snakes collide with themselves
            for segment in segments:
                if head.get_position().equals(segment.get_position()):
                    self._loser = players.index(player)
                    self._is_game_over = True

    def _handle_player_collision(self, cast):
        """Sets the game over flag if the snake collides with one of the other players segments.
        
        Args:
            cast (Cast): The cast of Actors in the game.
        """
        players = cast.get_actors("snakes")
        player_1 = players[constants.PLAYER_1]
        player_2 = players[constants.PLAYER_2]

        # Player 1
        head_1 = player_1.get_segments()[0]
        segments_1 = player_1.get_segments()[1:]
        
        # Player 2
        head_2 = player_2.get_segments()[0]
        segments_2 = player_2.get_segments()[1:]
        
        # if snake 1 hits snake 2
        for segment in segments_2:
            if head_1.get_position().equals(segment.get_position()):
                self._is_game_over = True
                self._loser = constants.PLAYER_1
        
        # if snake 2 hits snake 1
        for segment in segments_1:
            if head_2.get_position().equals(segment.get_position()):
                self._is_game_over = True
                self._loser = constants.PLAYER_2


                    
        
    def _handle_game_over(self, cast):
        """Shows the 'game over' message and turns the snake and food white if the game is over.
        
        Args:
            cast (Cast): The cast of Actors in the game.
        """
        if self._is_game_over:
            food = cast.get_first_actor("foods")
            food.set_color(constants.WHITE)

            x = int(constants.MAX_X / 2)
            y = int(constants.MAX_Y / 2)
            position = Point(x, y)

            # Sets color of snakes if they lost
            players = cast.get_actors("snakes")
            loser = players[self._loser]

            loser_segments = loser.get_segments()
            for segment in loser_segments:
                segment.set_color(constants.WHITE)

            message = Actor()
            message.set_text("Snake " + str(self._loser + 1) +" Wins!")
            message.set_position(position)
            cast.add_actor("messages", message)

            
                