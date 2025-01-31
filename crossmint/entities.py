from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class AstralObjectType(StrEnum):
    SPACE = "SPACE"
    POLYANET = "POLYANET"
    SOLOON = "SOLOON"
    COMETH = "COMETH"


class SoloonColor(StrEnum):
    BLUE = "blue"
    RED = "red"
    PURPLE = "purple"
    WHITE = "white"


class ComethDirection(StrEnum):
    UP = "up"
    DOWN = "down"
    RIGHT = "right"
    LEFT = "left"


class Position(BaseModel):
    row: int = Field(..., ge=0)
    column: int = Field(..., ge=0)
    model_config = ConfigDict(
        frozen=True,
        validate_default=True,
    )


class AstralObject(BaseModel):
    type: AstralObjectType
    position: Position
    model_config = ConfigDict(
        frozen=True,
        validate_default=True,
    )

    def __hash__(self) -> int:
        fields_values = tuple(getattr(self, field) for field in self.model_fields)
        return hash((type(self),) + fields_values)


class Polyanet(AstralObject):
    type: AstralObjectType = Field(default=AstralObjectType.POLYANET, frozen=True)


class Soloon(AstralObject):
    type: AstralObjectType = Field(default=AstralObjectType.SOLOON, frozen=True)
    color: SoloonColor


class Cometh(AstralObject):
    type: AstralObjectType = Field(default=AstralObjectType.COMETH, frozen=True)
    direction: ComethDirection
