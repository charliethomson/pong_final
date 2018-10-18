
class Vector2D:
    def __init__(self, x=0, y=0):
        self.x, self.y = x, y
        
    def __repr__(self):
        return f"{self.x}, {self.y}"
    
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)