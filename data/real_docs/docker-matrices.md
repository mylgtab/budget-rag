A matrix strategy lets you fork a single target into multiple different
variants, based on parameters that you specify. This works in a similar way to
Matrix strategies for GitHub Actions.
You can use this to reduce duplication in your Bake definition.

The matrix attribute is a map of parameter names to lists of values. Bake
builds each possible combination of values as a separate target.

Each generated target must have a unique name. To specify how target names
should resolve, use the name attribute.

The following example resolves the app target to app-foo and app-bar . It
also uses the matrix value to define the target build stage.

[code example]

[code example]

## Multiple axes

You can specify multiple keys in your matrix to fork a target on multiple axes.
When using multiple matrix keys, Bake builds every possible variant.

The following example builds four targets:

- app-foo-1-0 
- app-foo-2-0 
- app-bar-1-0 
- app-bar-2-0 

[code example]

## Multiple values per matrix target

If you want to differentiate the matrix on more than just a single value, you
can use maps as matrix values. Bake creates a target for each map, and you can
access the nested values using dot notation.

The following example builds two targets:

- app-foo-1-0 
- app-bar-2-0 

[code example]