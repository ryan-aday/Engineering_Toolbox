import numpy as np
from CoolProp.CoolProp import PropsSI
from material_data_scraper import retrieve_material_data, levenshtein_distance  # Import scraper and Levenshtein function

# Function to convert atm to Pa
def atm_to_pa(atm):
    """Convert pressure from atm to Pa."""
    return atm * 101325  # 1 atm = 101325 Pa

# Function to calculate inner radius of the pipe
def calculate_inner_radius(outer_diameter, thickness):
    """Calculate inner radius based on outer diameter and pipe thickness."""
    return (outer_diameter / 2) - thickness

# Function to calculate hoop stress in a pipe
def calculate_hoop_stress(Pi, Po, D, thickness):
    """Calculate hoop stress using the equation σh = ((Pi - Po) * D) / (2 * t)."""
    return ((Pi - Po) * D) / (2 * thickness)

# Function to get the dynamic viscosity of a fluid at a given temperature and pressure
def get_viscosity(fluid="Water", temperature=298.15, pressure=101325):
    """Get the dynamic viscosity of a fluid using CoolProp."""
    viscosity = PropsSI('V', 'T', temperature, 'P', pressure, fluid)  # 'V' is dynamic viscosity
    return viscosity

# Function to calculate the correction factor 'i'
def calculate_correction_factor(bend_radius, thickness, mean_radius):
    """Calculate the correction factor 'i' based on bend parameters."""
    h = (bend_radius * thickness) / (mean_radius ** 2)
    correction_factor = max(0.9 / (h ** (2/3)), 1)
    return correction_factor

# Function to get the closest match for yield strength using Levenshtein distance if direct match is not found
def get_yield_strength_from_scraper(material_name):
    """Retrieve the yield strength from the scraped material data."""
    # Use the material data scraper function to get the material table
    material_data = retrieve_material_data(material_name)
    
    if material_data is not None and not material_data.empty:
        # First, try to find rows that mention "Yield Strength" directly
        yield_data = material_data[material_data['Properties'].str.contains("Yield Strength", case=False)]
        
        # If direct match is not found, use Levenshtein to find the closest match
        if yield_data.empty:
            # Find the closest match to "Yield Strength" using Levenshtein distance
            material_properties = material_data['Properties'].tolist()
            closest_match = min(material_properties, key=lambda prop: levenshtein_distance("Yield Strength", prop))
            print(f"Closest match found for Yield Strength: {closest_match}")
            yield_data = material_data[material_data['Properties'] == closest_match]

        # If yield strength data is available, return the metric value (assumed to be in MPa)
        if not yield_data.empty:
            try:
                # Extract the first numerical value from the Metric column and convert to Pascals (1 MPa = 1e6 Pa)
                yield_strength_mpa = yield_data['Metric'].str.extract('(\d+\.?\d*)').astype(float).iloc[0, 0]
                return yield_strength_mpa * 1e6  # Convert MPa to Pascals
            except Exception as e:
                print(f"Error extracting yield strength: {e}")
                return None
    else:
        print(f"No yield strength data found for {material_name}.")
        return None

# Main function to prompt the user for inputs and calculate hoop stress
def main():
    print("Hoop Stress and Flow Rate Calculator")
    
    # Default values
    default_flow_rate = 100  # m³/s
    default_Po = atm_to_pa(1)  # 1 atm in Pa
    default_Pi = atm_to_pa(10)  # 10 atm in Pa
    default_length = 100  # meters
    default_fluid = "Water"
    default_temperature = 298.15  # room temperature in K
    default_thickness = 0.01  # meters
    default_material = "Copper"
    default_safety_factor = 1.0  # Default safety factor set to 1.0

    # Inputs for hoop stress calculation with default values
    outer_diameter = float(input("Enter the outer diameter of the pipe (in meters) [default: 1]: ") or 1)
    thickness = float(input(f"Enter the thickness of the pipe (in meters) [default: {default_thickness}]: ") or default_thickness)
    length = float(input(f"Enter the length of the pipe (in meters) [default: {default_length}]: ") or default_length)
    fluid = input(f"Enter the fluid type [default: {default_fluid}]: ") or default_fluid
    temperature = float(input(f"Enter the fluid temperature (in K) [default: {default_temperature}]: ") or default_temperature)
    material = input(f"Enter the tubing material [default: {default_material}]: ") or default_material
    safety_factor = float(input(f"Enter the safety factor [default: {default_safety_factor}]: ") or default_safety_factor)
    
    # Get fluid viscosity based on fluid type and temperature
    fluid_viscosity = get_viscosity(fluid, temperature)
    
    # Optional input for external pressure with default value
    Po = float(input(f"Enter the external pressure (in Pa) [default: {default_Po} Pa]: ") or default_Po)
    
    # Calculate inner radius from outer diameter and thickness
    inner_radius = calculate_inner_radius(outer_diameter, thickness)
    mean_radius = (outer_diameter / 2 + inner_radius) / 2  # mean radius calculation
    
    # Inputs for flow rate calculation with default value
    flow_rate = float(input(f"Enter the flow rate (in m³/s) [default: {default_flow_rate}]: ") or default_flow_rate)
    
    # Internal pressure provided by the user
    Pi = float(input(f"Enter the internal pressure (in Pa) [default: {default_Pi} Pa]: ") or default_Pi)
    
    # Get bend radius and calculate correction factor if there are bends
    has_bend = input("Does the pipe have bends? (Y/N) [default: N]: ").lower() or "n"
    if has_bend == 'y':
        bend_radius = float(input("Enter the bend radius (in meters): "))
        correction_factor = calculate_correction_factor(bend_radius, thickness, mean_radius)
        print(f"Correction Factor: {correction_factor:.2f}")
    else:
        correction_factor = 1  # No bends, correction factor is 1
    
    # Calculate the hoop stress with correction factor
    hoop_stress = correction_factor * calculate_hoop_stress(Pi, Po, outer_diameter, thickness)
    
    # Retrieve yield strength from the scraper
    yield_strength = get_yield_strength_from_scraper(material)
    
    # Apply safety factor to yield strength
    if yield_strength is not None:
        adjusted_yield_stress = yield_strength / safety_factor

        # Print results and check if the pipe will burst
        print(f"\nCalculated Hoop Stress (adjusted for bends): {hoop_stress:.2f} Pa")
        print(f"Material Yield Strength: {yield_strength:.2f} Pa")
        print(f"Adjusted Yield Strength (with Safety Factor): {adjusted_yield_stress:.2f} Pa")

        if hoop_stress > adjusted_yield_stress:
            print("Warning: The design fails. The calculated stress exceeds the adjusted yield stress.")
        else:
            print("Success: The design passes. The calculated stress is within the adjusted yield stress.")
    else:
        print(f"Warning: Yield strength data for {material} could not be retrieved. Please check the material.")

if __name__ == "__main__":
    main()
