import requests
import pyfiglet
import re
import csv
import json
from rich.console import Console
from rich.progress import track
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
import sys
import time

console = Console()

def print_banner(text):
    banner = pyfiglet.figlet_format(text)
    console.print(banner, style="bold green")

def validate_ip(ip_address):
    ipv4_pattern = re.compile(r'^(([0-9]{1,3}\.){3}[0-9]{1,3})$')
    ipv6_pattern = re.compile(r'^((([0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4})|(::))$')
    return bool(ipv4_pattern.match(ip_address) or ipv6_pattern.match(ip_address))

def get_geolocation(ip_address):
    url = f"http://ip-api.com/json/{ip_address}?fields=66846719"
    for _ in track(range(30), description="Carregando informações..."):
        time.sleep(0.02)
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Erro ao obter informações do IP.")

def display_ip_geolocation(ip_address):
    geo_info = get_geolocation(ip_address)
    if geo_info["status"] == "fail":
        raise Exception(f"Erro ao buscar IP: {geo_info['message']}")

    table = Table(title=f"IP Hunter: Informações para {ip_address}")
    table.add_column("Informação", justify="left", style="cyan")
    table.add_column("Detalhe", justify="left", style="magenta")

    table.add_row("Endereço IP", geo_info.get("query", "Desconhecido"))
    table.add_row("País", geo_info.get("country", "Desconhecido"))
    table.add_row("Região/Estado", geo_info.get("regionName", "Desconhecido"))
    table.add_row("Cidade", geo_info.get("city", "Desconhecido"))
    table.add_row("Código Postal", geo_info.get("zip", "Desconhecido"))
    table.add_row("Fuso Horário", geo_info.get("timezone", "Desconhecido"))
    table.add_row("Latitude/Longitude", f"{geo_info.get('lat', 'Desconhecido')}/{geo_info.get('lon', 'Desconhecido')}")
    table.add_row("ISP", geo_info.get("isp", "Desconhecido"))
    table.add_row("ASN", geo_info.get("as", "Desconhecido"))
    table.add_row("Organização", geo_info.get("org", "Desconhecido"))
    table.add_row("Domínio Reverso", geo_info.get("reverse", "Desconhecido"))

    console.print(table)
    return geo_info

def ask_to_continue():
    return Prompt.ask("Deseja procurar outro IP? (s/n)").lower() == "s"

def show_history(history):
    if history:
        console.print(Panel("\n".join(history), title="Histórico de IPs"))
    else:
        console.print("[bold yellow]Nenhum histórico disponível.[/bold yellow]")

def export_history_csv(history, filename):
    with open(filename, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Endereço IP"])
        writer.writerows([[ip] for ip in history])
    console.print(f"Histórico exportado para {filename}")

def export_history_json(history, filename):
    with open(filename, "w") as jsonfile:
        json.dump({"ips": history}, jsonfile)
    console.print(f"Histórico exportado para {filename}")

print_banner("IP Hunter")

ip_from_args = sys.argv[1] if len(sys.argv) > 1 else None
history = []

if ip_from_args:
    if validate_ip(ip_from_args):
        try:
            display_ip_geolocation(ip_from_args)
            history.append(ip_from_args)
        except Exception as e:
            console.print(f"[bold red]Erro:[/bold red] {e}")
    else:
        console.print("[bold red]Endereço IP inválido fornecido como argumento.[/bold red]")

while True:
    ip_address = console.input("Digite um IP para obter a localização: ")

    if not validate_ip(ip_address):
        console.print("[bold red]IP inválido. Tente novamente.[/bold red]")
        continue
    
    try:
        display_ip_geolocation(ip_address)
        history.append(ip_address)
    except Exception as e:
        console.print(f"[bold red]Erro:[/bold red] {e}")

    if not ask_to_continue():
        break
    
    if Prompt.ask("Deseja ver o histórico? (s/n)").lower() == "s":
        show_history(history)

export_choice = Prompt.ask("Exportar histórico para CSV ou JSON? (c/j)").lower()
if export_choice == "c":
    export_history_csv(history, "historico_ips.csv")
elif export_choice == "j":
    export_history_json(history, "historico_ips.json")

console.print("Saindo do IP Hunter. Até logo!")
