import os
import pandas as pd
from sqlalchemy import create_engine

db_url = os.getenv('DATABASE_URL', 'postgresql://de_user:de_password@localhost:5432/de_assignment')
engine = create_engine(db_url)

def run_pipeline():
    print("Starting ETL pipline")

    # load csv data
    categories = pd.read_csv('data/categories.csv')
    groceries = pd.read_csv('data/groceries.csv')

    # split each category into levels and expand them into new columns
    cat_split = categories['category'].str.split('/', expand=True)
    cat_split.columns = ['cat_level_1', 'cat_level_2', 'cat_level_3']

    # create a new table with the new columns
    items_mapped = pd.concat([categories['item'], cat_split], axis=1)
    items_mapped.rename(columns={'item': 'item_name'}, inplace=True)

    groceries['date'] = pd.to_datetime(groceries['date'], dayfirst=True)

    visits = groceries[['member_id', 'date']].drop_duplicates().reset_index(drop=True)
    visits.rename(columns={'date': 'visit_date'}, inplace=True)
    # visits['visit_id'] = visits.index + 1

    # insert DFs into the DB
    # members table
    groceries[['member_id']].drop_duplicates().to_sql('members', engine, if_exists='append', index=False)

    # visits table
    visits.to_sql('visits', engine, if_exists='append', index=False)

    # items and categories table
    items_mapped.to_sql('items', engine, if_exists='append', index=False)

    # sales table
    db_visits = pd.read_sql('select id as visit_id, member_id, visit_date from visits', engine)
    db_visits['visit_date'] = pd.to_datetime(db_visits['visit_date'])

    sales = pd.merge(
        groceries, 
        db_visits, 
        left_on=['member_id', 'date'], 
        right_on=['member_id', 'visit_date']
    )

    sales_final = sales[['visit_id', 'item']].rename(columns={'item':'item_name'})
    sales_final.to_sql('sales', engine, if_exists='append', index=False)

    print("Data successfully loaded into PostgreSQL")

    # Task no.1
    frequent_members_query = """
    select member_id, count(visit_date) as num_of_visits
    from visits 
    group by member_id
    order by count(visit_date) desc
    limit 10
    """
    df_frequent = pd.read_sql(frequent_members_query, engine)
    print("\n========================================================")
    print("# 1. Find the most frequent members")
    print(df_frequent)

    # Task no.2
    most_bought_items_query = """
    select item_name, count(visit_id) as times_bought
    from sales
    group by item_name
    order by count(visit_id) desc
    limit 10
    """
    df_bought_items = pd.read_sql(most_bought_items_query, engine)
    print("\n========================================================")
    print("# 2. Find the most bought items")
    print(df_bought_items)

    # Task no.3
    biggest_cart_query = """
    select s.visit_id, v.visit_date, v.member_id, count(s.item_name) as num_of_items
    from sales as s
    left join visits as v on s.visit_id = v.id
    group by s.visit_id, v.visit_date, v.member_id
    order by count(s.item_name) desc
    limit 10
    """
    df_biggest_cart = pd.read_sql(biggest_cart_query, engine)
    print("\n========================================================")
    print("# 3. Find the biggest cart in the database (= the largest number of items bought together)")
    print(df_biggest_cart)

    # Task no.4
    query = """
    select item_name
    from items
    where cat_level_1 = 'Meat-Seafood'
    """
    df_query = pd.read_sql(query, engine)
    print("\n========================================================")
    print("# 4. Find all the products under a category (e.g. `Meat-Seafood`)")
    print(df_query)

    # Task no.5
    query = """
    select cat_level_2, cat_level_3
    from items
    where cat_level_1 = 'Dairy-Eggs-Cheese'
    """
    df_query = pd.read_sql(query, engine)
    print("\n========================================================")
    print("# 5. Find all the first-level children of a category (e.g. `Dairy-Eggs-Cheese`)")
    print(df_query)

if __name__ == "__main__":
    run_pipeline()
