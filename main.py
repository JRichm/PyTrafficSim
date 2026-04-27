from simulation import TrafficSim

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


if __name__ == "__main__":
    sim = TrafficSim(SCREEN_WIDTH, SCREEN_HEIGHT)
    sim.start()