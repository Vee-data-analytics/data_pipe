import pandas as pd
import pcbflow as pbf


class MyPCB(pbf.PCB):
    def __init__(self, pick_and_place_data):
        super().__init__()
        
        # Define the board outline (for example, 100mm x 80mm)
        self.add_outline(pbf.Rect(100, 80))
        
        # Define footprints for different component types
        self.footprints = {
            'Capacitor': self.create_capacitor_footprint,
            'Resistor': self.create_resistor_footprint,
            'IC': self.create_ic_footprint
        }
        
        # Iterate over the pick-and-place data to add components
        for index, row in pick_and_place_data.iterrows():
            refdes = row['Designator']
            pos_x = row['Center-X']
            pos_y = row['Center-Y']
            rotation = row['Rotation']
            component_type = row['1st Vendor Part No']
            
            # Add the component using the appropriate footprint function
            if component_type in self.footprints:
                self.footprints[component_type](refdes, pos_x, pos_y, rotation)
            else:
                print(f"Unknown component type: {component_type}")

    def create_capacitor_footprint(self, refdes, x, y, rotation):
        # Example capacitor footprint: two pads
        self.add(pbf.Pad(refdes, pbf.Disc(x - 1, y, 1.5), pbf.Copper(), rotation=rotation))
        self.add(pbf.Pad(refdes, pbf.Disc(x + 1, y, 1.5), pbf.Copper(), rotation=rotation))

    def create_resistor_footprint(self, refdes, x, y, rotation):
        # Example resistor footprint: two rectangular pads
        self.add(pbf.Pad(refdes, pbf.Rect(x - 1, y, 2, 1), pbf.Copper(), rotation=rotation))
        self.add(pbf.Pad(refdes, pbf.Rect(x + 1, y, 2, 1), pbf.Copper(), rotation=rotation))

    def create_ic_footprint(self, refdes, x, y, rotation):
        # Example IC footprint: a simple square pad
        self.add(pbf.Pad(refdes, pbf.Rect(x, y, 3, 3), pbf.Copper(), rotation=rotation))

# Load pick-and-place data
pick_and_place_data = pd.read_csv('Pick Place for dma_dart_v3_V1_0.csv')

# Create the PCB using the pick-and-place data
pcb = MyPCB(pick_and_place_data)
pcb.save('mypcb.kicad_pcb')  # Save as KiCad PCB file
