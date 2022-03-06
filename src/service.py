import datetime
from typing import Any, Iterable, Iterator

import googleapiclient.discovery
import google.oauth2.service_account

import model
import config


# If modifying these scopes, delete the file token.json.
_API_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def _get_api_credentials(
    scopes: Iterable[str],
) -> google.oauth2.service_account.Credentials:
    """Get the credentials used to Google Oauth

    Args:
        scopes - A list of the scopes that will be available through
            the returned credentials

    Returns:
        The credentials object used to authenticate
    """
    path_to_creds = config.PROJECT_DIR / "secrets/calendar-fetcher-creds.json"
    return google.oauth2.service_account.Credentials.from_service_account_file(
        path_to_creds,
        scopes=scopes,
    )


def _format_as_zulu_date(date: datetime.datetime) -> str:
    return f"{date.isoformat()}Z"


def _replace_with_first_day_of_the_year(date: datetime.datetime) -> datetime.datetime:
    return date.replace(
        month=1,
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )


def get_past_year_events() -> Iterator[model.CalendarEvent]:
    """Retrieves the events that have taken place since the start of the current year

    Raises:
        googleapiclient.errors.HttpError
    """
    current_time = datetime.datetime.utcnow()
    yield from get_events(
        start_date=_replace_with_first_day_of_the_year(current_time),
        end_date=current_time,
    )


def get_current_year_events() -> Iterator[model.CalendarEvent]:
    """Retrieves all of the current year events

    Raises:
        googleapiclient.errors.HttpError
    """
    current_time = datetime.datetime.utcnow()
    yield from get_events(
        start_date=_replace_with_first_day_of_the_year(current_time),
        end_date=_replace_with_first_day_of_the_year(
            current_time.replace(year=current_time.year + 1)
        ),
    )


def get_events(
    start_date: datetime.datetime, end_date: datetime.datetime
) -> Iterator[model.CalendarEvent]:
    """Retrieves the events that have taken place between `start_date` and `end_date`

    Raises:
        googleapiclient.errors.HttpError
    """
    service = googleapiclient.discovery.build(
        "calendar", "v3", credentials=_get_api_credentials(_API_SCOPES)
    )

    event_dicts: Iterator[dict[str, Any]] = (
        service.events()
        .list(
            calendarId=config.secret_config["calendarId"],
            timeMin=_format_as_zulu_date(start_date),
            timeMax=_format_as_zulu_date(end_date),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
        .get("items", tuple())
    )
    return map(model.CalendarEvent.from_dict, event_dicts)


if __name__ == "__main__":
    from pprint import pprint

    pprint(get_past_year_events())
