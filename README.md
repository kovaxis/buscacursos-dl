# buscacursos-dl

La información en bruto de [Buscacursos](https://buscacursos.uc.cl/) y [Catálogo UC](https://catalogo.uc.cl/) en la palma de tu mano.

Un scraper simple basado en la implementación de [ramos-uc](https://github.com/open-source-uc/ramos-uc).

## Descargar datos precocinados

Los datos pre-scrapeados de buscacursos y catálogo UC están disponibles para descargar en [releases](https://github.com/negamartin/buscacursos-dl/releases) como archivos `.json` gigantes.

## Correr el scraper

El primer paso es clonar el repositorio:

```bash
git clone https://github.com/negamartin/buscacursos-dl.git
```

Luego, elegir si quieres scrapear buscacursos, catalogo, o ambos.

### Scrapear Buscacursos

Buscacursos contiene informacion sobre las instancias de los cursos que se han dictado en los últimos semestres,
incluyendo profesores, horarios, etc.
La información de buscacursos está asociada a un periodo particular, y *no* contiene información sobre los cursos
que no se dictaron ese periodo.

Para correr el scraper de buscacursos primero es necesario elegir los periodos a scrapear (eg. `2023-1`, `2022-2`).
Luego, se corre el archivo `main.py` con los periodos como argumentos:

```bash
python3 main.py 2023-1 2022-2 > stdout.txt 2> stderr.txt
```

### Scrapear Catálogo UC

Catálogo UC contiene información sobre todos los ramos en la base de datos de la UC, aunque no contiene información
sobre instancias particulares de estos ramos (eg. no tiene información sobre profesores, horarios ni periodos en
que se han dictado los cursos).
Hay aproximadamente 10x la cantidad de cursos disponibles que en Buscacursos, ya que se incluyen los cursos obsoletos.

Para correr el scraper de catálogo UC, es necesario entregar como único argumento la palabra `catalogo`:

```bash
python3 main.py catalogo > stdout.txt 2> stderr.txt
```

### Juntar resultados de varios scrapeos

El script `make-universal.py` permite agregar los resultados de varios scrapeos en una mega base de datos.
En particular, permite agrupar scrapeos de buscacursos y de catálogo UC en un mismo `.json` universal.

Por ejemplo, para juntar los datos de un scrapeo de catalogo y 2 scrapeos de buscacursos:

```bash
python3 make-universal.py catalogo.json buscacursos-1.json buscacursos-2.json
```

El script autodetecta si los `.json` son informacion de buscacursos o de catalogo.
Debe haber exactamente 1 `.json` de Catálogo UC.
Debe haber al menos 1 `.json` de Buscacursos, ya que se usa para suplir la información que Catálogo no provee.

### Detalles importantes

- El scraper puede tomar varias horas en descargar todos los cursos.
- El scraper imprime el progreso y el `.json` final a `stdout` y `stderr`.
    En particular, **no** guarda el `.json` resultante en ningún archivo en particular.
    Los únicos otros archivos con los que interactúa el scraper es `.cred` (cookies que incluir
    en los requests) y `.requestcache` (cache).
- El scraper **no** puede scrapear buscacursos y catalogo en una misma ejecucion.
- Para obtener un `.json` limpio con los resultados es necesario extrar la última línea de output de `stdout.txt`.

## Formato de los datos

### Formato del scraper de buscacursos

```javascript
{
    // Datos de un semestre (puede haber mas de un semestre en un mismo archivo)
    "2022-2": {
        // Datos de un ramo (con varias secciones)
        "IEE2713": {
            "name": "Sistemas Digitales",
            "credits": 10,
            // Requerimientos en terminos de que ramos hay que tomar antes
            "req": "MAT1202 o MAT1203",
            // Ver ejemplo mas adelante
            "conn": "No tiene",
            "restr": "No tiene",
            "equiv": "No tiene",
            // Descripcion del curso
            "program": "CURSO: SISTEMAS DIGITALES...",
            // Facultad
            "school": "Ingeniería",
            // Ver ejemplo mas adelante
            "area": "",
            "category": "",
            // Secciones del ramo en el semestre dado
            "sections": {
                // Los numeros de seccion son strings, porque pueden haber "hoyos"
                // (ie. que exista la seccion 2 pero no la 1)
                "1": {
                    // Unico para cada (ramo, seccion)
                    "nrc": "10962",
                    "teachers": "Cristian Garces",
                    "schedule": {
                        // Martes y Jueves 2do modulo, clase en la sala BC25
                        "m2": ["CLAS", "BC25"],
                        "j2": ["CLAS", "BC25"],
                        // Ayudantia Miercoles 6to modulo en la sala BC25
                        "w6": ["AYU", "BC25"]
                    },
                    // Presencial, hibrido o remoto
                    "format": "Presencial",
                    "campus": "San Joaquin",
                    "is_english": false,
                    // Es botable?
                    "is_removable": true,
                    // ?
                    "is_special": false,
                    // Cupos totales ofrecidos para la seccion
                    "total_quota": 60,
                    // Desglose sobre los programas para los que se ofrecen los cupos
                    "quota": {
                        "Vacantes libres": 57,
                        "09 - College": 3
                    }
                }
            }
        },
        "ICS3413": {
            "name": "Finanzas",
            // Este ramo se puede tomar si tomaste ICS2613 *o* si has aprobado 300 creditos o mas
            "req": "ICS2613",            // requirements
            "conn": "o",                 // connector
            "restr": "(Creditos >= 300)" // restrictions
            "equiv": "(ICS3532)",        // equivalencies
            // ... omitidos por brevedad ...
        },
        "SUS1000": {
            // Quizas para los OFG?
            "area": "Ecolog Integra y Sustentabilidad",
            "category": "Aprendizaje Servicio",
            // ... omitidos por brevedad ...
        },
        "TSL596": {
            // Requiere que la carrera sea distinta a "Trabajo Social"
            "restr": "(Carrera <> Trabajo Social)",
            // ... omitidos por brevedad ...
        },
        "IHI0224": {
            "sections": {
                "1": {
                    "quota": {
                        "Vacantes libres": 63,
                        // Programa compuesto de College y restringido a Pregrado
                        "09 - College/Pregrado": 18,
                        "20 - Educación/Pregrado": 10,
                        "56 - Historia/Pregrado": 4,
                        "97 - Actividades Universitarias": 2
                    },
                    // ... omitidos por brevedad ...
                },
                // ... omitidos por brevedad ...
            },
            // ... omitidos por brevedad ...
        }
    }
}
```
