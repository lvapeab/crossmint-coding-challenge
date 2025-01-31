from crossmint.client import MegaverseClient
from crossmint.megaverse import Megaverse


def solve() -> None:
    client = MegaverseClient()
    current_megaverse = Megaverse(astral_objects={}, client=client)
    goal_megaverse = Megaverse(astral_objects={}, client=client)
    goal = client.get_goal_map()
    goal_megaverse.load_goal(goal["goal"])
    current_megaverse.convert(goal_megaverse)
    return


if __name__ == "__main__":
    solve()
