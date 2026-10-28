from typing import Callable, Iterable
from .box import Box
from .particle import Particle
import random


CollisionDetector = Callable[[list[Particle]], Iterable[tuple[Particle, Particle]]]


def naive_collision_detection(particles):
  """Yield every overlapping pair. O(n^2), clear but slow for large counts."""
  for i in range(len(particles)):
    first = particles[i]
    for j in range(i + 1, len(particles)):
      second = particles[j]
      if first.overlaps(second):
        yield first, second


class Engine:
  """Advance a set of particles inside a box, one time step at a time."""

  def __init__(
    self,
    box: Box,
    particle_count: int = 250,
    particle_initial_speed: float = 100.0,
    particle_mass: float = 1.0,
    seed: int = 123,
    collision_detector: CollisionDetector = naive_collision_detection,
  ):
    self.box = box
    self.particle_count = particle_count
    self.particle_initial_speed = particle_initial_speed
    self.particle_mass = particle_mass
    self.seed = seed
    self.collision_detector = collision_detector
    self.collisions = 0
    self.time = 0.0

    self.rng = random.Random(seed)
    self.box.add_particles(self._spawn_beam())

  def _spawn_beam(self):
    """Build the initial particles with one speed, one direction but at random places.
    Every particle shares the same velocity, so the system starts maximally
    out of equilibrium."""
    max_radius = self.box.particle_max_radius
    half_width = self.box.width / 2 - max_radius
    half_height = self.box.height / 2 - max_radius

    return [
      Particle(
        x=self.rng.uniform(-half_width, half_width),
        y=self.rng.uniform(-half_height, half_height),
        vx=self.particle_initial_speed,
        vy=0.0,
        radius=max_radius,
        mass=self.particle_mass,
      )
      for _ in range(self.particle_count)
    ]

  def step(self, dt: float) -> None:
    """Advance the simulation by dt seconds."""
    for particle in self.box.particles:
      particle.move(dt)

    self.box.check_boundaries()

    for first, second in self.collision_detector(self.box.particles):
      if first.resolve_collision(second):
        self.collisions += 1

    self.time += dt
