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


def createTable(er_file, model):
    name = model["metadata"]["name"]
    columns = list(model["columns"].keys())
    start = "{"
    end = "}"

    er_file.write(f"Table {name} {start} \n")

    for column in columns:
        column = model["columns"][column] 
        name = column["name"]
        dtype = column["type"]

        er_file.write(f"{name} {dtype} \n")
    er_file.write(f"{end} \n")
    
    
def createRelatonship(er_file, schema):
    tables = []
    for model in schema["models"]:
        tables.append(model["name"].upper())
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
                            er_file.write(f"Ref: {r1}.{r1_field} > {r2}.{r2_field} \n")
                            


def genereateERD(schema_path, catalog_path, erd_path):
    catalog, schema = loadModel(catalog_path, schema_path)
    model_names = catalog["nodes"]
    
    tables = [model["name"].upper() for model in schema["models"]]
    
    filename = erd_path
    
    with open(filename, "w") as er_file:
        for model_name in model_names:
            model = catalog["nodes"][model_name]
            if model["metadata"]["name"] in tables: 
                createTable(er_file, model)        
        createRelatonship(er_file, schema)