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
my_dataframe = session.table("smoothies.public.fruit_options").select(col('Fruit_name'))

# Display data as a dataframe
st.dataframe(data=my_dataframe, use_container_width=True)

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

# API request to fruityvice.com
fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")

if fruityvice_response.status_code == 200:
    # Convert JSON response to dictionary
    fruit_info = fruityvice_response.json()
    
    # Display fruit info
    st.write("Information about Watermelon from Fruityvice API:")
    st.write(fruit_info)
    
    # Check if 'nutritions' field exists in the response
    if 'nutritions' in fruit_info:
        # Extract nutritions data from the response
        nutritions_data = fruit_info['nutritions']
        
        # Prepare data for st.dataframe
        nutritions_df_data = {
            'Nutrient': list(nutritions_data.keys()),
            'Value': list(nutritions_data.values())
        }
        
        # Display nutritions data as a dataframe using st.dataframe
        st.write("Nutritional Information:")
        st.dataframe(data=nutritions_df_data, use_container_width=True)
else:
    st.error(f"Failed to fetch data from Fruityvice API. Status code: {fruityvice_response.status_code}")
