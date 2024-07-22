import matplotlib.pyplot as plt
from IPython import display
import numpy as np

class RealTimePlotter:
    def __init__(self):
        plt.ion()  # Turn on interactive mode for real-time plotting
        self.scores = []
        self.mean_scores = []

    def plot(self):
        display.clear_output(wait=True)
        display.display(plt.gcf())
        plt.clf()
        plt.title('Training...')
        plt.xlabel('Number of Games')
        plt.ylabel('Score')
        plt.plot(self.scores, label='Scores')
        plt.plot(self.mean_scores, label='Mean Scores', color='orange')
        plt.ylim(ymin=0)
        plt.text(len(self.scores)-1, self.scores[-1], str(self.scores[-1]))
        plt.text(len(self.mean_scores)-1, self.mean_scores[-1], str(self.mean_scores[-1]))
        plt.legend()
        plt.show(block=False)
        plt.pause(0.1)

    def update(self, score):
        self.scores.append(score)
        mean_score = np.mean(self.scores[-100:])  # Calculate mean of last 100 scores
        self.mean_scores.append(mean_score)
        self.plot()

    def close(self):
        plt.ioff()  # Turn off interactive mode
        plt.show()  # Ensure final plot is displayed
