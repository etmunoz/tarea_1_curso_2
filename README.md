# Taller A2A

Proyecto de taller para crear agentes especializados que se comunican mediante el protocolo A2A. Incluye un supervisor coordinador que descubre agentes disponibles y deriva las consultas al más adecuado.

## Agentes disponibles

- **Viajes:** busca vuelos y hoteles ficticios.
- **Restaurantes:** recomienda restaurantes ficticios en LIM, BOG y EZE.
- **Agente meteorólogo:** entrega pronósticos ficticios para Santiago, Concepción y Valdivia.
- **Coordinador:** supervisa los agentes de viajes y restaurantes y delega la consulta al más adecuado.

## Uso desde la línea de comandos

Activa el entorno principal para viajes, meteorología y coordinador:

```bash
source .venv/bin/activate
```

Consulta viajes:

```bash
python main.py viajes "Busca vuelos de LIM a SCL para el 15 de diciembre"
python main.py viajes "Busca hoteles en Lima para 3 noches" --saltos
python main.py viajes --diagrama
```

Consulta meteorología:

```bash
python main.py meteorologo "Dame el pronóstico del tiempo para hoy en Valdivia"
python main.py meteorologo "¿Cómo estará el clima esta semana en Santiago?" --saltos
python main.py meteorologo --diagrama
```

Consulta el coordinador:

```bash
python main.py coordinador "Busca vuelos de LIM a SCL para el 15 de diciembre"
python main.py coordinador "Busca restaurantes de comida argentina en EZE" --saltos
python main.py coordinador --diagrama
```

Para restaurantes, activa primero su entorno aislado:

```bash
source .venv-crew/bin/activate
python main.py restaurantes "Busca restaurantes de comida argentina en EZE"
python main.py restaurantes "Dame el detalle de Parrilla Palermo" --saltos
python main.py restaurantes --diagrama
```

La opción `--saltos` muestra los nodos y herramientas utilizados. La opción `--diagrama` imprime la estructura Mermaid sin ejecutar el agente.
# taller_A2A_uai
