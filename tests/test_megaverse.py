from unittest.mock import Mock

import pytest

from crossmint.entities import AstralObject, Cometh, ComethDirection, Polyanet, Position, Soloon, SoloonColor
from crossmint.megaverse import Megaverse, MegaverseClient


class MockMegaverseClient(MegaverseClient):
    def __init__(self) -> None:
        self.create_polyanet = Mock()
        self.create_soloon = Mock()
        self.create_cometh = Mock()
        self.delete_polyanet = Mock()
        self.delete_soloon = Mock()
        self.delete_cometh = Mock()


class TestMegaverse:
    @pytest.fixture
    def client(self) -> MockMegaverseClient:
        return MockMegaverseClient()

    @pytest.fixture
    def empty_megaverse(self, client: MockMegaverseClient) -> Megaverse:
        return Megaverse(astral_objects={}, client=client)

    @pytest.fixture
    def sample_goal(self) -> list[list[str]]:
        return [
            ["SPACE", "POLYANET", "SPACE"],
            ["WHITE_SOLOON", "SPACE", "UP_COMETH"],
            ["SPACE", "BLUE_SOLOON", "SPACE"],
        ]

    def test_load_goal_empty(self, empty_megaverse: Megaverse) -> None:
        empty_megaverse.load_goal([])
        assert empty_megaverse.astral_objects == {}

    def test_load_goal(self, empty_megaverse: Megaverse, sample_goal: list[list[str]]) -> None:
        empty_megaverse.load_goal(sample_goal)

        expected_objects = {
            Position(row=0, column=1): Polyanet(position=Position(row=0, column=1)),
            Position(row=1, column=0): Soloon(position=Position(row=1, column=0), color=SoloonColor.WHITE),
            Position(row=1, column=2): Cometh(position=Position(row=1, column=2), direction=ComethDirection.UP),
            Position(row=2, column=1): Soloon(position=Position(row=2, column=1), color=SoloonColor.BLUE),
        }

        assert empty_megaverse.astral_objects == expected_objects

    def test_load_goal_invalid_format(self, empty_megaverse: Megaverse) -> None:
        with pytest.raises(ValueError, match="Unexpected value from goal"):
            empty_megaverse.load_goal([["INVALID_FORMAT_OBJECT"]])

    def test_create_polyanet(self, empty_megaverse: Megaverse) -> None:
        polyanet = Polyanet(position=Position(row=0, column=0))
        result = empty_megaverse._create_astral_object(polyanet)

        empty_megaverse.client.create_polyanet.assert_called_once_with(polyanet)
        assert result == polyanet

    def test_create_soloon(self, empty_megaverse: Megaverse) -> None:
        soloon = Soloon(position=Position(row=0, column=0), color=SoloonColor.WHITE)
        result = empty_megaverse._create_astral_object(soloon)

        empty_megaverse.client.create_soloon.assert_called_once_with(soloon)
        assert result == soloon

    def test_create_cometh(self, empty_megaverse: Megaverse) -> None:
        cometh = Cometh(position=Position(row=0, column=0), direction=ComethDirection.UP)
        result = empty_megaverse._create_astral_object(cometh)

        empty_megaverse.client.create_cometh.assert_called_once_with(cometh)
        assert result == cometh

    def test_create_invalid_object(self, empty_megaverse: Megaverse) -> None:
        mock_object = Mock(spec=AstralObject)
        type(mock_object).type = Mock(return_value="INVALID")

        with pytest.raises(ValueError, match="Unhandled astral object type"):
            empty_megaverse._create_astral_object(mock_object)

    def test_delete_polyanet(self, empty_megaverse: Megaverse) -> None:
        polyanet = Polyanet(position=Position(row=0, column=0))
        result = empty_megaverse._delete_astral_object(polyanet)

        empty_megaverse.client.delete_polyanet.assert_called_once_with(polyanet)
        assert result == polyanet

    def test_delete_soloon(self, empty_megaverse: Megaverse) -> None:
        soloon = Soloon(position=Position(row=0, column=0), color=SoloonColor.WHITE)
        result = empty_megaverse._delete_astral_object(soloon)

        empty_megaverse.client.delete_soloon.assert_called_once_with(soloon)
        assert result == soloon

    def test_delete_cometh(self, empty_megaverse: Megaverse) -> None:
        cometh = Cometh(position=Position(row=0, column=0), direction=ComethDirection.UP)
        result = empty_megaverse._delete_astral_object(cometh)

        empty_megaverse.client.delete_cometh.assert_called_once_with(cometh)
        assert result == cometh

    def test_delete_invalid_object(self, empty_megaverse: Megaverse) -> None:
        mock_object = Mock(spec=AstralObject)
        type(mock_object).type = Mock(return_value="INVALID")

        with pytest.raises(ValueError, match="Unhandled astral object type"):
            empty_megaverse._delete_astral_object(mock_object)

    def test_convert_empty_to_populated(self, client: MockMegaverseClient) -> None:
        empty_megaverse = Megaverse(astral_objects={}, client=client)
        goal_objects: dict = {Position(row=0, column=0): Polyanet(position=Position(row=0, column=0))}
        goal_megaverse = Megaverse(astral_objects=goal_objects, client=MockMegaverseClient())

        empty_megaverse.convert(goal_megaverse)

        client.create_polyanet.assert_called_once()
        assert empty_megaverse.astral_objects == goal_objects

    def test_convert_populated_to_empty(self, client: MockMegaverseClient) -> None:
        initial_objects: dict = {Position(row=0, column=0): Polyanet(position=Position(row=0, column=0))}
        megaverse = Megaverse(astral_objects=initial_objects, client=client)
        goal_megaverse = Megaverse(astral_objects={}, client=MockMegaverseClient())

        megaverse.convert(goal_megaverse)

        client.delete_polyanet.assert_called_once()
        assert megaverse.astral_objects == {}

    def test_convert_replace_object(self, client: MockMegaverseClient) -> None:
        initial_position = Position(row=0, column=0)
        initial_objects: dict = {initial_position: Polyanet(position=initial_position)}
        megaverse = Megaverse(astral_objects=initial_objects, client=client)

        goal_objects: dict = {initial_position: Soloon(position=initial_position, color=SoloonColor.WHITE)}
        goal_megaverse = Megaverse(astral_objects=goal_objects, client=MockMegaverseClient())

        megaverse.convert(goal_megaverse)

        client.delete_polyanet.assert_called_once()
        client.create_soloon.assert_called_once()
        assert megaverse.astral_objects == goal_objects
