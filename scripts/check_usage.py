#!/usr/bin/env python
import json
from pathlib import Path
import argparse
from datetime import datetime, timedelta
from tabulate import tabulate

def load_usage_stats(stats_file: Path = Path("stats/claude_usage.json")) -> dict:
    """Load usage statistics from the stats file."""
    if not stats_file.exists():
        return None
    
    try:
        with open(stats_file) as f:
            data = json.load(f)
            return {
                'date': data['date'],
                'calls': data['calls'],
                'tokens': data['tokens'],
                'cost': round(data['tokens'] * 0.000015, 4),  # $15 per million tokens
                'last_reset': datetime.fromisoformat(data['last_reset'])
            }
    except Exception as e:
        print(f"Error loading stats: {e}")
        return None

def format_stats(stats: dict) -> str:
    """Format stats for display."""
    if not stats:
        return "No usage statistics found."
    
    # Calculate time since last reset
    last_reset = stats['last_reset']
    time_since_reset = datetime.now() - last_reset
    
    headers = ['Metric', 'Value']
    table = [
        ['Date', stats['date']],
        ['API Calls Today', stats['calls']],
        ['Tokens Used', stats['tokens']],
        ['Estimated Cost', f"${stats['cost']:.4f}"],
        ['Last Reset', last_reset.strftime('%Y-%m-%d %H:%M:%S')],
        ['Time Since Reset', str(time_since_reset).split('.')[0]]  # Remove microseconds
    ]
    
    return tabulate(table, headers=headers, tablefmt='fancy_grid')

def main():
    parser = argparse.ArgumentParser(description='Check Claude API usage statistics')
    parser.add_argument('--stats-file', 
                       type=Path,
                       default=Path("stats/claude_usage.json"),
                       help='Path to the stats file')
    parser.add_argument('--json', 
                       action='store_true',
                       help='Output in JSON format')
    
    args = parser.parse_args()
    
    stats = load_usage_stats(args.stats_file)
    if not stats:
        print("No usage statistics found.")
        return
    
    if args.json:
        # Output as JSON
        print(json.dumps(
            {k: str(v) if isinstance(v, datetime) else v for k, v in stats.items()},
            indent=2
        ))
    else:
        # Output as formatted table
        print("\n=== Claude API Usage Statistics ===\n")
        print(format_stats(stats))
        
        # Add some helpful context
        cost = stats['cost']
        if cost > 0:
            remaining = 10.0 - cost  # Assuming $10 budget
            print(f"\nBudget Status:")
            print(f"  Remaining: ${remaining:.4f} of $10.00 ({(remaining/10)*100:.1f}% remaining)")

if __name__ == '__main__':
    main() 