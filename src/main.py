import re
from typing import Iterable

import unidecode
import pipe

import service
import model
import config

SEARCH_PATTERN = re.compile(config.config["event"]["search"]["re"], re.IGNORECASE)


def classify_by_type(
    events: Iterable[model.CalendarEvent],
) -> dict[str, Iterable[model.CalendarEventMetaData]]:
    classified_events = (
        events
        | pipe.map(extract_metadata)
        | pipe.groupby(lambda eventMeta: eventMeta.type)
    )
    return {key: value for key, value in classified_events}


def main():
    from pprint import pprint

    events = classify_by_type(service.get_past_year_events())

    pprint(events)


def extract_metadata(event: model.CalendarEvent) -> model.CalendarEventMetaData:
    def normalize_summary(summary: str) -> str:
        return unidecode.unidecode(summary).lower()

    def extract(
        normalized_summary: str, group_name: str, default: str | None = None
    ) -> str | None:
        match = SEARCH_PATTERN.fullmatch(normalized_summary)
        if match is None:
            return default
        value = match.group(group_name)
        if value is None:
            return default
        return value.strip()

    normalized_summary = normalize_summary(event.summary)
    type = extract(
        normalized_summary,
        group_name=config.config["event"]["search"]["type_group"],
        default=model.CalendarEventMetaData.UNKNOWN_TYPE,
    )
    assert type is not None
    assigned_person = extract(
        normalized_summary,
        group_name=config.config["event"]["search"]["assigned_person_group"],
    )
    return model.CalendarEventMetaData(event, normalized_summary, type, assigned_person)


if __name__ == "__main__":
    main()
