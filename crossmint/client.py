import os
from collections.abc import Callable
from types import TracebackType
from typing import Any

import requests
from dotenv import load_dotenv
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from crossmint.entities import Cometh, Polyanet, Soloon
from crossmint.urls import COMETHS_ENDPOINT, MAP_ENDPOINT, MEGAVERSE_URL, POLYANETS_ENDPOINT, SOLOONS_ENDPOINT


class MegaverseClient:
    retry_on_rate_limit: Callable = retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
    )

    def __init__(self, base_url: str = MEGAVERSE_URL, candidate_id: str | None = None) -> None:
        if not candidate_id:
            load_dotenv()

        self.base_url = base_url.rstrip("/")
        self.candidate_id = candidate_id or os.getenv("CANDIDATE_ID")
        self._default_data = {"candidateId": self.candidate_id}
        self.client = requests.Session()

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.client.close()
        return None

    def __repr__(self) -> str:
        return f"MegaverseClient(base_url='{self.base_url}', candidate_id='****')"

    def _make_request_data(self, **kwargs: Any) -> dict:
        return {**self._default_data, **kwargs}

    def get_goal_map(self) -> dict:
        response = self.client.get(f"{self.base_url}/{MAP_ENDPOINT}/{self.candidate_id}/goal")
        response.raise_for_status()
        goal_map: dict = response.json()
        return goal_map

    @retry_on_rate_limit
    def create_polyanet(self, polyanet: Polyanet) -> None:
        response = self.client.post(
            f"{self.base_url}/{POLYANETS_ENDPOINT}",
            json=self._make_request_data(
                row=polyanet.position.row,
                column=polyanet.position.column,
            ),
        )
        response.raise_for_status()

    @retry_on_rate_limit
    def delete_polyanet(self, polyanet: Polyanet) -> None:
        response = self.client.delete(
            f"{self.base_url}/{POLYANETS_ENDPOINT}",
            json=self._make_request_data(
                row=polyanet.position.row,
                column=polyanet.position.column,
            ),
        )
        response.raise_for_status()

    @retry_on_rate_limit
    def create_soloon(self, soloon: Soloon) -> None:
        response = self.client.post(
            f"{self.base_url}/{SOLOONS_ENDPOINT}",
            json=self._make_request_data(
                row=soloon.position.row,
                column=soloon.position.column,
                color=soloon.color,
            ),
        )
        response.raise_for_status()

    @retry_on_rate_limit
    def delete_soloon(self, soloon: Soloon) -> None:
        response = self.client.delete(
            f"{self.base_url}/{SOLOONS_ENDPOINT}",
            json=self._make_request_data(
                row=soloon.position.row,
                column=soloon.position.column,
            ),
        )
        response.raise_for_status()

    @retry_on_rate_limit
    def create_cometh(self, cometh: Cometh) -> None:
        response = self.client.post(
            f"{self.base_url}/{COMETHS_ENDPOINT}",
            json=self._make_request_data(
                row=cometh.position.row,
                column=cometh.position.column,
                direction=cometh.direction,
            ),
        )
        response.raise_for_status()

    @retry_on_rate_limit
    def delete_cometh(self, cometh: Cometh) -> None:
        response = self.client.delete(
            f"{self.base_url}/{COMETHS_ENDPOINT}",
            json=self._make_request_data(
                row=cometh.position.row,
                column=cometh.position.column,
            ),
        )
        response.raise_for_status()
