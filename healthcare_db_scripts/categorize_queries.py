import os

def count_component1(sql):
    # Example logic for counting component1
    count = 0
    count += sql.lower().count("join")
    count += sql.lower().count("group by")
    return count

def count_component2(sql):
    # Example logic for counting component2
    count = 0
    count += sql.lower().count("having")
    count += sql.lower().count("intersect")
    count += sql.lower().count("union")
    count += sql.lower().count("except")
    return count

def count_others(sql):
    # Example logic for counting others
    count = 0
    count += sql.lower().count("distinct")
    count += sql.lower().count("order by")
    count += sql.lower().count("limit")
    return count

class Evaluator:
    """A simple evaluator"""
    def eval_hardness(self, sql):
        count_comp1_ = count_component1(sql)
        count_comp2_ = count_component2(sql)
        count_others_ = count_others(sql)

        if count_comp1_ <= 1 and count_others_ == 0 and count_comp2_ == 0:
            return "easy"
        elif (count_others_ <= 2 and count_comp1_ <= 1 and count_comp2_ == 0) or \
                (count_comp1_ <= 2 and count_others_ < 2 and count_comp2_ == 0):
            return "medium"
        elif (count_others_ > 2 and count_comp1_ <= 2 and count_comp2_ == 0) or \
                (2 < count_comp1_ <= 3 and count_others_ <= 2 and count_comp2_ == 0) or \
                (count_comp1_ <= 1 and count_others_ == 0 and count_comp2_ <= 1):
            return "hard"
        else:
            return "extra"

def categorize_and_sort_queries(nl_input_file, sql_input_file, nl_output_file, sql_output_file):
    evaluator = Evaluator()

    # Read NL statements and SQL queries
    with open(nl_input_file, 'r') as nl_file:
        nl_statements = nl_file.readlines()

    with open(sql_input_file, 'r') as sql_file:
        sql_queries = sql_file.readlines()

    # Check if the number of NL statements matches the number of SQL queries
    if len(nl_statements) != len(sql_queries):
        print("Error: The number of NL statements does not match the number of SQL queries.")
        return

    # Pair NL statements with SQL queries and categorize them
    queries = []
    for nl_statement, sql_query in zip(nl_statements, sql_queries):
        hardness = evaluator.eval_hardness(sql_query)
        queries.append((hardness, nl_statement.strip(), sql_query.strip()))

    # Sort the queries by hardness
    queries.sort(key=lambda x: ("easy medium hard extra".split().index(x[0]), x[1]))

    # Write the sorted NL statements and SQL queries to new files
    with open(nl_output_file, 'w') as nl_out_file, open(sql_output_file, 'w') as sql_out_file:
        for hardness, nl_statement, sql_query in queries:
            nl_out_file.write(f"{nl_statement}\n")
            sql_out_file.write(f"{sql_query}\n")

if __name__ == "__main__":
    nl_input_file = './data_ibm/healthcare_db/simplified_db/final_nl_statements.txt'
    sql_input_file = './data_ibm/healthcare_db/simplified_db/final_queries.sql'
    nl_output_file = './data_ibm/healthcare_db/simplified_db/new_gold_statements.txt'
    sql_output_file = './data_ibm/healthcare_db/simplified_db/new_gold_queries.sql'

    categorize_and_sort_queries(nl_input_file, sql_input_file, nl_output_file, sql_output_file)
    print(f"Queries categorized and written to {nl_output_file} and {sql_output_file}")
