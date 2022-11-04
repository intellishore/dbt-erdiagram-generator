import click
from .core import generate_dbml
import subprocess


@click.command()
@click.argument("catalog_path", type=str, default="./target/catalog.json")
@click.argument("model_path", type=str, default="./models")
@click.argument("seed_path", type=str, default="./seeds")
@click.argument("erd_path", type=str, default="dbt_erd.dbml")
@click.argument("project_name", type=str, default="")
@click.argument("visualize", type=bool, default=False)
def cli(catalog_path, model_path, seed_path, erd_path, project_name, visualize):
    """ "Generate a DBML file from a dbt project and visualize it with dbdocs.io"""

    generate_dbml(catalog_path, model_path, seed_path, erd_path)

    if visualize:
        try:
            subprocess.run(f"dbdocs build {erd_path} --project {project_name}", text=True, shell=True)
        except Exception:
            print("dbdocs is not set up probably")
