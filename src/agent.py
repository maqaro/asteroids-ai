import torch
import random
import numpy as np
import torch.nn as nn
import torch.optim as optim
from game import Game
from collections import deque
from plotting import RealTimePlotter

MAX_MEMORY = 100000
BATCH_SIZE = 1000
LR = 0.0001

class LinearQNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(LinearQNet, self).__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = torch.relu(self.linear1(x))
        x = self.linear2(x)
        return x


class QTrainer:
    def __init__(self, model, lr, gamma):
        self.model = model
        self.lr = lr
        self.gamma = gamma
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )

        pred = self.model(state)
        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][torch.argmax(action[idx]).item()] = Q_new

        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()

class Agent:
    def __init__(self):
        self.num_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = LinearQNet(input_size=8, hidden_size=256, output_size=5)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        return game.get_state()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        for state, action, reward, next_state, done in mini_sample:
            self.trainer.train_step(state, action, reward, next_state, done)

    def train_short(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        self.epsilon = 80 - self.num_games
        final_move = [0, 0, 0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 4)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move


def train():
    record = 0
    agent = Agent()
    game = Game()
    plotter = RealTimePlotter()
    num_games = 0

    while True:
        game.handle_events()  # Handle events like closing the window

        old_state = agent.get_state(game)
        final_move = agent.get_action(old_state)
        reward, done, score = game.play_step(final_move)
        new_state = agent.get_state(game)

        agent.train_short(old_state, final_move, reward, new_state, done)
        agent.remember(old_state, final_move, reward, new_state, done)

        if done:
            game.reset()  # Reset the game, but not the score here
            num_games += 1
            agent.num_games += 1
            agent.train_long()
            if score > record:
                record = score
            print(f'Game {num_games} | Score: {score} | Reward: {reward} ')
            plotter.update(score)

        # Check if the game window should be closed
        if not game.running:
            break



if __name__ == '__main__':
    train()
