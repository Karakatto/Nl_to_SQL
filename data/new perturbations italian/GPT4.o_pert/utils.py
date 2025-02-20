import json
import os.path


def load_schema(schema_path):
    """Load schema from SQL file, focusing only on CREATE TABLE statements."""
    schema = []
    with open(schema_path, "r") as file:
        recording = False
        for line in file:
            if "CREATE TABLE" in line:
                recording = True
            if recording:
                if ";" in line:
                    schema.append(line)
                    recording = False
                else:
                    schema.append(line)
    return "".join(schema)


def load_all_schemas(databases_path):
    schemas_dict = {}
    databases_list = sorted(
        [d for d in os.listdir(databases_path) if d not in ["database_original", "README.md"]], key=str.casefold
    )

    for database in databases_list:

        schemas_database = []
        schema_file = os.path.join(databases_path, database, "schema.sql")

        with open(schema_file, "r") as file:
            recording = False
            for line in file:
                if line.startswith("CREATE TABLE") or line.startswith("PRAGMA"):
                    recording = True
                if recording:
                    schemas_database.append(line)
                if ";" in line:
                    recording = False

            schemas_dict[database] = "".join(schemas_database)

    return schemas_dict


def load_json_from_file(file_path):
    """Load JSON data from a file."""
    with open(file_path, "r") as file:
        return json.load(file)


def extract_sql(full_output):
    """Extract the SQL query using regex to accurately capture SQL statements."""
    splits = full_output.split(";", 1)
    query = "SELECT " + splits[0].strip().replace("\n", "")
    return query
