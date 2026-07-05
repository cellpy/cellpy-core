# Thoughts and possible issues

## Thoughts and ideas

### BDF format

Read and export in BDF format; should it be a part of cellpy-core, or should it be a part of another repo (cellpy-io)?

Idea: create a folder called scripts in cellpy-core repo and put it there for now. Then we can decide later where to finally put it.


### Ordered headers

Consider adding explicit ordering to the headers, e.g.

```python

class RawCols(Cols):
    __column_order__ = (
        "datapoint_num", "source_datapoint_num", "mask", ...
    )

    @classmethod
    def ordered_names(cls) -> list[str]:
        cols = cls()
        return [getattr(cols, name) for name in cls.__column_order__]

```



## Do we have an Issue?

### Syntax warning

When importing `cellpycore` using jupyterlab with python 3.14 we got this message:

```
C:\scripting\cellpy-core\src\cellpycore\legacy\mock_core.py:66: SyntaxWarning: 'return' in a 'finally' block
  return df

```

