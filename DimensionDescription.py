import adsk.core
import adsk.fusion
import adsk.cam
import traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        
        if not design:
            ui.messageBox('No active Fusion design')
            return
            
        # Get selected components
        selections = ui.activeSelections
        components = []
        
        if selections.count > 0:
            # Process selected components
            for i in range(selections.count):
                selection = selections.item(i)
                if selection.entity.objectType == adsk.fusion.Occurrence.classType():
                    components.append(selection.entity)
        else:
            # If no selections, process all occurrences
            root = design.rootComponent
            components = root.allOccurrences
            
        if len(components) == 0:
            ui.messageBox('No components selected or found in the design')
            return
            
        # Process each component
        updatedCount = 0
        for component in components:
            # Get the component's bounding box
            bbox = component.boundingBox
            
            if bbox and bbox.isValid:
                # Calculate dimensions in mm (multiplying by 10 to convert from cm)
                length = round((bbox.maxPoint.x - bbox.minPoint.x) * 10, 2)
                width = round((bbox.maxPoint.y - bbox.minPoint.y) * 10, 2)
                height = round((bbox.maxPoint.z - bbox.minPoint.z) * 10, 2)
                
                # Sort dimensions to match conventional L > W > H
                dimensions = sorted([length, width, height], reverse=True)
                
                # Format dimensions string
                dim_str = f"L: {dimensions[0]}mm, W: {dimensions[1]}mm, H: {dimensions[2]}mm"
                
                # Update description
                current_description = component.component.description
                
                # Check if dimensions are already in the description
                if "L:" in current_description and "W:" in current_description and "H:" in current_description:
                    # Replace the existing dimensions
                    import re
                    updated_description = re.sub(r'L: [\d\.]+mm, W: [\d\.]+mm, H: [\d\.]+mm', dim_str, current_description)
                else:
                    # Append the dimensions to the existing description
                    if current_description and current_description.strip():
                        updated_description = f"{current_description}\n{dim_str}"
                    else:
                        updated_description = dim_str
                
                # Set the updated description
                component.component.description = updated_description
                updatedCount += 1
        
        ui.messageBox(f'Updated dimensions for {updatedCount} component(s)')
            
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    pass