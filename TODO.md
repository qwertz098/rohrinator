# Basic Idea

Ich möchte eine Webapp zur Erzeugung von 3D Modellen von Rohrformstücken, meist bestehend aus Flanschen (vorschweißflansche), Rohrabschnitten, Anschweißmuffen, Bögen, T-Stücken und Reduzierstücken. UI and backend sollen getrennt sein, um die Funktionen bzw. UI später größeren Kontext nutzen zu können.

# Software Features

\[\] support ANSI and ISO flanges of the whole ranges (diameter, pressure) to select from, have the whole library in code not as models  
\[\] the pipe diameters are chosen depending on the flange of the pipe configuration section, if there are different flanges selected reducing parts need to be included and positioned  
\[\] user can chose wall thickness of pipe (see rohr.pdf) according to the flange rating and diameter connected to
\[\] implement a library of weld-on sleeves dimensions, see DB_Stahlschweissmuffen.pdf
\[\] selection of elbow design with 2x, 3x or 5x pipe diameter as the bending radius
\[\] UI desktop and mobile use, reactive design

# standards to be implemented

\[\] if not all information requested below is available on the internet prepare the tables to be filled later and populate with some example data

## flanges

\[\] ASME B16.5	Pipe Flanges and Flanged Fittings: NPS ½ to 24 	Class 150, 300, 600, 900, 1500, 2500
\[\] ISO 7005-1	Metallic flanges – Part 1: Steel flanges 	PN 2.5 to PN 400, DN 10–4000
\[\] EN 1092-1	Steel flanges, PN designated PN 2.5–400, DN 10–4000

## pipes

Wanddicken nach DIN EN 10253–2
Wanddicken / Schedule nach ASME B 36.10
Wanddickenreihen ASME B 36.19 Stainless Steel (Edelstahl–rostfrei) Reihen 5S, 10S, 40S, 80S

## other

### Carbon Steel

```
[] 90° Elbow 2D: EN 10253-1 Type A
[] 90° Elbow 3D: EN 10253-1 Type A
[] 90° Elbow 5D: EN 10253-1 Type A​
[] 45° Elbow 2D: EN 10253-1 Type A​
[] 45° Elbow 3D: EN 10253-1 Type A​
[] Concentric Reducer: EN 10253-1 Type A​
[] Eccentric Reducer: EN 10253-1 Type A​
[] Equal Tee: EN 10253-1 Type A​
[] Reducing Tee: EN 10253-1 Type A​
[] 90° Elbow LR/SR: ASME B16.9​
[] 45° Elbow: ASME B16.9​
[] Concentric Reducer: ASME B16.9​
[] Eccentric Reducer: ASME B16.9​
[] Equal Tee: ASME B16.9​
[] Reducing Tee: ASME B16.9​
```

### Low Alloy Steel

```
[] 90° Elbow 2D: EN 10253-2 Type A
[] 90° Elbow 3D: EN 10253-2 Type A
[] 90° Elbow 5D: EN 10253-2 Type A​
[] 45° Elbow 2D: EN 10253-2 Type A​
[] 45° Elbow 3D: EN 10253-2 Type A​
[] Concentric Reducer: EN 10253-2 Type A
[] Eccentric Reducer: EN 10253-2 Type A
[] Equal Tee: EN 10253-2 Type A​
[] Reducing Tee: EN 10253-2 Type A​
[] 90° Elbow 2D: EN 10253-2 Type B
[] 90° Elbow 3D: EN 10253-2 Type B​
[] Concentric Reducer: EN 10253-2 Type B​
[] Equal Tee: EN 10253-2 Type B
```

### Austenitic Stainless Steel

```
[] 90° Elbow 2D: EN 10253-3 Type A
[] 90° Elbow 3D: EN 10253-3 Type A​
[] 45° Elbow 2D: EN 10253-3 Type A​
[] Concentric Reducer: EN 10253-3 Type A​
[] Eccentric Reducer: EN 10253-3 Type A​
[] Equal Tee: EN 10253-3 Type A​
[] Reducing Tee: EN 10253-3 Type A​
[] 90° Elbow 2D: EN 10253-3 Type B​
[] 90° Elbow 3D: EN 10253-3 Type B​
```

### Duplex Stainless Steel

```
[] 90° Elbow 2D: EN 10253-4 Type A
[] 90° Elbow 3D: EN 10253-4 Type A​
[] 90° Elbow 5D: EN 10253-4 Type A​
[] 45° Elbow 2D: EN 10253-4 Type A​
[] Concentric Reducer: EN 10253-4 Type A​
[] Eccentric Reducer: EN 10253-4 Type A​
[] Equal Tee: EN 10253-4 Type A​
[] Reducing Tee: EN 10253-4 Type A​
[] 90° Elbow 2D: EN 10253-4 Type B
```

# Technicals

\[\] select english for all code comments, variables names and so on
\[\] modular design of the propgram to be maintainable by humans (have separate files to generate flanges, sleeves, ...)
\[\] use pyhon for the backend, maybe a framework
\[\] cadquery for generating the model and generate exports to different file formats like *.step
\[\] talk with me about other design decissons to be made
\[\] To reuse the functionality in a wider design system i suggest implementing the ui to backend interface via api. We should talk about api framework, use one if it comes with an api test page for Endpoints. And data format to be exchanged, like JSON or XML. Prefer human readable stuff

# App flow

 1. user is asked for some info, like project, designation, description
 2. select ratings, material and configuration (straight, elbow, U-shaped, T-shaped for now)
 3. select the flanges at the ends of the pipes and their positions in space, starting with one flange face as the origin, position in space is for a straight basically the flanges face distance
 4. select where the reducer(s) should sit (if different flange diameters)
 5. size piping material according to pressure rating
 6. user to select how many (if any) weld-on sleeves per pipe section shall be placed and on what angle (propose every 45° around the pipe) and axial position (measured from the individual flange of that pipe section)
 7. misc technical setting: just the welding gap (distance between later to weld parts like the weld-on flanges chamfer and the pipe chamfer) for now, more maybe later
 8. start generating the model wehen button pressed. If modifications made after model generation, colour the modified field with an alarming colour. Return to normal after regeneration
 9. the user can download the model after previewing in step format
10. The user can backup the configuration made (zip file incl. a more or less structured text file with the config, text file with the cadquery code to be run externally incl. requirements.txt and export functions setup, a step file of the model)
11. You can download a BOM listing all elbows, tees, flanges, pipe material, ... to be sourced later

# how to run the project

\[\] implement the model generating backend first
\[\] implement tests for every feature being implemented and run
\[\] generate example step models for all types of flanges, transition sections and weld-on sleeves and ask the user (me) for feedback and ok before proceeding, create a parts folder for this
\[\] generate example step models based on the following configurations, select pressure rating, diameter and standard by yourself, vary over the examplesand ask the user (me) for feedback and ok before proceeding, create a examples forder for this
\[\] straight, elbow 45, elbow 90, T-type, U-type examples without weld-on sleeve, section dimension in range of 0.2 to 3m
\[\] straight, elbow 45, elbow 90, T-type, U-type  with two different weld-on sleeves, first one on angle 0° in the middle of the respective section, second at 135° 0.1m from the initial flange
\[\] implement API test calls along with the api documentation page and test
\[\] implement the ui in a reusable way to be reused later within a wider context of a more complex app, maybe separate files/settings/... for late reuse with other frames and windows
\[\] implement a cadquery code inspector for later debugging reason parallel to the main user UI with the app flow, can be made visible during app usage

# UI

\[\] the app flow shall be kind of linear, but shall allow the user to go back to former decisions and keeping as much settings as possible, so keep it on one page
\[\] implement a 3D preview (maybe three.js) presenting the generated model
\[\] updating, dynamic UI, with now page reload needed for changing number of elements, ...
\[\] appearance technical
\[\] use mockups in ./mockups

# Setting your behavior

- inform me as soon as your context reaches about 50%

# Explanation of the pipe configurations

'''
|...Flange horizontal
\_...Flange vertical
=...horizontal pipe
‖...vertical pipe
T...T-Section
elbows:
Top-left: ┌ (U+250C)​
Top-right: ┐ (U+2510)​
Bottom-left: └ (U+2514)​
Bottom-right: ┘ (U+2518)
Sections of the pipes are indicated A,B,C
'''

## straight

'''
|=====|
'''

## elbow

'''
\_
‖
‖B
‖
|=====┘
A
'''

## T-shape

'''
A       B
|=====T===|
‖
‖C
‖
\_
'''

## U-shaped

'''
A
|=====┐
‖
‖B
‖
|===┘
C
'''