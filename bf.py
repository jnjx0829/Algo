import itertools
import time
import tracemalloc

# Data extracted based on the provided Distance and Time Matrices
# Format: 'Start': {'End': (Distance_in_km, Time_in_min)}
route_data = {
    'WH':   {'KW': (0.2, 1),  'IS': (0.95, 3), 'CS': (0.55, 2), 'CHM': (0.8, 2),  'BCM': (1.2, 3),  'TA': (9.8, 25),  'SLAB': (10.4, 26), 'BG': (10.0, 25)},
    'KW':   {'WH': (1.1, 3),  'IS': (0.75, 2), 'CS': (1.6, 4),  'CHM': (1.5, 4),  'BCM': (1.0, 3),  'TA': (9.2, 23),  'SLAB': (9.4, 24),  'BG': (11.0, 28)},
    'IS':   {'WH': (0.8, 2),  'KW': (1.0, 3),  'CS': (1.3, 4),  'CHM': (1.3, 4),  'BCM': (0.75, 2), 'TA': (8.9, 23),  'SLAB': (10.2, 26), 'BG': (10.8, 27)},
    'CS':   {'WH': (0.13, 1), 'KW': (0.3, 1),  'IS': (1.0, 3),  'CHM': (0.65, 2), 'BCM': (1.3, 4),  'TA': (9.2, 23),  'SLAB': (9.7, 25),  'BG': (10.4, 26)},
    'CHM':  {'WH': (0.65, 2), 'KW': (0.5, 2),  'IS': (1.3, 4),  'CS': (0.4, 1),   'BCM': (1.3, 4),  'TA': (9.4, 24),  'SLAB': (10.0, 25), 'BG': (10.2, 26)},
    'BCM':  {'WH': (1.7, 5),  'KW': (2.0, 5),  'IS': (1.4, 4),  'CS': (2.3, 6),   'CHM': (2.2, 6),  'TA': (8.6, 22),  'SLAB': (9.7, 25),  'BG': (10.4, 26)},
    'TA':   {'WH': (10.1, 26),'KW': (10.1, 26),'IS': (10.8, 27),'CS': (10.0, 25), 'CHM': (10.0, 25),'BCM': (10.9, 28),'SLAB': (1.2, 3),   'BG': (2.1, 6)},
    'SLAB': {'WH': (10.1, 26),'KW': (10.1, 26),'IS': (10.8, 27),'CS': (10.0, 25), 'CHM': (10.0, 25),'BCM': (10.9, 28),'TA': (0.7, 2),     'BG': (2.1, 6)},
    'BG':   {'WH': (9.4, 24), 'KW': (9.1, 23), 'IS': (11.0, 28),'CS': (9.1, 23),  'CHM': (9.6, 24), 'BCM': (10.4, 26),'TA': (2.1, 6),     'SLAB': (2.6, 7)}
}

def brute_force_tsp(data_dict, start_node):
    # Get all locations except the start node
    destinations = [loc for loc in data_dict.keys() if loc != start_node]
    
    best_dist = float('inf')
    best_time = float('inf')
    best_route = None

    # Generate all permutations (40,320 possible routes for 8 destinations)
    # We omit saving them all to a list to save memory, iterating instead (Requirement 1 & 3)
    all_routes = itertools.permutations(destinations)

    for perm in all_routes:
        current_dist = 0
        current_time = 0
        
        # Start at WH
        prev_node = start_node
        
        for next_node in perm:
            dist, time_taken = data_dict[prev_node][next_node]
            current_dist += dist
            current_time += time_taken
            prev_node = next_node
            
        # Return to WH
        dist, time_taken = data_dict[prev_node][start_node]
        current_dist += dist
        current_time += time_taken
        
        # Check if it's the best route
        # We optimize for Distance first. If distance is a tie, optimize for time.
        if current_dist < best_dist or (current_dist == best_dist and current_time < best_time):
            best_dist = current_dist
            best_time = current_time
            best_route = perm

    # Format the detailed path string
    detailed_path = f"[{start_node}] ---> " + " ---> ".join(f"[{loc}]" for loc in best_route) + f" ---> [{start_node}]"
    
    return detailed_path, best_dist, best_time

if __name__ == "__main__":
    # Start tracking time and memory
    start_time_exec = time.perf_counter()
    tracemalloc.start()
    
    print("Running Brute Force Algorithm. Checking all permutations...")
    
    best_path, best_distance, best_time = brute_force_tsp(route_data, 'WH')

    print("\n🏆 BEST BRUTE FORCE COMPLETE ROUTE 🏆")
    print(f"Detailed Path:        {best_path}")
    print(f"Grand Total:   {round(best_distance, 2)} km in {best_time} mins")
    print("-" * 45)
    
    # Stop tracking time and memory
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    end_time_exec = time.perf_counter()
    
    print("\n--- PERFORMANCE METRICS ---")
    print(f"Time Taken:  {end_time_exec - start_time_exec:.6f} seconds")
    print(f"Memory Used: {peak / 10**6:.6f} MB (Peak)")