#!/usr/bin/env python3
"""Send a daily email digest of anime episodes airing soon."""

from __future__ import annotations

import html
import json
import os
import smtplib
import ssl
import sys
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


ANILIST_ENDPOINT = "https://graphql.anilist.co"
JUSTWATCH_SEARCH = "https://www.justwatch.com/co/buscar?q={}"
ANILIST_QUERY = """
query ($from: Int!, $to: Int!, $page: Int!, $perPage: Int!) {
  Page(page: $page, perPage: $perPage) {
    airingSchedules(
      airingAt_greater: $from
      airingAt_lesser: $to
      notYetAired: true
      sort: TIME
    ) {
      id
      airingAt
      episode
      media {
        id
        siteUrl
        title { english romaji native }
      }
    }
  }
}
"""


def load_dotenv() -> None:
    """Load a simple .env file without overriding real environment variables."""
    env_file = Path(__file__).with_name(".env")
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key:
            os.environ.setdefault(key, value)


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Falta configurar {name} en .env o en los secretos del workflow.")
    return value


def fetch_airings(start: datetime, end: datetime) -> list[dict]:
    airings: list[dict] = []
    page = 1
    per_page = 50
    while page <= 5:
        payload = {
            "query": ANILIST_QUERY,
            "variables": {
                "from": int(start.timestamp()),
                "to": int(end.timestamp()),
                "page": page,
                "perPage": per_page,
            },
        }
        request = Request(
            ANILIST_ENDPOINT,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "AnimeEmailNotifier/1.0 (personal daily digest)",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError(f"AniList respondió HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(f"No se pudo conectar con AniList: {exc.reason}") from exc

        if result.get("errors"):
            messages = "; ".join(error.get("message", "error desconocido") for error in result["errors"])
            raise RuntimeError(f"AniList informó un error: {messages}")

        entries = result.get("data", {}).get("Page", {}).get("airingSchedules", [])
        airings.extend(entries)
        if len(entries) < per_page:
            break
        page += 1
    return airings


def title_for(airing: dict) -> str:
    titles = airing.get("media", {}).get("title", {})
    return titles.get("english") or titles.get("romaji") or titles.get("native") or "Anime sin título"


def watch_search_url(title: str) -> str:
    return JUSTWATCH_SEARCH.format(quote_plus(title))


def build_email(airings: list[dict], timezone_name: str, start: datetime, end: datetime) -> EmailMessage:
    local_zone = ZoneInfo(timezone_name)
    local_start = start.astimezone(local_zone)
    local_end = end.astimezone(local_zone)
    day_label = local_start.strftime("%d/%m/%Y")

    subject = f"Anime: {len(airings)} episodios próximos — {day_label}"
    plain_lines = [
        f"Próximos episodios de anime ({local_start:%d/%m %H:%M} a {local_end:%d/%m %H:%M}, {timezone_name})",
        "Preferencia: audio japonés original + subtítulos en español.",
        "Confirma los idiomas y la opción gratis en los detalles del servicio antes de reproducir.",
        "",
    ]
    html_items = []

    for airing in airings:
        title = title_for(airing)
        when = datetime.fromtimestamp(int(airing["airingAt"]), timezone.utc).astimezone(local_zone)
        episode = airing.get("episode", "?")
        media_url = airing.get("media", {}).get("siteUrl", "https://anilist.co/anime/")
        free_search_url = watch_search_url(title)

        plain_lines.extend([
            f"• {title} — episodio {episode} — {when:%a %d/%m, %H:%M}",
            f"  Calendario: {media_url}",
            f"  Consultar plataformas, precio e idiomas en Colombia: {free_search_url}",
            "",
        ])
        html_items.append(
            "<li style=\"margin:0 0 18px\">"
            f"<strong>{html.escape(title)}</strong> — episodio {html.escape(str(episode))}<br>"
            f"<span>{html.escape(when.strftime('%A %d/%m, %H:%M'))} ({html.escape(timezone_name)})</span><br>"
            f"<a href=\"{html.escape(media_url, quote=True)}\">Ver ficha y calendario</a> · "
            f"<a href=\"{html.escape(free_search_url, quote=True)}\">Consultar plataformas, precio e idiomas en Colombia</a>"
            "</li>"
        )

    html_body = (
        "<!doctype html><html><body style=\"font-family:Arial,sans-serif;line-height:1.5;color:#222\">"
        f"<h2>Anime: {len(airings)} episodios próximos</h2>"
        f"<p>Del {html.escape(local_start.strftime('%d/%m %H:%M'))} al "
        f"{html.escape(local_end.strftime('%d/%m %H:%M'))} ({html.escape(timezone_name)}).</p>"
        "<p><strong>Preferencia de reproducción:</strong> audio japonés original + subtítulos en español.</p>"
        f"<ul>{''.join(html_items)}</ul>"
        "<p style=\"font-size:12px;color:#555\">AniList proporciona el calendario, no los idiomas de reproducción. "
        "En la ficha de la plataforma, confirma que ese episodio o temporada tenga audio japonés y subtítulos en español; "
        "la disponibilidad gratuita depende de las licencias vigentes en Colombia. Si no aparece una oferta gratis con esos idiomas, "
        "el título no cumple ambos requisitos en ese momento.</p>"
        "</body></html>"
    )

    message = EmailMessage()
    message["Subject"] = subject
    message.set_content("\n".join(plain_lines))
    message.add_alternative(html_body, subtype="html")
    return message


def send_email(message: EmailMessage) -> None:
    smtp_host = os.getenv("SMTP_HOST", "").strip() or "smtp.gmail.com"
    smtp_port = int(os.getenv("SMTP_PORT", "").strip() or "465")
    smtp_user = required_env("SMTP_USER")
    smtp_password = required_env("SMTP_PASSWORD")
    sender = os.getenv("EMAIL_FROM", "").strip() or smtp_user
    recipients = [item.strip() for item in required_env("EMAIL_TO").split(",") if item.strip()]
    if not recipients:
        raise ValueError("EMAIL_TO debe contener al menos un correo destinatario.")

    message["From"] = sender
    message["To"] = ", ".join(recipients)
    context = ssl.create_default_context()

    if smtp_port == 465:
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=30) as server:
            server.login(smtp_user, smtp_password)
            server.send_message(message)
    else:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(smtp_user, smtp_password)
            server.send_message(message)


def main() -> int:
    load_dotenv()
    try:
        timezone_name = os.getenv("TIMEZONE", "America/Bogota").strip()
        local_zone = ZoneInfo(timezone_name)
        del local_zone  # Validate the timezone before making the API request.
        lookahead_hours = int(os.getenv("LOOKAHEAD_HOURS", "24"))
        if not 1 <= lookahead_hours <= 168:
            raise ValueError("LOOKAHEAD_HOURS debe estar entre 1 y 168.")

        now = datetime.now(timezone.utc)
        end = now + timedelta(hours=lookahead_hours)
        airings = fetch_airings(now, end)
        airings.sort(key=lambda item: (item.get("airingAt", 0), title_for(item).casefold()))
        if not airings:
            print(f"No hay episodios programados en las próximas {lookahead_hours} horas; no se envió correo.")
            return 0

        message = build_email(airings, timezone_name, now, end)
        send_email(message)
        print(f"Correo enviado con {len(airings)} episodios.")
        return 0
    except ZoneInfoNotFoundError as exc:
        print(f"Zona horaria no válida: {exc}", file=sys.stderr)
    except (ValueError, RuntimeError, OSError, smtplib.SMTPException) as exc:
        print(f"Error: {exc}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

