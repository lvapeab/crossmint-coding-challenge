# Crossmint's coding challenge

Crossmint's coding challenge: Build a Megaverse with a particular shape using the Megaverse Creator API. 

As an overview, I resolved it as follows:

1. Create a client to interact with the API. 
2. Define a "Megaverse" object: A data structure containing all elements from the Megaverse (not including the Space).
3. This object has a "convert" functionality: Given a goal Megaverse, the current Megaverse can be transformed into that one. Transformation consists in 3 steps:
   1. Deleting non-null objects in the current Megaverse that are null in the goal. Here null means "SPACE".
   2. Adding elements from the goal Megaverse in the empty positions of the current one.
   3. Checking that for the remaining non-null positions, the objects are the same. If not, transform the current object into the one defined by the goal.
4. With these, it is very simple to transform a Megaverse into another. So we read the goal Megaverse from the API and transform the current one into the goal.



## Installation and usage

Installation, via poetry:

```shell
pipx install poetry
poetry install
poetry run solve
```

Define the `CANDIDATE_ID` as a environment variable or add it to the `.env` file. 

Run:
```shell
poetry run solve
```


Run linting (ruff + isort + mypy):
```shell
poetry run lint
```

Run tests with coverage:

```shell
poetry run pytest --cov=crossmint
```

## Structure

```
crossmint-coding-challenge/
├── commands/         # CLI commands
├── crossmint/        # Main package
│   ├── client.py     # API client implementation
│   ├── entities.py   # Domain models
│   ├── megaverse.py  # Core logic
│   └── urls.py       # API endpoints
├── scripts/          # Development utilities
├── tests/            # Test suite
└── pyproject.toml    # Project configuration
```

