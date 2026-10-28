import pytest
import math
from gas.box import Box
from gas.engine import Engine, naive_collision_detection

box_width = 600
box_height = 600
particle_max_radius = 2.0
initial_speed = 100.0
dt = 1 / 120


def make_box():
  """Return a fresh box so every test starts from empty state."""
  return Box(box_width, box_height, particle_max_radius)


def make_engine(**overrides):
  """Return an engine with small defaults, so the tests stay fast."""
  settings = {"particle_count": 50, "seed": 42}
  settings.update(overrides)
  return Engine(make_box(), **settings)


def test_engine_fills_the_box_with_particles():
  engine = make_engine(particle_count=123)
  assert len(engine.box.particles) == 123


def test_new_engine_starts_with_a_clean_state():
  engine = make_engine()
  assert engine.collisions == 0
  assert engine.time == 0.0


def test_every_particle_starts_with_the_initial_speed_towards_x():
  engine = make_engine(particle_count=20)
  for particle in engine.box.particles:
    assert particle.vx == pytest.approx(initial_speed)
    assert particle.vy == pytest.approx(0.0)


def test_particles_are_spawned_inside_the_box():
  engine = make_engine(particle_count=50)
  limit_x = box_width / 2 - particle_max_radius
  limit_y = box_height / 2 - particle_max_radius

  for particle in engine.box.particles:
    assert -limit_x <= particle.x <= limit_x
    assert -limit_y <= particle.y <= limit_y


def test_same_seed_gives_the_same_particles():
  first = make_engine(seed=7)
  second = make_engine(seed=7)

  for a, b in zip(first.box.particles, second.box.particles):
    assert a.x == pytest.approx(b.x)
    assert a.y == pytest.approx(b.y)


def test_different_seeds_give_different_particles():
  first = make_engine(seed=7)
  second = make_engine(seed=8)

  moved = [a for a, b in zip(first.box.particles, second.box.particles) if a.x != b.x]
  assert moved


def test_time_accumulates_with_every_step():
  engine = make_engine()
  for _ in range(10):
    engine.step(dt)
  assert engine.time == pytest.approx(10 * dt)


def test_energy_is_conserved_through_collisions():
  engine = make_engine(particle_count=150, seed=1)

  energy_before = sum(p.kinetic_energy() for p in engine.box.particles)
  for _ in range(800):
    engine.step(dt)
  energy_after = sum(p.kinetic_energy() for p in engine.box.particles)

  assert energy_after == pytest.approx(energy_before, rel=1e-9)


def test_collisions_are_counted():
  engine = make_engine(particle_count=150, seed=1)
  for _ in range(300):
    engine.step(dt)
  assert engine.collisions > 0


def test_particles_stay_inside_the_box():
  engine = make_engine(particle_count=100, seed=3)
  for _ in range(1000):
    engine.step(dt)

  limit_x = box_width / 2 - particle_max_radius
  limit_y = box_height / 2 - particle_max_radius
  for particle in engine.box.particles:
    assert abs(particle.x) <= limit_x + 1e-9
    assert abs(particle.y) <= limit_y + 1e-9


def test_collisions_relax_the_beam_towards_maxwell_boltzmann():
  """The beam starts with a single speed; collisions must spread it out."""
  engine = make_engine(particle_count=250, seed=5)
  for _ in range(2000):
    engine.step(dt)

  speeds = [p.speed() for p in engine.box.particles]
  mean_speed = sum(speeds) / len(speeds)
  rms_speed = math.sqrt(sum(s * s for s in speeds) / len(speeds))

  assert mean_speed / rms_speed == pytest.approx(math.sqrt(math.pi) / 2, abs=0.05)


def test_collision_detector_is_injectable():
  def no_collisions(particles):
    return iter(())

  engine = make_engine(particle_count=100, seed=1, collision_detector=no_collisions)
  for _ in range(300):
    engine.step(dt)

  assert engine.collisions == 0


def test_naive_detector_yields_overlapping_pairs():
  from gas.particle import Particle

  overlapping = [Particle(0, 0, 0, 0, 1.0, 1.0), Particle(0.5, 0, 0, 0, 1.0, 1.0)]
  apart = [Particle(0, 0, 0, 0, 1.0, 1.0), Particle(50, 0, 0, 0, 1.0, 1.0)]

  assert len(list(naive_collision_detection(overlapping))) == 1
  assert len(list(naive_collision_detection(apart))) == 0
