# GlyphsMultipolation
Extention for the Glyphs app. With this script you can handle complex interpolations and any amount of axes.

### Showcase latest version: RobotoFlex v2
https://github.com/Manuel87/RobotoFlex

### Install
1. Move the “multipolation.min.py” to the script folder of Glyphs.
2. Now it is executable in Glyphs via: Script > Metapolation :)

### Features
- Infinte numbers of Axes
- Infinite numbers of Masters on one Axis
- An axis can be already added by adding only one Master
- Custom value-scales + simple math (e.g. "none+20", "half", "full", "min", "max-100", ...)
- Master-Relations, allowing multiple “Roots" (e.g. Root > Bold > Bold Inktraps)
- x- and y-interpolation
- Local interpolations (allowing different interpolation values for specified glyphs)
- Extrapolation
- Custom Parameters for Instances
- ...

### Todo
- Integration as a Custom Parameter in Glyphs Font Info (getting rid of the extra spec file)
- Interface (Setup, Slider, Knobs, ...)
- Full integration of complex axes (axes relations, math, switches, ...)
  - integration of the new, more descriptive syntax (NewMarkup folder)
- Direct export as a variable  font (though the variable font spec has to catch up with features)

### Predecessor
https://github.com/Manuel87/ExperimentalParametricTypeface
