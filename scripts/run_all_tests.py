#!/usr/bin/env python3
"""
Run all tests for the MoodReads project.

This script runs all tests, including unit tests, interface validation, and script tests.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
import time
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_command(command, description):
    """
    Run a command and log the output.
    
    Args:
        command: Command to run
        description: Description of the command
        
    Returns:
        True if the command succeeded, False otherwise
    """
    logger.info(f"Running {description}...")
    
    try:
        # Run the command
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            shell=True
        )
        
        # Log the output
        for line in process.stdout:
            print(line.strip())
        
        # Wait for the process to complete
        process.wait()
        
        # Check the exit code
        if process.returncode == 0:
            logger.info(f"{description} succeeded")
            return True
        else:
            logger.error(f"{description} failed with exit code {process.returncode}")
            return False
        
    except Exception as e:
        logger.error(f"Error running {description}: {str(e)}")
        return False

def run_unit_tests():
    """Run unit tests."""
    return run_command("python -m unittest discover tests", "unit tests")

def run_interface_validation():
    """Run interface validation."""
    return run_command("python scripts/validate_interfaces.py", "interface validation")

def run_script_tests():
    """Run script tests."""
    tests = [
        ("test_emotional_analyzer.py", "emotional analyzer tests"),
        ("test_process_batch.py", "process batch tests"),
        ("test_vector_embeddings.py", "vector embeddings tests")
    ]
    
    success = True
    for script, description in tests:
        if not run_command(f"python scripts/{script}", description):
            success = False
    
    return success

def run_integration_tests():
    """Run integration tests."""
    tests = [
        ("integration_test.py", "main integration tests"),
        ("test_process_batch_flow.py", "process batch flow tests"),
        ("test_vector_embeddings_flow.py", "vector embeddings flow tests")
    ]
    
    success = True
    for script, description in tests:
        if not run_command(f"python scripts/{script}", description):
            success = False
    
    return success

def run_small_integration_test():
    """Run a small integration test."""
    return run_command(
        "python scripts/test_advanced_scraper.py --category science-fiction --num-books 1 --db-name moodreads_test_integration --skip-analysis",
        "small integration test"
    )

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run all tests for the MoodReads project")
    parser.add_argument("--skip-unit-tests", action="store_true", help="Skip unit tests")
    parser.add_argument("--skip-interface-validation", action="store_true", help="Skip interface validation")
    parser.add_argument("--skip-script-tests", action="store_true", help="Skip script tests")
    parser.add_argument("--skip-integration-tests", action="store_true", help="Skip integration tests")
    parser.add_argument("--skip-small-integration-test", action="store_true", help="Skip small integration test")
    
    args = parser.parse_args()
    
    try:
        logger.info("Starting test run")
        start_time = time.time()
        
        # Track test results
        results = []
        
        # Run unit tests
        if not args.skip_unit_tests:
            unit_tests_success = run_unit_tests()
            results.append(("Unit tests", unit_tests_success))
        
        # Run interface validation
        if not args.skip_interface_validation:
            interface_validation_success = run_interface_validation()
            results.append(("Interface validation", interface_validation_success))
        
        # Run script tests
        if not args.skip_script_tests:
            script_tests_success = run_script_tests()
            results.append(("Script tests", script_tests_success))
        
        # Run integration tests
        if not args.skip_integration_tests:
            integration_tests_success = run_integration_tests()
            results.append(("Integration tests", integration_tests_success))
        
        # Run small integration test
        if not args.skip_small_integration_test:
            small_integration_test_success = run_small_integration_test()
            results.append(("Small integration test", small_integration_test_success))
        
        # Print summary
        logger.info("\n" + "=" * 50)
        logger.info("TEST RESULTS SUMMARY")
        logger.info("=" * 50)
        
        all_passed = True
        for name, result in results:
            status = "PASSED" if result else "FAILED"
            logger.info(f"{name}: {status}")
            if not result:
                all_passed = False
        
        logger.info("=" * 50)
        logger.info(f"OVERALL: {'PASSED' if all_passed else 'FAILED'}")
        logger.info("=" * 50)
        
        # Print timing
        elapsed_time = time.time() - start_time
        logger.info(f"Total test time: {elapsed_time:.2f} seconds")
        
        # Exit with appropriate code
        sys.exit(0 if all_passed else 1)
        
    except Exception as e:
        logger.error(f"Error during test run: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 