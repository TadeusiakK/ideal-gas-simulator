from dataclasses import dataclass
import math


@dataclass
class Particle:
    """Definition of Particle datatype.
    Particle has x and y, velocity in the x and y direction,
    radius and mass"""

    x: float
    y: float
    vx: float
    vy: float
    radius: float
    mass: float

    def move(self, dt: float) -> None:
        """Advance the particle by one time step of length dt."""
        self.x += self.vx * dt
        self.y += self.vy * dt

    def speed(self) -> float:
        """Return the magnitude of the velocity."""
        return math.sqrt(self.vx**2 + self.vy**2)

    def kinetic_energy(self) -> float:
        """Return the kinetic energy of the particle."""
        return 0.5 * self.mass * self.speed() ** 2

    def distance_to(self, other: "Particle") -> float:
        """Return the distance to another particle."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def overlaps(self, other: "Particle") -> bool:
        """Return True if this particle overlaps another one."""
        return self.distance_to(other) < self.radius + other.radius

    def resolve_collision(self, other: "Particle") -> bool:
        """Update the velocities of both particles, assuming an elastic
        two-body collision.

        Only the velocity components along the line joining the two centres
        change; the tangential components are left alone. The impulse comes
        from conservation of momentum and conservation of kinetic energy.

        Returns:
            True if the velocities were updated, False if the particles were
            moving apart already and no impulse was applied.
        """
        distance = self.distance_to(other)

        if distance == 0:
            return False

        normal_x = (other.x - self.x) / distance
        normal_y = (other.y - self.y) / distance

        relative_vx = other.vx - self.vx
        relative_vy = other.vy - self.vy
        relative_v_normal = relative_vx * normal_x + relative_vy * normal_y

        if relative_v_normal > 0:
            return False

        total_mass = self.mass + other.mass
        coefficient = 2 * relative_v_normal / total_mass

        self.vx += coefficient * other.mass * normal_x
        self.vy += coefficient * other.mass * normal_y
        other.vx -= coefficient * self.mass * normal_x
        other.vy -= coefficient * self.mass * normal_y

        return True
