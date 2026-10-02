from typing import List
from .particle import Particle


class Box:
  """Container for the particles. It owns the collection and keeps every
  particle inside its boundaries by reflecting the ones that cross a wall.
  Coordinates are centred on the box: x plane: (-width/2, width/2) and
  y plane: (-height/2, height/2)."""

  def __init__(self, width: float, height: float):
    if width <= 0 or height <= 0:
      raise ValueError(
        f"box dimensions must be positive, current dimensions: width={width}, height={height}"
      )

    self.width = width
    self.height = height
    self.particles = []

  def add_particles(self, particles: List[Particle]):
    """Add particles to the box."""
    max_radius = min(self.width, self.height) / 2

    for particle in particles:
      if particle.radius >= max_radius:
        raise ValueError(
          f"particle radius {particle.radius} does not fit in a "
          f"{self.width}x{self.height} box, it must be smaller than {max_radius}"
        )

    self.particles.extend(particles)

  def check_boundaries(self):
    for particle in self.particles:
      if particle.x + particle.radius > self.width / 2:
        particle.x = self.width / 2 - particle.radius
        particle.vx = -particle.vx
      elif particle.x - particle.radius < - self.width / 2:
        particle.x = - self.width / 2 + particle.radius
        particle.vx = -particle.vx

      if particle.y + particle.radius > self.height / 2:
        particle.y = self.height / 2 - particle.radius
        particle.vy = -particle.vy
      elif particle.y - particle.radius < - self.height / 2:
        particle.y = - self.height / 2 + particle.radius
        particle.vy = -particle.vy