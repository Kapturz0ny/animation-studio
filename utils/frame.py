class Frame:
    def __init__(self, number, figures = [], lights = []):
        self.number = number
        self.figures = figures
        self.lights = lights

    def delete_figure(self, index):
        self.figures.pop(index)
    
    def get_figure_items_copies(self):
        to_return = []
        for i in range(len(self.figures)):
            to_return.append(self.figures[i].clone())
        return to_return
    
    def add_figure(self, figure):
        self.figures.append(figure)