from unittest.mock import Mock

import pytest
from requests import Response, Session, exceptions
from requests_mock import Mocker
from tenacity import RetryError

from crossmint.client import MegaverseClient
from crossmint.entities import Cometh, ComethDirection, Polyanet, Position, Soloon, SoloonColor
from crossmint.urls import COMETHS_ENDPOINT, MAP_ENDPOINT, MEGAVERSE_URL, POLYANETS_ENDPOINT, SOLOONS_ENDPOINT


@pytest.fixture
def client() -> MegaverseClient:
    return MegaverseClient(candidate_id="test_id")


@pytest.fixture
def mock_success_response() -> Response:
    response = Response()
    response.status_code = 200
    response._content = b'{"ok": true, "message": "Operation completed successfully"}'
    return response


@pytest.fixture
def mock_error_response() -> Response:
    response = Response()
    response.status_code = 400
    response._content = (
        b'{"ok": false, "error": "Bad Request", "message": "Missing parameters. '
        b'The API accepts parameters as JSON, and remember to specify the proper Content-Type"}'
    )
    return response


@pytest.fixture
def mock_goal_map_response() -> Response:
    response = Response()
    response.status_code = 200
    response._content = b'{"goal": [["SPACE", "POLYANET", "SPACE"], ["PURPLE_SOLOON", "SPACE", "DOWN_COMETH"]]}'
    return response


@pytest.fixture
def mock_rate_limit_response() -> Response:
    response = Response()
    response.status_code = 429
    response._content = b'{"ok": false, "error": "Too Many Requests", "message": "Rate limit exceeded"}'
    response.headers["Retry-After"] = "30"
    return response


def test_client_initialization() -> None:
    client = MegaverseClient(candidate_id="test_id")
    assert client.candidate_id == "test_id"
    assert client.base_url == MEGAVERSE_URL


def test_client_initialization_without_candidate_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CANDIDATE_ID", "env_test_id")
    client = MegaverseClient()
    assert client.candidate_id == "env_test_id"


def test_make_request_data(client: MegaverseClient) -> None:
    data = client._make_request_data(test_key="test_value")
    assert data == {"candidateId": "test_id", "test_key": "test_value"}


def test_get_goal_map(client: MegaverseClient, requests_mock: Mocker, mock_goal_map_response: Response) -> None:
    requests_mock.get(
        f"{MEGAVERSE_URL}/{MAP_ENDPOINT}/test_id/goal",
        status_code=mock_goal_map_response.status_code,
        content=mock_goal_map_response._content or b"",
    )

    result = client.get_goal_map()
    assert result == {"goal": [["SPACE", "POLYANET", "SPACE"], ["PURPLE_SOLOON", "SPACE", "DOWN_COMETH"]]}


def test_get_goal_map_fails(client: MegaverseClient, requests_mock: Mocker, mock_error_response: Response) -> None:
    requests_mock.get(
        f"{MEGAVERSE_URL}/{MAP_ENDPOINT}/test_id/goal",
        status_code=mock_error_response.status_code,
        content=mock_error_response._content or b"",
    )

    with pytest.raises(exceptions.HTTPError) as exc_info:
        client.get_goal_map()

    assert exc_info.value.response.status_code == 400


def test_create_polyanet(
    client: MegaverseClient,
    requests_mock: Mocker,
    mock_success_response: Response,
) -> None:
    requests_mock.post(
        f"{MEGAVERSE_URL}/{POLYANETS_ENDPOINT}",
        status_code=mock_success_response.status_code,
        content=mock_success_response._content or b"",
    )

    polyanet = Polyanet(position=Position(row=1, column=2))
    client.create_polyanet(polyanet)

    assert requests_mock.last_request is not None
    assert requests_mock.last_request.json() == {
        "candidateId": "test_id",
        "row": 1,
        "column": 2,
    }


def test_create_soloon(
    client: MegaverseClient,
    requests_mock: Mocker,
    mock_success_response: Response,
) -> None:
    requests_mock.post(
        f"{MEGAVERSE_URL}/{SOLOONS_ENDPOINT}",
        status_code=mock_success_response.status_code,
        content=mock_success_response._content or b"",
    )
    soloon = Soloon(position=Position(row=1, column=2), color=SoloonColor.BLUE)
    client.create_soloon(soloon)

    assert requests_mock.last_request is not None
    assert requests_mock.last_request.json() == {
        "candidateId": "test_id",
        "row": 1,
        "column": 2,
        "color": "blue",
    }


def test_create_cometh(
    client: MegaverseClient,
    requests_mock: Mocker,
    mock_success_response: Response,
) -> None:
    requests_mock.post(
        f"{MEGAVERSE_URL}/{COMETHS_ENDPOINT}",
        status_code=mock_success_response.status_code,
        content=mock_success_response._content or b"",
    )

    cometh = Cometh(position=Position(row=1, column=2), direction=ComethDirection.UP)
    client.create_cometh(cometh)

    assert requests_mock.last_request is not None
    assert requests_mock.last_request.json() == {
        "candidateId": "test_id",
        "row": 1,
        "column": 2,
        "direction": "up",
    }


def test_delete_methods(
    client: MegaverseClient,
    requests_mock: Mocker,
    mock_success_response: Response,
) -> None:
    endpoints = {
        "polyanet": (POLYANETS_ENDPOINT, Polyanet(position=Position(row=1, column=2))),
        "soloon": (SOLOONS_ENDPOINT, Soloon(position=Position(row=3, column=3), color=SoloonColor.BLUE)),
        "cometh": (COMETHS_ENDPOINT, Cometh(position=Position(row=0, column=0), direction=ComethDirection.RIGHT)),
    }

    for entity_type, (endpoint, entity) in endpoints.items():
        requests_mock.delete(
            f"{MEGAVERSE_URL}/{endpoint}",
            status_code=mock_success_response.status_code,
            content=mock_success_response._content or b"",
        )

        delete_method = getattr(client, f"delete_{entity_type}")
        delete_method(entity)
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.json() == {
            "candidateId": "test_id",
            "row": entity.position.row,
            "column": entity.position.column,
        }


def test_retry_on_rate_limit(
    client: MegaverseClient,
    requests_mock: Mocker,
    mock_rate_limit_response: Response,
    mock_success_response: Response,
) -> None:
    requests_mock.post(
        f"{MEGAVERSE_URL}/{POLYANETS_ENDPOINT}",
        [
            {
                "status_code": mock_rate_limit_response.status_code,
                "content": mock_rate_limit_response._content,
                "headers": mock_rate_limit_response.headers,
            },
            {
                "status_code": mock_rate_limit_response.status_code,
                "content": mock_rate_limit_response._content,
                "headers": mock_rate_limit_response.headers,
            },
            {
                "status_code": mock_success_response.status_code,
                "content": mock_success_response._content,
            },
        ],
    )

    polyanet = Polyanet(position=Position(row=1, column=2))
    client.create_polyanet(polyanet)

    assert requests_mock.call_count == 3


def test_retry_on_rate_limit_fails(
    client: MegaverseClient,
    requests_mock: Mocker,
    mock_rate_limit_response: Response,
) -> None:
    requests_mock.post(
        f"{MEGAVERSE_URL}/{POLYANETS_ENDPOINT}",
        [
            {
                "status_code": mock_rate_limit_response.status_code,
                "content": mock_rate_limit_response._content,
                "headers": mock_rate_limit_response.headers,
            },
            {
                "status_code": mock_rate_limit_response.status_code,
                "content": mock_rate_limit_response._content,
                "headers": mock_rate_limit_response.headers,
            },
            {
                "status_code": mock_rate_limit_response.status_code,
                "content": mock_rate_limit_response._content,
                "headers": mock_rate_limit_response.headers,
            },
        ],
    )

    polyanet = Polyanet(position=Position(row=1, column=2))
    with pytest.raises(RetryError):
        client.create_polyanet(polyanet)

    assert requests_mock.call_count == 3


def test_client_exit(client: MegaverseClient) -> None:
    client.client = Mock(spec=Session)
    client.__exit__(None, None, None)
    client.client.close.assert_called_once()
