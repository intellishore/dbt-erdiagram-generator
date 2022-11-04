import json
import yaml
import re
import glob
from typing import List, Tuple


def load_catalog(catalog_path: str) -> dict:
    """Loads the dbt catalog.json file

    Args:
        catalog_path (str): path to the catalog.json file

    Returns:
        dict: Parses the contents and returns the Dictionary equivalent
    """
    with open(catalog_path) as f:
        catalog = json.load(f)

    return catalog


def load_schemas(path: str) -> List[dict]:
    """Load all *.yaml files under the provided file path.py
    File search is recursive

    Args:
        path (str): file path to search under

    Returns:
        List[dict]: list of schemas
    """
    schemas = []
    files = glob.glob(path + "/**/*.yml", recursive=True)

    for file_path in files:
        with open(file_path, "r") as f:
            schema = yaml.safe_load(f)
            schemas.append(schema)

    return schemas


def load_model(catalog_path: str, model_path: str, seed_path: str) -> Tuple[dict, List[dict], List[dict]]:
    """Loads the dbt catalog and model+seeds schemas.

    Args:
        catalog_path (str): Path to dbt catalog
        model_path (str): Path to the root of the dbt model schemas
        seed_path (str): Path to the root of the dbt seed schemas

    Returns:
        Tuple[dict, List[dict], List[dict]]: catalog, model schemas and seed schemas
    """
    catalog = load_catalog(catalog_path)
    model_schemas = load_schemas(model_path)
    seed_schemas = load_schemas(seed_path)

    return catalog, model_schemas, seed_schemas


def create_table(dbml_path, model) -> None:
    """Create a table in the dbml file.

    Args:
        dbml_path (dbml file): The file where to store the table
        model (dbt model): The dbt model to extract the table and columns from
    """
    name = model["metadata"]["name"]
    columns = list(model["columns"].keys())
    start = "{"
    end = "}"

    dbml_path.write(f"Table {name} {start} \n")

    for column_name in columns:
        column = model["columns"][column_name]
        # some fields come back with casting, we only want the column name. E.g. RETAIL_AMOUNT::NUMBER(38,2)
        name = column["name"].split("::")[0]
        dtype = column["type"]

        dbml_path.write(f"{name} {dtype} \n")
    dbml_path.write(f"{end} \n")


def create_relationship(dbml_path: str, models: List[dict]) -> None:
    """Create a relationship in the dbml file. Loops over all columns to find relationship tests
    and saves them to the dbml file

    Args:
        dbml_path (str): The file where to save the table dbml
        models (List[dict]): The List of dbt model schemas to extract relationships from
    """
    for model in models:
        for column in model["columns"]:
            if "tests" in column:
                tests = column["tests"]
                for test in tests:
                    if isinstance(test, dict):
                        if "relationships" in test:
                            relationship = test["relationships"]
                            r1 = relationship["to"].upper()
                            r1 = re.findall(r"('.*?')", r1, re.DOTALL)[0].replace("'", "")
                            r1_field = relationship["field"].upper()

                            r2 = model["name"].upper()
                            r2_field = column["name"].upper()
                            dbml_path.write(f"Ref: {r1}.{r1_field} > {r2}.{r2_field} \n")


def generate_dbml(catalog_path: str, model_path: str, seed_path: str, dbml_path: str) -> None:
    """Create dbml file for a dbt schema

    Args:
        catalog_path (str): Path to dbt catalog
        model_path (str): Path to dbt model schemas
        seed_path (str): Path to dbt seed schemas
        dbml_path (str): Path to save dbml file to
    """
    catalog, model_schemas, seed_schemas = load_model(catalog_path, model_path, seed_path)

    model_names = catalog["nodes"]
    models = [schema["models"][0] for schema in model_schemas if schema.get("models")]
    seeds = [schema["seeds"][0] for schema in seed_schemas if schema.get("seeds")]

    tables = [model["name"].upper() for model in models]
    seed_tables = [model["name"].upper() for model in seeds]
    tables.extend(seed_tables)

    with open(dbml_path, "w") as dbml_file:
        for model_name in model_names:
            model = catalog["nodes"][model_name]
            if model["metadata"]["name"] in tables:
                create_table(dbml_file, model)

        create_relationship(dbml_file, models)
        create_relationship(dbml_file, seeds)
