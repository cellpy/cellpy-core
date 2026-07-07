# Issue #112: make the unit conversion helper functions more user friendly

Source: https://github.com/cellpy/cellpy-core/issues/112

## Original issue text

Lets say I do `nom_cap_abs = calculate_nom_cap_abs_from_specific(3.579, 1.334)` (values taken directly from a cellpy session). What does it take as default units? It cannot know that 3.579 is in Ah/g and that 1.334 is in mg (as it is this time, since I used the default cellpy units). Another user might not use the default units. Does the function allow adding units, for example nom_cap_unit = "mA/g" etc.? Or can we use "3.579 mAh/g" etc.? I also suspect that the other helper functions struggle from the same "unclearity". Or is it only me who dont understand it properly?
