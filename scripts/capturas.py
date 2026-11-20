"""Regenera las capturas de docs/capturas/ (solo desarrollo).

Requiere la app corriendo:  streamlit run app.py --server.port 8599
y playwright instalado:      pip install playwright
Uso:  python scripts/capturas.py docs/capturas
"""
import os
import sys
from playwright.sync_api import sync_playwright
out = sys.argv[1]
shots = [("red_principal.json", "config_1_inicial"), ("config_2_sin_DH.json", "config_2_sin_DH"),
         ("config_3_nueva_ET.json", "config_3_nueva_ET")]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get("CHROMIUM") or None)
    pg = b.new_page(viewport={"width": 1500, "height": 1100}, color_scheme="light")
    pg.goto("http://localhost:8599/"); pg.wait_for_selector("svg", timeout=30000); pg.wait_for_timeout(1500)
    pg.screenshot(path=f"{out}/red_sin_calcular.png")
    for red, nombre in shots:
        pg2 = b.new_page(viewport={"width": 1500, "height": 1100}, color_scheme="light")
        pg2.goto(f"http://localhost:8599/?red={red}&calcular=1"); pg2.wait_for_selector("svg", timeout=30000); pg2.wait_for_timeout(1500)
        pg2.screenshot(path=f"{out}/{nombre}.png")
    # comparación
    pg3 = b.new_page(viewport={"width": 1500, "height": 2600}, color_scheme="light")
    pg3.goto("http://localhost:8599/"); pg3.wait_for_selector("svg", timeout=30000)
    pg3.get_by_role("button", name="Cargar las 3 configuraciones del proyecto").click(); pg3.wait_for_timeout(2500)
    pg3.screenshot(path=f"{out}/comparacion.png", clip={"x": 370, "y": 1010, "width": 1060, "height": 400})
    # arco rechazado
    pg3.get_by_role("tab", name="Agregar conexión").click(); pg3.wait_for_timeout(500)
    b.close()
