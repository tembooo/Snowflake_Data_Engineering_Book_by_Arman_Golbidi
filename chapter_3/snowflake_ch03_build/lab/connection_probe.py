"""Interactive Snowflake test. NOT RUN here; requires approved Snowflake access.

Only for human interactive development accounts supporting external-browser SSO.
Never insert password / token / private keys into this file.
"""
import os


def main():
    account = os.environ["SNOWFLAKE_ACCOUNT"]
    user = os.environ["SNOWFLAKE_USER"]
    import snowflake.connector  # install in a reviewed virtual environment

    with snowflake.connector.connect(
        account=account,
        user=user,
        authenticator="externalbrowser",
        role="BOOK_CH03_READER",
        warehouse="BOOK_CH03_XS",
        database="BOOK_CH03_DEV",
        schema="LAB",
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT CURRENT_ROLE(), CURRENT_REGION()")
            role, region = cursor.fetchone()
            if role.upper() != "BOOK_CH03_READER":
                raise RuntimeError("Unexpected Snowflake role; stop and investigate")
            print(f"Authenticated with expected role; region={region}")


if __name__ == "__main__":
    main()
