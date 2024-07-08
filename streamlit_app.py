import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title("Customize your smoothie :cup_with_straw:")
st.write("Choose the Fruit which you want in your smoothie")

# Text input for Name on Smoothie
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Get active session and retrieve data
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('Fruit_name'),col('SEARCH_ON'))


# Display data as a dataframe
st.dataframe(data=my_dataframe, use_container_width=True)
st.stop()

# Multiselect for choosing ingredients with max selection limit
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients",
    my_dataframe,  # Directly use the DataFrame column as options
    max_selections=5  # Limit the maximum selections to 5
)

# Check if ingredients are selected
if ingredients_list:
    # Join selected ingredients into a string
    ingredients_string = ', '.join(ingredients_list)

    # Remove trailing space
    ingredients_string = ingredients_string.strip()
    for fruit_chosen in ingredients_list:
	    ingredients_string += fruit_chosen + ' '
	    st.subheader(fruit_chosen + ' Nutrition Information')
	    fruityvice_response = requests.get("https://fruityvice.com/api/fruit/"+ fruit_chosen)
	    fv_df = st.dataframe(data = fruityvice_response.json(), use_container_width = True)

    # Button to submit the order
time_to_insert = st.button('Submit Order')

    # Execute SQL statement if button is clicked
if time_to_insert:
        # Construct SQL INSERT statement
        my_insert_stmt = """INSERT INTO smoothies.public.orders(ingredients, name_on_order)
                            VALUES ('{}', '{}')""".format(ingredients_string, name_on_order)

        # Execute the SQL statement
        session.sql(my_insert_stmt).collect()

        # Display success message
        st.success('Your Smoothie is ordered for {}! 🥤'.format(name_on_order))
