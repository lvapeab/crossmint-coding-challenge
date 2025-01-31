import pytest
from pydantic import ValidationError

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


class TestPosition:
    def test_position_valid_creation(self) -> None:
        position = Position(row=1, column=2)
        assert position.row == 1
        assert position.column == 2

    def test_position_negative_values(self) -> None:
        with pytest.raises(ValidationError):
            Position(row=-1, column=0)
        with pytest.raises(ValidationError):
            Position(row=0, column=-1)


class TestAstralObject:
    def test_equality(self) -> None:
        obj1 = AstralObject(
            type=AstralObjectType.SPACE,
            position=Position(row=0, column=0),
        )
        obj2 = AstralObject(
            type=AstralObjectType.SPACE,
            position=Position(row=0, column=0),
        )
        obj3 = AstralObject(
            type=AstralObjectType.POLYANET,
            position=Position(row=0, column=0),
        )

        assert obj1 == obj2
        assert obj1 != obj3
        assert obj1 != 3

    def test_hash(self) -> None:
        obj1 = AstralObject(
            type=AstralObjectType.SPACE,
            position=Position(row=0, column=0),
        )
        obj2 = AstralObject(
            type=AstralObjectType.SPACE,
            position=Position(row=0, column=0),
        )

        assert hash(obj1) == hash(obj2)
        assert len({obj1, obj2}) == 1


class TestPolyanet:
    def test_polyanet_creation(self) -> None:
        polyanet = Polyanet(position=Position(row=1, column=1))
        assert polyanet.type == AstralObjectType.POLYANET
        assert isinstance(polyanet, AstralObject)

    def test_polyanet_type_immutable(self) -> None:
        polyanet = Polyanet(position=Position(row=1, column=1))
        with pytest.raises(ValidationError):
            polyanet.type = AstralObjectType.SPACE


class TestSoloon:
    def test_soloon_creation(self) -> None:
        soloon = Soloon(
            position=Position(row=1, column=1),
            color=SoloonColor.BLUE,
        )
        assert soloon.type == AstralObjectType.SOLOON
        assert soloon.color == SoloonColor.BLUE

    def test_soloon_equality(self) -> None:
        soloon1 = Soloon(
            position=Position(row=1, column=1),
            color=SoloonColor.BLUE,
        )
        soloon2 = Soloon(
            position=Position(row=1, column=1),
            color=SoloonColor.BLUE,
        )
        soloon3 = Soloon(
            position=Position(row=1, column=1),
            color=SoloonColor.RED,
        )

        assert soloon1 == soloon2
        assert soloon1 != soloon3


class TestCometh:
    def test_cometh_creation(self) -> None:
        cometh = Cometh(
            position=Position(row=1, column=1),
            direction=ComethDirection.UP,
        )
        assert cometh.type == AstralObjectType.COMETH
        assert cometh.direction == ComethDirection.UP

    def test_cometh_equality(self) -> None:
        cometh1 = Cometh(
            position=Position(row=1, column=1),
            direction=ComethDirection.UP,
        )
        cometh2 = Cometh(
            position=Position(row=1, column=1),
            direction=ComethDirection.UP,
        )
        cometh3 = Cometh(
            position=Position(row=1, column=1),
            direction=ComethDirection.DOWN,
        )

        assert cometh1 == cometh2
        assert cometh1 != cometh3
