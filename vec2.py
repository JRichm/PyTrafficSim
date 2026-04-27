'''copied from another project'''

from math import sqrt


class Vector2:
    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y


    @property
    def x(self) -> float:
        return self._x
    
    
    @property
    def y(self) -> float:
        return self._y
    

    def __eq__(self, other: "Vector2") -> bool:
        return self.x == other.x and self.y == other.y


    def __sub__(self, other: "Vector2") -> "Vector2":
        return Vector2(
            self.x - other.x,
            self.y - other.y
        )
    

    def __add__(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x + other.x, self.y + other.y)


    def __mul__(self, scalar: float) -> "Vector2":
        return Vector2(self.x * scalar, self.y * scalar)


    def __truediv__(self, divisor: float) -> "Vector2":
        return Vector2(self.x / divisor, self.y / divisor)


    @ property
    def magnitude(self) -> float:
        return sqrt(self.x**2 + self.y**2)


    @property
    def normalized(self) -> "Vector2":
        mag = self.magnitude

        if mag == 0:
            return Vector2(0, 0)
        
        return Vector2(
            self.x / mag,
            self.y / mag
        )


    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"
    
    
    @classmethod
    def zero(cls) -> "Vector2":
        return cls(0, 0)
    
    
    @classmethod
    def up(cls) -> "Vector2":
        return cls(0, 1)
    
    
    @classmethod
    def down(cls) -> "Vector2":
        return cls(0, -1)
    
    
    @classmethod
    def left(cls) -> "Vector2":
        return cls(-1, 0)
    
    
    @classmethod
    def right(cls) -> "Vector2":
        return cls(1, 0)
    
Vector2.zero = Vector2.zero()
Vector2.up = Vector2.up()
Vector2.down = Vector2.down()
Vector2.left = Vector2.left()
Vector2.right = Vector2.right()