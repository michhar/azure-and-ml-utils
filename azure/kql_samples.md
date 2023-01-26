# Kusto Query Language Examples

## Check Python and package versions

The following creates a function to check Python version and specific Python package versions.

```
.create function with (folder = "Packages\\Utils", docstring = "Returns version information for the Python engine and the specified packages")
get_modules_version_sf(modules:(*))
{
    let code =
    'import importlib\n'
    'import sys\n'
    '\n'
    'result = df\n'
    'for i in range(df.shape[0]):\n'
    '    try:\n'
    '        m = importlib.import_module(df.iloc[i, 0])\n'
    '        result.loc[i, "ver"] = m.__version__ if hasattr(m, "__version__") else "missing __version__ attribute"\n'
    '    except Exception as ex:\n'
    '        result.loc[i, "ver"] = "ERROR: " + (ex.msg if hasattr(ex, "msg") else "exception, no msg")\n'
    'id = df.shape[0]\n'
    'result.loc[id, df.columns[0]] = "Python"\n'
    'result.loc[id, "ver"] = sys.version\n';
    modules
    | evaluate python(typeof(*, ver:string), code)
}

let get_modules_version_sf = (modules:(*))
{
    let code =
    'import importlib\n'
    'import sys\n'
    '\n'
    'result = df\n'
    'for i in range(df.shape[0]):\n'
    '    try:\n'
    '        m = importlib.import_module(df.iloc[i, 0])\n'
    '        result.loc[i, "ver"] = m.__version__ if hasattr(m, "__version__") else "missing __version__ attribute"\n'
    '    except Exception as ex:\n'
    '        result.loc[i, "ver"] = "ERROR: " + (ex.msg if hasattr(ex, "msg") else "exception, no msg")\n'
    'id = df.shape[0]\n'
    'result.loc[id, df.columns[0]] = "Python"\n'
    'result.loc[id, "ver"] = sys.version\n';
    modules
    | evaluate python(typeof(*, ver:string), code)
};

datatable(module:string)
['numpy', 'scipy', 'pandas', 'statsmodels', 'sklearn', 'tensorflow', 'keras']
| invoke get_modules_version_sf()
```