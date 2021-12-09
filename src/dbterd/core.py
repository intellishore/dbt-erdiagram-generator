import json
import yaml
import re

def loadModel(catalog_path, schema_path):
    """Loads the dbt catalog and schema. The schema selected is the one that will be used to generate the ERD diagram.

    Args:
        catalog_path (Path): Path to dbt catalog
        schema_path (Path): Path to dbt schema

    Returns:
        dict, dict: Return schema and catalog dicts.  
    """    
    with open(catalog_path) as f:
        catalog = json.load(f)


    with open(schema_path, 'r') as f:
        schema = yaml.safe_load(f)

    return catalog, schema


def createTable(dbml_path, model):
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
        name = column["name"]
        dtype = column["type"]

        dbml_path.write(f"{name} {dtype} \n")
    dbml_path.write(f"{end} \n")
    
    
def createRelatonship(dbml_path, schema):
    """Create a relationship in the dbml file. Loops over all columns to find relationship tests and saves them to the dbml file

    Args:
        dbml_path (dbml file): The file where to store the table
        schema (dbt schema): The dbt schema to extract relationships from 
    """    
    for model in schema["models"]:
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
                            


def genereatedbml(schema_path, catalog_path, dbml_path):
    """Create dbml file for a dbt schema

    Args:
        catalog_path (Path): Path to dbt catalog
        schema_path (Path): Path to dbt schema
        dbml_path (Path): Pat to save dbml file 
    """    
    catalog, schema = loadModel(catalog_path, schema_path)
    model_names = catalog["nodes"]
    
    tables = [model["name"].upper() for model in schema["models"]]
    
    with open(dbml_path, "w") as dbml_file:
        for model_name in model_names:
            model = catalog["nodes"][model_name]
            if model["metadata"]["name"] in tables: 
                createTable(dbml_file, model)        
        createRelatonship(dbml_file, schema)