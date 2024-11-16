import os
import json
import yara
from typing import Dict, List
from src.logging_config import logger
from pathlib import Path

def compile_all_rules(rules_path: Path) -> List[yara.Rules]:
    logger.info(f"Starting compilation of YARA rules from {rules_path}")
    try:
        rules_list = []
        
        # Compile each rule file individually
        for root, dirs, files in os.walk(rules_path):
            for file in files:
                if file.endswith('.yar') or file.endswith('.y4:0'):
                    full_path = os.path.join(root, file)
                    logger.debug(f"Processing rule file: {full_path}")
                    
                    try:
                        compiled_rule = yara.compile(filepath=full_path)
                        rules_list.append(compiled_rule)
                    except Exception as e:
                        logger.error(f"Error compiling rule {file}: {str(e)}")
        logger.info(f"Compilation of all {len(rules_list)} YARA rules completed")
        return rules_list
    except Exception as e:
        logger.error(f"Error compiling all rules: {str(e)}")
        return []

def scan_file(file_path: Path, compiled_rules: List[yara.Rules]) -> Dict[str, List[str]]:
    logger.info(f"Starting scan of file: {file_path}")
    try:
        matches = []
        for rule in compiled_rules:
            rule_matches = rule.match(file_path)
            matches.extend(rule_matches)
        
        result = {}
        for match in set(matches):  # Use set to remove duplicates
            rule_name = match.rule
            strings = [str(s) for s in match.strings]  # Convert bytes to string
            
            if rule_name not in result:
                result[rule_name] = []
            
            result[rule_name].extend(strings)
        logger.info(f"Scan of {file_path} completed")
        return result
    except Exception as e:
        logger.error(f"Error scanning file {file_path}: {str(e)}")
        return {}

def process_samples(samples_dir: Path, rules_path: Path):
    logger.info(f"Starting processing of samples in {samples_dir}")
    try:
        samples = os.listdir(samples_dir)
    except Exception as e:
        logger.error(f"Error accessing samples directory: {str(e)}")
        return

    compiled_rules = compile_all_rules(rules_path)
    if not compiled_rules:
        logger.warning("No valid rules were compiled. Skipping sample processing.")
        return

    results = []
    for sample in samples:
        sample_path = os.path.join(samples_dir, sample)
        try:
            yara_results = scan_file(sample_path, compiled_rules)
            results.append({
                "filename": sample,
                "results": yara_results
            })
            logger.info(f"Processed sample: {sample}")
        except Exception as e:
            logger.error(f"Error processing sample {sample}: {str(e)}")
    
    output_file = os.path.join(samples_dir, 'yara_results.json')
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"Results saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving results: {str(e)}")
