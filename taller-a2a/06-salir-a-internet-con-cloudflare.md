<!--encabezado-grupo-->
> **Archivo:** `taller-a2a/06-salir-a-internet-con-cloudflare.md`  
> **Objetivo:** Salir a internet con Cloudflare  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1450 · **Última modificación:** 20261111 1227
<!--/encabezado-grupo-->

<!-- clase: Taller · tu skill es un agente y habla por A2A · 61408ca1 | sección: sf8f5c9 | slide 6/10 · Parte 2 · Internet -->

Parte 2 · Internet · Paso 6 · terminal

# Salir a internet con Cloudflare

Lo mismo del paso 10 de la clase, pero con tu agente en tu puerto. El túnel te da una dirección https; la pones en `URL_PUBLICA` para que tu ficha la publique, y la compartes en el chat con tu nombre y tu skill.

**terminal · túnel, .env y lo que pegas en el chat**

```markdown
# terminal 1 · tu agente (ya corriendo en el 8003)
uvicorn src.agente_jose.server:app --port 8003

# terminal 2 · el túnel apuntando a TU puerto
cloudflared tunnel --url http://127.0.0.1:8003
# ... imprime algo como:  https://verde-luna-456.trycloudflare.com

# en tu .env, y reinicia la terminal 1 (así tu ficha publica la dirección pública):
URL_PUBLICA=https://verde-luna-456.trycloudflare.com

# comprueba desde el teléfono o desde otro computador que la ficha se ve:
curl -s https://verde-luna-456.trycloudflare.com/.well-known/agent-card.json | python3 -m json.tool

# pega en el chat de la clase UNA línea con este formato:
José · TI y soporte técnico · https://verde-luna-456.trycloudflare.com
```

**Una línea en el chat** Nombre · skill · dirección. Así todos saben a quién están sumando y qué sabe.
**La dirección cambia** Cada vez que arrancas cloudflared sale otra. Si lo reinicias, vuelve a pegarla.
**Deja las dos terminales abiertas** Si cierras el túnel o el agente, tus compañeros ven “no responde” en su catálogo.
**Cualquiera con la URL puede usarlo** Y gasta tu clave. Compártela solo en el chat de la clase y cierra el túnel con Ctrl+C al terminar.

Entregables de este paso

- `evidencias/03-tunel.png`: la terminal de cloudflared con tu URL y, al lado, tu ficha abierta desde el teléfono o desde el computador de un compañero.
- La fila “Dirección pública” de tu blueprint completada con esa URL (aunque después cambie).

**Lo logré ✓** Mi ficha se ve desde fuera de mi computador y publica mi dirección https.
