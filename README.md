# Fusion 360 Add Dimensions to Description

A Fusion 360 add-in that automatically adds bounding box dimensions (Length, Width, Height) to component descriptions.

## Overview

This add-in creates a command in Fusion 360 that calculates the bounding box dimensions of selected components and adds them to the component description in a standardized format (L: XXmm, W: XXmm, H: XXmm). Dimensions are sorted so that Length > Width > Height, following conventional notation.

## Features

- Adds or updates component dimensions in the description field
- Automatically sorts dimensions (Length > Width > Height)
- Works with single or multiple component selections
- Updates existing dimension information if already present
- Converts dimensions to millimeters

## Installation

1. Download the repository as a ZIP file or clone it
2. In Fusion 360, go to the **Scripts and Add-Ins** dialog (under **Tools** tab)
3. Select the **Add-Ins** tab and click the green "+" icon
4. Navigate to and select the folder containing this add-in
5. Click **Run** to start the add-in

## Usage

1. Select one or more components in your design
2. Click the **Add Dimensions to Description** command in the Inspect panel or right-click menu
3. The dimensions will be added to each component's description

## How It Works

The add-in:
1. Gets the bounding box for each selected component
2. Calculates the length, width, and height dimensions
3. Sorts the dimensions to follow the convention where Length > Width > Height
4. Updates the component description with the formatted dimension string
5. If dimensions already exist in the description, they are updated rather than duplicated

## Requirements

- Fusion 360 (2018 or newer)

## Known Issues

- Length and width values might need to be corrected in some cases depending on your model orientation
