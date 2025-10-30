# Settlements Json Generator

Downloads data from https://docs.google.com/spreadsheets/d/1myQi-Y6-asM3UkoqUpDEAJSPvYiaOhx-oy7UthgweUk and generates a corresponding CivSettlements.json file

## Github Actions

This script is called automatically by the github action ``generate_settlements.yml`` which runs when a workflow run is triggered.

## Install Locally

### Using UV

1. Install uv ``pip install uv``
2. Choose the generate_civ_settlements directory ``cd .github/scripts/generate_civ_settlements``
3. Install the dependencies script ``uv sync``
4. Run the script ``uv run main.py``

A file named CivMCSettlements.json was generated in your working directory.
