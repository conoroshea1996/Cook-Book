# The CookBook

A socailly website for user to put up there own recipes in which others can like the recipe 

## UX

*User Stories:*
As a user of the recipe cookbook I should be able to do the following things:
* Look through all of the current recipes on the site in a simple way
* Search the recipes by keywords and other filters such as cusine,skill etc....
* Ability to sign up and login with with own username and password
* Add recipes to the site when I have logged in or sign up  
* Have full CRUD functionality when I am logged in. So it is possible to update, delete and edit a users own recipe
* Get a more detailed view of each recipe where I can see ingredients and how to make it.
* Like recipes

## Current Features
*Register and  Login*
* A user can sign up and create a new account. 
* The password of the user is hased before its stored in the database
* Username and password are checked to make sure its the corect user
* Once the user is logged in there nav will change giving them access to extra features

*Recipes*
* A user can look through all the current recipes in the data base

*Single Recipe*
* Where a user can view a more detailed view of the recipe.
* Info such as ingredients and instruction can be viewed here.

*Like Button*
* Once a user is logged in they have the ability to like a recipe
* the number of liked is displayed in the recipe page based on how many users have liked the recipe

*Add and Edit Recipes*
* A form input which allows the user to add a recipe to the database.
* HTML form validation used to make sure the required fields cant be empty
* The same form is used to edit and updated the recipe.

*Delete a Recipe*
* The user can delete there own recipes which they have created 


## Technologies Used

#### Python
* Provides the logic for this site


#### Flask
* Template langauge that provides all the routes and redirects for this projects web pages

#### Jinja
* To implement python code into html files

#### Pymongo
* Pymongo was used for interacting with MongoDB database from Python


