#!/usr/bin/env python3
"""
Test script to simulate the inspection process without running the Streamlit app.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.inspection_service import InspectionService
import time

def simulate_inspection():
    """Simulate a complete inspection process."""
    # Initialize the inspection service
    service = InspectionService()
    
    # Start inspection for a small part with scratches inspection
    print("\n=== Starting Inspection ===")
    success = service.start_inspection("Small Part", "scratches_small")
    if not success:
        print("Failed to start inspection")
        return
        
    print(f"\nInspection sequence created with {len(service.inspection_sequence)} steps")
    print("Inspection points:")
    for i, point in enumerate(service.inspection_sequence):
        print(f"\nStep {i+1}:")
        print(f"  Position: {point['position']}")
        print(f"  Orientation: {point['orientation']}")
        print(f"  Type: {point['type']}")
        print(f"  Description: {point['description']}")
    
    # Execute all steps
    print("\n=== Executing Inspection Steps ===")
    while service.current_step < len(service.inspection_sequence):
        print(f"\nExecuting step {service.current_step + 1} of {len(service.inspection_sequence)}")
        success = service.execute_step()
        
        if success:
            # Get the result of the last step
            result = service.results[-1]
            print(f"Step completed successfully:")
            print(f"  Type: {result['type']}")
            print(f"  Status: {result['result']['status']}")
            print(f"  Description: {result['result']['description']}")
            if result['result']['defects']:
                print(f"  Defects found: {result['result']['defects']}")
        else:
            print("Step execution failed")
            break
            
        # Add a small delay to simulate real inspection time
        time.sleep(1)
    
    # Print final results
    print("\n=== Inspection Complete ===")
    print(f"Total steps executed: {len(service.results)}")
    print("\nResults summary:")
    for result in service.results:
        print(f"\nStep {result['step'] + 1}:")
        print(f"  Type: {result['type']}")
        print(f"  Status: {result['result']['status']}")
        print(f"  Description: {result['result']['description']}")
        if result['result']['defects']:
            print(f"  Defects found: {result['result']['defects']}")

if __name__ == "__main__":
    simulate_inspection() 