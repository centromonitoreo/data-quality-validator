# data-quality-validator

This project validates thematic datasets using different data sources. The `ValidationEngine`
can read data from a file geodatabase or from a PostgreSQL database.

## Using the PostgreSQL reader

The `reader` argument of `ValidationEngine` accepts the value `"postgres_reader"`.
Pass a PostgreSQL connection string through the parameter `pg_conn_string` or set
the environment variable `PG_DATABASE_URL`.

Example:

```python
from src.main import validate_data

result = validate_data(
    "Flora",
    "database_rule_reader",
    "delete_strategy",
    "postgres_reader",
    pg_conn_string="postgresql://user:pass@host/dbname",
)
```


