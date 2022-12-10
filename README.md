# buscacursos-dl

La información de buscacursos en la palma de tu mano.

Un scraper simple basado en la implementación de [ramos-uc](https://github.com/open-source-uc/ramos-uc).

## Datos precocinados

Los datos pre-scrapeados de buscacursos están disponibles para descargar en [releases](https://github.com/negamartin/buscacursos-dl/releases) como un `.json` gigante para cada semestre (solo 2022-2 hasta ahora).

## Correr el scraper

Para correr el scraper basta con clonar el repositorio y correr:

```sh
python3 main.py 2022-2 2022-1 2021-2 > courses.json 2> log.txt
```

Notar que el scraper puede tomar varias horas en descargar todos los ramos.
