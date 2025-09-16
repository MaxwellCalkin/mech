from mech_arena.player import Player


def test_move_respects_dt():
    p = Player(x=0, y=0, speed=100)
    p.move(1, 0, dt=0.5)
    assert p.x == 50
    assert p.y == 0


def test_try_fire_consumes_energy_and_sets_cooldown():
    p = Player(x=0, y=0)
    projectile = p.try_fire((100, 0))
    assert projectile is not None
    assert p.energy < p.max_energy
    assert p.try_fire((100, 0)) is None  # cooldown prevents immediate firing


def test_consume_scan_energy():
    p = Player(x=0, y=0)
    assert p.consume_scan_energy() is True
    assert p.energy == p.max_energy - p.scan_cost
    p.energy = 0
    assert p.consume_scan_energy() is False
