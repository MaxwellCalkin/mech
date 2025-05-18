from mech_arena.level import Level
from mech_arena.player import Player
from mech_arena.enemy import Enemy


def test_level_update_moves_enemy_toward_player():
    player = Player(x=0, y=0, speed=1)
    enemy = Enemy(x=10, y=0, speed=1)
    level = Level(name="test", description="desc", player=player, enemies=[enemy])
    level.update()
    assert enemy.x == 9
    assert enemy.y == 0


def test_level_player_takes_damage_on_collision():
    player = Player(x=0, y=0, speed=0, health=2)
    enemy = Enemy(x=0, y=0, speed=0)
    level = Level(name="test", description="desc", player=player, enemies=[enemy])
    level.update()
    assert player.health == 1


def test_level_no_damage_without_collision():
    player = Player(x=0, y=0, speed=0, health=2)
    enemy = Enemy(x=100, y=100, speed=0)
    level = Level(name="test", description="desc", player=player, enemies=[enemy])
    level.update()
    assert player.health == 2
