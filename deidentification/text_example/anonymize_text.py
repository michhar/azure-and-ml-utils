"""
This script works to anonymize a text document.  Please ensure you
evaluate the results carefully before using for production systems.
"""
import argparse
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_analyzer.nlp_engine import NerModelConfiguration, NlpEngineProvider
from presidio_analyzer.nlp_engine import StanzaNlpEngine, TransformersNlpEngine


def main(model_choice, filename, output_file):


    # 1. Sample text - read
    with open(filename, 'r') as f:
        input_text = f.read()

    # ner_model_configuration = NerModelConfiguration(model_to_presidio_entity_mapping=entity_mapping)

    if model_choice == "stanza":
        # Define which model to use
        model_config = [{"lang_code": "en", "model_name": "en"}]
        # Create the Stanza NLP Engine based on this configuration
        nlp_engine = StanzaNlpEngine(models=model_config, ner_model_configuration=configuration)
    elif model_choice == "spacy":
        # Create NLP engine based on configuration
        configuration = {
            "nlp_engine_name": "spacy",
            "models": [
                {"lang_code": "en", "model_name": "en_core_web_lg"},
            ],
        }
        provider = NlpEngineProvider(nlp_configuration=configuration)
        nlp_engine = provider.create_engine()
    elif model_choice == "hugging_face":
        # Transformer model config
        model_config = [
            {"lang_code": "en",
            "model_name": {
                "spacy": "en_core_web_sm", # for tokenization, lemmatization
                "transformers": "StanfordAIMI/stanford-deidentifier-base" # for NER
            }
        }]

        # Entity mappings between the model's and Presidio's
        mapping = dict(
            PER="PERSON",
            LOC="LOCATION",
            ORG="ORGANIZATION",
            AGE="AGE",
            ID="ID",
            EMAIL="EMAIL",
            DATE="DATE_TIME",
            PHONE="PHONE_NUMBER",
            PERSON="PERSON",
            LOCATION="LOCATION",
            GPE="LOCATION",
            ORGANIZATION="ORGANIZATION",
            NORP="NRP",
            PATIENT="PERSON",
            STAFF="PERSON",
            HOSP="LOCATION",
            PATORG="ORGANIZATION",
            TIME="DATE_TIME",
            HCW="PERSON",
            HOSPITAL="LOCATION",
            FACILITY="LOCATION",
            VENDOR="ORGANIZATION",
        )

        labels_to_ignore = ["O"]

        ner_model_configuration = NerModelConfiguration(
            model_to_presidio_entity_mapping=mapping,
            alignment_mode="expand", # "strict", "contract", "expand"
            aggregation_strategy="max", # "simple", "first", "average", "max"
            labels_to_ignore = labels_to_ignore)

        nlp_engine = TransformersNlpEngine(
            models=model_config,
            ner_model_configuration=ner_model_configuration)
        
    else:
        return NotImplementedError

    # # Run it as part of Presidio's AnalyzerEngine
    # call_analyzer_and_print_results(stanza_nlp_engine)

    # 2. Initialize the Analyzer and Anonymizer Engines
    # The analyzer engine loads the NLP model (spaCy by default) and PII recognizers
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
    anonymizer = AnonymizerEngine()

    # 3. Analyze the text to find PII entities
    # You can specify which entities to look for or let the analyzer use its default set
    # Common entities include PERSON, LOCATION, PHONE_NUMBER, DATE_TIME, etc.
    analyzer_results = analyzer.analyze(text=input_text, language='en')

    # 4. Anonymize the identified entities
    # Define an operator configuration (optional, uses default if not provided)
    # The default operator replaces the PII with its entity type, e.g., <PHONE_NUMBER>
    # You can customize the operators. For example, to use a specific replacement value:
    operator_config = {
        "DATE_TIME": OperatorConfig("keep"), # Keep dates
        "AGE": OperatorConfig("keep") 
    }

    anonymized_results = anonymizer.anonymize(
        text=input_text,
        analyzer_results=analyzer_results,
        operators=operator_config # Use the custom operators
    )

    # 5. Save the anonymized text
    with open(output_file, 'w') as f:
        f.write(anonymized_results.text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A script that anonymizes text in a file."
    )
    parser.add_argument("-f", "--file",
                        required=True,
                        help="The name of the file to process.")
    parser.add_argument("-m", "--model",
                        required=True,
                        help="Model name (spacy, stanza, hugging_face).")
    parser.add_argument("-o", "--output",
                        required=False,
                        default="text_anonymized.md",
                        help="Output file path for anonymized text (default: text_anonymized.md).")
    args = parser.parse_args()

    main(model_choice=args.model, filename=args.file, output_file=args.output)
