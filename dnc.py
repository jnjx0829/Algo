import itertools
import pandas as pd
import time
import tracemalloc

# --- 1. Complete Data Dictionary ---
# Format: 'Start': {'End': (Distance in km, Time in min)}
route_data = {
    'WH':  {'KW': (1.1, 3), 'IS': (0.8, 2), 'CS': (0.13, 1), 'CHM': (0.65, 2), 'BCM': (1.7, 5), 'TA': (10.1, 26), 'SLAB': (10.1, 26), 'BG': (9.4, 24)},
    'KW':  {'WH': (0.2, 1), 'IS': (1.0, 3), 'CS': (0.3, 1), 'CHM': (0.5, 2)},
    'IS':  {'WH': (0.95, 3), 'KW': (0.75, 2), 'CS': (1.0, 3), 'CHM': (1.3, 4)},
    'CS':  {'WH': (0.55, 2), 'KW': (1.6, 4), 'IS': (1.3, 4), 'CHM': (0.4, 1)},
    'CHM': {'WH': (0.8, 2), 'KW': (1.5, 4), 'IS': (1.3, 4), 'CS': (0.65, 2)},
    'BCM': {'WH': (1.2, 3)},
    'TA':  {'WH': (9.8, 25), 'SLAB': (0.7, 2), 'BG': (2.1, 6)},
    'SLAB':{'WH': (10.4, 26), 'TA': (1.2, 3), 'BG': (2.6, 7)},
    'BG':  {'WH': (10.0, 25), 'TA': (2.1, 6), 'SLAB': (2.1, 6)}
}

# --- 2. Subset Definitions ---
subset_1 = ['KW', 'IS', 'CS', 'CHM']
subset_2 = ['BCM']
subset_3 = ['TA', 'SLAB', 'BG']

# --- 3. Route Processing Function ---
def create_subset_table(locations, data_dict):
    """
    Generates permutations for a given subset and returns a clean Pandas DataFrame.
    """
    results_list = []
    
    # Handle single-location subsets
    if len(locations) <= 1:
        results_list.append({
            'Route Sequence': locations[0],
            'Total Distance (km)': 0,
            'Total Time (min)': 0
        })
        return pd.DataFrame(results_list)

    # Generate all permutations
    routes = list(itertools.permutations(locations))

    # Calculate distance and time for each route
    for route in routes:
        route_str = " -> ".join(route)
        total_dist = 0.0
        total_time = 0
        is_valid = True
        
        for i in range(len(route) - 1):
            start = route[i]
            end = route[i+1]
            
            # Check if connection exists
            if start in data_dict and end in data_dict[start]:
                total_dist += data_dict[start][end][0]
                total_time += data_dict[start][end][1]
            else:
                is_valid = False
                break
                
        # Append ONLY valid routes to keep the table clean
        if is_valid:
            results_list.append({
                'Route Sequence': route_str,
                'Total Distance (km)': round(total_dist, 2),
                'Total Time (min)': total_time
            })
            
    # Convert to DataFrame and sort by shortest distance first
    df = pd.DataFrame(results_list)
    if not df.empty:
        df = df.sort_values(by=['Total Distance (km)', 'Total Time (min)'], ascending=[True, True])
        
    return df

def print_optimal_route(df, subset_name):
    """
    Grabs the very first row of the sorted DataFrame, which represents the optimal route.
    """
    if not df.empty:
        # .iloc[0] gets the first row (the best route because the df is sorted)
        optimal = df.iloc[0]
        print(f"\n✅ Optimal Route for {subset_name}:")
        print(f"   Sequence: {optimal['Route Sequence']}")
        print(f"   Distance: {optimal['Total Distance (km)']} km")
        print(f"   Time:     {optimal['Total Time (min)']} min")
    else:
        print(f"\n❌ No valid routes found for {subset_name}.")


# --- 5. Inter-Subset Jump Data ---
# Format: Start_Subset: {End_Subset: (Distance, Time, Start_Node, End_Node)}
inter_subset_jumps = {
    1: {2: (2.2, 6, 'CHM', 'BCM'), 3: (9.6, 24, 'CHM', 'BG')},
    2: {1: (0.75, 2, 'BCM', 'IS'), 3: (10.4, 26, 'BCM', 'BG')},
    3: {1: (10.2, 26, 'SLAB', 'IS'), 2: (9.7, 25, 'SLAB', 'BCM')}
}

# --- 6. Complete Route Processing ---
def generate_complete_routes(df1, df2, df3, jump_data):
    """
    Combines the best route from each subset with the inter-subset jump distances
    to find the overall optimal complete route.
    """
    if df1.empty or df2.empty or df3.empty:
        return pd.DataFrame() 
        
    # Extract optimal subset stats (first row)
    opt1 = df1.iloc[0]
    opt2 = df2.iloc[0]
    opt3 = df3.iloc[0]
    
    subsets = {
        1: {'dist': opt1['Total Distance (km)'], 'time': opt1['Total Time (min)'], 'seq': opt1['Route Sequence']},
        2: {'dist': opt2['Total Distance (km)'], 'time': opt2['Total Time (min)'], 'seq': opt2['Route Sequence']},
        3: {'dist': opt3['Total Distance (km)'], 'time': opt3['Total Time (min)'], 'seq': opt3['Route Sequence']}
    }
    
    # Generate all permutations of visiting Subsets 1, 2, and 3
    subset_orders = list(itertools.permutations([1, 2, 3]))
    complete_routes = []
    
    for order in subset_orders:
        total_dist = 0.0
        total_time = 0
        
        # Start with the first subset
        current_sub = order[0]
        total_dist += subsets[current_sub]['dist']
        total_time += subsets[current_sub]['time']
        
        route_desc = f"[S{current_sub}: {subsets[current_sub]['seq']}]"
        
        is_valid = True
        for i in range(len(order) - 1):
            current_sub = order[i]
            next_sub = order[i+1]
            
            # Check if jump data exists
            if next_sub in jump_data[current_sub]:
                jump_dist, jump_time, j_start, j_end = jump_data[current_sub][next_sub]
                
                # Add jump distance & time
                total_dist += jump_dist
                total_time += jump_time
                
                # --- UPDATED FORMATTING HERE ---
                # Replaced the long (Jump: X to Y | Zkm) string with just an arrow
                route_desc += " ---> " 
                
                # Add the next subset's internal distance & time
                total_dist += subsets[next_sub]['dist']
                total_time += subsets[next_sub]['time']
                route_desc += f"[S{next_sub}: {subsets[next_sub]['seq']}]"
            else:
                is_valid = False
                break
                
        if is_valid:
            complete_routes.append({
                'Route Order': " -> ".join([str(x) for x in order]),
                'Detailed Path': route_desc,
                'Total Distance (km)': round(total_dist, 2),
                'Total Time (min)': total_time
            })
            
    df_complete = pd.DataFrame(complete_routes)
    if not df_complete.empty:
        df_complete = df_complete.sort_values(by=['Total Distance (km)', 'Total Time (min)'], ascending=[True, True])
    return df_complete


# --- 4. Execution and Export ---
if __name__ == "__main__":
    # Start tracking time and memory
    start_time_exec = time.perf_counter()
    tracemalloc.start()
    
    print("Calculating subset routes...")
    
    # Generate tables for each subset
    df_subset_1 = create_subset_table(subset_1, route_data)
    df_subset_2 = create_subset_table(subset_2, route_data)
    df_subset_3 = create_subset_table(subset_3, route_data)
    
    print("\n--- OPTIMAL ROUTES SUMMARY ---")
    print_optimal_route(df_subset_1, "Subset 1 (Upper South Bank)")
    print_optimal_route(df_subset_2, "Subset 2 (Lower South Bank)")
    print_optimal_route(df_subset_3, "Subset 3 (North Bank)")
    print("-" * 30)

    # --- Generate Complete Routes ---
    df_complete_routes = generate_complete_routes(df_subset_1, df_subset_2, df_subset_3, inter_subset_jumps)
    
    if not df_complete_routes.empty:
        best_complete = df_complete_routes.iloc[0]
        print("\n🏆 BEST COMPLETE ROUTE 🏆")
        print(f"Subset Order:  {best_complete['Route Order']}")
        print(f"Detailed Path: {best_complete['Detailed Path']}")
        print(f"Grand Total:   {best_complete['Total Distance (km)']} km in {best_complete['Total Time (min)']} mins")
        print("-" * 30)
        
        # --- 7. Hotel to Hotel Complete Route ---
        order = [int(x) for x in best_complete['Route Order'].split(' -> ')]
        seqs = {
            1: df_subset_1.iloc[0]['Route Sequence'],
            2: df_subset_2.iloc[0]['Route Sequence'],
            3: df_subset_3.iloc[0]['Route Sequence']
        }
        
        first_node = seqs[order[0]].split(' -> ')[0]
        last_node = seqs[order[-1]].split(' -> ')[-1]
        
        start_dist, start_time = route_data['WH'][first_node]
        end_dist, end_time = route_data[last_node]['WH']
        
        total_dist_with_hotel = best_complete['Total Distance (km)'] + start_dist + end_dist
        total_time_with_hotel = best_complete['Total Time (min)'] + start_time + end_time
        
        hotel_detailed_path = f"[Hotel: WH] ---> {best_complete['Detailed Path']} ---> [Hotel: WH]"
        
        print("\n🏨 FULL ROUTE WITH HOTEL (Round Trip) 🏨")
        print(f"Detailed Path: {hotel_detailed_path}")
        print(f"Grand Total:   {round(total_dist_with_hotel, 2)} km in {total_time_with_hotel} mins")
        print("-" * 30)
    
    # Stop tracking time and memory BEFORE Excel export (for fair algorithm comparison)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    end_time_exec = time.perf_counter()
    
    print("\n--- PERFORMANCE METRICS ---")
    print(f"Time Taken:  {end_time_exec - start_time_exec:.6f} seconds")
    print(f"Memory Used: {peak / 10**6:.6f} MB (Peak)")
    
    output_filename = "Kuching_Route_Analysis.xlsx"
    
    # Export to Excel, placing each table in its own separate sheet
    try:
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
            df_subset_1.to_excel(writer, sheet_name="Subset 1 (Upper South Bank)", index=False)
            df_subset_2.to_excel(writer, sheet_name="Subset 2 (Lower South Bank)", index=False)
            df_subset_3.to_excel(writer, sheet_name="Subset 3 (North Bank)", index=False)
            
            # --- Export Complete Routes to Sheet 4 ---
            if not df_complete_routes.empty:
                df_complete_routes.to_excel(writer, sheet_name="Complete Routes", index=False)
            
        print(f"\nSuccess! 4 full tables have been exported to '{output_filename}' in your current folder.")
    except Exception as e:
        print(f"\nError saving to Excel: {e}\n(Make sure the Excel file isn't currently open on your computer!)")