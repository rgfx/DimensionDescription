import adsk.core
import adsk.fusion
import adsk.cam
import traceback

# Global variables to maintain command handler references
app = None
ui = None
handlers = []

def run(context):
    try:
        global app, ui
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Create command definition
        commandDefinitions = ui.commandDefinitions
        cmdDef = commandDefinitions.itemById('addDimensionsToDescriptionCmd')
        if not cmdDef:
            cmdDef = commandDefinitions.addButtonDefinition(
                'addDimensionsToDescriptionCmd', 
                'Add Dimensions to Description', 
                'Adds bounding box dimensions (L, W, H) to the component description'
            )
        
        # Connect to the command created event
        onCommandCreated = CommandCreatedEventHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)
        
        # Get workspace and add to the MODEL workspace context menu
        workspaces = ui.workspaces
        modelWS = workspaces.itemById('FusionSolidEnvironment')

        if modelWS:
            # Add to component context menu

            
            modelWS.toolbarPanels.itemById('AssemblePanel').controls.addCommand(cmdDef)
            
            # Add to browser context menu
            contextPanel = modelWS.toolbarPanels.itemById('InspectPanel')
            if contextPanel:
                contextPanel.controls.addCommand(cmdDef)
        
        # Keep the add-in loaded when the script completes execution
        adsk.autoTerminate(False)
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            


# CommandCreatedEventHandler for the command
class CommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
        
    def notify(self, args):
        try:
            # Get the command
            cmd = args.command
            
            # Add a handler to trigger when the command is executed
            onExecute = CommandExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)
            
        except:
            ui = adsk.core.Application.get().userInterface
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# CommandExecuteHandler for when the command is executed
class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
        
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            design = adsk.fusion.Design.cast(app.activeProduct)
            
            if not design:
                ui.messageBox('No active Fusion design')
                return
            
            # Get selected components from the active selections
            selections = ui.activeSelections
            components = []
            
            if selections.count > 0:
                # Process selected components
                for i in range(selections.count):
                    selection = selections.item(i)
                    if selection.entity.objectType == adsk.fusion.Occurrence.classType():
                        components.append(selection.entity)
            else:
                ui.messageBox('No components selected. Please select at least one component.')
                return
                
            if len(components) == 0:
                ui.messageBox('No valid components selected')
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
                    dimensions = sorted([width, length, height], reverse=True)  # Reorder here
                    
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
            ui = adsk.core.Application.get().userInterface
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Remove the command definition
        cmdDef = ui.commandDefinitions.itemById('addDimensionsToDescriptionCmd')
        if cmdDef:
            cmdDef.deleteMe()
            
        # Clear all event handlers
        handlers.clear()
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))