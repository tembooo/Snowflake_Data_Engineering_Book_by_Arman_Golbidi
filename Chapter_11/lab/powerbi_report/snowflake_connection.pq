// TEMPLATE ONLY: replace account identifier, warehouse, database, schema, relation.
// Power Query implementation details and availability must be checked in installed product.
let
  Source = Snowflake.Databases(
    "YOUR_ACCOUNT_IDENTIFIER.snowflakecomputing.com",
    "BI_WH", [Implementation="2.0", Role="BI_READER"]
  ),
  Database = Source{[Name="FINLAND_ENERGY_DEMO", Kind="Database"]}[Data],
  Schema = Database{[Name="GOLD", Kind="Schema"]}[Data],
  Fact = Schema{[Name="FCT_ENERGY_HOURLY", Kind="Table"]}[Data]
in
  Fact
