"""EXPLICITLY OPT-IN! Executes SELECT queries and incurs Snowflake charges.

Prerequisite: execute sql/optional_cloud_fixture.sql in THE SAME session.
Since that fixture uses TEMP tables (session-scoped), the convenient workflow is
run in a Snowpark worksheet with an injected session, or adapt the script to
execute SQL fixture statements through the SAME Session deliberately.

This script instead expects *existing approved conformed tables* (not TEMP
objects from another session); it never creates or destroys Snowflake objects.
"""
import os
from decimal import Decimal
from snowflake.snowpark import Session
from snowpark_pipeline import build_snowpark_dataframe

def main():
    if os.getenv('CH09_LIVE_APPROVED') != 'YES':
        raise SystemExit('Not running. Set CH09_LIVE_APPROVED=YES after approval.')
    name = os.environ['SNOWFLAKE_CONNECTION_NAME']
    source = os.environ['CH09_APPROVED_SOURCE_TABLE']
    dimension = os.environ['CH09_APPROVED_DIM_TABLE']
    session = Session.builder.config('connection_name', name).create()
    try:
        plan = build_snowpark_dataframe(session, source, dimension)
        rows = plan.collect()
        by_category = {r['CATEGORY']: Decimal(str(r['TOTAL_MWH'])) for r in rows}
        assert by_category == {'Renewable':Decimal('46.000'),
                               'OtherLowCarbon':Decimal('16.000'),
                               'Other':Decimal('4.000')}, by_category
        print('PASS: three categories, total=66.000 MWh (live integration)')
    finally:
        session.close()

if __name__ == '__main__':
    main()
