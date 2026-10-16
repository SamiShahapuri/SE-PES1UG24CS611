# Lab 5: Issues Found

**Name:** Sami Shahapuri  
**Project:** Food Delivery Order Management System

## Issues Identified and Fixes

| Issue | Type | Description | Fix Approach |
|---|---|---|---|
| Mutable default argument (Pylint W0102) | Bug | A default list used for order history can be shared across function calls, causing order IDs to accumulate unexpectedly. | Changed the default to `None` and append only when a history list is provided. |
| Unsafe pickle deserialization (Bandit B301) | Security | Loading serialized data using `pickle.load()` can execute malicious code if the file is untrusted. | Replaced pickle-based backup and restoration with JSON serialization. |
| Unnecessary pickle import (Bandit B403) | Security | Importing pickle was unnecessary after switching to JSON and could encourage unsafe deserialization. | Removed the pickle import and used the JSON module. |
| Broad exception handling and silent failure (Bandit B110) | Bug / Security | Catching exceptions and silently ignoring them can hide errors and make debugging difficult. | Removed the silent exception-handling pattern and handled specific file and JSON errors where needed. |
| Invalid customer or empty order | Bug | Empty customer names or orders without items could be accepted, creating invalid orders. | Added validation and raise `ValueError` for invalid input. |
| Unknown menu items | Bug | An item that is absent from the menu could cause an error or produce an incorrect order total. | Check that each item exists in the menu before calculating its price. |
| Invalid order status | Bug | Unsupported status values could be assigned to orders. | Added validation against the permitted order statuses. |
| Global state management (Pylint W0603) | Design | Rebinding global variables makes functions harder to test and maintain. | Updated existing dictionaries in place with `clear()` and `update()` instead of rebinding them. |
| File handling and encoding (Pylint W1514 / R1732) | Reliability | Files opened without an explicit encoding or context manager can cause inconsistent text handling or leave files open after errors. | Used `with open(...)` and explicitly specified `encoding="utf-8"`. |
| Missing docstrings (Pylint C0114 / C0116) | Style | Missing module and function documentation makes the code harder to understand. | Added a module docstring and docstrings for functions. |
| Naming and formatting issues (Pylint / Flake8) | Style | Naming conventions, indentation, blank lines, and long lines reduced readability and produced static-analysis warnings. | Used snake_case names, consistent indentation, appropriate blank lines, and wrapped long statements. |
| Inefficient dictionary iteration (Pylint C0206) | Style | Iterating over dictionary keys and then looking up each value adds unnecessary lookups. | Used `.items()` or `.values()` where appropriate. |
| Script executes when imported | Design | Running the demonstration directly at module level causes it to execute even when another module imports it. | Added an `if __name__ == "__main__":` guard. |

## Static Analysis Results

| Tool | Before | After |
|---|---|---|
| Pylint | See `pylint_report_before.txt` | **10.00/10** |
| Bandit | See `bandit_report_before.txt` | **0 findings** |
| Flake8 | See `flake8_report_before.txt` | **0 warnings** |

## Conclusion

Static analysis helped identify security risks, potential bugs, design concerns, and style problems in the original food delivery program. The code was updated to address these findings and then checked again with Pylint, Bandit, and Flake8. The final checks reported a Pylint score of 10.00/10, no Bandit findings, and no Flake8 warnings.
