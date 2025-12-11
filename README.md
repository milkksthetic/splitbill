# SplitBill - A Bill Splitting Website
#### Video Demo:  [SplitBill - A Bill Splitting Website](https://youtu.be/wGrF7kDmYsg?si=o8tm3eiD5yX-fskh)

## Table of Contents
- [Description](#description)
- [Project Structure](#project-structure)
- [Functionality](#functionality)
- [Database Schema](#database-schema)
- [Design Choices](#design-choices)
- [Additional Ideas](#additional-ideas)
- [Conclusion](#conclusion)
- [Acknowledgements](#acknowledgements)

## Description

**SplitBill** is a web application designed to aid the management of shared expenses among users in Malaysia. This application allows users to create bills, add items with their associated costs, and share these costs among multiple users. It provides a clear overview of who owes what, making it an ideal tool for friends or anyone who shares expenses. This application is built using Flask, a lightweight web framework in Python, and utilises SQLite for data storage.

## Project Structure
This project consists of several files and directories, each serving their own purpose:

- **app.py**: This is the main application file that contains the Flask application instance and the routes for handling user requests. It manages the flow of data between the front-end and the database, ensuring that the user's actions are processed correctly. The routes are as followed in the table:

### Routes in app.py
*Note: The table below was made with the assistance of AI summarisation, which was then edited by me.*

| Route            | Method        | Description                                      | Parameters                                                                 | Response                                      |
|------------------|---------------|--------------------------------------------------|---------------------------------------------------------------------------|-----------------------------------------------|
| `/` | `GET` | Displays the dashboard of the logged-in user. | None | Renders the `index.html` template with user data. |
|   |   | <br> |
| `/login` | `GET`, `POST` | Logs the user into their account. | `username`: The username of the user.<br>`password`: The password of the user. | Renders the `login.html` template on GET; redirects to the home page on successful login. |
| `/logout` | `GET` | Logs the user out of their account. | None | Redirects to the login page with a flash message. |
| `/register` | `GET`, `POST` | Allows new users to create an account. | `username`: The desired username.<br>`password`: The desired password.<br>`confirmation`: Confirmation of the password. | Renders the `register.html` template on GET; redirects to the home page on successful registration. |
| `/changepassword`| `GET`, `POST` | Allows users to change their password. | `current_password`: The user's current password.<br>`new_password`: The new password.<br>`confirmation`: Confirmation of the new password. | Renders the `changepassword.html` template on GET; redirects to the home page on successful password change. |
|   |   | <br> |
| `/friends` | `GET` | Displays the user's friends and pending requests. | None | Renders the `friends.html` template with friend data. |
| `/addfriend` | `POST` | Sends a friend request to another user by username. | `username`: The username of the friend to add. | Redirects to the friends page with a flash message. |
| `/acceptfriend` | `POST` | Accepts a pending friend request. | `friend_id`: The ID of the friend whose request is being accepted. | Redirects to the friends page with a flash message. |
| `/removefriend`  | `POST` | Removes a friend from the user's friend list.   | `friend_id`: The ID of the friend to remove. | Redirects to the friends page with a flash message. |
|   |   | <br> |
| `/newbill` | `GET`, `POST` | Allows users to create a new bill and add items.| `bill_name`: The name of the bill.<br>`category`: The category of the bill.<br>`paid_by`: The user ID of the person who paid.<br>`item_count`: The number of items being added. | Renders the `newbill.html` template on GET; redirects to the bill details page on successful creation. |
| `/billdetails` | `GET` | Displays the details of a specific bill. | `bill_id`: The ID of the bill to display. | Renders the `billdetails.html` template with bill and item data. |
| `/settlebills` | `POST` | Updates the payment status of selected bills. | `bills`: A list of bill IDs to mark as paid. | Redirects to the home page. |
<br><br>
- **helpers.py**: This file describes the utility functions used in the application, which are error handling, user authentication, and currency formatting.
<br><br>
- **templates/**: This directory contains all the HTML tempaltes used to render the web pages. Each template is designed to provide a user-friendly interface for the user to interact with the application.
  <br><br>
  - **layout.html**: The base template that defines the voerall structure of the web pages, including the header, footer, and links to CSS, Javascript, Icon and Bootstrap files. Other templates extend this layout to maintain a consistent look and feel across the application.
  <br><br>
  - **index.html**: The homepage of the application, where users can see an overview of:
    - The grand summary of the amount they are owed by others and the amount they owe to others.
    - The table for bills with pagination links.
    - The table for current friends and pending requests.
  <br><br>
  - **newbill.html**: The form for creating a new bill, allowing users to input bill details and add items dynamically.
  - **billdetails.html**: This template displays detailed information about a specific bill, including the bill name, items, total amount, paid by, and who owes what.
  <br><br>
  - **friends.html**: The page where the users can see an overview of their current friends, pending requests, outgoing requests and option to add new friends.
  - **login.html**: The login page for users to access their account.
  - **register.html**: The registration page for new users to create an account.
  - **changepassword.html**: The page for users to change their passwords.
  <br><br>
  - **apology.html**: The page that shows the users a specified error message and HTTP status code.
  <br><br>

- **static/**: This directory contain staic files which are CSS and icons.
  - **styles.css**: Custom CSS styles that makes a design that resembles the GitHub Dark Default theme for the application.

  - **favicon.ico**: The favicon for the website, providing a visual identity in the brower tab, which is a receipt.
<br><br>

- **requirements.txt**: This text file lists all the Python packages required to run the application.

## Functionality
SplitBill offers several key functionalities:
1. **User Authentication**: Users can create accounts and log in to manage their bills securely. <br><br>
2. **Bill Creation**: Users can create new bills by providing a name, category, and who paid. They can also add multiple items to each bill, specifying the price and shared users for each item. <br><br>
3. **Cost Sharing**: The application calculates how much each user owes based on the items they are sharing. This proceeds to be shown on the bill details and grand summary of who owes what.<br><br>
4. **Friend Management**: Users can add friends, accept friend reqeust and remove friends. This functionality allows users to manage who they are sharing their bills with. <br><br>
5. **Password Management**: Users can change their passwords securely, ensuring that their accounts remain protected.
<br><br>


## Database Schema
*Note: The following tables were made with the assistance of AI summarisation, which was then edited by me.*

### Users Table

| Column Name | Data Type | Constraints                     | Description                          |
|-------------|-----------|---------------------------------|--------------------------------------|
| `id`        | INTEGER   | PRIMARY KEY AUTOINCREMENT NOT NULL | Unique identifier for each user.    |
| `username`  | TEXT      | NOT NULL UNIQUE                 | The username of the user, must be unique. |
| `hash`      | TEXT      | NOT NULL                        | The hashed password of the user.    |

**Purpose**: Stores user account information.
<br><br><br>

---

### Friends Table

| Column Name | Data Type | Constraints                     | Description                          |
|-------------|-----------|---------------------------------|--------------------------------------|
| `id`        | INTEGER   | PRIMARY KEY AUTOINCREMENT NOT NULL | Unique identifier for each friendship. |
| `user_id`   | INTEGER   | NOT NULL                        | The ID of the user who sent the friend request. |
| `friend_id` | INTEGER   | NOT NULL                        | The ID of the user who received the friend request. |
| `status`    | TEXT      | NOT NULL CHECK (status IN ('pending', 'accepted')) | The status of the friendship (pending or accepted). |

**Purpose**: Manages friendships between users.

**Relationships**:
- `user_id` and `friend_id` are foreign keys referencing the `users` table.
<br><br><br>

---

### Bills Table

| Column Name    | Data Type | Constraints                     | Description                          |
|----------------|-----------|---------------------------------|--------------------------------------|
| `id`           | INTEGER   | PRIMARY KEY AUTOINCREMENT       | Unique identifier for each bill.    |
| `name`         | TEXT      | NOT NULL                        | The name of the bill.               |
| `category`     | TEXT      | NOT NULL                        | The category of the bill.           |
| `total_amount` | DECIMAL(10,2) | NOT NULL                    | The total amount of the bill.       |
| `paid_by`      | INTEGER   | NOT NULL                        | The ID of the user who paid the bill. |
| `created_at`   | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP       | The timestamp when the bill was created. |
| `payment_status` | TEXT    | DEFAULT 'Unpaid'                | The payment status of the bill.     |

**Purpose**: Stores information about bills created by users.

**Relationships**:
- `paid_by` is a foreign key referencing the `users` table.
<br><br><br>

---

### Items Table

| Column Name | Data Type | Constraints                     | Description                          |
|-------------|-----------|---------------------------------|--------------------------------------|
| `id`        | INTEGER   | PRIMARY KEY AUTOINCREMENT       | Unique identifier for each item.    |
| `bill_id`   | INTEGER   | NOT NULL                        | The ID of the bill to which the item belongs. |
| `name`      | TEXT      | NOT NULL                        | The name of the item.               |
| `price`     | DECIMAL(10,2) | NOT NULL                    | The price of the item.              |

**Purpose**: Stores individual items associated with bills.

**Relationships**:
- `bill_id` is a foreign key referencing the `bills` table.
<br><br><br>

---

### Splits Table

| Column Name | Data Type | Constraints                     | Description                          |
|-------------|-----------|---------------------------------|--------------------------------------|
| `id`        | INTEGER   | PRIMARY KEY                     | Unique identifier for each split.    |
| `user_id`   | INTEGER   | NOT NULL                        | The ID of the user who owes a portion of the bill. |
| `bill_id`   | INTEGER   | NOT NULL                        | The ID of the bill being split.     |
| `amount`    | REAL      |                                 | The amount owed by the user.        |
| `item_id`   | INTEGER   |                                 | The ID of the item associated with the split (if applicable). |

**Purpose**: Manages the distribution of bill amounts among users.

**Relationships**:
- `user_id` is a foreign key referencing the `users` table.
- `bill_id` is a foreign key referencing the `bills` table.
- `item_id` is a foreign key referencing the `items` table.
<br><br><br>

---
<br>


## Design Choices
Several design choices were made during the development of this application:
- **Framework Selection**: Flask was chosen for its simplicity and flexibility, which allows for rapid development. This choice helped me  implement the required features without unnecessary complexity. <br><br>

- **Database Stucture**: SQLite was selected as the database for its ease of use. The database schema was designed to efficiently handle bills, items and user relationships. <br><br>

- **User Interface**: Bootstrap was used for styling to ensure a responsive and modern design. It came with pre-built components that enhance the user experience and reduce development time. The dark theme was chosen to align with the GitHub Dark Default theme design of the application, improving readability. <br><br>

- **Dynamic Item Addition**: JavaScript was used to implement the ability to dynamically add items to a bill in the newbill.html, allowing users to input multiple items without refreshing the page, creating a smoother experience. <br><br>

- **Security Measures**: Passwords are hashed using Werkzeug's security functions to ensure that users' passwords are stored securely. Additionally, session management is implemented to maintain user authentication throughout their intereaction with the application. <br><br>

## Additional Ideas
I originally wanted the web application to be able to add the names of non-registered users but I figured it was unnecessary. In the future, I would also like to include functions such as:
- Other currencies.
- Option to forego tax, and include different type of taxes.
- Notifications for due amounts.
- Ability to change password if the user forgets their password.
- Option to select groups of friends that are frequent sharers of bills.
<br><br>

## Conclusion
SplitBill is a useful tool for managing shared expenses among users in Malaysia, designed with user experience and functionality in mind. The project demonstrates the application of web development principles learnt in CS50, showcasing the integration of front-end and back-end technologies.

## Acknowledgements
I would like to give special thanks to the CS50 course for providing the foundational knowledge necessary to develop this web application. The open-source community has also been invaluable in providing resources and libraries that facilitates web development. I also acknowledge the use of ChatGPT, Blackbox AI, DeepSeek and Cursor AI which assisted in decision making, debugging, generating code snippets, explanations, and documentation throughout the development of this project. The essence of the work is my own, and I have reviewed and modified the AI-generated content.

