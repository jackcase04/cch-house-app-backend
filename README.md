# CCH App Backend

This repo stores all the backend logic for the repo https://github.com/jackcase04/cch-house-app. It has multiple  GET endpoints: An endpoint to fetch all the chores for all users, an endpoint to fetch all chores corresponding to a users name, an endpoint to get a single chore corresponding to a users name and a date, and an endpoint to get all the names from the database. The endpoints are protected by an API key.

## Technologies Used

Backend: PostgreSQL, Python, Flask
Deployment: Railway

## Process

A significant obstacle in creating this app was parsing the complicated chore sheet into a format that could be imported into a PostgreSQL database (CSV format). The chore sheet has people look at a sheet corresponding to their side of the house with their room and names for the week, then go over and look at another sheet to see what chore they have for the day. I created a working sheet that pulls the cells of each name (each name corresponds to 2 chore "events", having a name, date, and chore description). Then from there slowly pull all the data depending on those cells so that each chore "event" was accounted for. In the end, they are exported into a final sheet with each chore "event" that can be exported as a CSV file.

I also exported each name into a CSV file.

From there I could simply copy the data from the CSV files into the PostgreSQL database seamlessly.

I then connect to the database in the app.py file using environment variables. This way, it can be tested on localhost and then deployed without changing anything.

I also used Swagger to test the endpoints.
