import dataclasses

import unidecode

import service
import model


def main():
    from pprint import pprint

    events = map(
        normalize_event,
        service.get_past_year_events(),
    )

    pprint(list(events))


def normalize_event(event: model.CalendarEvent) -> model.CalendarEvent:
    def _normalize_summary(summary: str) -> str:
        return unidecode.unidecode(summary).lower()

    return dataclasses.replace(event, summary=_normalize_summary(event.summary))


if __name__ == "__main__":
    main()
