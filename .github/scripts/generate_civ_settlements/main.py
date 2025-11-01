from requests import get
from csv import DictReader
from io import StringIO
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from collections.abc import Iterator
from json import dumps, loads


class SettlementData(BaseModel):
    # Name,x,z,Nation,Contact,image,image_album,Discord,Web,Wiki,Symbol,Visitors,Zoom Visibility,id,Notes,Nickname
    name: str = Field(alias="Name")
    x: int
    z: int
    nation: str = Field(alias="Nation")
    contact: Optional[str] = Field(None, alias="Contact")
    image: Optional[str] = None
    image_album: Optional[str] = None
    discord: Optional[str] = Field(None, alias="Discord")
    web: Optional[str] = Field(None, alias="Web")
    wiki: Optional[str] = Field(None, alias="Wiki")
    symbol: Optional[str] = Field(None, alias="Symbol")
    visitors: Optional[str] = Field(None, alias="Visitors")
    zoom_visibility: Optional[int] = Field(None, alias="Zoom Visibility")
    id: int = None
    notes: Optional[str] = Field(None, alias="Notes")
    nickname: Optional[str] = Field(None, alias="Nickname")

    @field_validator("*")
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


class StreamArray(list):
    ### Class is used to stream a generator object in json.dumps method. Otherwise I get a TypeError: Object of type generator is not JSON serializable
    def __init__(self, iterator: Iterator):
        self.iterator = iterator

    def __iter__(self):
        return self.iterator

    # according to the comment below
    def __len__(self):
        return 1


def download_sheet() -> Iterator[str]:
    SHEET_ID = "1myQi-Y6-asM3UkoqUpDEAJSPvYiaOhx-oy7UthgweUk"
    SHEET_NAME = "Settlements"

    # Google Sheets CSV export link
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

    response = get(url, stream=True)
    response.raise_for_status()
    return (line.decode('utf-8') for line in response.iter_lines())


def parse_google_sheet_data(file: Iterator[str]) -> Iterator[SettlementData]:
    parsed_count = 0
    parsing_errors = 0
    # Skips the first 5 metadata lines
    for _ in range(5):
        next(file)
    headers = [
        "Name",
        "x",
        "z",
        "Nation",
        "Contact",
        "image",
        "image_album",
        "Discord",
        "Web",
        "Wiki",
        "Symbol",
        "Visitors",
        "Zoom Visibility",
        "id",
        "Notes",
        "Nickname",
    ]
    for row in DictReader(file, fieldnames=headers):
        try:
            yield SettlementData.model_validate(row)
            parsed_count += 1
        except ValueError as e:
            if all(
                str(v) == "" for v in row.values()
            ):  # Ignore entries that are just empty rows
                continue
            print(f"Failed to parse row {row} because of {e}")
            parsing_errors += 1
    print(f"Parsed {parsed_count} entries correctly and {parsing_errors} incorrectly")


def generate_file_contents(features: Iterator[SettlementData]) -> dict:
    with open("settlements_config.json", "r") as settlements_config_file:
        settlement_config = loads(settlements_config_file.read())
        settlement_config["features"] = StreamArray(feature.model_dump(exclude_none=True, by_alias=True) for feature in features)
        return settlement_config


def write_to_output_settlements_file(settlements: Iterator[SettlementData]):
    with open("CivMCSettlements.json", "w+", encoding="utf-8") as output_file:
        output_file.write(
            dumps(
                generate_file_contents(settlements),
                indent=4,
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    write_to_output_settlements_file(parse_google_sheet_data(download_sheet()))
