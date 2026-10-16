import html
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlsplit

import database
import weather


DATABASE_PATH = Path(os.environ.get("DATABASE_PATH", "data/cities.db"))


def render_page(cities, message=None, is_error=False):
    cards = []
    for city in cities:
        title = html.escape(city["name"])
        location = ", ".join(
            part for part in (city["region"], city["country"]) if part
        )
        location = html.escape(location)
        try:
            current = weather.get_current_weather(
                city["latitude"], city["longitude"]
            )
            details = (
                f'<p class="temperature">{html.escape(str(current["temperature"]))}'
                f'<span>°C</span></p>'
                f'<p class="condition">{html.escape(current["description"])}</p>'
                f'<p class="humidity">Umidade: '
                f'{html.escape(str(current["humidity"]))}%</p>'
            )
        except weather.WeatherServiceError as error:
            details = (
                f'<p class="weather-error">{html.escape(str(error))}</p>'
            )

        cards.append(
            f"""
            <article class="city-card">
              <div>
                <h2>{title}</h2>
                <p class="location">{location}</p>
                {details}
              </div>
              <form method="post" action="/delete">
                <input type="hidden" name="city_id" value="{city['id']}">
                <button class="remove" type="submit"
                        aria-label="Remover {title}">Remover</button>
              </form>
            </article>
            """
        )

    if not cards:
        city_content = (
            '<div class="empty"><span aria-hidden="true">☀</span>'
            "<p>Nenhuma cidade salva ainda.</p>"
            "<p>Busque uma cidade para acompanhar o clima por aqui.</p></div>"
        )
    else:
        city_content = f'<div class="city-list">{"".join(cards)}</div>'

    notice = ""
    if message:
        role = "alert" if is_error else "status"
        css_class = "notice error" if is_error else "notice success"
        notice = (
            f'<p class="{css_class}" role="{role}">'
            f"{html.escape(message)}</p>"
        )

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#f6f8ff">
  <title>Clima em Foco</title>
  <style>
    :root {{ color-scheme: light; font-family: Inter, ui-sans-serif, system-ui,
      -apple-system, "Segoe UI", sans-serif; color: #172554; background: #f6f8ff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-height: 100vh; }}
    .shell {{ width: min(900px, calc(100% - 32px)); margin: 0 auto; padding: 56px 0; }}
    .hero {{ padding: 36px; border-radius: 24px; color: #fff;
      background: linear-gradient(130deg, #1d4ed8, #6d28d9); }}
    .eyebrow {{ margin: 0 0 8px; opacity: .8; font-size: .8rem;
      font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }}
    h1 {{ margin: 0; font-size: clamp(2rem, 5vw, 3rem); letter-spacing: -.04em; }}
    .intro {{ max-width: 560px; margin: 12px 0 0; color: #e0e7ff; }}
    .search {{ display: flex; gap: 10px; margin: 24px 0 0; }}
    .search input {{ min-width: 0; flex: 1; padding: 14px 16px; border: 1px solid #dbe3f0;
      border-radius: 12px; font: inherit; }}
    button {{ border: 0; border-radius: 12px; padding: 13px 18px; font: inherit;
      font-weight: 700; cursor: pointer; }}
    .search button {{ color: #fff; background: #172554; }}
    button:focus-visible, input:focus-visible {{ outline: 3px solid #fbbf24; outline-offset: 2px; }}
    .notice {{ padding: 12px 16px; border-radius: 12px; }}
    .success {{ color: #166534; background: #dcfce7; }}
    .error {{ color: #991b1b; background: #fee2e2; }}
    .section-heading {{ display: flex; align-items: baseline; justify-content: space-between;
      margin: 36px 0 14px; }}
    .section-heading h2 {{ margin: 0; font-size: 1.35rem; }}
    .section-heading p {{ margin: 0; color: #64748b; font-size: .9rem; }}
    .city-list {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(245px, 1fr));
      gap: 14px; }}
    .city-card {{ display: flex; justify-content: space-between; gap: 12px; min-height: 190px;
      padding: 20px; border: 1px solid #e2e8f0; border-radius: 18px; background: #fff;
      box-shadow: 0 8px 24px #1e3a8a0a; }}
    .city-card h2 {{ margin: 0; font-size: 1.25rem; }}
    .location, .condition, .humidity {{ margin: 5px 0; color: #64748b; }}
    .temperature {{ margin: 18px 0 0; font-size: 2.4rem; font-weight: 750;
      letter-spacing: -.06em; }}
    .temperature span {{ margin-left: 3px; font-size: 1.2rem; }}
    .remove {{ padding: 8px 10px; color: #64748b; background: #f1f5f9;
      font-size: .8rem; }}
    .empty {{ padding: 40px 20px; border: 1px dashed #cbd5e1; border-radius: 18px;
      color: #64748b; background: #fff; text-align: center; }}
    .empty span {{ color: #f59e0b; font-size: 2rem; }}
    .empty p {{ margin: 6px 0; }}
    footer {{ margin-top: 32px; color: #94a3b8; font-size: .8rem; text-align: center; }}
    @media (max-width: 540px) {{
      .shell {{ padding: 24px 0; }}
      .hero {{ padding: 24px; }}
      .search {{ flex-direction: column; }}
      .search button {{ width: 100%; }}
      .section-heading {{ align-items: flex-start; flex-direction: column; gap: 4px; }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <header class="hero">
      <p class="eyebrow">Seu clima, em um só lugar</p>
      <h1>Clima em Foco</h1>
      <p class="intro">Salve suas cidades favoritas e acompanhe as condições
        atuais do tempo em cada uma delas.</p>
      <form class="search" method="post" action="/add">
        <label hidden for="city-name">Nome da cidade</label>
        <input id="city-name" name="name" type="search" minlength="2" maxlength="80"
          placeholder="Ex.: Brasília, São Paulo..." required>
        <button type="submit">Adicionar cidade</button>
      </form>
    </header>
    {notice}
    <section aria-labelledby="saved-heading">
      <div class="section-heading">
        <h2 id="saved-heading">Cidades salvas</h2>
        <p>Condições atuais · Open-Meteo</p>
      </div>
      {city_content}
    </section>
    <footer>Dados de clima fornecidos pela API pública Open-Meteo.</footer>
  </main>
</body>
</html>"""


class ClimaHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path)
        if path.path == "/health":
            self.send_text(200, "ok")
            return
        if path.path != "/":
            self.send_text(404, "Página não encontrada")
            return

        params = parse_qs(path.query)
        message = params.get("message", [""])[0]
        is_error = params.get("error", [""])[0] == "1"
        body = render_page(database.list_cities(DATABASE_PATH), message, is_error)
        self.send_html(200, body)

    def do_POST(self):
        path = urlsplit(self.path).path
        length = int(self.headers.get("Content-Length", "0"))
        if length > 10_000:
            self.send_text(413, "Formulário muito grande")
            return
        form = parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True)

        try:
            if path == "/add":
                city = weather.search_city(form.get("name", [""])[0])
                database.add_city(city, DATABASE_PATH)
                self.redirect(f"Cidade adicionada: {city['name']}")
            elif path == "/delete":
                city_id = int(form.get("city_id", [""])[0])
                if not database.delete_city(city_id, DATABASE_PATH):
                    raise ValueError("A cidade selecionada não existe.")
                self.redirect("Cidade removida.")
            else:
                self.send_text(404, "Página não encontrada")
        except (ValueError, weather.WeatherServiceError) as error:
            self.redirect(str(error), is_error=True)
        except sqlite3.IntegrityError:
            self.redirect("Essa cidade já está salva.", is_error=True)

    def redirect(self, message, is_error=False):
        query = ("error=1&" if is_error else "") + f"message={quote(message)}"
        self.send_response(303)
        self.send_header("Location", f"/?{query}")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def send_html(self, status, content):
        encoded = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(encoded)

    def send_text(self, status, content):
        encoded = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format_string, *args):
        print(f"{self.address_string()} - {format_string % args}")


if __name__ == "__main__":
    database.init_db(DATABASE_PATH)
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer((host, port), ClimaHandler)
    print(f"Clima em Foco disponível em http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
        server.server_close()
