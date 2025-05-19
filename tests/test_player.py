from mech_arena.player import Player


def test_move_left():
    p = Player(x=10, y=0, speed=2)
    p.move(-1, 0)
    assert p.x == 8
    assert p.y == 0


def test_move_up():
    p = Player(x=0, y=10, speed=3)
    p.move(0, -1)
    assert p.y == 7


def test_take_damage():
    p = Player(x=0, y=0, health=20)
    p.take_damage(5)
    assert p.health == 15
    assert p.alive
    p.take_damage(20)
    assert p.health == 0
    assert not p.alive
