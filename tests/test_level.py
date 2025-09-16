import math

from mech_arena.enemy import Enemy
from mech_arena.level import Level
from mech_arena.player import Player


def test_projectile_neutralises_enemy_and_spawns_insight():
    player = Player(x=0, y=0)
    enemy = Enemy(x=0, y=0, topic="Residual Stream", summary="Test enemy", health=1)
    level = Level(
        name="test",
        description="desc",
        player=player,
        enemies=[enemy],
        width=500,
        height=400,
    )
    level.update(dt=1.0, fire_target=player.center)
    assert len(level.insights) == 0  # collected immediately
    assert level.knowledge_log
    title, body = level.knowledge_log[0]
    assert title == "Residual Stream"
    assert "Residual" in body


def test_scan_consumes_energy_and_slows_enemies():
    player = Player(x=0, y=0)
    enemy = Enemy(x=200, y=0, topic="Induction Head", summary="", speed=100)
    level = Level(
        name="scan",
        description="",
        player=player,
        enemies=[enemy],
        width=500,
        height=400,
    )
    start_energy = player.energy
    start_pos = (enemy.x, enemy.y)
    level.update(dt=1.0, trigger_scan=True)
    assert level.scan_timer > 0
    assert player.energy == start_energy - player.scan_cost
    movement = math.hypot(enemy.x - start_pos[0], enemy.y - start_pos[1])
    assert 0 < movement < enemy.speed  # slower than full-speed drift due to scan
    assert level.messages  # message logged


def test_messages_queue_keeps_recent_entries():
    player = Player(x=0, y=0)
    enemy = Enemy(x=300, y=300, topic="Circuit Breaker", summary="")
    level = Level(
        name="messages",
        description="",
        player=player,
        enemies=[enemy],
        width=500,
        height=400,
    )
    for _ in range(10):
        level.add_message("Test message")
    assert len(level.messages) <= level.messages.maxlen


def test_analysis_command_requires_scan_for_ablation():
    player = Player(x=100, y=100)
    enemy = Enemy(x=120, y=120, topic="Residual Stream", summary="")
    level = Level(
        name="analysis",
        description="",
        player=player,
        enemies=[enemy],
        width=500,
        height=400,
    )
    # Without scan the ablation should not trigger.
    level.update(dt=0.1, analysis_commands=[("toggle_ablation", 0)])
    assert not enemy.ablated
    # Activate scan timer and ensure ablation toggles.
    level.scan_timer = 1.0
    level.update(dt=0.1, analysis_commands=[("toggle_ablation", 0)])
    assert enemy.ablated
    assert level.analysis_tags.get("residual_ablation")


def test_collecting_insight_unlocks_tasks_and_journal():
    player = Player(x=0, y=0)
    enemy = Enemy(x=0, y=0, topic="Residual Stream", summary="Test enemy", health=1)
    level = Level(
        name="research",
        description="",
        player=player,
        enemies=[enemy],
        width=500,
        height=400,
    )
    level.update(dt=0.1, fire_target=player.center)
    assert any(task.concept == "Residual Stream" for task in level.active_tasks)
    assert "Residual Stream" in level.research_journal.records
