import dataclasses
import datetime
from pathlib import Path
from typing import Collection, Iterable, Iterator
import uuid

import jinja2
import pipe
import weasyprint

import config
import model


@dataclasses.dataclass(frozen=True)
class EventReportData:
    type: model.EventType
    readable_name: str
    current_progress: int
    annual_minimum: int
    dates: tuple[datetime.date, ...]


@dataclasses.dataclass(frozen=True)
class UnknownEventReportData:
    summary: str
    date: datetime.date


@dataclasses.dataclass(frozen=True)
class ReportData:
    current_date: datetime.date
    events: tuple[EventReportData, ...]
    unknown_events: tuple[UnknownEventReportData, ...]


def _create_report_data_events(
    events_dict: dict[model.EventType, Iterable[model.CalendarEventMetaData]]
) -> tuple[EventReportData, ...]:
    events: Collection[EventReportData] = list()
    for event_type, event_type_data in config.config["event"]["types"].items():
        events_data = tuple(events_dict.get(event_type, tuple()))
        events.append(
            EventReportData(
                type=event_type,
                readable_name=event_type_data["readable_name"],
                current_progress=len(events_data),
                annual_minimum=event_type_data["annual_minimum"],
                dates=tuple(
                    events_data | pipe.map(lambda event: event.data.start.date())
                ),
            )
        )
    return tuple(events)


def _create_report_data_unknown_events(
    events_dict: dict[model.EventType, Iterable[model.CalendarEventMetaData]]
) -> tuple[UnknownEventReportData]:
    unknown_events: Collection[UnknownEventReportData] = list()
    if model.CalendarEventMetaData.UNKNOWN_TYPE not in events_dict:
        return tuple()
    for event in events_dict[model.CalendarEventMetaData.UNKNOWN_TYPE]:
        unknown_events.append(
            UnknownEventReportData(event.data.summary, event.data.start.date())
        )
    return tuple(unknown_events)


def _create_report_data(
    events_dict: dict[model.EventType, Iterable[model.CalendarEventMetaData]]
) -> ReportData:

    return ReportData(
        current_date=datetime.date.today(),
        events=_create_report_data_events(events_dict),
        unknown_events=_create_report_data_unknown_events(events_dict),
    )


def _generate_rendered_report_lines(data: ReportData) -> Iterator[str]:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(config.RESOURCES_DIR),
        autoescape=jinja2.select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("report.html")
    yield from template.generate(data=data)


def _get_report_file_path(filename: str, extension: str) -> Path:
    """Generates a file_path with the given filename and extension, ensuring the file does not already exist

    Args:
        filename: The desired filename
        extension: The file extension. E.g. `.html`

    Returns:
        A non existent path starting with `filename` and ending with `extension`
    """
    dest_dir = config.PROJECT_DIR / "reports"
    dest_dir.mkdir(exist_ok=True)

    dest_file = dest_dir / f"{filename}{extension}"
    while dest_file.exists():
        dest_file = dest_dir / f"{filename}_{uuid.uuid4()}{extension}"

    return dest_file


def generate_html_report(
    events_dict: dict[model.EventType, Iterable[model.CalendarEventMetaData]],
) -> Path:
    data = _create_report_data(events_dict)

    dest_file = _get_report_file_path(
        filename=f"report-{data.current_date}",
        extension=".html",
    )

    with dest_file.open("w", encoding="utf-8") as f:
        for line in _generate_rendered_report_lines(data):
            f.write(line)

    return dest_file


def generate_report(
    events_dict: dict[model.EventType, Iterable[model.CalendarEventMetaData]],
) -> Path:
    tmp_html_report_path = generate_html_report(events_dict)

    pdf_report_path = _get_report_file_path(
        filename=tmp_html_report_path.stem,
        extension=".pdf",
    )

    html = weasyprint.HTML(filename=tmp_html_report_path)
    html.write_pdf(target=pdf_report_path)
    tmp_html_report_path.unlink()
    
    return tmp_html_report_path
