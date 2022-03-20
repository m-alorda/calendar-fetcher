import re
from typing import Iterable, Iterator
import logging

import unidecode
import pipe

import config
import service
import model
import report


SEARCH_PATTERN = re.compile(config.config["event"]["search"]["re"], re.IGNORECASE)

log = logging.getLogger()


def classify_by_type(
    events: Iterator[model.CalendarEvent],
) -> dict[model.EventType, Iterable[model.CalendarEventMetaData]]:
    log.debug("Classifying events by type")
    classified_events = (
        events
        | pipe.map(extract_metadata)
        | pipe.groupby(lambda eventMeta: eventMeta.type)
    )
    # See <https://stackoverflow.com/a/19589718/13688761> as to why a list has to be created for the group values
    return {key: tuple(value) for key, value in classified_events}


def extract_metadata(event: model.CalendarEvent) -> model.CalendarEventMetaData:
    log.debug("Extracting metadata from %s", event)

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
    log.debug("Normalized summay is '%s'", normalized_summary)

    type = extract(
        normalized_summary,
        group_name=config.config["event"]["search"]["type_group"],
        default=model.CalendarEventMetaData.UNKNOWN_TYPE,
    )
    assert type is not None
    type = type.replace(" ", "_")
    log.debug("Event type is '%s'", type)

    assigned_person = extract(
        normalized_summary,
        group_name=config.config["event"]["search"]["assigned_person_group"],
    )
    log.debug("Assigned person is '%s'", assigned_person)

    return model.CalendarEventMetaData(event, normalized_summary, type, assigned_person)


def main():
    log.info("Generating a report with past year events")
    events_dict = classify_by_type(service.retrieve_past_year_events())
    generated_report = report.generate_report(events_dict)
    log.info("Generated report: %s", generated_report)


if __name__ == "__main__":
    main()
