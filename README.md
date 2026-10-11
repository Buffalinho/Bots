# Bots
Creacion de bots para test

---

# Bot gratuito de avisos de anime por correo

Consulta el calendario público de AniList y, una vez al día, envía por correo los episodios que se estrenan durante las próximas 24 horas. Cada título incluye su ficha/calendario y una búsqueda en JustWatch Colombia para consultar plataformas, precio e idiomas. La preferencia indicada es **audio japonés original + subtítulos en español**.

El bot no reproduce ni descarga episodios. AniList no proporciona los idiomas de reproducción, y no hay una fuente pública estable que confirme automáticamente para cada anime si una oferta en Colombia es gratuita y tiene audio japonés con subtítulos en español. El correo enlaza la búsqueda para que consultes los detalles de la plataforma; JustWatch puede mostrar idiomas por oferta cuando esos datos están disponibles. La disponibilidad cambia según licencia, temporada y episodio. Si no aparecen ambos idiomas y una oferta gratis, ese título no cumple los criterios en ese momento.

## Activarlo gratis con GitHub Actions

1. Crea un repositorio de GitHub y sube el contenido de esta carpeta a la raíz. Para que el ejecutor estándar de GitHub Actions no tenga costo, usa un repositorio público. El código quedará visible, pero los secretos configurados en GitHub no se publican.
2. En **Settings → Secrets and variables → Actions**, crea estos *repository secrets*:

   | Nombre | Valor |
   | --- | --- |
   | `SMTP_USER` | Correo que enviará los avisos, por ejemplo tu Gmail |
   | `SMTP_PASSWORD` | Contraseña de aplicación del correo; nunca la contraseña normal |
   | `EMAIL_TO` | Correo destinatario; puedes indicar varios separados por comas |
   | `SMTP_HOST` | `smtp.gmail.com` para Gmail |
   | `SMTP_PORT` | `465` para Gmail |
   | `EMAIL_FROM` | El correo remitente; normalmente el mismo `SMTP_USER` |

3. Si usas Gmail, habilita la verificación en dos pasos y crea una contraseña de aplicación en la configuración de tu cuenta Google. Guarda ese código como `SMTP_PASSWORD`. Google puede no mostrar esta opción en algunas cuentas administradas o con ciertas políticas.
4. En **Actions**, habilita los workflows si GitHub lo solicita. El bot se ejecutará a las **6:00 a. m. hora de Colombia** y enviará un correo solo cuando encuentre episodios próximos. También puedes abrir el workflow y elegir **Run workflow** para ejecutarlo manualmente.

La programación usa GitHub Actions, y no requiere dejar un computador encendido. GitHub indica que sus ejecutores estándar son gratuitos en repositorios públicos; las condiciones del proveedor de correo siguen aplicando.

## Ejecutarlo en tu computador

1. Instala Python 3.9 o posterior. El bot no requiere paquetes externos.
2. Haz doble clic en `configurar-local.bat` y completa SMTP_USER, SMTP_PASSWORD y EMAIL_TO en el archivo que se abre.
3. Haz doble clic en `probar-local.bat` para consultar AniList y ver una vista previa sin enviar correos.
4. Cuando quieras mandar el resumen real, haz doble clic en `enviar-local.bat`.

Para recibir el resumen automáticamente todos los días en tu computador, crea una tarea diaria en el Programador de tareas de Windows que ejecute `enviar-local.bat`. El computador debe estar encendido y conectado a Internet a la hora programada. Si prefieres no mantenerlo encendido, usa el workflow de GitHub Actions descrito arriba.

## Configuración

- `TIMEZONE`: zona horaria para mostrar las horas; por defecto `America/Bogota`.
- `LOOKAHEAD_HOURS`: horas futuras que se consultan; por defecto `24` y máximo `168`.
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_FROM`, `EMAIL_TO`: conexión y destinatarios del correo.

El archivo `.env` está excluido de Git para no subir credenciales por accidente. No pegues contraseñas de aplicación en el código ni en mensajes públicos.

## Fuentes de datos

- [Documentación oficial de la API de AniList](https://docs.anilist.co/guide/graphql/)
- [JustWatch Colombia: catálogo y filtros de disponibilidad](https://www.justwatch.com/co/series)
- [Ayuda de Crunchyroll para revisar idiomas por título](https://help.crunchyroll.com/es/article/What-languages-are-available-for-shows)
- [Ayuda de Google sobre contraseñas de aplicación](https://support.google.com/accounts/answer/6009563?hl=es)

