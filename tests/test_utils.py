from mech_arena.utils import rects_collide


def test_rects_collide_true():
    assert rects_collide((0, 0, 10, 10), (5, 5, 4, 4))


def test_rects_collide_false():
    assert not rects_collide((0, 0, 10, 10), (20, 20, 5, 5))
