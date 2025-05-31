import os
from optimization.result_interpreter import ResultInterpreter
from visualization.result_visualizer import ResultVisualizer

def main():
    # Directory containing the result files
    results_dir = "./optimization/results"  # Current directory, adjust as needed
    
    # Get all .npz files in the directory
    result_files = [f for f in os.listdir(results_dir) if f.endswith('.npz')]
    
    if not result_files:
        print(f"No .npz files found in {results_dir}")
        return
        
    print("Available result files:")
    for i, file in enumerate(result_files):
        print(f"{i+1}. {file}")
    
    # Let user select a file
    try:
        selection = int(input("\nEnter the number of the file to visualize (0 for all): "))
        if selection == 0:
            files_to_process = result_files
        elif 1 <= selection <= len(result_files):
            files_to_process = [result_files[selection-1]]
        else:
            print("Invalid selection")
            return
    except ValueError:
        print("Please enter a valid number")
        return
    
    # Process selected file(s)
    for file in files_to_process:
        file_path = file
        print(f"Processing: {file}")
        
        search_result = ResultInterpreter().read_results(filename=file_path)
        rv = ResultVisualizer(search_result)
        rv.print_stats()
        
        if len(files_to_process) > 1:
            input("Press Enter for next visualization...")
            print("\n")

if __name__ == "__main__":
    main()