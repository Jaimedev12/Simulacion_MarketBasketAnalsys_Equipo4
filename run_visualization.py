from optimization.result_interpreter import ResultInterpreter
from visualization.result_visualizer import ResultVisualizer

def main():
    search_result = ResultInterpreter().read_results(filename="ideal_layout.npz")
    rv = ResultVisualizer(search_result)
    rv.visualize()

if __name__ == "__main__":
    main()