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
            # Add to the add-ins menu with try/except to handle potential errors
            try:
                addInsPanel = modelWS.toolbarPanels.itemById('SolidScriptsAddinsPanel')
                if addInsPanel:
                    addInsPanel.controls.addCommand(cmdDef)
            except:
                pass  # Continue even if we can't add to the panel
            
            # Add to browser context menu
            try:
                contextPanel = modelWS.toolbarPanels.itemById('InspectPanel')
                if contextPanel:
                    contextPanel.controls.addCommand(cmdDef)
            except:
                pass  # Continue even if we can't add to the panel
        
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
                    # Calculate dimensions in mm (multiplying by 10 to convert from cm to mm)
                    length = (bbox.maxPoint.x - bbox.minPoint.x) * 10
                    width = (bbox.maxPoint.y - bbox.minPoint.y) * 10
                    height = (bbox.maxPoint.z - bbox.minPoint.z) * 10

                    # Sort dimensions 
                    dimensions = sorted([length, width, height], reverse=True)

                    # Format with consistent decimal places
                    dim_str = f"L: {dimensions[0]:.1f}mm, W: {dimensions[1]:.1f}mm, H: {dimensions[2]:.1f}mm"
                    
                    # Completely replace the description with the dimensions
                    component.component.description = dim_str
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