import datetime
from typing import Iterable, Iterator

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


def _get_formatted_current_time() -> str:
    return _format_as_zulu_date(datetime.datetime.utcnow())


def _get_formatted_first_day_of_current_year() -> str:
    return _format_as_zulu_date(
        datetime.datetime.utcnow().replace(
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
    )


def get_past_year_events() -> Iterator[model.CalendarEvent]:
    """Retrieves the events that have taken place since the start of the current year

    Raises:
        googleapiclient.errors.HttpError
    """
    service = googleapiclient.discovery.build(
        "calendar", "v3", credentials=_get_api_credentials(_API_SCOPES)
    )

    event_dicts = (
        service.events()
        .list(
            calendarId=config.secret_config["calendarId"],
            timeMin=_get_formatted_first_day_of_current_year(),
            timeMax=_get_formatted_current_time(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
        .get("items", [])
    )
    return map(model.CalendarEvent.from_dict, event_dicts)


if __name__ == "__main__":
    from pprint import pprint

    pprint(get_past_year_events())
