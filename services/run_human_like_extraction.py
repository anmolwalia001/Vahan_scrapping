# run_human_like_extraction.py
"""
Simple runner for human-like extraction - runs ALL states automatically
"""

import logging
from services.extraction_service_human_like import start_human_like_extraction

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('human_extraction.log'),
        logging.StreamHandler()
    ]
)

def main():
    print("=" * 60)
    print("VAHAN HUMAN-LIKE EXTRACTION - ALL STATES")
    print("=" * 60)
    print()
    print("This extraction will process ALL states and simulates human behavior with:")
    print("- Sequential filter application (MOTOR CAR/CAB first, then ELECTRIC/EV)")
    print()
    
    print("Starting extraction for ALL STATES...")
    print("This will take several hours to complete.")
    print("You can monitor progress in the console and in 'human_extraction.log'")
    print("The browser will remain visible so you can see what's happening.")
    print()
    
    try:
        # Start extraction for ALL states (states=None means all states)
        summary = start_human_like_extraction(states=None)
        
        # Print results
        print("\n" + "=" * 60)
        print("EXTRACTION COMPLETED!")
        print("=" * 60)
        print(f"Duration: {summary['duration_minutes']:.1f} minutes ({summary['duration_minutes']/60:.1f} hours)")
        print(f"States processed: {summary['states_processed']}")
        print(f"Total RTOs: {summary['total_rtos']}")
        print(f"Files downloaded: {summary['files_downloaded']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        print(f"Browser restarts: {summary['browser_restarts']}")
        
        print(f"\nState-by-state results:")
        for state_result in summary['state_results']:
            success_rate = (state_result['files_downloaded'] / state_result['total_rtos'] * 100) if state_result['total_rtos'] > 0 else 0
            print(f"  {state_result['state_name']}: {state_result['files_downloaded']}/{state_result['total_rtos']} files ({success_rate:.1f}%)")
        
        print(f"\nFiles saved in: result/{summary.get('output_directory', 'extraction_output')}")
        
        # Summary statistics
        total_possible = sum(r['total_rtos'] for r in summary['state_results'])
        total_success = sum(r['files_downloaded'] for r in summary['state_results'])
        
        print(f"\nFINAL SUMMARY:")
        print(f"- Total possible files: {total_possible}")
        print(f"- Successfully downloaded: {total_success}")
        print(f"- Overall success rate: {(total_success/total_possible*100):.1f}%")
        print(f"- Time per state: {summary['duration_minutes']/summary['states_processed']:.1f} minutes average")
        
    except KeyboardInterrupt:
        print("\n\nExtraction stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\n\nExtraction failed with error: {e}")
        print("Check the log file 'human_extraction.log' for detailed error information")
        
        # Print any partial results if available
        try:
            import traceback
            print("\nFull error traceback:")
            traceback.print_exc()
        except:
            pass

if __name__ == "__main__":
    main()