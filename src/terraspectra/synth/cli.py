"""CLI command interface for synthetic hyperspectral data generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from terraspectra.core.console import console
from terraspectra.core.paths import ensure_dir
from terraspectra.core.settings import settings
from terraspectra.synth.cube import compose_cube, generate_time_series

app = typer.Typer(
    name="synth",
    help="TerraSpectra synthetic hyperspectral data generator CLI",
    add_completion=False,
)


@app.command()
def generate(
    scene_id: str = typer.Option("farm_001", "--scene-id", "-s", help="Unique scene identifier"),
    rows: int = typer.Option(128, "--rows", "-r", help="Scene height in pixels"),
    cols: int = typer.Option(128, "--cols", "-c", help="Scene width in pixels"),
    bands: int = typer.Option(224, "--bands", "-b", help="Number of spectral bands"),
    hotspot_acres: float = typer.Option(5.0, "--hotspot-acres", help="Target disease zone area in acres"),
    day: float = typer.Option(14.0, "--day", "-d", help="Progression day (14 = pre-symptomatic stress)"),
    seed: int = typer.Option(42, "--seed", help="Random seed for reproducibility"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Output directory"),
    time_series: bool = typer.Option(False, "--time-series", "-t", help="Generate 4-date revisit series"),
) -> None:
    """Generate physically-realistic synthetic hyperspectral cubes and ground-truth masks."""
    out = output_dir or settings.synthetic_data_dir
    ensure_dir(out)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        if not time_series:
            task = progress.add_task(f"Generating synthetic scene [cyan]{scene_id}[/] (day {day})...", total=1)
            scene = compose_cube(
                rows=rows,
                cols=cols,
                n_bands=bands,
                day_in_progression=day,
                hotspot_acres=hotspot_acres,
                seed=seed,
                scene_id=scene_id,
            )

            # Save cube as compressed numpy array / metadata JSON
            cube_file = out / f"{scene_id}.npz"
            import numpy as np

            np.savez_compressed(
                cube_file,
                cube=scene.cube,
                wavelengths_nm=scene.wavelengths_nm,
                state_mask=scene.state_mask,
                severity_mask=scene.severity_mask,
                days_to_symptoms=scene.days_to_symptoms,
                forecast_7d=scene.forecast_7d,
                forecast_14d=scene.forecast_14d,
                forecast_21d=scene.forecast_21d,
                farm_mask=scene.farm_mask,
                dem_m=scene.dem_m,
            )

            meta_file = out / f"{scene_id}_meta.json"
            meta_file.write_text(json.dumps(scene.metadata, indent=2), encoding="utf-8")
            progress.advance(task)
        else:
            task = progress.add_task(f"Generating time-series for [cyan]{scene_id}[/]...", total=4)
            series = generate_time_series(
                scene_id=scene_id,
                hotspot_acres=hotspot_acres,
                seed=seed,
                rows=rows,
                cols=cols,
            )
            for sc in series:
                fpath = out / f"{sc.scene_id}.npz"
                import numpy as np

                np.savez_compressed(
                    fpath,
                    cube=sc.cube,
                    wavelengths_nm=sc.wavelengths_nm,
                    state_mask=sc.state_mask,
                    severity_mask=sc.severity_mask,
                    days_to_symptoms=sc.days_to_symptoms,
                )
                mpath = out / f"{sc.scene_id}_meta.json"
                mpath.write_text(json.dumps(sc.metadata, indent=2), encoding="utf-8")
                progress.advance(task)

    console.print(f"[bold green]Successfully generated synthetic data in[/bold green] [dim]{out}[/dim]")


if __name__ == "__main__":
    app()

