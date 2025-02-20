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

def categorize_queries(input_file, output_file):
    evaluator = Evaluator()
    with open(input_file, 'r') as file:
        queries = file.readlines()
    
    with open(output_file, 'w') as file:
        for i, query in enumerate(queries):
            hardness = evaluator.eval_hardness(query)
            file.write(f"Query {i+1}: {hardness}\n")

if __name__ == "__main__":
    input_file = './data_ibm/healthcare_db/simplified_db/new_gold_queries.sql'
    output_file = './data_ibm/healthcare_db/simplified_db/new_query_classification.txt'
    categorize_queries(input_file, output_file)
    print(f"Queries categorized and written to {output_file}")
