# cocktail-api

Python api server for the Cocktail App, built with FastAPI and SuperTokens.

## Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [SuperTokens](https://supertokens.com/) (passwordless authentication)

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env.dev` file with the following variables:
   ```
   API_DOMAIN=
   WEBSITE_DOMAIN=
   SUPERTOKENS_CONNECTION_URI=
   SUPERTOKENS_API_KEY=
   ```
3. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

## Copyright and Licensing

Copyright (c) 2026 Dan Howard
Licensed under the MIT license.
