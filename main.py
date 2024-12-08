from Game import Game
from pyinstrument import Profiler

def main():
    game = Game()
    game.run()

if __name__ == "__main__": 
    main()

    # Finally, exit the program
    import sys
    sys.exit()