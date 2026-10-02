import pytest
from gas.particle import Particle
from gas.box import Box
import random as r

box_width = 10
box_height = 10
max_speed = 10
particle_count = 5


def make_box():
  """Return a fresh box so every test starts from empty state."""
  return Box(box_width, box_height)


def make_particles(count=particle_count):
  """Return particles that are guaranteed to fit inside the box."""
  max_radius = min(box_width, box_height) / 4
  return [
    Particle(
      r.uniform(-box_width / 2, box_width / 2),
      r.uniform(-box_height / 2, box_height / 2),
      r.uniform(1, max_speed),
      r.uniform(1, max_speed),
      r.uniform(0.5, max_radius),
      r.randint(1, 10),
    )
    for _ in range(count)
  ]


def test_add_particles():
  box = make_box()
  box.add_particles(make_particles())
  assert len(box.particles) == particle_count


def test_oversized_particle_is_rejected():
  box = make_box()
  oversized = Particle(0, 0, 0, 0, box_width / 2, 1)
  with pytest.raises(ValueError):
    box.add_particles([oversized])


def test_rejected_batch_leaves_box_unchanged():
  box = make_box()
  box.add_particles(make_particles())
  oversized = Particle(0, 0, 0, 0, box_width / 2, 1)
  with pytest.raises(ValueError):
    box.add_particles(make_particles() + [oversized])
  assert len(box.particles) == particle_count


def test_non_positive_dimensions_are_rejected():
  with pytest.raises(ValueError):
    Box(0, box_height)


def test_particles_stay_inside_the_box():
  box = make_box()
  box.add_particles(make_particles())

  for _ in range(2000):
    for particle in box.particles:
      particle.move(1 / 120)
    box.check_boundaries()

  for particle in box.particles:
    assert abs(particle.x) <= box_width / 2 - particle.radius + 1e-9
    assert abs(particle.y) <= box_height / 2 - particle.radius + 1e-9


def test_wall_reflection_flips_velocity():
  box = make_box()
  particle = Particle(box_width / 2 - 0.5, 0.0, 10.0, 0.0, 1.0, 1.0)
  box.add_particles([particle])

  box.check_boundaries()

  assert particle.x == pytest.approx(box_width / 2 - 1.0)
  assert particle.vx == pytest.approx(-10.0)
  assert particle.vy == pytest.approx(0.0)


def test_energy_is_conserved_through_reflections():
  box = make_box()
  box.add_particles(make_particles())

  energy_before = sum(p.kinetic_energy() for p in box.particles)

  for _ in range(2000):
    for particle in box.particles:
      particle.move(1 / 120)
    box.check_boundaries()

  energy_after = sum(p.kinetic_energy() for p in box.particles)

  assert energy_after == pytest.approx(energy_before, rel=1e-12)


def test_equal_masses_exchange_velocities():
  first = Particle(0.0, 0.0, 1.0, 0.0, 1.0, 1.0)
  second = Particle(1.5, 0.0, -1.0, 0.0, 1.0, 1.0)

  assert first.resolve_collision(second) is True
  assert first.vx == pytest.approx(-1.0)
  assert second.vx == pytest.approx(1.0)
