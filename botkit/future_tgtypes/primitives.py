from pydantic import constr

Username = constr(regex=r"\@?[a-zA-Z0-9_]{5,33}", strip_whitespace=True)
