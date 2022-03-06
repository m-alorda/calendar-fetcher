import dataclasses
import datetime
from typing import ClassVar, TypeAlias

import dataclasses_json
import dateutil.parser

EventType: TypeAlias = str


def _create_datetime_field() -> datetime.datetime:
    def datetime_encoder(date: datetime.datetime):
        return date.isoformat() + "Z"

    def datetime_decoder(date_obj: dict | str):
        return dateutil.parser.parse(
            date_obj["dateTime"] if isinstance(date_obj, dict) else date_obj
        )

    return dataclasses.field(
        metadata=dataclasses_json.config(
            encoder=datetime_encoder,
            decoder=datetime_decoder,
        ),
    )


@dataclasses_json.dataclass_json(
    letter_case=dataclasses_json.LetterCase.CAMEL,
    undefined=dataclasses_json.Undefined.EXCLUDE,
)
@dataclasses.dataclass(frozen=True)
class CalendarEvent(dataclasses_json.DataClassJsonMixin):
    id: str
    summary: str
    status: str
    event_type: str
    etag: str
    kind: str
    iCalUID: str
    html_link: str
    start: datetime.datetime = _create_datetime_field()
    end: datetime.datetime = _create_datetime_field()
    created: datetime.datetime = _create_datetime_field()
    updated: datetime.datetime = _create_datetime_field()
    location: str | None = None
    recurring_event_id: str | None = None


@dataclasses.dataclass(frozen=True)
class CalendarEventMetaData:
    UNKNOWN_TYPE: ClassVar[EventType] = "unknown"

    data: CalendarEvent
    normalized_summary: str
    type: EventType = UNKNOWN_TYPE
    assigned_person: str | None = None
