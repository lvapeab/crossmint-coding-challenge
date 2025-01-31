import logging

from pydantic import BaseModel, ConfigDict

from crossmint.client import MegaverseClient
from crossmint.entities import (
    AstralObject,
    AstralObjectType,
    Cometh,
    ComethDirection,
    Polyanet,
    Position,
    Soloon,
    SoloonColor,
)

logger = logging.getLogger(__name__)

MegaverseMap = dict[Position, AstralObject]


class Megaverse(BaseModel):
    astral_objects: MegaverseMap
    client: MegaverseClient
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def load_goal(self, goal: list[list[str]]) -> None:
        astral_objects: MegaverseMap = {}
        if not goal:
            return

        logger.info(f"Loading a goal with size {len(goal)} x {len(goal[0])}")
        for i in range(len(goal)):
            for j in range(len(goal[0])):
                match goal[i][j].split("_"):
                    case [obj]:
                        astral_object_type = obj
                        astral_attr = None
                    case [attr, obj]:
                        astral_object_type = obj
                        astral_attr = attr.lower()
                    case _:
                        raise ValueError(f"Unexpected value from goal: {goal[i][j]}")
                assert astral_object_type is not None
                astral_object = AstralObjectType(astral_object_type)

                if astral_object is AstralObjectType.SPACE:
                    continue

                position = Position(row=i, column=j)

                if astral_object is AstralObjectType.POLYANET:
                    astral_objects[position] = Polyanet(position=position)

                if astral_object is AstralObjectType.SOLOON:
                    assert astral_attr is not None
                    astral_objects[position] = Soloon(position=position, color=SoloonColor(astral_attr))

                if astral_object is AstralObjectType.COMETH:
                    assert astral_attr is not None
                    astral_objects[position] = Cometh(position=position, direction=ComethDirection(astral_attr))
            self.astral_objects = astral_objects
        logger.info("Loading done")
        return

    def _create_astral_object(self, astral_object: AstralObject) -> AstralObject:
        if astral_object.type is AstralObjectType.POLYANET:
            assert isinstance(astral_object, Polyanet)
            self.client.create_polyanet(astral_object)
            return astral_object
        if astral_object.type is AstralObjectType.SOLOON:
            assert isinstance(astral_object, Soloon)
            self.client.create_soloon(astral_object)
            return astral_object
        if astral_object.type is AstralObjectType.COMETH:
            assert isinstance(astral_object, Cometh)
            self.client.create_cometh(astral_object)
            return astral_object
        raise ValueError(f"Unhandled astral object type: {astral_object}")

    def _delete_astral_object(self, astral_object: AstralObject) -> AstralObject:
        if astral_object.type is AstralObjectType.POLYANET:
            assert isinstance(astral_object, Polyanet)
            self.client.delete_polyanet(astral_object)
            return astral_object
        if astral_object.type is AstralObjectType.SOLOON:
            assert isinstance(astral_object, Soloon)
            self.client.delete_soloon(astral_object)
            return astral_object
        if astral_object.type is AstralObjectType.COMETH:
            assert isinstance(astral_object, Cometh)
            self.client.delete_cometh(astral_object)
            return astral_object
        raise ValueError(f"Unhandled astral object type: {astral_object}")

    def convert(self, goal_megaverse: "Megaverse") -> None:
        current_positions = set(self.astral_objects.keys())
        goal_positions = set(goal_megaverse.astral_objects.keys())

        positions_to_create = goal_positions - current_positions
        positions_to_delete = current_positions - goal_positions
        positions_to_check = current_positions & goal_positions
        logger.info(
            f"Creating {len(positions_to_create)} astral objects. "
            f"Deleting {len(positions_to_delete)} astral objects. "
            f"Checking {len(positions_to_check)} positions."
        )
        for position in positions_to_delete:
            self._delete_astral_object(self.astral_objects[position])

        for position in positions_to_create:
            self._create_astral_object(goal_megaverse.astral_objects[position])

        for position in positions_to_check:
            current_object = self.astral_objects[position]
            goal_object = goal_megaverse.astral_objects[position]
            if current_object != goal_object:
                self._delete_astral_object(current_object)
                self._create_astral_object(goal_object)
        self.astral_objects = goal_megaverse.astral_objects
        logger.info("Done")
        return
