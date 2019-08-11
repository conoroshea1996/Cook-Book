from flask import Flask, render_template, request, url_for, redirect, session, flash
import os
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt
import random
import re
import datetime

from flask_paginate import Pagination, get_page_parameter

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'task_manager'
app.config["MONGO_URI"] = os.environ.get('MONGO_URI')
app.secret_key = 'secret_key'

mongo = PyMongo(app)

"""
Helper Functions
"""


def defaultImage(image):
    if image:
        return image
    else:
        return 'https://mamadips.com/wp-content/uploads/2016/11/defimage.gif'


def defaultUserImage(image):
    if image:
        return image
    else:
        return 'https://image.shutterstock.com/image-vector/male-user-account-profile-flat-260nw-274504883.jpg'


@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        username = session['username']
    else:
        username = ''
    return render_template('index.html', user=username)


@app.route('/test')
def test():

    return render_template('test.html')


"""
Checks if user is in database then check passwords match
"""


@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name': request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            flash('Password does not match username', 'error')
            return redirect(url_for('index'))
    else:
        flash("We sorry but this username doesn't seem to exist", 'error')
        return redirect(url_for('index'))


"""
Clears session
"""


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


"""
Check if user already exist if not adds user
"""


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(
                request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert(
                {'name': request.form['username'], 'password': hashpass, 'avatar': defaultUserImage(request.form.get('avatar'))})
            session['username'] = request.form['username']
            return redirect(url_for('index'))

        flash('User already exist try something else', 'error')
        return redirect(url_for('index'))

    return render_template('register.html')


"""
Get all recipes and display them
"""


@app.route('/recipes')
def get_recipes():
    if 'username' in session:
        username = session['username']
    else:
        username = ''

    cusine_filter = request.args.get('cusine')
    skill_filter = request.args.get('skill')
    recipes = mongo.db.Recipes.find()

    if cusine_filter and skill_filter == 'Choose...':
        recipes = mongo.db.Recipes.find(
            {'cusine': cusine_filter})
    elif cusine_filter and skill_filter:
        recipes = mongo.db.Recipes.find(
            {'cusine': cusine_filter, 'skill': skill_filter})

    if skill_filter and cusine_filter == 'Choose...':
        recipes = mongo.db.Recipes.find(
            {'skill': skill_filter})

    per_page = 6
    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = Pagination(page=page, total=recipes.count(), per_page=per_page,
                            search=False, record_name='recipes', css_framework='bootstrap4', alignment='center')
    recipe_page = recipes.skip((page - 1) * per_page).limit(per_page)

    return render_template('recipes.html', recipe=recipe_page, pagination=pagination, skill=mongo.db.skill.find(), orgin=mongo.db.cusine.find(), user=username)


"""
Gets recipes of current user in session
"""


@app.route('/users_recipes')
def users_recipes():
    if 'username' in session:
        username = session['username']
    else:
        username = ''

    per_page = 3
    page = request.args.get(get_page_parameter(), type=int, default=1)
    recipes = mongo.db.Recipes.find({'userid': username})
    pagination = Pagination(page=page, total=recipes.count(), per_page=per_page,
                            search=False, record_name='recipes', css_framework='bootstrap4', alignment='center')

    recipe_page = recipes.skip((page - 1) * per_page).limit(per_page)
    return render_template('usersRecipes.html', recipe=recipe_page, pagination=pagination, skill=mongo.db.skill.find(), orgin=mongo.db.cusine.find(), user=username)


@app.route('/add_recipe')
def add_recipe():
    if 'username' not in session:
        return render_template('error404.html')

    if 'username' in session:
        username = session['username']
    else:
        username = ''

    return render_template('addrecipe.html', skill=mongo.db.skill.find(), orgin=mongo.db.cusine.find(), vegan=mongo.db.vegan.find(), user=username)


"""
Inserts recipe into database
"""


@app.route('/insert_recipe', methods=['POST'])
def insert_recipe():
    recipes = mongo.db.Recipes
    recipes.insert_one({
        'name': request.form.get('name'),
        'skill': request.form.get('skill'),
        'cusine': request.form.get('cusine'),
        'recipe_des': request.form.get('recipe_des'),
        'image': defaultImage(request.form.get('image')),
        'ingredients': request.form.get('ingredients'),
        'instuctions': request.form.get('instuctions'),
        'tags': request.form.get('tags'),
        'vegan': request.form.get('vegan'),
        'userid': session['username']
    })

    return redirect(url_for('get_recipes'))


"""
Gets single recipe by id and displays more information
"""


@app.route('/single/<recipe_id>')
def recipe_info(recipe_id):
    if 'username' in session:
        username = session['username']
    else:
        username = ''

    randomcolors = ['info', 'primary', 'danger', 'success', 'warning']
    recipe = mongo.db.Recipes.find_one_and_update(
        {'_id': ObjectId(recipe_id)},
        {'$inc': {'hits': 1}}
    )
    votes = mongo.db.votes
    current_recipe = mongo.db.votes.find_one({'recipeId': recipe_id})

    if current_recipe in votes.find():
        pass
    else:
        votes.insert({
            'recipeId': recipe_id,
            'users': []
        })

    likes = mongo.db.votes.find_one({'recipeId': recipe_id})
    num_likes = len(likes['users'])
    if num_likes > 0:
        total_likes = len(likes['users'])
    else:
        total_likes = 0

    return render_template('recipeInfo.html', recipeInfo=recipe, colors=randomcolors, user=username, likes=total_likes, userlike=likes)


"""
Adds object to comments array
"""


@app.route('/comments/<recipe_id>', methods=['POST'])
def add_coment(recipe_id):
    users = mongo.db.users
    current = users.find_one({'name': session['username']})

    if request.method == 'POST':
        recipe = mongo.db.Recipes
        thisrecipe = mongo.db.Recipes.find_one({'_id': ObjectId(recipe_id)})
        recipe.update(
            {'_id': ObjectId(recipe_id)},
            {'$push': {'comments': {
                'userid': session['username'],
                'comments': request.form.get('comment'),
                'date': datetime.datetime.now(),
                'avatar': current['avatar']
            }}}
        )
        return redirect(url_for('recipe_info', recipe_id=recipe_id))


"""
Deletes recipe from database
"""


@app.route('/delete_recipe/<recipe_id>')
def delete_recipe(recipe_id):
    recipes = mongo.db.Recipes.find()

    mongo.db.Recipes.remove({'_id': ObjectId(recipe_id)})
    return redirect(url_for('get_recipes'))


@app.route('/edit_recipe/<recipe_id>')
def edit_recipe(recipe_id):
    if 'username' not in session:
        return render_template('error404.html')

    if 'username' in session:
        username = session['username']
    else:
        username = ''

    recipe = mongo.db.Recipes.find_one({'_id': ObjectId(recipe_id)})
    return render_template('editrecipe.html', recipeInfo=recipe, skill=mongo.db.skill.find(), orgin=mongo.db.cusine.find(), vegan=mongo.db.vegan.find(), user=username)


"""
Updates Recipes
"""


@app.route('/update_recipe/<recipe_id>', methods=['POST'])
def update_recipe(recipe_id):
    recipe = mongo.db.Recipes
    thisrecipe = mongo.db.Recipes.find_one({'_id': ObjectId(recipe_id)})

    def staySame(value, string):
        if value:
            return value
        else:
            return thisrecipe[string]

    recipe.update({'_id': ObjectId(recipe_id)}, {
        'name': staySame(request.form.get('name'), 'name'),
        'skill': request.form.get('skill'),
        'image': staySame(request.form.get('image'), 'image'),
        'cusine': request.form.get('cusine'),
        'recipe_des': request.form.get('recipe_des'),
        'ingredients': request.form.get('ingredients').strip(),
        'instuctions': request.form.get('instuctions').strip(),
        'tags': request.form.get('tags'),
        'vegan': request.form.get('vegan'),
        'userid': session['username']
    })
    return redirect(url_for('get_recipes'))


"""
Filters recipes that contain keyword using regex
"""


@app.route('/filter_recipes', methods=['GET', 'POST'])
def filter_recipes():
    recipe = mongo.db.Recipes
    if 'username' in session:
        username = session['username']
    else:
        username = ''

    if request.method == 'POST':
        skill = request.form.get('skill')
        cusine = request.form.get('cusine')
        search_text = request.form.get('query')

        """ THANKS TO MY MENTOR SPENCER FOR HELPING ME WITH SEARCH QUERY LOGIC  """
        query = {'$regex': re.compile(
            '.*{}.*'.format(search_text)), '$options': 'i'}

        recipes = recipe.find({'$or':
                               [
                                   {'name': query},
                                   {'tags': query},
                                   {'ingredients': query}
                               ]
                               })

    recipeValues = recipes.count()

    return render_template('filter.html', recipe=recipes, user=username, count=recipeValues, query=query, search=search_text)


"""
Like recipes
"""


@app.route('/vote/<recipe_id>')
def vote(recipe_id):
    recipe = mongo.db.Recipes
    thisrecipe = mongo.db.Recipes.find_one({'_id': ObjectId(recipe_id)})
    votes = mongo.db.votes
    user = mongo.db.users.find_one({'name': session['username']})

    current_recipe = mongo.db.votes.find_one({'recipeId': recipe_id})

    if current_recipe in votes.find():
        pass
    else:
        votes.insert({
            'recipeId': recipe_id,
            'users': []
        })

    if session['username'] in current_recipe['users']:
        votes.update({'recipeId': recipe_id}, {
                     '$pull': {'users': session['username']}})
    else:
        votes.update(
            {'recipeId': recipe_id},
            {'$push': {'users': session['username']}}
        )

    if 'username' in session:
        username = session['username']
    else:
        username = ''

    randomcolors = ['info', 'primary', 'danger', 'success', 'warning']

    return redirect(url_for('recipe_info', recipe_id=recipe_id))


"""
Renders 404 page if 404 error
"""


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error404.html'), 404


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=os.environ.get('PORT'), debug=False)
