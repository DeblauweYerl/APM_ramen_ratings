class Som:
    def __init__(self, getal1, getal2):
        self.getal1 = getal1
        self.getal2 = getal2
        self.som = None

    def __str__(self):
        if self.som is None:
            return f"Som voor getal {self.getal1} en getal {self.getal2} is onbekend"
        else:
            return f"Som voor getal {self.getal1} en getal {self.getal2} is {self.som}"

    def __eq__(self, other):
        return (self.getal1 == other.getal1) and (self.getal2 == other.getal2)


