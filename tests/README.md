# Tests

## Running Tests
```bash
cd backend
python -m pytest ../tests/ -v
```

## Test Structure
| File | Description |
|------|-------------|
| test_new_prompt.py | Prompt engine tests |

## Adding Tests
1. Create `test_<module>.py` in this directory
2. Follow pytest conventions
3. Use fixtures for common setup
4. Cover both success and error cases
