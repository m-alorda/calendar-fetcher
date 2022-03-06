import dataclasses
import datetime
from typing import Collection, Iterable, Iterator

import jinja2
import pipe

import config
import model


@dataclasses.dataclass(frozen=True)
class EventReportData:
    type: model.EventType
    readable_name: str
    current_progress: int
    annual_minimum: int
    dates: Iterator[datetime.date]


@dataclasses.dataclass(frozen=True)
class ReportData:
    current_date: datetime.date
    events: Iterable[EventReportData]


def _create_report_data(
    events_dict: dict[model.EventType, Iterable[model.CalendarEventMetaData]]
) -> ReportData:
    events: Collection[EventReportData] = list()
    for event_type, event_type_data in config.config["event"]["types"].items():
        events_data = tuple(events_dict.get(event_type, tuple()))
        events.append(
            EventReportData(
                type=event_type,
                readable_name=event_type_data["readable_name"],
                current_progress=len(events_data),
                annual_minimum=event_type_data["annual_minimum"],
                dates=events_data | pipe.map(lambda event: event.data.start.date()),
            )
        )
    return ReportData(current_date=datetime.date.today(), events=events)


def _generate_rendered_report_lines(data: ReportData) -> Iterator[str]:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(config.PROJECT_DIR / "resources"),
        autoescape=jinja2.select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("report.html")
    yield from template.generate(data=data)


def generate_report(
    events_dict: dict[model.EventType, Iterable[model.CalendarEventMetaData]],
) -> None:
    data = _create_report_data(events_dict)
    dest_dir = config.PROJECT_DIR / "reports"
    dest_dir.mkdir()
    dest_file = dest_dir / f"report-{data.current_date}.html"
    with dest_file.open("w") as f:
        for line in _generate_rendered_report_lines(data):
            f.write(line)
