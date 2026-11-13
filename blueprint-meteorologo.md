## Blueprint · Agente de NOMBRE

| Qué definir        | Mi agente                                                                 |
|--------------------|---------------------------------------------------------------------------|
| Quién soy          | Agente meteorologo                                            |
| Hace               | Entrega el estado del clima por ciudad y puede hacer pronostico del tiempo para hoy o para la semana solo para las ciudades De Santiago, Concepcion y Valdivia.       |
| No hace            |    No entrega pronostico para otras ciudades que no sean las mencionadas o pronósticos del clima que excedan 7 dias en el futuro.                                                        |
| Herramientas       | pronostico_hoy(ciudad:str):devuelve el pronostico del tiempo para el dia de hoy , dada una ciudad ,  pronostico_semana(ciudad:str):devuelve el pronostico del tiempo para la semana , dada una ciudad como parámetro |
| Decide solo        | …                                                                         |
| Nunca sin persona  | …                                                                         |
| Deriva a otro      | Cuando la pregunta es de … → lo dice en una frase y no responde           |
| Dónde se ejecuta   | http://127.0.0.1:8003 · src/agente_meteorologo/ · python main.py meteorologo “Cual es el pronostico del tiempo para Santiago el dia de hoy?        |
| Dirección pública  | https://advised-holiday-against-economic.trycloudflare.com                     |