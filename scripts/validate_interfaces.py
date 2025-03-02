#!/usr/bin/env python3
"""
Interface validation script for MoodReads.

This script checks that method calls across the codebase match the expected signatures,
helping to catch interface mismatches before runtime.
"""

import os
import sys
import inspect
import importlib
import logging
import ast
from typing import Dict, List, Set, Tuple, Any, Optional
from pathlib import Path
import argparse

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MethodCallVisitor(ast.NodeVisitor):
    """AST visitor to find method calls in Python code."""
    
    def __init__(self):
        self.method_calls = []
    
    def visit_Call(self, node):
        """Visit a function or method call node."""
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            # This looks like a method call (obj.method())
            obj_name = node.func.value.id
            method_name = node.func.attr
            
            # Get positional and keyword arguments
            args = []
            for arg in node.args:
                if isinstance(arg, ast.Constant):
                    args.append(arg.value)
                else:
                    args.append("*")  # Placeholder for non-constant args
            
            kwargs = {}
            for keyword in node.keywords:
                kwargs[keyword.arg] = "*"  # Placeholder for keyword values
            
            self.method_calls.append({
                'object': obj_name,
                'method': method_name,
                'args': args,
                'kwargs': kwargs,
                'lineno': node.lineno
            })
        
        # Continue visiting child nodes
        self.generic_visit(node)

def get_method_signatures(module_name: str) -> Dict[str, Dict[str, Any]]:
    """
    Get method signatures from a module.
    
    Args:
        module_name: Name of the module to inspect
        
    Returns:
        Dictionary mapping class names to dictionaries of method signatures
    """
    try:
        # Import the module
        module = importlib.import_module(module_name)
        
        # Find all classes in the module
        signatures = {}
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj.__module__ == module_name:
                class_methods = {}
                
                # Get all methods of the class
                for method_name, method in inspect.getmembers(obj):
                    if inspect.isfunction(method) and not method_name.startswith('_') or method_name == '__init__':
                        # Get the signature
                        sig = inspect.signature(method)
                        
                        # Store parameter info
                        params = []
                        for param_name, param in sig.parameters.items():
                            if param_name == 'self':
                                continue
                            
                            params.append({
                                'name': param_name,
                                'kind': str(param.kind),
                                'default': param.default is not inspect.Parameter.empty,
                                'annotation': str(param.annotation) if param.annotation is not inspect.Parameter.empty else None
                            })
                        
                        class_methods[method_name] = {
                            'params': params,
                            'return_annotation': str(sig.return_annotation) if sig.return_annotation is not inspect.Parameter.empty else None
                        }
                
                signatures[name] = class_methods
        
        return signatures
    
    except Exception as e:
        logger.error(f"Error getting method signatures from {module_name}: {str(e)}")
        return {}

def find_method_calls(file_path: str) -> List[Dict[str, Any]]:
    """
    Find method calls in a Python file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of method call information
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Skip files that are too large (likely generated or not relevant)
        if len(code) > 500000:  # Skip files larger than 500KB
            logger.warning(f"Skipping large file: {file_path}")
            return []
            
        tree = ast.parse(code)
        visitor = MethodCallVisitor()
        visitor.visit(tree)
        
        # Add file path to each method call
        for call in visitor.method_calls:
            call['file'] = file_path
        
        return visitor.method_calls
    except RecursionError:
        logger.error(f"Recursion error while parsing {file_path}. Skipping file.")
        return []
    except Exception as e:
        logger.error(f"Error parsing {file_path}: {str(e)}")
        return []

def validate_method_calls(signatures: Dict[str, Dict[str, Dict[str, Any]]], calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate method calls against signatures.
    
    Args:
        signatures: Dictionary mapping module names to class signatures
        calls: List of method calls to validate
        
    Returns:
        List of validation errors
    """
    errors = []
    
    for call in calls:
        obj_name = call['object']
        method_name = call['method']
        
        # Check if we have signature information for this class
        for module_name, classes in signatures.items():
            if obj_name in classes and method_name in classes[obj_name]:
                # Get the method signature
                method_sig = classes[obj_name][method_name]
                
                # Check number of positional arguments
                required_params = [p for p in method_sig['params'] if not p['default']]
                if len(call['args']) < len(required_params):
                    errors.append({
                        'file': call['file'],
                        'line': call['lineno'],
                        'object': obj_name,
                        'method': method_name,
                        'error': f"Missing required positional argument(s): {', '.join(p['name'] for p in required_params[len(call['args']):])}"
                    })
                
                # Check for unknown keyword arguments
                param_names = {p['name'] for p in method_sig['params']}
                for kwarg in call['kwargs']:
                    if kwarg not in param_names:
                        errors.append({
                            'file': call['file'],
                            'line': call['lineno'],
                            'object': obj_name,
                            'method': method_name,
                            'error': f"Unknown keyword argument: {kwarg}"
                        })
    
    return errors

def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Validate method interfaces in Python code.')
    parser.add_argument('--skip', action='store_true', help='Skip validation and exit with success')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Skip validation if requested
    if args.skip:
        logger.info("Skipping validation as requested")
        sys.exit(0)
    
    try:
        logger.info("Starting interface validation")
        
        # Get the project root directory
        project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Modules to check
        modules_to_check = [
            'moodreads.scraper.goodreads',
            'moodreads.analysis.claude',
            'moodreads.analysis.vector_embeddings',
            'moodreads.database.mongodb',
            'scripts.scrape_books'
        ]
        
        # Get method signatures
        logger.info("Getting method signatures")
        signatures = {}
        for module_name in modules_to_check:
            signatures[module_name] = get_method_signatures(module_name)
        
        # Find Python files to check
        logger.info("Finding Python files")
        python_files = []
        
        # Directories to exclude
        exclude_dirs = [
            '.moodreads-env',  # Virtual environment
            '.git',            # Git directory
            '__pycache__',     # Python cache
            'node_modules',    # Node modules if any
            'venv',            # Alternative virtual env name
            'env',             # Alternative virtual env name
        ]
        
        for root, dirs, files in os.walk(project_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        logger.info(f"Found {len(python_files)} Python files to analyze")
        
        # Find method calls
        logger.info("Finding method calls")
        all_calls = []
        total_files = len(python_files)
        
        for i, file_path in enumerate(python_files):
            if i % 10 == 0 or i == total_files - 1:
                logger.info(f"Processing file {i+1}/{total_files}: {os.path.basename(file_path)}")
            calls = find_method_calls(file_path)
            all_calls.extend(calls)
        
        # Validate method calls
        logger.info("Validating method calls")
        errors = validate_method_calls(signatures, all_calls)
        
        # Report errors
        if errors:
            logger.error(f"Found {len(errors)} interface errors:")
            for i, error in enumerate(errors, 1):
                logger.error(f"{i}. {error['file']}:{error['line']} - {error['object']}.{error['method']}: {error['error']}")
            sys.exit(1)
        else:
            logger.info("No interface errors found")
        
    except Exception as e:
        logger.error(f"Error during interface validation: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 