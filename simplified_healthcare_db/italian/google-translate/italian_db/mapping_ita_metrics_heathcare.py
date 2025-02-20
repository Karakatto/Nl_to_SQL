import os
import sqlite3
import multiprocessing
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from tqdm import tqdm
import re
from collections import defaultdict
from datetime import datetime

def count_component1(sql):
    count = 0
    count += sql.lower().count("join")
    count += sql.lower().count("group by")
    return count

def count_component2(sql):
    count = 0
    count += sql.lower().count("having")
    count += sql.lower().count("intersect")
    count += sql.lower().count("union")
    count += sql.lower().count("except")
    return count

def count_others(sql):
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

# Configuration
english_db_path = './data_ibm/healthcare_db/simplified_db/simplified_healthcare.db'
italian_db_path = './data_ibm/healthcare_db/simplified_db/italian/google-translate/italian_db/ita_schema_and_population/hospital_management_ita.db'
gold_standard_file = './data_ibm/healthcare_db/simplified_db/new_gold_queries.sql'
predicted_file = './predictions/healthcare/meta-llama/llama-3-8b-instruct/italian/pre_perturbation/pred_preperturbation_itaschema.sql'
questions_file = './data_ibm/healthcare_db/simplified_db/italian/google-translate/italian_healthcare.json'
timeout_seconds = 10
log_dir = './logs/healthcare_simple/italian/pre_perturbation/ita_schema_ita_pop2'

# Ensure the logging directory exists
os.makedirs(log_dir, exist_ok=True)

# Example translation mappings (to be filled in)
translation_map = {
    # Gender
    "Femmina": "Female",
    "Maschio": "Male",
    "F" : "Female",
    "M" : "Male",
    # Emergency Contact Relation
    "Marito" : "Husband",
    "Moglie": "Wife",
    "Sorella": "Sister",
    "Fratello": "Brother",
    # Departments
    "Emergenza": "Emergency",
    "Anestesiologia": "Anesthesiology",
    "Medicina d'emergenza" : "Emergency Medicine",
    "Cardiologia": "Cardiology",
    "Ortopedia": "Orthopedics",
    "Radiologia": "Radiology",
    "Neurologia": "Neurology",
    "Oncologia": "Oncology",
    "Pediatria": "Pediatrics",
    "Gastroenterologia": "Gastroenterology",
    "Urologia": "Urology",
    "Chirurgia generale": "General Surgery",
    # Medications
    "Aspirina": "Aspirin",
    "Ibuprofene": "Ibuprofen",
    "Paracetamolo": "Paracetamol",
    "Amoxicillina": "Amoxicillin",
    "Ciprofloxacina": "Ciprofloxacin",
    "Metformina": "Metformin",
    "Omeprazolo": "Omeprazole",
    "Lisinopril": "Lisinopril",
    "Amlodipina": "Amlodipine",
    "Metoprololo": "Metoprolol",
    "Atorvastatina": "Atorvastatin",
    "Simvastatina": "Simvastatin",
    "Clopidogrel": "Clopidogrel",
    "Warfarin": "Warfarin",
    "Eparina": "Heparin",
    "Enoxaparina": "Enoxaparin",
    "Insulina": "Insulin",
    "Albuterolo": "Albuterol",
    "Prednisone": "Prednisone",
    "Idrocortisone": "Hydrocortisone",
    "Morfina": "Morphine",
    "Vitamina D": "Vitamin D",
    "Tramadolo": "Tramadol",
    "Diazepam": "Diazepam",
    "Lorazepam": "Lorazepam",
    "Sertralina": "Sertraline",
    "Fluoxetina": "Fluoxetine",
    "Ketorolac": "Ketorolac",
    "Escitalopram": "Escitalopram",
    "Bupropione": "Bupropion",
    # Surgeries
    "Chirurgia di bypass dell'arteria coronaria": "Coronary Artery Bypass Surgery",
    "Intervento di bypass dell'arteria coronaria" : "Coronary Artery Bypass Surgery",
    "Angioplastica": "Angioplasty",
    "Sostituzione totale del ginocchio": "Total Knee Replacement",
    "Intervento di sostituzione dell'anca": "Hip Replacement Surgery",
    "Chirurgia dell'ernia del disco": "Herniated Disk Surgery",
    "Chirurgia del cancro del colon": "Colon Cancer Surgery",
    "Prostatectomia": "Prostatectomy",
    "Appendicectomia": "Appendectomy",
    "Intervento chirurgico di rimozione della cistifellea": "Gallbladder Removal Surgery",
    "Intervento chirurgico per la rimozione della cistifellea": "Gallbladder Removal Surgery",
    "Riduzione chiusa e fissazione": "Closed Reduction and Fixation",
    "Chirurgia del fegato": "Liver Surgery",
    "Intervento chirurgico di resezione polmonare": "Lung Resection Surgery",
    "Chirurgia di resezione polmonare" : "Lung Resection Surgery",
    "Chirurgia ortopedica traumatologica": "Orthopedic Trauma Surgery",
    "Rimozione della cisti": "Cyst Removal",
    "Chirurgia endoscopica dei seni paranasali": "Endoscopic Sinus Surgery",
    "Tiroidectomia": "Thyroidectomy",
    "Chirurgia renale": "Kidney Surgery",
    "Isterectomia": "Hysterectomy",
    "Chirurgia di bypass gastrico": "Gastric Bypass Surgery",
    "Intervento di bypass gastrico": "Gastric Bypass Surgery",
    "Colecistectomia laparoscopica": "Laparoscopic Cholecystectomy",
    # Treatments
    "Trasfusione di sangue": "Blood Transfusion",
    "Fisioterapia": "Physical Therapy",
    "Chemioterapia": "Chemotherapy",
    "Radioterapia": "Radiation Therapy",
    "Dialisi": "Dialysis",
    "Elettrocardiogramma": "Electrocardiogram",
    "Risonanza magnetica": "MRI Scan",
    "Scansione MRI" : "MRI Scan",
    "Scansione TC": "CT Scan",
    "TAC": "CT Scan",
    "Ultrasuoni": "Ultrasound",
    "raggi X": "X-rays",
    "Vaccinazione": "Vaccination",
    "Test allergologici": "Allergy Testing",
    "Cura delle ferite": "Wound Care",
    "Gestione del dolore": "Pain Management",
    "Operazione chirurgica": "Surgical Procedure",
    "Cateterizzazione cardiaca": "Cardiac Catheterization",
    "Endoscopia": "Endoscopy",
    "Colonscopia": "Colonoscopy",
    "Test di funzionalità polmonare": "Pulmonary Function Test",
    "Test della densità ossea": "Bone Density Test",
    # Procedures
    "Test della densità ossea": "Bone Density Test",
    "TAC": "CT Scan",
    "Risonanza magnetica": "MRI Scan",
    "Radioterapia": "Radiation Therapy",
    # Initial Diagnoses
    "Ictus": "Stroke",
    "Tumore al cervello": "Brain Tumor",
    "Diabete": "Diabetes",
    "Sindrome coronarica acuta": "Acute Coronary Syndrome",
    "Appendicite": "Appendicitis",
    "Asma": "Asthma",
    "Cancro alla vescica": "Bladder Cancer",
    "Tumore al cervello": "Brain Tumor",
    "Cataratta": "Cataract",
    "Cancro al colon": "Colon Cancer",
    "Insufficienza cardiaca congestizia": "Congestive Heart Failure",
    "BPCO (Broncopneumopatia Cronica Ostruttiva)": "Chronic Obstructive Pulmonary Disease (COPD)",
    "Coronaropatia": "Coronary Artery Disease",
    "Morbo di Crohn": "Crohn's Disease",
    "Paralisi cerebrale": "Cerebral Palsy",
    "Demenza": "Dementia",
    "Diabete mellito": "Diabetes Mellitus",
    "Infezione alle orecchie": "Ear Infection",
    "Endometriosi": "Endometriosis",
    "Epilessia": "Epilepsy",
    "Fibromialgia": "Fibromyalgia",
    "Femore fratturato": "Fractured Femur",
    "Calcoli biliari": "Gallstones",
    "Ulcera gastrica": "Gastric Ulcer",
    "Gotta": "Gout",
    "Ernia del disco": "Herniated Disk",
    "Epatite C": "Hepatitis C",
    "HIV/AIDS": "HIV/AIDS",
    "Ipertiroidismo": "Hyperthyroidism",
    "Ipertensione": "Hypertension",
    "Calcoli renali": "Kidney Stones",
    "Cancro ai polmoni": "Lung Cancer",
    "Emicrania": "Migraine",
    "Sclerosi multipla": "Multiple Sclerosis",
    "Obesità": "Obesity",
    "Apnea ostruttiva del sonno": "Obstructive Sleep Apnea",
    "Osteoartrite": "Osteoarthritis",
    "Cancro ovarico": "Ovarian Cancer",
    "Morbo di Parkinson": "Parkinson's Disease",
    "Cancro alla prostata": "Prostate Cancer",
    "Artrite reumatoide": "Rheumatoid Arthritis",
    "Anemia falciforme": "Sickle Cell Anemia",
    "Schizofrenia": "Schizophrenia",
    "Ictus": "Stroke",
    "Lupus eritematoso sistemico": "Systemic Lupus Erythematosus",
    "Lupus Eritematoso Sistemico": "Systemic Lupus Erythematosus",
    "Cancro alla tiroide": "Thyroid Cancer",
    "Colite ulcerosa": "Ulcerative Colitis"
     # Add other translations as needed
}


# Logging setup
detailed_log = []
error_log = []
unprocessed_queries = []
overall_metrics = {
    'Total Queries': 0,
    'Execution Exact Matches': 0,
    'String Exact Matches': 0,
    'Executable Queries': 0,
    'Executable Execution Matches': 0,
    'Execution Accuracy': 0.0,
    'String Accuracy': 0.0,
    'Average Cosine Similarity': 0.0,
    'Executable Execution Accuracy': 0.0,
    'Easy Execution Accuracy': 0.0,
    'Medium Execution Accuracy': 0.0,
    'Hard Execution Accuracy': 0.0,
    'Extra Execution Accuracy': 0.0,
    'Easy Queries': 0,
    'Medium Queries': 0,
    'Hard Queries': 0,
    'Extra Queries': 0
}
error_counts = defaultdict(int)


def translate(text):
    for key in translation_map:
        if key.lower() == text.lower():
            return translation_map[key]
    return text

def standardize_date(date_str):
    # Attempt to parse and standardize the date to YYYY-MM-DD
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    # Return the original string if no format matched
    return date_str

def normalize_and_sort_result(result):
    normalized = []
    for row in result:
        normalized_row = []
        for item in row:
            if isinstance(item, str):
                item = item.strip()
                standardized_item = standardize_date(item)
                if ',' in item:
                    terms = [term.strip() for term in item.split(',')]
                    normalized_terms = [translate(term) for term in terms]
                    normalized_row.append(', '.join(sorted(normalized_terms)))
                else:
                    normalized_row.append(translate(standardized_item))
            else:
                normalized_row.append(item)
        # Ensure the structure is consistent with expected format:
        # For example: (Gender, Count) should be (str, int)
        if len(normalized_row) == 2:
            if isinstance(normalized_row[0], str) and isinstance(normalized_row[1], int):
                normalized_row = (normalized_row[0], normalized_row[1])
            elif isinstance(normalized_row[1], str) and isinstance(normalized_row[0], int):
                normalized_row = (normalized_row[1], normalized_row[0])
            else:
                # If both are strings or both are numbers, log and skip reorder
                normalized_row = tuple(normalized_row)
        else:
            normalized_row = tuple(normalized_row)
        normalized.append(normalized_row)
    return sorted(normalized)


# Function to execute SQL with timeout
def worker(db_path, query, result_queue):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        result_queue.put(cursor.fetchall())
        conn.close()
    except Exception as e:
        result_queue.put(e)

def execute_sql_with_timeout(db_path, query, timeout):
    result_queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=worker, args=(db_path, query, result_queue))
    process.start()
    process.join(timeout)

    if process.is_alive():
        process.terminate()
        process.join()
        return "Timeout"

    result = result_queue.get()
    if isinstance(result, Exception):
        raise result

    return result

# Function to calculate cosine similarity using TfidfVectorizer
def cosine_similarity_score(a, b):
    vectorizer = TfidfVectorizer().fit_transform([a, b])
    vectors = vectorizer.toarray()
    return cosine_similarity(vectors)[0, 1]

# Load queries from SQL files
def load_queries(file_path):
    with open(file_path, 'r') as f:
        queries = f.readlines()
    return queries

# Function to categorize errors
def categorize_error(error):
    patterns = {
        "syntax_error": re.compile(r"syntax error", re.IGNORECASE),
        "no_such_table": re.compile(r"no such table", re.IGNORECASE),
        "no_such_column": re.compile(r"no such column", re.IGNORECASE),
        "misuse_of_aggregate": re.compile(r"misuse of aggregate", re.IGNORECASE),
        "timeout": re.compile(r"timeout", re.IGNORECASE),
        "ambiguous_column_name": re.compile(r"ambiguous column name", re.IGNORECASE),
        "no_such_function": re.compile(r"no such function", re.IGNORECASE),
        "incorrect_bindings": re.compile(r"Incorrect number of bindings", re.IGNORECASE),
    }

    for category, pattern in patterns.items():
        if pattern.search(error):
            return category
    return "other"

def analyze_errors(error_log):
    categorized_error_counts = defaultdict(int)
    specific_error_counts = defaultdict(int)

    for error in error_log:
        category = categorize_error(error)
        categorized_error_counts[category] += 1
        specific_error_counts[error] += 1

    return categorized_error_counts, specific_error_counts

def write_error_counts_to_file(categorized_errors, specific_errors, output_file):
    with open(output_file, 'w') as f:
        f.write("Categorized Error Counts:\n")
        for error_type, count in sorted(categorized_errors.items(), key=lambda item: item[1], reverse=True):
            f.write(f"{error_type}: {count}\n")
        
        f.write("\nSpecific Error Counts:\n")
        for error, count in sorted(specific_errors.items(), key=lambda item: item[1], reverse=True):
            f.write(f"{error}: {count}\n")

def main():
    start_time = datetime.now()
    evaluator = Evaluator()  # Instantiate the Evaluator

    gold_standard_queries = load_queries(gold_standard_file)
    predicted_queries = load_queries(predicted_file)
    with open(questions_file, 'r') as f:
        questions = json.load(f)

    if len(gold_standard_queries) != len(predicted_queries):
        raise ValueError("The number of queries in the gold standard file does not match the number in the predicted file.")

    for i, (gold_standard_query, predicted_query) in tqdm(enumerate(zip(gold_standard_queries, predicted_queries)), total=len(gold_standard_queries)):
        # ... [other parts of the loop]        
        gold_standard_query = gold_standard_query.strip()
        predicted_query = predicted_query.strip()
        question = questions[i]['question']

        hardness = evaluator.eval_hardness(gold_standard_query)  # Evaluate hardness

        gold_standard_result = None
        predicted_result = None
        gold_error = None
        pred_error = None

        try:
            gold_standard_result = execute_sql_with_timeout(english_db_path, gold_standard_query, timeout_seconds)
            if isinstance(gold_standard_result, list):
                gold_standard_result = normalize_and_sort_result(gold_standard_result)
        except Exception as e:
            gold_error = str(e)
            error_counts[gold_error] += 1
            error_log.append(f"Error executing gold query {i} on English database: {gold_error}")

        try:
            predicted_result = execute_sql_with_timeout(italian_db_path, predicted_query, timeout_seconds)
            if isinstance(predicted_result, list):
                predicted_result = normalize_and_sort_result(predicted_result)
        except Exception as e:
            pred_error = str(e)
            error_counts[pred_error] += 1
            error_log.append(f"Error executing predicted query {i} on Italian database: {pred_error}")

        exact_execution_match = gold_standard_result == predicted_result
        exact_string_match = predicted_query == gold_standard_query
        cosine_sim = cosine_similarity_score(predicted_query, gold_standard_query)

        overall_metrics['Total Queries'] += 1
        if exact_execution_match:
            overall_metrics['Execution Exact Matches'] += 1
        if exact_string_match:
            overall_metrics['String Exact Matches'] += 1
        overall_metrics['Average Cosine Similarity'] += cosine_sim

        if gold_standard_result is not None and predicted_result is not None:
            overall_metrics['Executable Queries'] += 1
            if exact_execution_match:
                overall_metrics['Executable Execution Matches'] += 1

        # Update hardness-specific metrics
        if hardness == 'easy':
            overall_metrics['Easy Queries'] += 1
            if exact_execution_match:
                overall_metrics['Easy Execution Accuracy'] += 1
        elif hardness == 'medium':
            overall_metrics['Medium Queries'] += 1
            if exact_execution_match:
                overall_metrics['Medium Execution Accuracy'] += 1
        elif hardness == 'hard':
            overall_metrics['Hard Queries'] += 1
            if exact_execution_match:
                overall_metrics['Hard Execution Accuracy'] += 1
        elif hardness == 'extra':
            overall_metrics['Extra Queries'] += 1
            if exact_execution_match:
                overall_metrics['Extra Execution Accuracy'] += 1

        detailed_log.append({
            'Question ID': i,
            'Question': question,
            'Gold standard query': gold_standard_query,
            'Predicted query': predicted_query,
            'Prediction result': predicted_result,
            'Gold standard result': gold_standard_result,
            'Exact execution match': exact_execution_match,
            'Cosine similarity': cosine_sim,
            'Exact string match': exact_string_match,
            'Gold error': gold_error,
            'Prediction error': pred_error,
            'Hardness': hardness  # Add hardness to the log
        })

        if gold_error or pred_error:
            unprocessed_queries.append((i, gold_standard_query, predicted_query, gold_error or pred_error))

    if overall_metrics['Total Queries'] > 0:
        overall_metrics['Execution Accuracy'] = round((overall_metrics['Execution Exact Matches'] / overall_metrics['Total Queries']) * 100, 2)
        overall_metrics['String Accuracy'] = round((overall_metrics['String Exact Matches'] / overall_metrics['Total Queries']) * 100, 2)
        overall_metrics['Average Cosine Similarity'] = round(overall_metrics['Average Cosine Similarity'] / overall_metrics['Total Queries'], 2)
        if overall_metrics['Executable Queries'] > 0:
            overall_metrics['Executable Execution Accuracy'] = round((overall_metrics['Executable Execution Matches'] / overall_metrics['Executable Queries']) * 100, 2)
        if overall_metrics['Easy Queries'] > 0:
            overall_metrics['Easy Execution Accuracy'] = round((overall_metrics['Easy Execution Accuracy'] / overall_metrics['Easy Queries']) * 100, 2)
        if overall_metrics['Medium Queries'] > 0:
            overall_metrics['Medium Execution Accuracy'] = round((overall_metrics['Medium Execution Accuracy'] / overall_metrics['Medium Queries']) * 100, 2)
        if overall_metrics['Hard Queries'] > 0:
            overall_metrics['Hard Execution Accuracy'] = round((overall_metrics['Hard Execution Accuracy'] / overall_metrics['Hard Queries']) * 100, 2)
        if overall_metrics['Extra Queries'] > 0:
            overall_metrics['Extra Execution Accuracy'] = round((overall_metrics['Extra Execution Accuracy'] / overall_metrics['Extra Queries']) * 100, 2)

    # Write detailed log
    with open(os.path.join(log_dir, 'detailed_log.json'), 'w') as f:
        json.dump(detailed_log, f, indent=4)

    # Write error log
    with open(os.path.join(log_dir, 'error_log.json'), 'w') as f:
        json.dump(error_log, f, indent=4)

    # Write unprocessed queries log
    with open(os.path.join(log_dir, 'unprocessed_queries.json'), 'w') as f:
        json.dump(unprocessed_queries, f, indent=4)

    # Write overall metrics
    with open(os.path.join(log_dir, 'overall_metrics.json'), 'w') as f:
        json.dump(overall_metrics, f, indent=4)

    # Analyze and write error counts
    categorized_error_counts, specific_error_counts = analyze_errors(error_log)
    write_error_counts_to_file(categorized_error_counts, specific_error_counts, os.path.join(log_dir, 'error_counts.txt'))

    end_time = datetime.now()
    elapsed_time = end_time - start_time

    print("\nOverall Metrics:")
    print(f"Total Queries: {overall_metrics['Total Queries']}")
    print(f"Execution Exact Matches: {overall_metrics['Execution Exact Matches']}")
    print(f"String Exact Matches: {overall_metrics['String Exact Matches']}")
    print(f"Execution Accuracy: {overall_metrics['Execution Accuracy']:.2f}%")
    print(f"String Accuracy: {overall_metrics['String Accuracy']:.2f}%")
    print(f"Average Cosine Similarity: {overall_metrics['Average Cosine Similarity']:.2f}")
    print(f"Executable Queries: {overall_metrics['Executable Queries']}")
    print(f"Executable Execution Matches: {overall_metrics['Executable Execution Matches']}")
    print(f"Executable Execution Accuracy: {overall_metrics['Executable Execution Accuracy']:.2f}%")
    print(f"Easy Execution Accuracy: {overall_metrics['Easy Execution Accuracy']:.2f}%")
    print(f"Medium Execution Accuracy: {overall_metrics['Medium Execution Accuracy']:.2f}%")
    print(f"Hard Execution Accuracy: {overall_metrics['Hard Execution Accuracy']:.2f}%")
    print(f"Extra Execution Accuracy: {overall_metrics['Extra Execution Accuracy']:.2f}%")
    print(f"Time taken: {elapsed_time}")

    print("\nError Counts:")
    for error_type, count in sorted(categorized_error_counts.items(), key=lambda item: item[1], reverse=True):
        print(f"{error_type}: {count}")

if __name__ == '__main__':
    main()
