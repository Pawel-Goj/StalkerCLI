import time
import requests
import psutil
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.text import Text

GITHUB_USER = "Pawel-Goj"
GITHUB_REPO = "Pico-Threat-Monitor"


def get_cpu_usage():
    try:
        return f"{psutil.cpu_percent(interval=None):.1f}%"
    except Exception:
        return 'N/A'


def get_disk_space():
    try:
        usage = psutil.disk_usage('/')
        used_gb = usage.used / (1024 ** 3)
        total_gb = usage.total / (1024 ** 3)
        return f"Used: {used_gb:.1f}GB / Total: {total_gb:.1f}GB ({usage.percent}%)"
    except Exception:
        return 'N/A'


def get_latest_github_commit():
    try:
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/commits"
        headers = {"Accept": "application/vnd.github.v3+json"}
        response = requests.get(url, headers=headers, timeout=3)

        if response.status_code == 200:
            commits = response.json()
            if commits:
                latest = commits[0]
                sha = latest['sha'][:7]
                message = latest['commit']['message'].split('\n')[0]
                author = latest['commit']['author']['name']
                return f"{sha} - {message} ({author})"
        return "No commits found"
    except Exception:
        return "Connection failed"


def get_top_processes():
    try:
        procs = []
        for p in psutil.process_iter(['name', 'memory_percent']):
            try:
                procs.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        procs = sorted(procs, key=lambda x: x['memory_percent'] or 0, reverse=True)[:3]
        return "\n".join([f"• {p['name']} ({p['memory_percent']:.1f}%)" for p in procs if p['name']])
    except Exception:
        return "N/A"


def get_weather():
    try:
        res = requests.get("https://wttr.in/?format=3", timeout=2)
        if res.status_code == 200:
            return res.text.strip()
        return "Unavailable"
    except Exception:
        return "Offline"


def generate_dashboard():
    layout = Layout()

    layout.split(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3)
    )

    layout["body"].split_row(
        Layout(name="left"),
        Layout(name="right")
    )

    header_text = Text("STALKER CLI v1.0.0", justify="center", style="bold green")
    layout["header"].update(Panel(header_text, style="bold green"))

    table = Table(show_header=True, header_style="bold magenta", expand=True)
    table.add_column("Metric", style="dim")
    table.add_column("Value", justify="right")
    table.add_row("CPU Load", get_cpu_usage())
    table.add_row("Root Disk", get_disk_space())
    table.add_row("Local Weather", get_weather())
    table.add_row("Time", time.strftime("%Y-%m-%d %H:%M:%S"))

    table.add_row("Top Memory", "")
    table.add_row(get_top_processes(), "")

    layout["left"].update(Panel(table, title="[bold red]System Telemetry[/bold red]", border_style="red"))
    log_text = Text()
    log_text.append('[*] Initializing dashboard subsystems...\n', style="dim")
    log_text.append('[*] psutil hardware monitoring active...\n', style="dim")
    log_text.append(f'[*] Latest GitHub Commit:\n    {get_latest_github_commit()}\n', style="bold yellow")
    log_text.append('[*] All systems nominal. Ready for deployment.\n', style="bold green")

    layout["right"].update(Panel(log_text, title="[bold cyan]Event Stream[/bold cyan]", border_style="cyan"))

    footer_text = Text("Press Ctrl+C to exit dashboard.", justify="center", style="dim")
    layout["footer"].update(Panel(footer_text, border_style="dim"))

    return layout


if __name__ == "__main__":
    psutil.cpu_percent(interval=None)

    with Live(generate_dashboard(), refresh_per_second=2, screen=True) as live:
        try:
            while True:
                time.sleep(0.5)
                live.update(generate_dashboard())
        except KeyboardInterrupt:
            pass