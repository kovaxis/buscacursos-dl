# buscacursos-dl

La información en bruto de buscacursos en la palma de tu mano.

Un scraper simple basado en la implementación de [ramos-uc](https://github.com/open-source-uc/ramos-uc).

## Datos precocinados

Los datos pre-scrapeados de buscacursos están disponibles para descargar en [releases](https://github.com/negamartin/buscacursos-dl/releases) como un `.json` gigante para cada semestre (solo 2022-2 hasta ahora).

## Correr el scraper

Para correr el scraper basta con clonar el repositorio y correr:

```sh
python3 main.py 2022-2 2022-1 2021-2 > courses.json 2> log.txt
```

Notar que el scraper puede tomar varias horas en descargar todos los ramos.

## Formato de los datos

Un ejemplo con comentarios:

```javascript
{
    // Datos de un semestre (puede haber mas de un semestre en un mismo archivo)
    "2022-2": {
        // Datos de un ramo (con varias secciones)
        "IEE2713": {
            "name": "Sistemas Digitales",
            "credits": 10,
            // Requerimientos en terminos de que ramos hay que tomar antes
            "requirements": "MAT1202 o MAT1203",
            // Ver ejemplo mas adelante
            "connector": "No tiene",
            "restrictions": "No tiene",
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
                    // Cupos totales para la seccion
                    "total_quota": 60,
                    // Cupos disponibles al momento de scrapear (informacion inutil)
                    "available_quota": 11
                }
            }
        },
        "ICS3413": {
            "name": "Finanzas",
            // Este ramo se puede tomar si tomaste ICS2613 *o* si has aprobado 300 creditos o mas
            "requirements": "ICS2613",
            "connector": "o",
            "restrictions": "(Creditos >= 300)"
            // ... omitidos por brevedad ...
        },
        "SUS1000": {
            // Quizas para los OFG?
            "area": "Ecolog Integra y Sustentabilidad",
            "category": "Aprendizaje Servicio",
            // ... omitidos por brevedad ...
        }
    }
}
```
